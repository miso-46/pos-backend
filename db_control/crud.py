from sqlalchemy.orm import sessionmaker
import json
from db_control.connect import engine
from db_control.mymodels import Product, Trade, TradeDetail

# 商品コードで検索して該当する商品情報を取得する
def myselect(code : str):
    # Session構築
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        # データを取得するだけなら with session.begin(): は不要
        # 商品は1つなので1件だけ取得
        product = session.query(Product).filter(Product.CODE == code).first()
        if product:
            # 結果をオブジェクトから辞書に変換し、リストに追加
            result_dict = {
                "code": product.CODE,
                "name": product.NAME,
                "price": product.PRICE
            }
            # JSON に変換（ensure_ascii=Falseで日本語などの非ASCII文字を Unicode エスケープせずにそのまま出力。）
            result_json = json.dumps(result_dict, ensure_ascii=False)
        else:
            # 商品が未登録の場合
            result_json = json.dumps({"error": "商品がマスタ未登録です"}, ensure_ascii=False)
    except Exception as e:
        print(f"Error fetching product: {e}")
        result_json = json.dumps({"error": "データベースエラーです"}, ensure_ascii=False)

    # セッションを閉じる
    finally:
        session.close()

    # jsonを返す
    return result_json


# カートに入っている商品を購入する
def save_purchase(request):
    """
    購入情報をデータベースに保存する
    - `request.items` に `{code, name, price, quantity}` のリストが含まれる
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        # 1. 取引（Trade）を作成
        new_trade = Trade(
            EMP_CD=request.emp_cd or "9999999999",
            STORE_CD=request.store_cd or "30",
            POS_NO=request.pos_no or "90",
            TOTAL_AMT=0  # 初期値は 0、後で更新
        )
        session.add(new_trade)
        session.commit()  # 取引 ID を取得するためにコミット

        trade_id = new_trade.TRD_ID  # 生成された取引IDを取得

        # 2. 取引明細（TradeDetail）を作成
        total_amount = 0
        for item in request.items:
            product = session.query(Product).filter(Product.CODE == item.code).first()
            if not product:
                raise ValueError(f"商品 '{item.name}' (コード: {item.code}) が見つかりません")

            # 取引明細の登録
            trade_detail = TradeDetail(
                TRD_ID=trade_id,
                PRD_ID=product.PRD_ID,
                PRD_CODE=item.code,
                PRD_NAME=item.name,
                PRD_PRICE=item.price
            )
            session.add(trade_detail)

            # 合計金額を計算
            total_amount += item.price * item.quantity

        # 3. 取引テーブルの合計金額を更新
        new_trade.TOTAL_AMT = total_amount
        session.commit()

        return total_amount  # フロントエンドに返す合計金額

    except ValueError as ve:
        session.rollback() #データベースの変更をすべて取り消す
        raise ve  # 商品が見つからない場合は 400 エラーを発生

    except Exception as e:
        session.rollback() #データベースの変更をすべて取り消す
        raise e  # その他のエラー（DBエラーなど）は 500 エラー

    finally:
        session.close()