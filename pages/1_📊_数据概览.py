import streamlit as st
import plotly.express as px
from data_utils import load_data, render_sidebar # 导入共享工具

st.set_page_config(page_title="数据概览", page_icon="📊", layout="wide")

# 加载数据和侧边栏
with st.spinner('正在加载数据缓存...'):
    df, df_finance = load_data()
selected_years = render_sidebar(df)

# 根据侧边栏过滤数据
df_filtered = df[(df['release_year'] >= selected_years[0]) & (df['release_year'] <= selected_years[1])]

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