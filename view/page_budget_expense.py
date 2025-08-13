"""予算実績表示画面"""
import streamlit as st
import pandas as pd
from view.repo import fetch_budget_data
from view.dp_budget_expense import (
    create_pivot_dataframe,
    create_grouped_categories_chart
)
from config import CATEGORY_GROUPS

def show_budget_view():
    try:
        with st.spinner('データを読み込み中...'):
            df = fetch_budget_data()
        
        if df.empty:
            st.warning("データが見つかりません。")
            return
        
        st.success(f"データを取得しました。（{len(df)}件）")

        st.header("全予算項目")
        st.subheader("全支払方法")
        st.dataframe(
            create_pivot_dataframe(df, 'amount_all'),
            use_container_width=False,
            column_config={
                "title": st.column_config.TextColumn(width="medium"),
            }
        )
        st.subheader("流動資金")
        st.dataframe(
            create_pivot_dataframe(df, 'amount_liquid'),
            use_container_width=False,
            column_config={
                "title": st.column_config.TextColumn(width="medium"),
            }
        )
        st.subheader("クレカ")
        st.dataframe(
            create_pivot_dataframe(df, 'amount_credit'),
            use_container_width=False,
            column_config={
                "title": st.column_config.TextColumn(width="medium"),
            }
        )
        
        for group_name, categories in CATEGORY_GROUPS.items():
            st.header(f"{group_name}")
            try:
                graph_amount_all = create_grouped_categories_chart(df, categories, 'amount_all')
                st.plotly_chart(graph_amount_all, use_container_width=True)

                graph_amount_liquid = create_grouped_categories_chart(df, categories, 'amount_liquid')
                st.plotly_chart(graph_amount_liquid, use_container_width=True)

                graph_amount_credit = create_grouped_categories_chart(df, categories, 'amount_credit')
                st.plotly_chart(graph_amount_credit, use_container_width=True)

            except Exception as e:
                st.error(f"グループ別グラフの作成でエラーが発生しました: {e}")
    
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
        st.info("データベース接続設定やビューの定義を確認してください。")