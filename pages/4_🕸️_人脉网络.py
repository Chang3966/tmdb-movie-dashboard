import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
import sys
import os
import tempfile
import math
from itertools import combinations

# 确保能正确导入上一级目录的 data_utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data_utils import load_data, apply_apple_glass_style

st.set_page_config(page_title="巨头合作网", page_icon="🕸️", layout="wide")

# ====================================================
# ✨ 注入 Apple 毛玻璃液态框全局样式
# ====================================================
apply_apple_glass_style()

# 加载数据
with st.spinner('正在加载数据缓存...'):
    df, _ = load_data()

st.title("🕸️ 影视帝国：全球制片厂合作生态网")
st.markdown("探索好莱坞巨头们是如何抱团取暖、联合出品巨制的。拖拽节点体验动态引力！")
st.markdown("---")

if 'production_companies' not in df.columns:
    st.error("数据集缺少 production_companies 字段，无法构建网络图。")
else:
    # ====================================================
    # 🚀 核心性能优化：只取最受关注的前 3000 部大片！
    # 避免浏览器被上万个物理节点卡死
    # ====================================================
    df_net = df.dropna(subset=['production_companies']).sort_values('popularity', ascending=False).head(3000).copy()
    
    # UI 布局：左侧控制台，右侧星系图
    col_ctrl, col_graph = st.columns([1, 3])
    
    with col_ctrl:
        st.subheader("🎛️ 控制台")
        
        # 让用户通过滑动条控制图谱的密度
        min_coops = st.slider(
            "筛选最低【联合出品】次数：", 
            min_value=1, max_value=15, value=2,
            help="调高此数值，可以过滤掉偶然的合作，只看最核心的“铁杆商业联盟”。"
        )
        
        st.markdown(f"""
        **💡 性能提示：**
        为了保证网页流畅度，当前网络图基于全球最受欢迎的 **{len(df_net)}** 部顶级影片计算生成。
        
        **图例说明：**
        * 🟠 **星球节点**：代表一家制片巨头
        * 📏 **星球大小**：代表该公司的核心产出量
        * 🔗 **连线粗细**：代表联合出品的紧密程度
        """)

    with col_graph:
        with st.spinner('正在计算商业生态引力场... (瞬间完成)'):
            G = nx.Graph()
            
            company_counts = {}
            co_productions = {}
            
            for comps_str in df_net['production_companies']:
                comps = [c.strip() for c in str(comps_str).split(',') if c.strip()]
                
                for c in comps:
                    company_counts[c] = company_counts.get(c, 0) + 1
                    
                if len(comps) > 1:
                    for pair in combinations(sorted(comps), 2):
                        co_productions[pair] = co_productions.get(pair, 0) + 1
                        
            # 将满足最低合作次数的数据添加到网络图中
            for pair, count in co_productions.items():
                if count >= min_coops:
                    comp1, comp2 = pair
                    
                    if comp1 not in G:
                        node_size = 10 + math.log(company_counts[comp1] + 1) * 10
                        G.add_node(comp1, size=node_size, title=f"{comp1}\n顶级大片产量: {company_counts[comp1]} 部", color="#FF9500") 
                    if comp2 not in G:
                        node_size = 10 + math.log(company_counts[comp2] + 1) * 10
                        G.add_node(comp2, size=node_size, title=f"{comp2}\n顶级大片产量: {company_counts[comp2]} 部", color="#FF9500")
                        
                    G.add_edge(comp1, comp2, value=count, title=f"联合出品: {count} 次")
                    
            if len(G.nodes) == 0:
                st.info("当前筛选条件太严格啦，没有找到符合条件的商业联盟，请尝试调低左侧的滑动条。")
            else:
                # 限制最大节点数，防止极端情况卡死
                if len(G.nodes) > 400:
                    st.warning("节点数量过多，为了防卡顿，仅展示核心骨架。建议调高左侧过滤阈值。")
                
                nt = Network(height='600px', width='100%', bgcolor='rgba(0,0,0,0)', font_color='#1D1D1F')
                nt.from_nx(G)
                
                # 调整物理引擎参数，让图表展开得更快、更稳定
                nt.barnes_hut(gravity=-3000, central_gravity=0.15, spring_length=200, damping=0.09)
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
                    nt.save_graph(tmp_file.name)
                    HtmlFile = open(tmp_file.name, 'r', encoding='utf-8')
                    source_code = HtmlFile.read() 
                    st.components.v1.html(source_code, height=620)