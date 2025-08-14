import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

def create_graph_inout(df):
    """
    収支のグラフ
    ・横軸は年月昇順
    ・収入/支出額は棒グラフで表示
    ・収支額は折れ線グラフで表示
    """

    target_df = df[['ym', 'amount_all', 'amount_income_all', 'amount_outcome_all']]
    target_df.columns = ['年月', '収支', '収入', '支出']

    fig = go.Figure()

    fig.add_trace(go.Bar(x=target_df['年月'], y=target_df['収入'], name='収入', marker_color='green'))
    fig.add_trace(go.Bar(x=target_df['年月'], y=target_df['支出'], name='支出', marker_color='red'))

    current_ym = datetime.now().strftime('%Y-%m')
    if len(target_df) > 1 and target_df['年月'].iloc[-1].strftime('%Y-%m') == current_ym:
        fig.add_trace(
            go.Scatter(x=target_df['年月'].iloc[:-1], y=target_df['収支'].iloc[:-1], 
            name='収支', mode='lines+markers', line=dict(color=px.colors.qualitative.Plotly[3], width=2), 
            yaxis='y2', showlegend=True)
        )
        fig.add_trace(
            go.Scatter(x=[target_df['年月'].iloc[-1]], y=[target_df['収支'].iloc[-1]], 
            mode='markers', marker=dict(size=6), 
            yaxis='y2', showlegend=False, name='収支', 
            line=dict(color=px.colors.qualitative.Plotly[3]))
        )
    else:
        fig.add_trace(
            go.Scatter(x=target_df['年月'], y=target_df['収支'], name='収支', 
            mode='lines+markers', line=dict(width=2), yaxis='y2')
        )

    fig.update_layout(
        yaxis2=dict(overlaying='y', side='right'),
        barmode='group'
    )
    fig.update_yaxes(title_text="金額", tickformat=",")
    fig.update_xaxes(title_text="年月", tickformat="%Y年%m月")

    return fig

def create_graph_out(df):
    """
    支出のグラフ
    ・横軸は年月昇順
    ・支出額は折れ線グラフで表示
    """

    target_df = df[['ym', 'amount_outcome_all', 'amount_outcome_liquid', 'amount_outcome_credit']]
    outcome_columns = ['支出合計', '支出（流動）', '支出（クレジット）']
    target_df.columns = ['年月'] + outcome_columns

    fig = go.Figure()

    current_ym = datetime.now().strftime('%Y-%m')
    
    for col in outcome_columns:
        if len(target_df) > 1 and target_df['年月'].iloc[-1].strftime('%Y-%m') == current_ym:
            # 最後の点以外を線で繋ぐ
            fig.add_trace(
                go.Scatter(x=target_df['年月'].iloc[:-1], y=target_df[col].iloc[:-1].abs(), 
                name=col, mode='lines+markers', line=dict(width=2))
            )
            # 最後の点は単独のマーカー
            fig.add_trace(
                go.Scatter(x=[target_df['年月'].iloc[-1]], y=[abs(target_df[col].iloc[-1])], 
                mode='markers', marker=dict(size=6), 
                showlegend=False, name=col,
                line=dict(color=fig.data[-1].line.color))
            )
        else:
            fig.add_trace(
                go.Scatter(x=target_df['年月'], y=target_df[col].abs(), name=col, 
                mode='lines+markers', line=dict(width=2))
            )

    fig.update_layout(
        barmode='group'
    )
    fig.update_yaxes(title_text="金額", tickformat=",")
    fig.update_xaxes(title_text="年月", tickformat="%Y年%m月")

    return fig