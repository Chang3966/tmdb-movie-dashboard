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
    极客美容时间！
    集中注入 Apple 毛玻璃液态框 (Glassmorphism) 全局样式。
    """
    st.markdown("""
        <style>
        /* ====================================================
           🎨 APPLE GLASS LAYOUT & LAYERING
           利用自定义 CSS 全局实现毛玻璃卡片式布局
           ==================================================== */
           
        /* 1. 设置侧边栏和主页面的全局背景，模拟 iOS 的层次感 */
        [data-testid="stSidebar"] {
            background-color: rgba(245, 245, 247, 0.5) !important; /* 极浅灰半透明 */
            backdrop-filter: blur(20px) !important; /* 侧边栏整体毛玻璃 */
        }
        
        .main .block-container {
            background-color: #FDFDFD !important; /* 保持主页面的极简纯白底色 */
        }
        
        /* 2. 核心模块：为每一个独立的 st.metric, st.dataframe, st.plotly_chart 容器
           添加 Apple 经典的毛玻璃液态框样式 */
        .main .element-container {
            /* 基础设置：确保内容不会超出圆角边界 */
            overflow: visible !important;
            margin-bottom: 2rem !important;
        }

        /* 我们将针对 st.metric, st.container, st.dataframe, st.plotly_chart 等容器
           添加全局的卡片化和毛玻璃样式 */
        .main .stMetric,
        .main .stPlotlyChart > div,
        .main .stTable > div,
        .main .stDataframe > div,
        .main .stMarkdown > div {
            /* 真正的毛玻璃配方 (Glassmorphism) */
            background: rgba(255, 255, 255, 0.4) !important; /* 半透明白色背景 */
            backdrop-filter: blur(15px) !important; /* 关键：磨砂模糊背景，比效果图的 20px 柔和一点，兼容性更好 */
            
            /* Apple 优雅的大圆角 */
            border-radius: 18px !important;
            
            /* 极其柔和且有层次感的阴影 */
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.08) !important;
            
            /* 极其细微的边框高亮，模拟玻璃的物理光泽 */
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            
            /* 优雅的内边距，减少视觉拥挤 */
            padding: 1.5rem !important;
        }

        /* 3. 字体美化：全系统强制使用 Apple 无衬线字体系统 */
        .main, .stMarkdown, .stText, .stDataFrame, .stMetric label {
            font-family: "sans serif", "SF Pro", -apple-system, system-ui, BlinkMacSystemFont !important;
            color: #1D1D1F !important; /* macOS 文字颜色 */
        }

        /* 4. 排版微调：确保所有 h1-h6 标题也使用 Apple 字体系统 */
        .main h1, .main h2, .main h3, .main h4, .main h5, .main h6 {
            font-family: "sans serif", "SF Pro Display", -apple-system, system-ui !important;
            color: #1D1D1F !important;
            font-weight: 700 !important;
        }
        
        /* 5. 针对 metric 的指标值进行特殊排版，粗化字重 */
        .main .stMetric > div:nth-child(2) > div:nth-child(1) {
            font-size: 2.2rem !important;
            font-weight: 700 !important;
            letter-spacing: -0.5px !important;
        }
        </style>
    """, unsafe_allow_html=True)