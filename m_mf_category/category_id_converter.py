import os
import csv
import psycopg2
from dotenv import load_dotenv
import sys

def load_environment():
    """環境変数を読み込む"""
    load_dotenv()
    
    db_config = {
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT'),
        'database': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD')
    }
    
    table_name = os.getenv('DB_TABLE_NAME', 'categories_master')
    
    # 必須項目のチェック
    missing_vars = [key for key, value in db_config.items() if value is None]
    if missing_vars:
        raise ValueError(f"環境変数が設定されていません: {', '.join(missing_vars)}")
    
    return db_config, table_name

def connect_to_database(db_config):
    """PostgreSQLデータベースに接続"""
    try:
        connection = psycopg2.connect(**db_config)
        return connection
    except psycopg2.Error as e:
        print(f"データベース接続エラー: {e}")
        sys.exit(1)

def get_category_mapping(connection, table_name):
    """大分類マスタテーブルから名前とIDのマッピングを取得"""
    cursor = connection.cursor()
    
    try:
        # 大分類マスタテーブルからIDとタイトルを取得
        # テーブル構造は id, title を想定
        query = f"SELECT id, title FROM {table_name}"
        cursor.execute(query)
        
        category_mapping = {}
        for row in cursor.fetchall():
            category_id, category_name = row
            category_mapping[category_name] = category_id
        
        print(f"大分類マスタから {len(category_mapping)} 件のデータを取得しました")
        return category_mapping
        
    except psycopg2.Error as e:
        print(f"クエリ実行エラー: {e}")
        sys.exit(1)
    finally:
        cursor.close()

def process_csv(input_file, output_file, category_mapping):
    """CSVファイルを処理して大分類をIDに変換"""
    not_found_categories = set()
    processed_count = 0
    
    try:
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', encoding='utf-8', newline='') as outfile:
            
            reader = csv.reader(infile)
            writer = csv.writer(outfile)
            
            # ヘッダー行を処理
            header = next(reader)
            writer.writerow(header)
            
            # データ行を処理
            for row in reader:
                if len(row) >= 2:
                    category_name = row[0]  # 大分類名
                    subcategory = row[1]    # 中分類
                    
                    # 大分類名をIDに変換
                    if category_name in category_mapping:
                        category_id = category_mapping[category_name]
                        writer.writerow([category_id, subcategory])
                        processed_count += 1
                    else:
                        # IDが見つからない場合は元の名前のまま出力し、警告として記録
                        not_found_categories.add(category_name)
                        writer.writerow([category_name, subcategory])
                        processed_count += 1
                else:
                    # 空行などはそのまま出力
                    writer.writerow(row)
        
        print(f"処理完了: {processed_count} 行を処理しました")
        
        if not_found_categories:
            print("\n警告: 以下の大分類がマスタテーブルに見つかりませんでした:")
            for category in sorted(not_found_categories):
                print(f"  - {category}")
        
    except FileNotFoundError:
        print(f"ファイルが見つかりません: {input_file}")
        sys.exit(1)
    except Exception as e:
        print(f"CSV処理エラー: {e}")
        sys.exit(1)

def main():
    """メイン処理"""
    input_file = 'm_mf_category_m.csv'
    output_file = 'm_mf_category_m_with_ids.csv'
    
    try:
        # 環境変数を読み込み
        db_config, table_name = load_environment()
        
        # データベースに接続
        print("データベースに接続中...")
        connection = connect_to_database(db_config)
        
        # 大分類マッピングを取得
        print("大分類マスタを取得中...")
        category_mapping = get_category_mapping(connection, table_name)
        
        # CSVファイルを処理
        print(f"CSVファイルを処理中: {input_file}")
        process_csv(input_file, output_file, category_mapping)
        
        print(f"\n処理完了: {output_file} を生成しました")
        
    except Exception as e:
        print(f"エラー: {e}")
        sys.exit(1)
    finally:
        if 'connection' in locals() and connection:
            connection.close()
            print("データベース接続を閉じました")

if __name__ == "__main__":
    main()
