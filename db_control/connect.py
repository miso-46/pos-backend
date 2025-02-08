from sqlalchemy import create_engine

import os
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# データベース接続情報
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

# MySQLのURL構築
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# エンジンの作成
engine = create_engine(
    DATABASE_URL,
    echo=True, #SQLクエリのログを出力（デバッグ用）
    pool_pre_ping=True, #接続プールの管理（切断された接続を検出し、再接続を試みる）。本番環境では False にするのが一般的。
    pool_recycle=3600 # 接続プールの自動リサイクル（3600秒=1時間ごとに新しい接続を作成）
)
