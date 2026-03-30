import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

# 确保能正确导入上一级目录的 data_utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data_utils import load_data, render_sidebar, apply_apple_glass_style

st.set_page_config(page_title="商业分析", page_icon="💰", layout="wide")

# ====================================================
# ✨ 注入 Apple 毛玻璃液态框全局样式
# ====================================================
apply_apple_glass_style()

# 加载数据与侧边栏
with st.spinner('正在加载数据缓存...'):
    df, df_finance = load_data()
selected_years = render_sidebar(df)

# 应用过滤
df_filtered = df[(df['release_year'] >= selected_years[0]) & (df['release_year'] <= selected_years[1])]
df_finance_filtered = df_finance[(df_finance['release_year'] >= selected_years[0]) & (df_finance['release_year'] <= selected_years[1])]

st.title("💰 商业与产业分析")
st.markdown("深度挖掘票房背后的秘密，分析各大制片厂的表现与全球电影产业分布。")
st.markdown("---")

# 模块 1：预算与票房的关系
st.header("📈 预算 vs 票房")
if not df_finance_filtered.empty:
    fig_scatter = px.scatter(
        df_finance_filtered, x="budget", y="revenue", 
        hover_data=['title', 'release_year'], color="vote_average",
        color_continuous_scale="Hot", # 修改为 Hot 配色，科技感发光效果
        labels={"budget": "预算 ($)", "revenue": "票房 ($)", "vote_average": "评分"}
    )
    # 让图表背景透明，完美融入毛玻璃卡片
    fig_scatter.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_scatter, use_container_width=True)
else:
    st.info("所选年份区间内缺乏有效的财务数据。")

st.markdown("---")

# 模块 2：双榜单 & ROI 分析 (使用左右分栏)
col_left, col_right = st.columns(2)

with col_left:
    st.header("🏆 顶级大片排行榜")
    tab1, tab2 = st.tabs(["最高票房 Top 10", "最受欢迎 Top 10"])
    with tab1:
        top_rev = df_filtered.sort_values(by="revenue", ascending=False).head(10)
        fig_rev = px.bar(top_rev, x="revenue", y="title", orientation='h', color="revenue", color_continuous_scale="Plasma")
        fig_rev.update_layout(yaxis={'categoryorder':'total ascending'}, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_rev, use_container_width=True)
    with tab2:
        top_pop = df_filtered.sort_values(by="popularity", ascending=False).head(10)
        fig_pop = px.bar(top_pop, x="popularity", y="title", orientation='h', color="popularity", color_continuous_scale="Plasma")
        fig_pop.update_layout(yaxis={'categoryorder':'total ascending'}, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_pop, use_container_width=True)

with col_right:
    st.header("💸 投资回报率 (ROI) 排行")
    df_roi = df_finance_filtered[df_finance_filtered['budget'] >= 100000].copy()
    if not df_roi.empty:
        df_roi['profit'] = df_roi['revenue'] - df_roi['budget']
        df_roi['roi_pct'] = (df_roi['profit'] / df_roi['budget']) * 100
        top_roi = df_roi.sort_values(by='roi_pct', ascending=False).head(10)
        top_roi['short_title'] = top_roi['title'].apply(lambda x: x[:20] + '...' if len(x) > 20 else x)
        
        fig_roi = px.bar(
            top_roi, x="roi_pct", y="short_title", orientation='h', 
            color="roi_pct", color_continuous_scale="Greens",
            hover_data=['title', 'budget', 'revenue', 'profit']
        )
        fig_roi.update_layout(yaxis={'categoryorder':'total ascending'}, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_roi, use_container_width=True)

st.markdown("---")

# 模块 3：影视巨头大比拼 & 全球地图
st.header("🏢 影视巨头与全球产地")
tab_studio, tab_map = st.tabs(["制片厂票房比拼", "全球电影产量地图"])

with tab_studio:
    if 'production_companies' in df_finance_filtered.columns:
        df_comp = df_finance_filtered.dropna(subset=['production_companies']).copy()
        df_comp['production_companies'] = df_comp['production_companies'].str.split(',')
        df_exploded = df_comp.explode('production_companies')
        df_exploded['production_companies'] = df_exploded['production_companies'].str.strip()
        company_stats = df_exploded.groupby('production_companies').agg(
            total_revenue=('revenue', 'sum'), avg_rating=('vote_average', 'mean'), movie_count=('title', 'count')
        ).reset_index()
        top_studios = company_stats[company_stats['movie_count'] >= 5].sort_values('total_revenue', ascending=False).head(15)
        
        fig_studios = px.bar(
            top_studios, x='production_companies', y='total_revenue', 
            color='avg_rating', color_continuous_scale='RdYlBu',
            labels={'production_companies': '制作公司', 'total_revenue': '总票房 ($)', 'avg_rating': '平均评分'}
        )
        fig_studios.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_studios, use_container_width=True)

with tab_map:
    if 'production_countries' in df_filtered.columns:
        countries_series = df_filtered['production_countries'].dropna().str.split(',').explode().str.strip()
        country_counts = countries_series.value_counts().reset_index()
        country_counts.columns = ['Country', 'Movie Count']
        fig_map = px.choropleth(
            country_counts, locations="Country", locationmode="country names",
            color="Movie Count", hover_name="Country", color_continuous_scale="YlGnBu"
        )
        fig_map.update_layout(
            geo=dict(showframe=False, showcoastlines=True, projection_type='equirectangular', bgcolor='rgba(0,0,0,0)'),
            paper_bgcolor="rgba(0,0,0,0)", margin={"r":0,"t":40,"l":0,"b":0}
        )
        st.plotly_chart(fig_map, use_container_width=True)