"""状況画面（メイン）"""
import streamlit as st
import pandas as pd
from repo import fetch_budget_yms, fetch_budget_amount_status, fetch_budget_total_amount_status, fetch_income
from dp_status import create_graph_budget_status

def show_page_status():
    try:
        with st.spinner('予算年月を読み込み中...'):
            df_budget_yms = fetch_budget_yms()

        if df_budget_yms.empty:
            st.warning("予算年月が設定されていません。")
            return

        selected_ym_title = st.selectbox("予算年月", df_budget_yms.index)
        selected_ym_id = df_budget_yms.loc[selected_ym_title].id

        with st.spinner('データを読み込み中...'):
            df_total_amount_status = fetch_budget_total_amount_status(selected_ym_id)
            df_income = fetch_income(selected_ym_id)
            df_amount_status = fetch_budget_amount_status(selected_ym_id)
        
        st.success(f"データを取得しました。")

        st.header("予算消化状況")
        st.subheader("全体")

        projected_amount = df_total_amount_status['projected_amount'].values[0]
        present_amount = df_total_amount_status['present_amount'].values[0]
        present_planned_amount = df_total_amount_status['present_planned_amount'].values[0]
        income = df_income['income'].values[0]
        rest_free_amount = income - projected_amount
        projected_amount_ratio = projected_amount / income if income != 0 else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("支出（予測）", f"¥{projected_amount:,.0f}")
        col2.metric("支出（実績）", f"¥{present_amount:,.0f}")
        col3.metric("支出（実績+計画）", f"¥{present_planned_amount:,.0f}")
        col1, col2, col3 = st.columns(3)
        col1.metric("収入", f"¥{income:,.0f}")
        col2.metric("残支出可能額", f"¥{rest_free_amount:,.0f}")
        col3.metric("支出（予測）/収入", f"{projected_amount_ratio:,.1%}")

        fig = create_graph_budget_status(df_amount_status, "all")
        st.plotly_chart(fig)

        st.subheader("クレジット")
        col1, col2, col3 = st.columns(3)
        col1.metric("支出（予測）", f"¥{df_total_amount_status['projected_amount_credit'].values[0]:,.0f}")
        col2.metric("支出（実績）", f"¥{df_total_amount_status['present_amount_credit'].values[0]:,.0f}")
        col3.metric("支出（実績+計画）", f"¥{df_total_amount_status['present_planned_amount_credit'].values[0]:,.0f}")
        fig = create_graph_budget_status(df_amount_status, "credit")
        st.plotly_chart(fig)

    except Exception as e:
        st.error(f"エラーが発生しました: {e}")