import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    # 修改为：
    df = pd.read_csv("TMDB_small.csv")
    df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
    df['release_year'] = df['release_date'].dt.year
    df_finance = df[(df['revenue'] > 0) & (df['budget'] > 0)].copy()
    return df, df_finance

def render_sidebar(df):
    st.sidebar.header("⚙️ 全局过滤条件")
    min_year = int(df['release_year'].min()) if pd.notna(df['release_year'].min()) else 1900
    max_year = int(df['release_year'].max()) if pd.notna(df['release_year'].max()) else 2024
    
    selected_years = st.sidebar.slider(
        "选择电影上映年份区间",
        min_value=min_year, max_value=max_year, value=(2000, max_year)
    )
    return selected_years

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