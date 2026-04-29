import streamlit as st
import pandas as pd     # ✨ 加上这一行！让 Python 认识 pd
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
# 现在侧边栏直接吐出过滤好的完美数据！
df_filtered = render_sidebar(df)

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
st.markdown("---")

# st.header("🎭 电影剧情情感演变趋势")
# # 按年份分组计算平均情感得分
# sentiment_trend = df_filtered.groupby('release_year')['sentiment'].mean().reset_index()
# fig_sent = px.line(sentiment_trend, x='release_year', y='sentiment', title="电影剧情从‘悲伤/黑暗’到‘积极/光明’的演变")
# st.plotly_chart(fig_sent, use_container_width=True)



# st.markdown("---")
st.header("💯 高分神作")
st.markdown("在庞大的片库中，能拿到高分的往往是特定粉丝群体的狂欢或是极具特色的隐藏神作。我们为您提取了当前年份区间内**热度最高**的 10 部满分影片：")

# 1. 筛选评分为 8.0 及以上的电影
df_perfect = df_filtered[df_filtered['vote_average'] >= 8.0]

if not df_perfect.empty:
    # 2. 按受欢迎程度 (popularity) 和 投票人数 (vote_count) 降序排列，取前 10 名
    if 'vote_count' in df_perfect.columns:
        top_perfect = df_perfect.sort_values(by=['popularity', 'vote_count'], ascending=[False, False]).head(10)
    else:
        top_perfect = df_perfect.sort_values(by='popularity', ascending=False).head(10)
    
    # 3. 采用 5 列海报画廊布局展示
    cols = st.columns(5)
    for i, (_, row) in enumerate(top_perfect.iterrows()):
        with cols[i % 5]: # 使用取余数的方式，让 10 部电影完美分配到两行（每行 5 个）
            if pd.notna(row.get('poster_path')):
                poster_url = f"https://image.tmdb.org/t/p/w500{row['poster_path']}"
                st.image(poster_url, use_container_width=True)
            else:
                # 如果没有海报，占位显示
                st.info("🚫 暂无海报")
            
            # 显示精简的电影信息
            st.markdown(f"**{row['title']}**")
            
            # 安全地读取年份和投票人数
            release_year = str(row['release_date'])[:4] if pd.notna(row.get('release_date')) else '未知'
            vote_info = f" | 👤 {int(row['vote_count'])}票" if 'vote_count' in row and pd.notna(row['vote_count']) else ""
            st.caption(f"📅 {release_year}{vote_info}")
else:
    st.info("💡 在当前选定的年份区间内，没有找到评分为 8以上的电影哦。尝试在左侧边栏拉大年份范围看看！")