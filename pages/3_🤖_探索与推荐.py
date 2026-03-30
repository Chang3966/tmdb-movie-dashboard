import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sys
import os

# 确保能正确导入上一级目录的 data_utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data_utils import load_data, render_sidebar, apply_apple_glass_style

st.set_page_config(page_title="探索与推荐", page_icon="🤖", layout="wide")

# ====================================================
# ✨ 注入 Apple 毛玻璃液态框全局样式
# ====================================================
apply_apple_glass_style()

# 加载数据与侧边栏
with st.spinner('正在加载数据缓存...'):
    df, _ = load_data()
selected_years = render_sidebar(df)
df_filtered = df[(df['release_year'] >= selected_years[0]) & (df['release_year'] <= selected_years[1])]

st.title("🤖 探索影片与 AI 智能推荐")
st.markdown("搜寻您喜爱的经典电影，或者让我们的机器学习算法为您推荐下一部值得一看的佳作。")
st.markdown("---")

# 模块 1：带有海报的迷你搜索引擎
st.header("🔍 电影资料库检索")
search_query = st.text_input("输入电影名称的关键词 (如: Inception, Matrix, Titanic)：", "")

if search_query:
    search_results = df_filtered[df_filtered['title'].str.contains(search_query, case=False, na=False)].head(5)
    if not search_results.empty:
        st.success(f"为您找到前 {len(search_results)} 部最匹配的电影：")
        for index, row in search_results.iterrows():
            col1, col2 = st.columns([1, 4]) 
            with col1:
                if pd.notna(row['poster_path']):
                    poster_url = f"https://image.tmdb.org/t/p/w500{row['poster_path']}"
                    st.image(poster_url, use_column_width=True)
                else:
                    st.info("🚫 暂无海报")
            with col2:
                st.subheader(row['title'])
                st.write(f"📅 **上映:** {row['release_date']} | ⭐ **评分:** {row['vote_average']} | ⏳ **时长:** {row['runtime']} 分钟")
                if row['revenue'] > 0:
                    st.write(f"💰 **票房:** ${row['revenue']:,.0f}")
                st.write(f"📖 **简介:** {row['overview']}")
            st.markdown("---")
    else:
        st.warning("未找到匹配的电影，请尝试更换关键词。")

st.markdown("---")

# 模块 2：AI 推荐系统 & 词云 (左右布局)
col_left, col_right = st.columns([2, 1])

with col_left:
    st.header("✨ AI 智能推荐系统")
    st.markdown("基于 TF-IDF 和余弦相似度，寻找在类型、关键词和剧情上最匹配的电影。")
    
    # 扩大推荐池到 20000 部电影
    df_rec = df_filtered.dropna(subset=['title', 'overview']).sort_values('popularity', ascending=False).head(20000).reset_index(drop=True)
    if not df_rec.empty:
        df_rec['combined_features'] = df_rec['genres'].fillna('') + ' ' + df_rec['keywords'].fillna('') + ' ' + df_rec['overview'].fillna('')
        movie_list = df_rec['title'].tolist()
        selected_movie = st.selectbox("请在下拉框中选择一部您喜欢的电影：", ["-- 请选择 --"] + movie_list)

        if selected_movie != "-- 请选择 --":
            with st.spinner('AI 正在计算全库特征矩阵相似度...'):
                tfidf = TfidfVectorizer(stop_words='english')
                tfidf_matrix = tfidf.fit_transform(df_rec['combined_features'])
                idx = df_rec[df_rec['title'] == selected_movie].index[0]
                sim_scores = cosine_similarity(tfidf_matrix[idx], tfidf_matrix).flatten()
                top_indices = sim_scores.argsort()[-6:-1][::-1]
                
                st.success(f"为您找到 5 部与《{selected_movie}》高度相似的影片：")
                cols = st.columns(5)
                for i, c in enumerate(cols):
                    rec_idx = top_indices[i]
                    rec_movie = df_rec.iloc[rec_idx]
                    with c:
                        if pd.notna(rec_movie.get('poster_path')):
                            poster_url = f"https://image.tmdb.org/t/p/w500{rec_movie['poster_path']}"
                            st.image(poster_url, use_column_width=True)
                        st.write(f"**{rec_movie['title']}**")
                        st.caption(f"相似度: {sim_scores[rec_idx]:.2f}")
    else:
         st.info("数据量不足，无法初始化推荐引擎。")

with col_right:
    st.header("☁️ 流行电影词云")
    st.markdown("字号大小代表受欢迎程度")
    top_popular = df_filtered.dropna(subset=['popularity', 'title']).sort_values(by='popularity', ascending=False).head(80)
    if not top_popular.empty:
        movie_pop_dict = dict(zip(top_popular['title'], top_popular['popularity']))
        wordcloud = WordCloud(
            width=600, height=800, background_color='rgba(255, 255, 255, 0)', # 词云背景透明化，适配毛玻璃卡片
            mode='RGBA', colormap='magma', max_words=80
        ).generate_from_frequencies(movie_pop_dict)
        
        # 将 matplotlib 图表背景设为透明
        fig_wc, ax = plt.subplots(figsize=(6, 8))
        fig_wc.patch.set_alpha(0)
        ax.patch.set_alpha(0)
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig_wc)