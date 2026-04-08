import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    # 修改为：
    df = pd.read_csv("TMDB_small.csv.gz")
    df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
    df['release_year'] = df['release_date'].dt.year
    df_finance = df[(df['revenue'] > 0) & (df['budget'] > 0)].copy()
    return df, df_finance

def render_sidebar(df):
    st.sidebar.header("🎛️ 筛选控制中心")
    
    # 1. 年份筛选
    min_year, max_year = int(df['release_year'].min()), int(df['release_year'].max())
    year_range = st.sidebar.slider("上映年份范围", min_year, max_year, (2000, max_year))
    
    # 2. 类型筛选 (处理多标签)
    all_genres = set()
    df['genres'].dropna().str.split(',').apply(lambda x: [all_genres.add(g.strip()) for g in x])
    selected_genres = st.sidebar.multiselect("电影类型", sorted(list(all_genres)), default=[])
    
    # 3. 语言筛选
    top_languages = df['original_language'].value_counts().head(10).index.tolist()
    selected_langs = st.sidebar.multiselect("原声语言 (Top 10)", sorted(top_languages), default=[])
    
    # 4. 最低评分筛选
    min_score = st.sidebar.number_input("最低评分要求", 0.0, 10.0, 0.0, step=0.5)

    # 封装过滤逻辑
    mask = (df['release_year'] >= year_range[0]) & (df['release_year'] <= year_range[1]) & (df['vote_average'] >= min_score)
    
    if selected_genres:
        mask &= df['genres'].apply(lambda x: any(g in str(x) for g in selected_genres) if pd.notna(x) else False)
    
    if selected_langs:
        mask &= df['original_language'].isin(selected_langs)
        
    return df[mask]


def apply_apple_glass_style():
    """
    升级版 Apple 毛玻璃注入代码：使用底层 data-testid 精准锁定组件
    """
    st.markdown("""
        <style>
        /* 1. 强制主背景为极浅的高级灰，这样白色的毛玻璃卡片才能凸显出来！ */
        [data-testid="stAppViewContainer"] {
            background-color: #F5F5F7 !important; 
        }
        
        /* 2. 侧边栏整体毛玻璃 */
        [data-testid="stSidebar"] {
            background-color: rgba(255, 255, 255, 0.5) !important;
            backdrop-filter: blur(20px) !important;
            border-right: 1px solid rgba(255,255,255,0.3) !important;
        }

        /* 3. 精准锁定核心组件：指标卡片、图表、数据表格，强行注入毛玻璃 */
        [data-testid="stMetric"], 
        [data-testid="stPlotlyChart"], 
        [data-testid="stDataFrame"],
        [data-testid="stTable"] {
            background: rgba(255, 255, 255, 0.65) !important; /* 65% 透明度的纯白 */
            backdrop-filter: blur(16px) !important; /* 磨砂玻璃模糊效果 */
            border-radius: 20px !important; /* Apple 标准的大圆角 */
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.04) !important; /* 极其柔和的高级阴影 */
            border: 1px solid rgba(255, 255, 255, 0.8) !important; /* 玻璃边缘的高光反光 */
            padding: 20px !important;
            transition: transform 0.2s ease-in-out !important; /* 鼠标悬停动画准备 */
        }
        
        /* 4. 鼠标悬停在卡片上时微微上浮（增加交互灵动感） */
        [data-testid="stMetric"]:hover, 
        [data-testid="stPlotlyChart"]:hover {
            transform: translateY(-3px) !important;
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.08) !important;
        }

        /* 5. 字体与排版强制全局美化 */
        html, body, [class*="css"] {
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
            color: #1D1D1F !important;
        }
        
        /* 特别加粗强化数字指标 (Metric) */
        [data-testid="stMetricValue"] {
            font-size: 2.4rem !important;
            font-weight: 700 !important;
            color: #1D1D1F !important;
            letter-spacing: -1px !important;
        }
        </style>
    """, unsafe_allow_html=True)