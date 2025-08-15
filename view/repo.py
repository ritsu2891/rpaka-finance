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
    """m_budgetテーブルから予算タイトルを取得"""
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
            ym,
            title,
            ABS(amount_all) AS amount_all,
            ABS(amount_liquid) AS amount_liquid,
            ABS(amount_credit) AS amount_credit
        FROM v_budget
        """
        df = pd.read_sql_query(query, conn)
        budget_titles = fetch_budget_titles()
        df['title'] = pd.Categorical(df['title'], categories=budget_titles, ordered=True)
        df['ym_str'] = pd.to_datetime(df['ym']).dt.strftime("%Y/%m")
        df['ym_str'] = pd.Categorical(df['ym_str'], ordered=True)
        return df
    except Exception as e:
        raise Exception(f"データ取得エラー: {e}")
    finally:
        if conn:
            conn.close()

def fetch_inout_data():
    """c_inoutビューからデータを取得"""
    conn = None
    try:
        conn = get_connection()
        query = """
        SELECT
            ym,
            amount_all,
            amount_liquid,
            amount_credit,
            amount_all_calc,
            amount_income_all,
            amount_income_liquid,
            amount_income_credit,
            amount_income_all_calc,
            amount_outcome_all,
            amount_outcome_liquid,
            amount_outcome_credit,
            amount_outcome_all_calc
        FROM v_inout;
        """
        df = pd.read_sql_query(query, conn)
        df['ym_str'] = pd.to_datetime(df['ym']).dt.strftime("%Y/%m")
        df['ym_str'] = pd.Categorical(df['ym_str'], ordered=True)
        return df
    except Exception as e:
        raise Exception(f"データ取得エラー: {e}")
    finally:
        if conn:
            conn.close()

def fetch_budget_amount_status():
    """v_budget_amount_statusビューからデータを取得"""
    conn = None
    try:
        conn = get_connection()
        query = """
        SELECT
            title,
            set_amount,
            present_amount,
            remaining_amount,
            ratio_amount,
            planned_amount,
            present_planned_amount,
            remaining_planned_amount,
            ratio_planned_amount,
            set_amount_credit,
            present_amount_credit,
            remaining_amount_credit,
            ratio_amount_credit,
            planned_amount_credit,
            present_planned_amount_credit,
            remaining_planned_amount_credit,
            ratio_planned_amount_credit
        FROM v_budget_amount_status;
        """
        df = pd.read_sql_query(query, conn)
        budget_titles = fetch_budget_titles()
        df['title'] = pd.Categorical(df['title'], categories=budget_titles, ordered=True)
        return df
    except Exception as e:
        raise Exception(f"データ取得エラー: {e}")
    finally:
        if conn:
            conn.close()

def fetch_budget_total_amount_status():
    """v_budget_total_amount_statusビューからデータを取得"""
    conn = None
    try:
        conn = get_connection()
        query = """
        SELECT
            set_amount,
            present_amount,
            planned_amount,
            present_planned_amount,
            ratio_amount,
            ratio_planned_amount,
            projected_amount,
            set_amount_credit,
            present_amount_credit,
            planned_amount_credit,
            present_planned_amount_credit,
            ratio_amount_credit,
            ratio_planned_amount_credit,
            projected_amount_credit
        FROM v_budget_total_amount_status;
        """
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        raise Exception(f"データ取得エラー: {e}")
    finally:
        if conn:
            conn.close()