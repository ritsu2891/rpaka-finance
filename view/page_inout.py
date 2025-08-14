"""予算項目別支出画面"""
import streamlit as st
import pandas as pd
from repo import fetch_inout_data
from dp_inout import create_graph_inout, create_graph_out

def show_inout_view():
    try:
        with st.spinner('データを読み込み中...'):
            df = fetch_inout_data()
        
        if df.empty:
            st.warning("データが見つかりません。")
            return
        
        st.success(f"データを取得しました。（{len(df)}件）")

        fig = create_graph_inout(df)
        st.plotly_chart(fig)

        fig = create_graph_out(df)
        st.plotly_chart(fig)

        # 元データ（トグルで表示）
        with st.expander("元データ", expanded=False):
            st.dataframe(df)

    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
        st.info("データベース接続設定やビューの定義を確認してください。")