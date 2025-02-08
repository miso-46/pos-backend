from db_control.mymodels import Base
from db_control.connect import engine
from sqlalchemy import inspect


def init_db():
    # インスペクターを作成
    inspector = inspect(engine)

    # 既存のテーブルを取得
    existing_tables = inspector.get_table_names()

    print("Checking tables...")

    # すでにテーブルが存在するか確認
    required_tables = {'product', 'trade', 'trade_detail'}
    missing_tables = required_tables - set(existing_tables)

    # もしテーブルが存在しなかったら新規作成
    if missing_tables:
        print(f"Creating missing tables: {missing_tables}")
        try:
            Base.metadata.create_all(bind=engine)
            print("Tables created successfully!")
        except Exception as e:
            print(f"Error creating tables: {e}")
            raise
    else:
        print("All required tables already exist.")

if __name__ == "__main__":
    init_db()
