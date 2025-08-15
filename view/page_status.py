"""状況画面（メイン）"""
import streamlit as st
import pandas as pd
from repo import fetch_budget_amount_status, fetch_budget_total_amount_status
from dp_status import create_graph_budget_status

def show_page_status():
    try:
        with st.spinner('データを読み込み中...'):
            df_amount_status = fetch_budget_amount_status()
            df_total_amount_status = fetch_budget_total_amount_status()

        if df_amount_status.empty:
            st.warning("データが見つかりません。")
            return
        
        st.success(f"データを取得しました。（{len(df_amount_status)}件）")

        st.header("予算消化状況")
        st.subheader("全体")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("支出（予測）", f"¥{df_total_amount_status['projected_amount'].values[0]:,.0f}")
        col2.metric("支出（実績）", f"¥{df_total_amount_status['present_amount'].values[0]:,.0f}")
        col3.metric("支出（実績+計画）", f"¥{df_total_amount_status['present_planned_amount'].values[0]:,.0f}")
        col4.metric("予算消化率", f"{df_total_amount_status['ratio_planned_amount'].values[0]*100:.1f}%")
        fig = create_graph_budget_status(df_amount_status, "all")
        st.plotly_chart(fig)

        st.subheader("クレジット")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("支出（予測）", f"¥{df_total_amount_status['projected_amount_credit'].values[0]:,.0f}")
        col2.metric("支出（実績）", f"¥{df_total_amount_status['present_amount_credit'].values[0]:,.0f}")
        col3.metric("支出（実績+計画）", f"¥{df_total_amount_status['present_planned_amount_credit'].values[0]:,.0f}")
        col4.metric("予算消化率", f"{df_total_amount_status['ratio_planned_amount_credit'].values[0]*100:.1f}%")
        fig = create_graph_budget_status(df_amount_status, "credit")
        st.plotly_chart(fig)

        # 元データ（トグルで表示）
        with st.expander("元データ", expanded=False):
            st.dataframe(df_amount_status)

    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
        st.info("データベース接続設定やビューの定義を確認してください。")