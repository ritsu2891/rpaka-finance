#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
収入・支出詳細CSVファイルをPostgreSQLのt_mf_cfテーブルに取り込むスクリプト
"""

print("スクリプト開始")

import argparse
import csv
import os
import sys
from datetime import datetime
from decimal import Decimal
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

print("ライブラリのインポート完了")

def load_env():
    """環境変数を読み込む"""
    load_dotenv()
    return {
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT'),
        'database': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'created_by': os.getenv('CREATED_BY', 'us0p0siaro4nkn0z'),
        'updated_by': os.getenv('UPDATED_BY', 'us0p0siaro4nkn0z')
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
        conn.autocommit = False  # トランザクション制御のため
        return conn
    except Exception as e:
        print(f"データベース接続エラー: {e}")
        sys.exit(1)

def get_max_nc_order(cursor, table_name):
    """指定テーブルの最大nc_order値を取得"""
    cursor.execute(f"SELECT COALESCE(MAX(nc_order), 0) FROM {table_name}")
    return cursor.fetchone()[0]

def get_account_id(cursor, account_name):
    """口座名からアカウントIDを取得"""
    cursor.execute("SELECT id FROM m_account WHERE title = %s", (account_name,))
    result = cursor.fetchone()
    return result[0] if result else None

def get_category_l_id(cursor, category_name):
    """大項目名から大項目IDを取得"""
    cursor.execute("SELECT id FROM m_mf_category_l WHERE title = %s", (category_name,))
    result = cursor.fetchone()
    return result[0] if result else None

def get_category_m_id(cursor, category_name):
    """中項目名から中項目IDを取得"""
    cursor.execute("SELECT id FROM m_mf_category_m WHERE title = %s", (category_name,))
    result = cursor.fetchone()
    return result[0] if result else None

def check_existing_record(cursor, mf_id):
    """既存レコードの確認"""
    cursor.execute("SELECT id FROM t_mf_cf WHERE mf_id = %s", (mf_id,))
    result = cursor.fetchone()
    return result[0] if result else None

def parse_csv_row(row):
    """CSVの行をパース"""
    return {
        'calc_target': row['計算対象'],
        'date': row['日付'],
        'title': row['内容'],
        'amount': row['金額（円）'],
        'account': row['保有金融機関'],
        'category_l': row['大項目'],
        'category_m': row['中項目'],
        'memo': row['メモ'],
        'transfer': row['振替'],
        'mf_id': row['ID']
    }

def validate_and_convert_data(cursor, row_data, row_num):
    """データの検証と変換"""
    errors = []
    
    # 口座IDの取得
    account_id = get_account_id(cursor, row_data['account'])
    if account_id is None:
        errors.append(f"口座「{row_data['account']}」がm_accountテーブルに存在しません")
    
    # 大項目IDの取得
    category_l_id = get_category_l_id(cursor, row_data['category_l'])
    if category_l_id is None:
        errors.append(f"大項目「{row_data['category_l']}」がm_mf_category_lテーブルに存在しません")
    
    # 中項目IDの取得
    category_m_id = get_category_m_id(cursor, row_data['category_m'])
    if category_m_id is None:
        errors.append(f"中項目「{row_data['category_m']}」がm_mf_category_mテーブルに存在しません")
    
    if errors:
        return None, errors
    
    # 日付の変換
    try:
        date_obj = datetime.strptime(row_data['date'], '%Y/%m/%d').date()
    except ValueError:
        errors.append(f"日付形式が不正です: {row_data['date']}")
        return None, errors
    
    # 金額の変換
    try:
        amount = Decimal(row_data['amount'])
    except ValueError:
        errors.append(f"金額形式が不正です: {row_data['amount']}")
        return None, errors
    
    return {
        'title': row_data['title'],
        'calc_target': row_data['calc_target'] == '1',
        'date': date_obj,
        'amount': amount,
        'account_id': account_id,
        'category_l_id': category_l_id,
        'category_m_id': category_m_id,
        'memo': row_data['memo'],
        'transfer': row_data['transfer'] == '1',
        'mf_id': row_data['mf_id']
    }, []

def insert_new_record(cursor, data, nc_order, created_by):
    """新規レコードの挿入"""
    now = datetime.now()
    
    insert_query = """
    INSERT INTO t_mf_cf (
        created_at, created_by, nc_order, title, calc_target, date, amount,
        m_account_id, m_mf_category_l_id, m_mf_category_m_id, memo, transfer, mf_id
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    )
    """
    
    cursor.execute(insert_query, (
        now, created_by, nc_order, data['title'], data['calc_target'],
        data['date'], data['amount'], data['account_id'],
        data['category_l_id'], data['category_m_id'],
        data['memo'], data['transfer'], data['mf_id']
    ))

def update_existing_record(cursor, existing_id, data, updated_by):
    """既存レコードの更新"""
    now = datetime.now()
    
    update_query = """
    UPDATE t_mf_cf SET
        updated_at = %s, updated_by = %s, title = %s, calc_target = %s,
        date = %s, amount = %s, m_account_id = %s, m_mf_category_l_id = %s,
        m_mf_category_m_id = %s, memo = %s, transfer = %s
    WHERE id = %s
    """
    
    cursor.execute(update_query, (
        now, updated_by, data['title'], data['calc_target'],
        data['date'], data['amount'], data['account_id'],
        data['category_l_id'], data['category_m_id'],
        data['memo'], data['transfer'], existing_id
    ))

def process_csv_file(csv_file_path):
    """CSVファイルを処理"""
    print(f"CSVファイル処理開始: {csv_file_path}")
    
    # 環境変数の読み込み
    print("環境変数を読み込み中...")
    db_config = load_env()
    print(f"DB接続先: {db_config['host']}:{db_config['port']}/{db_config['database']}")
    
    # データベース接続
    print("データベースに接続中...")
    conn = get_db_connection(db_config)
    cursor = conn.cursor()
    print("データベース接続成功")
    
    try:
        # 現在の最大nc_orderを取得
        print("最大nc_orderを取得中...")
        max_nc_order = get_max_nc_order(cursor, 't_mf_cf')
        next_nc_order = max_nc_order + 1
        print(f"次のnc_order: {next_nc_order}")
        
        # 処理結果の統計
        stats = {
            'processed': 0,
            'inserted': 0,
            'updated': 0,
            'errors': 0
        }
        
        # CSVファイルの読み込み
        print("CSVファイルを開いています...")
        with open(csv_file_path, 'r', encoding='shift_jis') as csvfile:
            reader = csv.DictReader(csvfile)
            print(f"CSVヘッダー: {reader.fieldnames}")
            
            for row_num, row in enumerate(reader, start=2):  # ヘッダーを除いて2行目から
                try:
                    stats['processed'] += 1
                    
                    # CSVデータのパース
                    row_data = parse_csv_row(row)
                    
                    # データの検証と変換
                    validated_data, validation_errors = validate_and_convert_data(cursor, row_data, row_num)
                    
                    if validation_errors:
                        print(f"エラー（{row_num}行目）: {', '.join(validation_errors)}")
                        stats['errors'] += 1
                        raise Exception(f"データ検証エラー（{row_num}行目）")
                    
                    # 既存レコードの確認
                    existing_id = check_existing_record(cursor, validated_data['mf_id'])
                    
                    if existing_id:
                        # 既存レコードを更新
                        update_existing_record(cursor, existing_id, validated_data, db_config['updated_by'])
                        stats['updated'] += 1
                        print(f"更新（{row_num}行目）: ID={validated_data['mf_id']}")
                    else:
                        # 新規レコードを挿入
                        insert_new_record(cursor, validated_data, next_nc_order, db_config['created_by'])
                        stats['inserted'] += 1
                        next_nc_order += 1
                        print(f"挿入（{row_num}行目）: ID={validated_data['mf_id']}")
                
                except Exception as e:
                    print(f"処理エラー（{row_num}行目）: {e}")
                    stats['errors'] += 1
                    conn.rollback()
                    return stats
        
        # 全ての処理が正常に完了した場合、コミット
        conn.commit()
        print("\n=== 処理完了 ===")
        print(f"処理済み行数: {stats['processed']}")
        print(f"新規挿入: {stats['inserted']}")
        print(f"更新: {stats['updated']}")
        print(f"エラー: {stats['errors']}")
        
        return stats
        
    except Exception as e:
        print(f"処理中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        return stats
    
    finally:
        cursor.close()
        conn.close()
        print("データベース接続を閉じました")

def main():
    """メイン関数"""
    print("メイン関数開始")
    try:
        print("argparseを初期化中...")
        parser = argparse.ArgumentParser(description='収入・支出詳細CSVファイルをPostgreSQLに取り込む')
        parser.add_argument('csv_file', help='取り込むCSVファイルのパス')
        
        print("引数を解析中...")
        args = parser.parse_args()
        print(f"指定されたCSVファイル: {args.csv_file}")
        
        # if not os.path.exists(args.csv_file):
        #     print(f"エラー: ファイルが存在しません: {args.csv_file}")
        #     sys.exit(1)
        
        # print("ファイルの存在を確認しました")
        
        # CSV処理の実行
        print("CSV処理を開始します...")
        stats = process_csv_file(args.csv_file)
        
        # エラーがあった場合は異常終了
        if stats['errors'] > 0:
            print("エラーが発生したため終了します")
            sys.exit(1)
        
        print("処理が正常に完了しました")
    
    except Exception as e:
        print(f"予期しないエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
