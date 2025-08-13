import psycopg2
from dotenv import load_dotenv
import pandas as pd
import os

load_dotenv()

def get_connection():
    """データベース接続を取得"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        return conn
    except Exception as e:
        raise Exception(f"データベース接続エラー: {e}")

def fetch_budget_titles():
    conn = None
    try:
        conn = get_connection()
        query = """
        SELECT
            title
        FROM m_budget
        ORDER BY nc_order;
        """
        df = pd.read_sql_query(query, conn)
        return df['title']
    except Exception as e:
        raise Exception(f"データ取得エラー: {e}")
    finally:
        if conn:
            conn.close()

def fetch_budget_data():
    """v_budgetビューからデータを取得"""
    conn = None
    try:
        conn = get_connection()
        query = """
        SELECT 
            ym, title,
            ABS(amount_all) AS amount_all, ABS(amount_liquid) AS amount_liquid, ABS(amount_credit) AS amount_credit
        FROM v_budget
        """
        df = pd.read_sql_query(query, conn)

        budget_titles = fetch_budget_titles()
        df['title'] = pd.Categorical(df['title'], categories=budget_titles, ordered=True)

        # df['ym'] (Date)から"年/月"形式の文字列の列をカテゴリカル型として作成
        df['ym_str'] = pd.to_datetime(df['ym']).dt.strftime("%Y/%m")
        df['ym_str'] = pd.Categorical(df['ym_str'], ordered=True)

        return df
    except Exception as e:
        raise Exception(f"データ取得エラー: {e}")
    finally:
        if conn:
            conn.close()
