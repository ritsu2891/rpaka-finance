#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
繰り返し予定入出金マスタから指定月の予定入出金を生成するスクリプト
"""

import argparse
import os
import sys
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv


def load_env():
    """環境変数を読み込む"""
    load_dotenv()
    return {
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT'),
        'database': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD')
    }


def get_db_connection(db_config):
    """データベース接続を取得"""
    try:
        conn = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['database'],
            user=db_config['user'],
            password=db_config['password']
        )
        conn.autocommit = False
        return conn
    except Exception as e:
        print(f"データベース接続エラー: {e}")
        sys.exit(1)


def get_target_year_month(months_offset):
    """対象年月を取得（現在月からのオフセット）"""
    if months_offset < 0:
        raise ValueError("過去の月は指定できません")
    
    today = datetime.now()
    target_date = today + relativedelta(months=months_offset)
    return target_date.year, target_date.month


def delete_existing_planned_cf(cursor, year, month):
    """対象月の既存の予定入出金（マスタ生成分）を削除"""
    delete_query = """
    DELETE FROM t_planned_cf 
    WHERE EXTRACT(YEAR FROM date) = %s 
      AND EXTRACT(MONTH FROM date) = %s 
      AND m_repeat_planned_cf_id IS NOT NULL
    """
    cursor.execute(delete_query, (year, month))
    deleted_count = cursor.rowcount
    print(f"削除された既存予定入出金件数: {deleted_count}")
    return deleted_count


def get_repeat_planned_cf_for_month(cursor, month):
    """指定月に発生する繰り返し予定入出金マスタを取得"""
    select_query = """
    SELECT 
        id,
        title,
        interval_type,
        month,
        day,
        amount,
        m_mf_category_l_id,
        m_mf_category_m_id,
        m_account_id,
        display_order
    FROM m_repeat_planned_cf 
    WHERE enable = TRUE 
      AND (
          (interval_type = 'yearly' AND month = %s) OR 
          (interval_type = 'monthly')
      )
    ORDER BY display_order
    """
    cursor.execute(select_query, (month,))
    return cursor.fetchall()

def generate_planned_cf_date(year, month, day):
    """予定入出金の日付を生成"""
    try:
        # 指定日が月末を超える場合は月末日に調整
        if day > 28:  # 2月を考慮
            from calendar import monthrange
            _, last_day = monthrange(year, month)
            if day > last_day:
                day = last_day
        
        return datetime(year, month, day).date()
    except ValueError as e:
        print(f"日付生成エラー: 年={year}, 月={month}, 日={day}, エラー={e}")
        raise


def insert_planned_cf(cursor, repeat_cf, target_year, target_month):
    """予定入出金レコードを挿入"""
    now = datetime.now()
    
    # 日付を生成
    planned_date = generate_planned_cf_date(target_year, target_month, repeat_cf['day'])
    
    insert_query = """
    INSERT INTO t_planned_cf (
        title,
        date,
        amount,
        m_mf_category_l_id,
        m_mf_category_m_id,
        m_account_id,
        m_repeat_planned_cf_id
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s
    )
    RETURNING id
    """
    
    cursor.execute(insert_query, (
        repeat_cf['title'],
        planned_date,
        repeat_cf['amount'],
        repeat_cf['m_mf_category_l_id'],
        repeat_cf['m_mf_category_m_id'],
        repeat_cf['m_account_id'],
        repeat_cf['id']
    ))
    
    result = cursor.fetchone()
    return result['id'] if result else None


def get_generated_planned_cf(cursor, year, month):
    """生成された予定入出金を取得して表示用に整形"""
    select_query = """
    SELECT 
        p.id,
        p.title,
        p.date,
        p.amount,
        l.title as category_l,
        m.title as category_m,
        a.title as account
    FROM t_planned_cf p
    LEFT JOIN m_mf_category_l l ON p.m_mf_category_l_id = l.id
    LEFT JOIN m_mf_category_m m ON p.m_mf_category_m_id = m.id
    LEFT JOIN m_account a ON p.m_account_id = a.id
    WHERE EXTRACT(YEAR FROM p.date) = %s 
      AND EXTRACT(MONTH FROM p.date) = %s 
      AND p.m_repeat_planned_cf_id IS NOT NULL
    ORDER BY p.date
    """
    cursor.execute(select_query, (year, month))
    return cursor.fetchall()


def print_generated_planned_cf(planned_cf_list, year, month):
    """生成された予定入出金を標準出力に表示"""
    print(f"\n=== {year}年{month}月の生成された予定入出金 ===")
    if not planned_cf_list:
        print("生成された予定入出金はありません。")
        return
    
    print(f"{'ID':>6} {'日付':>12} {'金額':>12} {'タイトル':>20} {'大項目':>15} {'中項目':>15} {'口座':>15}")
    print("-" * 120)
    
    total_amount = 0
    for cf in planned_cf_list:
        amount_str = f"{cf['amount']:,}" if cf['amount'] else "0"
        total_amount += cf['amount'] if cf['amount'] else 0
        date_str = cf['date'].strftime('%Y/%m/%d') if cf['date'] else ''
        
        print(f"{cf['id']:>6} {date_str:>12} {amount_str:>12} {cf['title']:>20} "
              f"{cf['category_l'] or '':>15} {cf['category_m'] or '':>15} {cf['account'] or '':>15}")
    
    print("-" * 120)
    print(f"{'合計':>31} {total_amount:,}")
    print(f"生成件数: {len(planned_cf_list)}件")


def process_repeat_planned_cf(months_offset):
    """繰り返し予定入出金の処理メイン"""
    print(f"繰り返し予定入出金生成処理開始（現在月+{months_offset}ヶ月）")
    
    # 環境変数の読み込み
    db_config = load_env()
    print(f"DB接続先: {db_config['host']}:{db_config['port']}/{db_config['database']}")
    
    # 対象年月の計算
    try:
        target_year, target_month = get_target_year_month(months_offset)
        print(f"対象年月: {target_year}年{target_month}月")
    except ValueError as e:
        print(f"エラー: {e}")
        sys.exit(1)
    
    # データベース接続
    conn = get_db_connection(db_config)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # 既存の予定入出金（マスタ生成分）を削除
        print("既存の予定入出金を削除中...")
        delete_existing_planned_cf(cursor, target_year, target_month)
        
        # 繰り返し予定入出金マスタを取得
        print("繰り返し予定入出金マスタを取得中...")
        repeat_cf_list = get_repeat_planned_cf_for_month(cursor, target_month)
        print(f"対象レコード数: {len(repeat_cf_list)}")
        
        if repeat_cf_list:
            # タイプ別の件数を表示
            yearly_count = sum(1 for cf in repeat_cf_list if cf['interval_type'] == 'yearly')
            monthly_count = sum(1 for cf in repeat_cf_list if cf['interval_type'] == 'monthly')
            print(f"  - 年次: {yearly_count}件")
            print(f"  - 月次: {monthly_count}件")
        
        if not repeat_cf_list:
            print("対象月に発生する繰り返し予定入出金マスタが見つかりません。")
            conn.commit()
            return
        
        # 繰り返し予定入出金から予定入出金を生成
        print("予定入出金を生成中...")
        generated_count = 0
        
        for repeat_cf in repeat_cf_list:
            try:
                planned_cf_id = insert_planned_cf(
                    cursor, repeat_cf, target_year, target_month,
                )
                
                if planned_cf_id:
                    generated_count += 1
                    interval_type_jp = "年次" if repeat_cf['interval_type'] == 'yearly' else "月次"
                    print(f"生成: {repeat_cf['title']} ({interval_type_jp}) (ID: {planned_cf_id})")
                
            except Exception as e:
                print(f"レコード生成エラー: {repeat_cf['title']}, エラー: {e}")
                raise
        
        # コミット
        conn.commit()
        print(f"生成完了: {generated_count}件")
        
        # 生成された予定入出金を取得して表示
        planned_cf_list = get_generated_planned_cf(cursor, target_year, target_month)
        print_generated_planned_cf(planned_cf_list, target_year, target_month)
        
    except Exception as e:
        print(f"処理中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        sys.exit(1)
    
    finally:
        cursor.close()
        conn.close()
        print("データベース接続を閉じました")


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description='繰り返し予定入出金マスタから指定月の予定入出金を生成する'
    )
    parser.add_argument(
        'months_offset', 
        nargs='?', 
        type=int, 
        default=0,
        help='現在月からの月数オフセット（デフォルト: 0=当月、負の値は不可）'
    )
    
    args = parser.parse_args()
    
    try:
        process_repeat_planned_cf(args.months_offset)
        print("処理が正常に完了しました")
    
    except Exception as e:
        print(f"予期しないエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()