import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from data_utils import load_data, render_sidebar, apply_apple_glass_style # 导入新函数
# 全局页面配置 (font 部分不再需要，CSS 里有全局强制)
st.set_page_config(page_title="TMDB 数据看板", page_icon="🎬", layout="wide")

# ====================================================
# ✨ 第 1 步：一键全局注入 Apple 液态玻璃框美容代码！
# ====================================================
apply_apple_glass_style()

st.title("🎬 欢迎来到 TMDB 电影数据分析系统")
st.markdown("---")
st.markdown("""
### 👈 请通过左侧导航栏探索不同模块：

* **📊 数据概览**：查看宏观电影数量、评分、类型与时长分布，以及流行趋势。
* **💰 商业分析**：深度挖掘预算与票房的关系，计算投资回报率 (ROI)，分析好莱坞影视巨头。
* **🤖 探索与推荐**：利用机器学习算法，根据您的喜好智能推荐相似电影，并附带动态海报画廊。

> **🌟 数据集与工程说明**: 
> 本系统的数据底座源自 TMDB 庞大的 **百万级** 电影数据库。考虑到真实场景下的数据冗余（存在大量无票房、无海报的学生作品或短片），为了保障绝佳的网页交互与云端“秒开”体验，我们在数据清洗阶段按受欢迎程度（Popularity）进行了严格的降维过滤，为您精炼并呈现了全球最具分析价值的 **190,000+** 部核心影视佳作。
""")

st.info("💡 提示：您可以在任何页面的左侧边栏调整【上映年份】来全局过滤这近 20 万部核心数据。")