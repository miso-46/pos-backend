from sqlalchemy import String, Integer, CHAR, TIMESTAMP, ForeignKey, CheckConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """SQLAlchemy 2.0 の基盤となる Declarative Base"""
    pass

# 商品テーブル
class Product(Base):
    __tablename__ = "product"

    PRD_ID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)  # 商品一意キー
    CODE: Mapped[str] = mapped_column(CHAR(13), unique=True, nullable=False)  # 商品コード（13桁）
    NAME: Mapped[str] = mapped_column(String(50), nullable=False)  # 商品名称（最大50文字）
    PRICE: Mapped[int] = mapped_column(Integer, nullable=False)  # 商品単価（0以上）

    __table_args__ = (
        CheckConstraint('PRICE >= 0', name='check_price_positive'),
    )


# 取引テーブル
class Trade(Base):
    __tablename__ = "trade"

    TRD_ID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)  # 取引一意キー
    DATETIME: Mapped[str] = mapped_column(TIMESTAMP, nullable=False, server_default="CURRENT_TIMESTAMP")  # 取引日時
    EMP_CD: Mapped[str] = mapped_column(CHAR(10), nullable=False)  # レジ担当者コード
    STORE_CD: Mapped[str] = mapped_column(CHAR(5), nullable=False)  # 店舗コード
    POS_NO: Mapped[str] = mapped_column(CHAR(3), nullable=False)  # POS機ID
    TOTAL_AMT: Mapped[int] = mapped_column(Integer, nullable=False)  # 合計金額（0以上）

    __table_args__ = (
        CheckConstraint('TOTAL_AMT >= 0', name='check_total_amt_positive'),
    )


# 取引明細テーブル
class TradeDetail(Base):
    __tablename__ = "trade_detail"

    TRD_ID: Mapped[int] = mapped_column(Integer, ForeignKey("trade.TRD_ID"), primary_key=True)  # 取引一意キー（外部キー）
    DTL_ID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)  # 取引明細一意キー
    PRD_ID: Mapped[int] = mapped_column(Integer, ForeignKey("product.PRD_ID"), nullable=False)  # 商品一意キー（外部キー）
    PRD_CODE: Mapped[str] = mapped_column(CHAR(13), nullable=False)  # 商品コード（13文字）
    PRD_NAME: Mapped[str] = mapped_column(String(50), nullable=False)  # 商品名称（最大50文字）
    PRD_PRICE: Mapped[int] = mapped_column(Integer, nullable=False)  # 商品単価

    trade = relationship("Trade", backref="trade_details")  # Tradeとのリレーション
    product = relationship("Product", backref="trade_details")  # Productとのリレーション