import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    df = pd.read_csv("TMDB_movie_dataset_v11.zip")
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