import os
import urllib.parse
from dotenv import load_dotenv
from sqlalchemy import create_engine

# 環境変数の読み込み
load_dotenv()

# データベース接続情報
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = urllib.parse.quote(os.getenv("DB_PASSWORD")) # パスワードに＠が含まれるのでエンコード
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

# SSL証明書情報（AzureのDBと繋ぐ用）
DB_SSL_CA = os.getenv('DB_SSL_CA')

# MySQLのURL構築
if not DB_USER or not DB_PASSWORD or not DB_HOST or not DB_PORT or not DB_NAME or not DB_SSL_CA:
    raise ValueError("環境変数が不足しています。.envファイルを確認してください。")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# エンジンの作成
engine = create_engine(
    DATABASE_URL,
    echo=True, #SQLクエリのログを出力（デバッグ用）
    pool_pre_ping=True, #接続プールの管理（切断された接続を検出し、再接続を試みる）。本番環境では False にするのが一般的。
    pool_recycle=3600, # 接続プールの自動リサイクル（3600秒=1時間ごとに新しい接続を作成）
    connect_args={"ssl_ca": DB_SSL_CA} # AzureのSSL証明書DBと繋ぐ用
)
