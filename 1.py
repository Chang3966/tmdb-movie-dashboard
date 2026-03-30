import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud          # 新增
import matplotlib.pyplot as plt          # 新增
# 在文件最顶部添加这行
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 设置页面配置
st.set_page_config(page_title="TMDB 电影数据可视化", page_icon="🎬", layout="wide")

# 加载数据 (使用缓存机制，避免每次刷新都重新加载大型数据集)
@st.cache_data
def load_data():
    # 注意：如果 100 万行数据导致内存不足，可以在开发阶段加上 nrows=10000 限制行数
    df = pd.read_csv("TMDB_movie_dataset_v11.csv") 
    
    # 数据预处理
    df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
    df['release_year'] = df['release_date'].dt.year
    
    # 过滤掉票房和预算为 0 的异常或缺失数据，以便于进行财务分析
    df_finance = df[(df['revenue'] > 0) & (df['budget'] > 0)].copy()
    return df, df_finance

st.title("🎬 TMDB 电影数据分析看板")
st.markdown("探索包含超过百万部电影的庞大数据库，发掘票房、评分与趋势背后的秘密！")

# 加载数据
with st.spinner('正在加载数据，请稍候...'):
    df, df_finance = load_data()

# --- 侧边栏：全局过滤器 ---
st.sidebar.header("过滤条件")
# 由于数据集年份跨度可能很大，我们提取有效年份
min_year = int(df['release_year'].min()) if pd.notna(df['release_year'].min()) else 1900
max_year = int(df['release_year'].max()) if pd.notna(df['release_year'].max()) else 2024

selected_years = st.sidebar.slider(
    "选择电影上映年份区间",
    min_value=min_year,
    max_value=max_year,
    value=(2000, max_year)
)

# 应用过滤
df_filtered = df[(df['release_year'] >= selected_years[0]) & (df['release_year'] <= selected_years[1])]
df_finance_filtered = df_finance[(df_finance['release_year'] >= selected_years[0]) & (df_finance['release_year'] <= selected_years[1])]

# --- 主页面内容 ---

# 模块 1：数据概览
st.header("📊 数据概览")
col1, col2, col3, col4 = st.columns(4)
col1.metric("当前筛选条件下的电影总数", f"{len(df_filtered):,}")
col2.metric("平均评分 (Vote Average)", f"{df_filtered['vote_average'].mean():.2f}")
if not df_finance_filtered.empty:
    col3.metric("最高票房记录 ($)", f"{df_finance_filtered['revenue'].max():,.0f}")
col4.metric("平均片长 (分钟)", f"{df_filtered['runtime'].mean():.0f}")

st.subheader("数据集预览")
st.dataframe(df_filtered[['title', 'release_date', 'vote_average', 'revenue', 'genres', 'popularity']].head(10))

st.markdown("---")

# 模块 2：财务分析 (预算 vs 票房)
st.header("💰 预算与票房的关系")
st.markdown("分析投入与产出，看看高预算是否一定能带来高票房？")

if not df_finance_filtered.empty:
    fig_scatter = px.scatter(
        df_finance_filtered, 
        x="budget", 
        y="revenue", 
        hover_data=['title', 'release_year'],
        color="vote_average",
        color_continuous_scale="Viridis",
        title="预算 vs 票房 (颜色代表评分)",
        labels={"budget": "预算 ($)", "revenue": "票房 ($)", "vote_average": "评分"}
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
else:
    st.info("所选年份区间内缺乏包含预算和票房的有效数据。")

st.markdown("---")

# 模块 3：排行榜 (Top 10)
st.header("🏆 电影排行榜 Top 10")
tab1, tab2 = st.tabs(["最高票房", "最受欢迎"])

with tab1:
    top_revenue = df_filtered.sort_values(by="revenue", ascending=False).head(10)
    fig_revenue = px.bar(
        top_revenue, 
        x="revenue", 
        y="title", 
        orientation='h',
        title="总票房 Top 10",
        color="revenue",
        labels={"revenue": "总票房 ($)", "title": "电影名称"}
    )
    fig_revenue.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_revenue, use_container_width=True)

with tab2:
    top_pop = df_filtered.sort_values(by="popularity", ascending=False).head(10)
    fig_pop = px.bar(
        top_pop, 
        x="popularity", 
        y="title", 
        orientation='h',
        title="受欢迎程度 Top 10",
        color="popularity",
        color_continuous_scale="Reds",
        labels={"popularity": "受欢迎度", "title": "电影名称"}
    )
    fig_pop.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_pop, use_container_width=True)

st.markdown("---")



# 模块 4：时间趋势分析
st.header("📈 发行趋势分析")
movies_per_year = df_filtered.groupby('release_year').size().reset_index(name='count')
fig_trend = px.line(
    movies_per_year, 
    x="release_year", 
    y="count", 
    title="每年上映电影数量趋势",
    labels={"release_year": "上映年份", "count": "电影数量"},
    markers=True
)
st.plotly_chart(fig_trend, use_container_width=True)


st.markdown("---")

# 模块 5：电影类型分布 (Genres)
st.header("🎭 电影类型分布")
st.markdown("看看什么类型的电影在市场上占据主导地位。")

if 'genres' in df_filtered.columns:
    # 剔除空值，按逗号拆分字符串，然后展开成多行，最后去除首尾空格
    genres_series = df_filtered['genres'].dropna().str.split(',').explode().str.strip()
    genre_counts = genres_series.value_counts().reset_index()
    genre_counts.columns = ['Genre', 'Count']
    
    # 选取排名前 15 的类型绘制环形图
    top_genres = genre_counts.head(15)
    fig_genres = px.pie(
        top_genres, 
        values='Count', 
        names='Genre', 
        title="Top 15 电影类型占比", 
        hole=0.4, # 设置中心空白，变成环形图
        color_discrete_sequence=px.colors.sequential.Plasma
    )
    fig_genres.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_genres, use_container_width=True)
else:
    st.warning("数据集中未找到 'genres' 列。")

st.markdown("---")

# 模块 6：电影时长分布 (Runtime)
st.header("⏳ 电影时长分布")
st.markdown("了解大多数导演倾向于将电影剪辑成多长时间。")

# 过滤掉时长为 0 或异常长的数据（例如超过 5 小时 / 300 分钟的）
valid_runtime_df = df_filtered[(df_filtered['runtime'] > 0) & (df_filtered['runtime'] <= 300)]

if not valid_runtime_df.empty:
    fig_runtime = px.histogram(
        valid_runtime_df, 
        x="runtime", 
        nbins=60, # 将数据分为 60 个柱子
        title="电影时长分布", 
        labels={'runtime': '时长 (分钟)', 'count': '电影数量'},
        color_discrete_sequence=['#ef553b']
    )
    fig_runtime.update_layout(bargap=0.1)
    st.plotly_chart(fig_runtime, use_container_width=True)
else:
    st.info("当前筛选条件下没有有效的时长数据。")

st.markdown("---")


# 模块 7：探索特定电影 (带动态海报)
st.header("🔍 迷你电影搜索引擎 (附带海报)")
st.markdown("不仅能查数据，还能看海报！输入关键词试试 (例如: Inception, Avatar, Batman)")

search_query = st.text_input("输入电影名称的关键词：", "")

if search_query:
    # 模糊搜索，并限制只取前 5 条结果，防止加载过多图片导致网页卡顿
    search_results = df_filtered[df_filtered['title'].str.contains(search_query, case=False, na=False)].head(5)
    
    if not search_results.empty:
        st.success(f"为您找到并展示前 {len(search_results)} 部最匹配的电影：")
        st.markdown("---")
        
        # 遍历搜索结果，逐个渲染
        for index, row in search_results.iterrows():
            # 使用 st.columns 将页面分为左右两列，左边 1 份宽度放海报，右边 3 份宽度放信息
            col1, col2 = st.columns([1, 3]) 
            
            with col1:
                # 检查是否存在海报路径
                if pd.notna(row['poster_path']):
                    # 拼接 TMDB 的图片基础 URL 和数据里的路径
                    poster_url = f"https://image.tmdb.org/t/p/w500{row['poster_path']}"
                    st.image(poster_url, use_column_width=True)
                else:
                    st.info("🚫 暂无海报")
                    
            with col2:
                # 展示详细信息
                st.subheader(row['title'])
                st.write(f"📅 **上映日期:** {row['release_date']}")
                st.write(f"⭐ **评分:** {row['vote_average']} / 10")
                st.write(f"⏳ **时长:** {row['runtime']} 分钟")
                
                # 如果有票房数据，格式化显示
                if row['revenue'] > 0:
                    st.write(f"💰 **票房:** ${row['revenue']:,.0f}")
                else:
                    st.write("💰 **票房:** 暂无数据")
                    
                st.write(f"📖 **剧情简介:** {row['overview']}")
                
            st.markdown("---") # 每部电影之间加一条分割线
    else:
        st.warning("未找到匹配的电影，请尝试更换关键词。")

st.markdown("---")

# 模块 8：最受欢迎电影词云图
st.header("☁️ 最受欢迎电影词云")
st.markdown("字号越大的电影，代表其在 TMDB 上的受欢迎程度（Popularity）越高！")

# 为了保证词云图清晰且不拥挤，我们选取受欢迎程度排名前 100 的电影
top_popular_movies = df_filtered.dropna(subset=['popularity', 'title']).sort_values(by='popularity', ascending=False).head(100)

if not top_popular_movies.empty:
    # 将电影标题和受欢迎程度转换为字典格式：{'电影名': 受欢迎度数值}
    movie_popularity_dict = dict(zip(top_popular_movies['title'], top_popular_movies['popularity']))
    
    # 创建词云对象
    # 提示：如果你的电影标题里有中文，需要在这里添加 font_path='你的中文字体路径.ttf'
    wordcloud = WordCloud(
        width=1000, 
        height=500, 
        background_color='white',
        colormap='magma', # 使用 magma 配色，视觉冲击力更强
        max_words=100,
        contour_width=3,
        contour_color='steelblue'
    ).generate_from_frequencies(movie_popularity_dict)
    
    # 使用 matplotlib 绘制图表并传递给 Streamlit
    fig_wc, ax = plt.subplots(figsize=(12, 6))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off') # 隐藏坐标轴
    
    # 在 Streamlit 中展示
    st.pyplot(fig_wc)
else:
    st.warning("当前筛选条件下没有足够的数据生成词云。")

st.markdown("---")

# 模块 9：投资回报率 (ROI) 深度分析
st.header("💸 投资回报率 (ROI) 排行榜")
st.markdown("真正的“以小博大”！看看哪些电影用最少的预算赚取了最丰厚的利润。")

# 过滤掉预算极低（可能是脏数据）的电影，设置最低预算阈值为 10 万美元
df_roi = df_finance_filtered[df_finance_filtered['budget'] >= 100000].copy()

if not df_roi.empty:
    # 计算利润和 ROI
    df_roi['profit'] = df_roi['revenue'] - df_roi['budget']
    df_roi['roi_pct'] = (df_roi['profit'] / df_roi['budget']) * 100
    
    # 选取 ROI 最高的 Top 10
    top_roi_movies = df_roi.sort_values(by='roi_pct', ascending=False).head(10)
    
    # 为了图表显示美观，我们把长片名截断
    top_roi_movies['short_title'] = top_roi_movies['title'].apply(lambda x: x[:20] + '...' if len(x) > 20 else x)
    
    fig_roi = px.bar(
        top_roi_movies, 
        x="roi_pct", 
        y="short_title", 
        orientation='h',
        title="投资回报率 (ROI) Top 10",
        color="roi_pct",
        color_continuous_scale="Greens", # 绿色代表赚钱！
        labels={"roi_pct": "投资回报率 (%)", "short_title": "电影名称"},
        hover_data=['title', 'budget', 'revenue', 'profit']
    )
    # 格式化悬停提示里的金额
    fig_roi.update_traces(
        hovertemplate="<b>%{customdata[0]}</b><br>" +
                      "投资回报率: %{x:,.0f}%<br>" +
                      "预算: $%{customdata[1]:,.0f}<br>" +
                      "票房: $%{customdata[2]:,.0f}<br>" +
                      "净利润: $%{customdata[3]:,.0f}"
    )
    fig_roi.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_roi, use_container_width=True)
else:
    st.warning("当前筛选条件下没有足够的财务数据来计算 ROI。")

st.markdown("---")


# 模块 10：全球电影产地分布
st.header("🌍 全球电影产地分布")
st.markdown("鼠标悬停在国家上，查看其在筛选范围内的电影产量。")

if 'production_countries' in df_filtered.columns:
    # 拆分并清理国家数据
    countries_series = df_filtered['production_countries'].dropna().str.split(',').explode().str.strip()
    country_counts = countries_series.value_counts().reset_index()
    country_counts.columns = ['Country', 'Movie Count']
    
    # 绘制热力地图
    fig_map = px.choropleth(
        country_counts,
        locations="Country",
        locationmode="country names", # 直接使用国家全拼进行匹配
        color="Movie Count",
        hover_name="Country",
        color_continuous_scale=px.colors.sequential.YlGnBu,
        title="各国电影产量分布"
    )
    
    # 调整地图外观
    fig_map.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='equirectangular'
        ),
        margin={"r":0,"t":40,"l":0,"b":0}
    )
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.warning("数据集中未找到 'production_countries' 列。")

st.markdown("---")
# 模块 11：基于内容的电影推荐系统
st.header("🤖 智能电影推荐系统")
st.markdown("基于机器学习中的 TF-IDF 和余弦相似度算法，根据电影的类型、关键词和剧情简介为您推荐相似影片。")

# 提取受欢迎度排名前 10000 的电影作为推荐池，并重置索引
df_rec = df_filtered.dropna(subset=['title', 'overview']).sort_values('popularity', ascending=False).head(10000).reset_index(drop=True)

if not df_rec.empty:
    # 组合文本特征
    df_rec['combined_features'] = df_rec['genres'].fillna('') + ' ' + df_rec['keywords'].fillna('') + ' ' + df_rec['overview'].fillna('')
    
    # 建立下拉菜单供用户选择电影
    movie_list = df_rec['title'].tolist()
    selected_movie = st.selectbox("请选择一部您喜欢的电影：", ["-- 请选择 --"] + movie_list)

    if selected_movie != "-- 请选择 --":
        with st.spinner('AI 正在计算相似度，请稍候...'):
            # 初始化 TF-IDF 向量化器（去除英文停用词如 the, is, at）
            tfidf = TfidfVectorizer(stop_words='english')
            
            # 将文本转换为特征矩阵
            tfidf_matrix = tfidf.fit_transform(df_rec['combined_features'])
            
            # 获取选中电影的索引
            idx = df_rec[df_rec['title'] == selected_movie].index[0]
            
            # 计算该电影与推荐池中所有电影的余弦相似度
            sim_scores = cosine_similarity(tfidf_matrix[idx], tfidf_matrix).flatten()
            
            # 找到相似度最高的前 6 个索引（第 1 个是它自己，所以取前 6）
            top_indices = sim_scores.argsort()[-6:-1][::-1]
            
            st.success(f"如果您喜欢《{selected_movie}》，您可能也会喜欢以下影片：")
            
            # 使用多列展示推荐结果
            cols = st.columns(5)
            for i, col in enumerate(cols):
                rec_idx = top_indices[i]
                rec_movie = df_rec.iloc[rec_idx]
                with col:
                    if pd.notna(rec_movie.get('poster_path')):
                        poster_url = f"https://image.tmdb.org/t/p/w500{rec_movie['poster_path']}"
                        st.image(poster_url, use_column_width=True)
                    st.write(f"**{rec_movie['title']}**")
                    st.caption(f"匹配度: {sim_scores[rec_idx]:.2f}")
else:
    st.info("当前筛选条件数据量不足，无法生成推荐池。")

st.markdown("---")

# 模块 12：影视巨头大比拼 (公司票房与评分分析)
st.header("🏢 影视巨头大比拼")
st.markdown("好莱坞六大制片厂谁最赚钱？谁的电影口碑最好？")

if 'production_countries' in df_finance_filtered.columns:
    # 复制财务数据集并清理空值
    df_comp = df_finance_filtered.dropna(subset=['production_companies']).copy()
    
    # 拆分公司名称并展开成多行
    df_comp['production_companies'] = df_comp['production_companies'].str.split(',')
    df_exploded = df_comp.explode('production_companies')
    df_exploded['production_companies'] = df_exploded['production_companies'].str.strip()
    
    # 按公司分组聚合数据
    company_stats = df_exploded.groupby('production_companies').agg(
        total_revenue=('revenue', 'sum'),
        avg_rating=('vote_average', 'mean'),
        movie_count=('title', 'count')
    ).reset_index()
    
    # 过滤掉偶尔拍了一两部高票房电影的小公司（至少 5 部以上）
    valid_companies = company_stats[company_stats['movie_count'] >= 5]
    
    # 选取总票房排名前 15 的巨头
    top_studios = valid_companies.sort_values('total_revenue', ascending=False).head(15)
    
    # 使用 Plotly 绘制双轴图表：柱状图代表票房，颜色代表评分
    fig_studios = px.bar(
        top_studios,
        x='production_companies',
        y='total_revenue',
        title='总票房 Top 15 制作公司 (颜色代表平均评分)',
        color='avg_rating',
        color_continuous_scale='RdYlBu', # 红黄蓝配色，蓝色高分，红色低分
        labels={
            'production_companies': '制作公司', 
            'total_revenue': '总票房 ($)',
            'avg_rating': '平均评分'
        },
        hover_data=['movie_count']
    )
    
    fig_studios.update_layout(xaxis_tickangle=-45) # 倾斜 X 轴标签防止重叠
    st.plotly_chart(fig_studios, use_container_width=True)
else:
    st.warning("数据集中未找到相关公司字段，无法进行比拼分析。")