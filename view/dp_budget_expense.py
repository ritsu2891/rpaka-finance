import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def create_pivot_dataframe(df, amount_type):
    pivot_df = df.pivot_table(
        index='title', 
        columns='ym_str', 
        values=amount_type, 
        aggfunc='sum',
        fill_value=0
    )
    pivot_df = pivot_df[sorted(pivot_df.columns, reverse=True)]
    
    return pivot_df

def create_grouped_categories_chart(df, categories, amount_type):
    group_df = df[df['title'].isin(categories)].copy()

    if group_df.empty:
        fig = go.Figure()
        fig.update_layout(title="データがありません")
        return fig
    
    fig = go.Figure()
    for title in group_df['title'].unique():
        title_data = group_df[group_df['title'] == title].sort_values('ym')
        
        current_ym = pd.Timestamp.now().strftime('%Y/%m')
        is_last_current_month = title_data.iloc[-1]['ym_str'] == current_ym if not title_data.empty else False
        
        if is_last_current_month and len(title_data) > 1:
            # Get consistent color for this title
            title_index = list(group_df['title'].unique()).index(title)
            title_color = px.colors.qualitative.Set1[title_index % len(px.colors.qualitative.Set1)]
            
            fig.add_trace(
                go.Scatter(
                    x=title_data['ym'].iloc[:-1],
                    y=title_data[amount_type].iloc[:-1].fillna(0),
                    mode='lines+markers',
                    name=title,
                    marker=dict(color=title_color),
                    line=dict(color=title_color),
                    showlegend=False
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=[title_data['ym'].iloc[-1]],
                    y=[title_data[amount_type].iloc[-1]],
                    mode='markers',
                    name=title,
                    marker=dict(color=title_color)
                )
            )
        else:
            fig.add_trace(
                go.Scatter(
                    x=title_data['ym'],
                    y=title_data[amount_type],
                    mode='lines+markers',
                    name=title
                )
            )
    if amount_type == 'amount_all':
        title_text = "全支払方法"
    elif amount_type == 'amount_liquid':
        title_text = "流動資金"
    elif amount_type == 'amount_credit':
        title_text = "クレカ"
    else:
        title_text = "---"
    fig.update_layout(title=title_text)
    fig.update_yaxes(title_text="金額", tickformat=",")
    fig.update_xaxes(title_text="年月", tickformat="%Y年%m月")
    return fig