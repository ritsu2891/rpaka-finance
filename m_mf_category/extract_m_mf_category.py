#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTMLから大分類・中分類を抽出してCSVに変換する（標準ライブラリのみ使用）
"""

import csv
import re
import sys
import argparse


def extract_categories_regex_only(html_file_path):
    """
    HTMLファイルから大分類と中分類を正規表現のみで抽出
    """
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    categories_data = []
    
    # 大分類とそのIDを抽出
    large_cat_pattern = r'<a class="dropdown-toggle anchor-color-off"[^>]*href="#"[^>]*id="(\d+)"[^>]*>\s*([^<\n]+)\s*</a>'
    large_categories = re.findall(large_cat_pattern, html_content)
    
    for large_id, large_name in large_categories:
        large_name = large_name.strip()
        print(f"大分類を処理中: {large_name}")
        
        # この大分類に対応するサブメニューを探す
        # large_idを使って対応するサブメニューセクションを特定
        submenu_start = html_content.find(f'id="{large_id}"')
        if submenu_start == -1:
            continue
        
        # サブメニューの開始位置を探す
        submenu_ul_start = html_content.find('<ul class="dropdown-menu sub_menu', submenu_start)
        if submenu_ul_start == -1:
            continue
        
        # サブメニューの終了位置を探す
        submenu_ul_end = html_content.find('</ul>', submenu_ul_start)
        if submenu_ul_end == -1:
            continue
        
        submenu_content = html_content[submenu_ul_start:submenu_ul_end + 5]
        
        # 中分類（ユーザー定義）を抽出
        user_middle_pattern = r'<span class="middle_category_user"[^>]*>\s*<i[^>]*></i>\s*([^\n<]+)'
        user_middles = re.findall(user_middle_pattern, submenu_content)
        
        for middle_name in user_middles:
            middle_name = middle_name.strip()
            # リンクテキストを除去
            middle_name = re.sub(r'<a[^>]*>.*?</a>', '', middle_name, flags=re.DOTALL)
            middle_name = middle_name.strip()
            if middle_name and len(middle_name) > 0:
                categories_data.append([large_name, middle_name])
                print(f"  - ユーザー定義: {middle_name}")
        
        # 中分類（デフォルト）を抽出
        default_middle_pattern = r'<span class="middle_category_default"[^>]*>\s*([^\n<]+)\s*</span>'
        default_middles = re.findall(default_middle_pattern, submenu_content)
        
        for middle_name in default_middles:
            middle_name = middle_name.strip()
            if middle_name and len(middle_name) > 0:
                categories_data.append([large_name, middle_name])
                print(f"  - デフォルト: {middle_name}")
    
    return categories_data


def main():
    # コマンドライン引数の設定
    parser = argparse.ArgumentParser(description='HTMLから大分類・中分類を抽出してCSVに変換')
    parser.add_argument('--type', '-t', choices=['large', 'middle', 'both'], default='both',
                       help='抽出する分類の種類 (large:大分類のみ, middle:中分類のみ, both:両方)')
    parser.add_argument('--input', '-i', 
                       default=r"c:\Users\rpaka\Downloads\finance\m_mf_category_m.html",
                       help='入力HTMLファイルのパス')
    parser.add_argument('--output-large', '-ol',
                       default=r"c:\Users\rpaka\Downloads\finance\m_mf_category_l.csv",
                       help='大分類CSVファイルの出力パス')
    parser.add_argument('--output-middle', '-om',
                       default=r"c:\Users\rpaka\Downloads\finance\m_mf_category_m.csv",
                       help='中分類CSVファイルの出力パス')
    
    args = parser.parse_args()
    
    input_html_file = args.input
    output_csv_file_l = args.output_large
    output_csv_file_m = args.output_middle
    
    try:
        print("HTMLファイルからカテゴリデータを抽出中...")
        categories_data = extract_categories_regex_only(input_html_file)
        
        # 大分類の処理
        if args.type in ['large', 'both']:
            # 大分類のみで重複排除（順番を保持）
            large_cats = []
            seen = set()
            for large_cat, _ in categories_data:
                if large_cat not in seen:
                    seen.add(large_cat)
                    large_cats.append(large_cat)
            
            with open(output_csv_file_l, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['大分類'])
                for large_cat in large_cats:
                    writer.writerow([large_cat])

            print(f"[大分類] CSVファイルを作成しました: {output_csv_file_l}")
            print(f"[大分類] 合計 {len(large_cats)} 行のデータを出力しました。")

        # 中分類の処理
        if args.type in ['middle', 'both']:
            with open(output_csv_file_m, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['大分類', '中分類'])
                for row in categories_data:
                    writer.writerow(row)

            print(f"[中分類] CSVファイルを作成しました: {output_csv_file_m}")
            print(f"[中分類] 合計 {len(categories_data)} 行のデータを出力しました。")
            
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
