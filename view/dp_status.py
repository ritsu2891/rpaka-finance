import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def create_graph_budget_status(df, account_type):
    """
    予算消化状況を表示する横向き積み上げ棒グラフを作成する
    
    Args:
        df: v_budget_amount_statusビューのデータ
        account_type: アカウントタイプ（使用されていないが互換性のため保持）
    
    Returns:
        plotly.graph_objects.Figure: グラフオブジェクト
    """
    if df.empty:
        return go.Figure()
    
    if account_type == 'all':
        col_set_amount = 'set_amount'
        col_present_amount = 'present_amount'
        col_planned_amount = 'planned_amount'
        col_present_planned_amount = 'present_planned_amount'
        col_ratio_planned_amount = 'ratio_planned_amount'
    elif account_type == 'credit':
        col_set_amount = 'set_amount_credit'
        col_present_amount = 'present_amount_credit'
        col_planned_amount = 'planned_amount_credit'
        col_present_planned_amount = 'present_planned_amount_credit'
        col_ratio_planned_amount = 'ratio_planned_amount_credit'

    df = df.copy()
    df[col_present_amount] = df[col_present_amount].fillna(0)
    df[col_planned_amount] = df[col_planned_amount].fillna(0)
    df[col_present_planned_amount] = df[col_present_planned_amount].fillna(0)
    df[col_ratio_planned_amount] = df[col_ratio_planned_amount].fillna(0)
    df = df.sort_values('title', ascending=False)
    
    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=df['title'],
        x=df[col_present_amount],
        name='現在支出額',
        orientation='h',
        marker=dict(color='#3498db'),
        hovertemplate='<b>%{y}</b><br>現在支出額: ¥%{x:,.0f}<extra></extra>'
    ))
    
    fig.add_trace(go.Bar(
        y=df['title'],
        x=df[col_planned_amount],
        name='支出予定額',
        orientation='h',
        marker=dict(
            color='#85c1e9',
            pattern_shape='/',
            pattern_size=8,
            pattern_solidity=0.3
        ),
        hovertemplate='<b>%{y}</b><br>支出予定額: ¥%{x:,.0f}<extra></extra>'
    ))
    
    for idx, (i, row) in enumerate(df.iterrows()):
        fig.add_shape(
            type="line",
            x0=row[col_set_amount], x1=row[col_set_amount],
            y0=idx-0.4, y1=idx+0.4,
            line=dict(color="red", width=3),
        )
    
    for idx, (i, row) in enumerate(df.iterrows()):
        ratio_percent = row[col_ratio_planned_amount] * 100

        fig.add_annotation(
            x=row[col_set_amount],
            y=idx,
            text=f" ¥{row[col_set_amount]:,.0f} ",
            showarrow=False,
            xanchor="left",
            xshift=5,
            font=dict(size=15, color="red"),
            bgcolor="white",
            bordercolor="red",
            borderwidth=1,
            yshift=-15
        )
        
        fig.add_annotation(
            x=row[col_present_planned_amount],
            y=idx,
            text=f" ¥{row[col_present_planned_amount]:,.0f} ({ratio_percent:.1f}%) ",
            showarrow=False,
            xanchor="left",
            xshift=5,
            font=dict(size=15, color="blue"),
            bgcolor="white",
            bordercolor="blue",
            borderwidth=1,
            yshift=15
        )
    
    fig.update_layout(
        xaxis_title='金額',
        yaxis_title='予算項目',
        barmode='stack',
        height=max(400, len(df) * 60),
        margin=dict(l=150, r=100, t=80, b=50),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis=dict(
            tickformat=',.0f',
            tickprefix='¥'
        ),
        hovermode='closest'
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    fig.update_yaxes(showgrid=False)
    
    return fig