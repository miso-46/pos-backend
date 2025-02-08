from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from db_control import crud, mymodels
from pydantic import BaseModel
import json
from typing import List

# MySQLのテーブル作成
from db_control.create_tables import init_db

# アプリケーション初期化時にテーブルを作成
init_db()

app = FastAPI()

# CORSの設定 フロントエンドからの接続を許可する部分
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 許可するオリジン（フロントエンドのURL）
    allow_credentials=True, # Cookie や認証情報を許可
    allow_methods=["*"], # すべてのHTTPメソッド（GET, POST, PUT, DELETEなど）を許可
    allow_headers=["*"] # すべてのHTTPヘッダーを許可
)

# 購入データのリクエストモデルの型定義
class PurchaseItem(BaseModel):
    code: str  # 商品コード
    name: str  # 商品名
    price: int  # 商品単価
    quantity: int  # 購入数量

class PurchaseRequest(BaseModel):
    emp_cd: str = "9999999999"  # レジ担当者コード（デフォルト値あり）
    store_cd: str = "30"  # 店舗コード（固定値）
    pos_no: str = "90"  # POS機ID（固定値）
    items: List[PurchaseItem]  # 商品リスト


@app.get("/")
def root():
    return {"message": "Hello World"}

# 商品コードで検索して該当する商品情報を取得する
@app.get("/products/{code}")
def search_product(code: str):
    # CRUD 関数を呼び出して商品を検索
    result_json = crud.myselect(code)

    # JSON を Python のオブジェクトに変換
    result_obj = json.loads(result_json)

    # 商品が見つからない場合はエラーを返す
    if "error" in result_obj:
        error_message = result_obj["error"]
        
        # 商品が見つからない場合
        if error_message == "商品がマスタ未登録です":
            raise HTTPException(status_code=404, detail=error_message)
        # データベース関連のエラーの場合（500 Internal Server Error）
        elif error_message == "データベースエラーです":
            raise HTTPException(status_code=500, detail=error_message)
        # その他のエラー（400 Bad Request など）
        else:
            raise HTTPException(status_code=400, detail=error_message)

    return result_obj  # 商品情報を返す


# カートに入っている商品を購入する
@app.post("/purchase")
def purchase(request:PurchaseRequest):
    """
    購入処理：
    - 取引テーブルに新規レコード作成
    - 取引明細テーブルに購入商品の詳細を登録
    - 合計金額を計算し、取引情報を更新
    """
    try:
        total_amount = crud.save_purchase(request)
        return {"message": "購入完了", "total": total_amount}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"購入処理に失敗しました: {str(e)}")