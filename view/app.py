"""
ファイナンスデータ集計・表示アプリ
MoneyForwardの入出金明細実績を表示・分析するStreamlitアプリ
"""
import streamlit as st
import sys
import os

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from page_inout import show_inout_view
from page_budget_expense import show_budget_view

# ページ設定
st.set_page_config(
    page_title="rpaka-finance-view",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """メイン関数"""
    st.title("rpaka-finance-view")
    
    st.sidebar.title("メニュー")
    
    page = st.sidebar.selectbox(
        "表示画面",
        [
            "収支額",
            "予算項目別支出",
        ]
    )
    
    if page == "収支額":
        show_inout_view()
    elif page == "予算項目別支出":
        show_budget_view()

if __name__ == "__main__":
    main()
