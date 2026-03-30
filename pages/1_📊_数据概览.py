import streamlit as st
import plotly.express as px
import sys
import os

# 确保能正确导入上一级目录的 data_utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data_utils import load_data, render_sidebar, apply_apple_glass_style # 导入新函数

st.set_page_config(page_title="数据概览", page_icon="📊", layout="wide")

# 加载数据与侧边栏
with st.spinner('正在加载数据缓存...'):
    df, _ = load_data()
selected_years = render_sidebar(df)

# 应用过滤
df_filtered = df[(df['release_year'] >= selected_years[0]) & (df['release_year'] <= selected_years[1])]

# ====================================================
# ✨ 第 1 步：子页面也必须一键全局美容！
# ====================================================
apply_apple_glass_style()

st.header("📊 数据概览")
col1, col2, col3, col4 = st.columns(4)

# (继续之前的图表绘制和指标展示代码...)
# ...
st.header("📊 数据概览")
col1, col2, col3, col4 = st.columns(4)
col1.metric("总电影数", f"{len(df_filtered):,}")
col2.metric("平均评分", f"{df_filtered['vote_average'].mean():.2f}")
col3.metric("最高评分", f"{df_filtered['vote_average'].max():.1f}")
col4.metric("平均片长", f"{df_filtered['runtime'].mean():.0f} 分钟")

st.markdown("---")

# 历年发行趋势
st.subheader("📈 历年电影发行趋势")
movies_per_year = df_filtered.groupby('release_year').size().reset_index(name='count')
fig_trend = px.line(movies_per_year, x="release_year", y="count", markers=True)
st.plotly_chart(fig_trend, use_container_width=True)