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
    # 🚀 核心性能优化：只取最受关注的前 3000 部大片
    df_net = df.dropna(subset=['production_companies']).sort_values('popularity', ascending=False).head(3000).copy()
    
    # ====================================================
    # 🧠 第一步：预先计算所有的合作频次和公司产量
    # ====================================================
    company_counts = {}
    co_productions = {}
    
    for comps_str in df_net['production_companies']:
        comps = [c.strip() for c in str(comps_str).split(',') if c.strip()]
        for c in comps:
            company_counts[c] = company_counts.get(c, 0) + 1
        if len(comps) > 1:
            for pair in combinations(sorted(comps), 2):
                co_productions[pair] = co_productions.get(pair, 0) + 1

    # 提取所有有合作关系的公司，并按产量排序（用于下拉菜单）
    valid_companies = sorted(
        [comp for comp, count in company_counts.items() if count > 1], 
        key=lambda x: company_counts[x], 
        reverse=True
    )

    # UI 布局：左侧控制台，右侧星系图
    col_ctrl, col_graph = st.columns([1, 3])
    
    with col_ctrl:
        st.subheader("🎛️ 控制台")
        
        # 🎯 A+ 级交互升级：聚光灯模式 (Ego Graph)
        st.markdown("##### 🔍 聚光灯模式")
        focus_company = st.selectbox(
            "选择一家制片厂，过滤并高亮其专属合作网：",
            options=["-- 显示全局星系 --"] + valid_companies,
            help="选择特定公司后，图谱将只显示该公司的直接合作伙伴，彻底告别“毛线球”般的混乱！"
        )
        
        st.markdown("---")
        
        # 全局密度控制
        st.markdown("##### ⚙️ 全局密度控制")
        min_coops = st.slider(
            "筛选最低【联合出品】次数：", 
            min_value=1, max_value=15, value=2,
            help="调高此数值，可以过滤掉偶然的合作，只看最核心的“铁杆商业联盟”。（仅在全局星系模式下生效）"
        )
        
        st.markdown(f"""
        **💡 性能提示：**
        当前图谱基于全球最受欢迎的 **{len(df_net)}** 部顶级影片计算。
        
        **图例说明：**
        * 🟠 **星球节点**：代表一家制片巨头
        * 📏 **星球大小**：代表该公司的核心产出量
        * 🔗 **连线粗细**：代表联合出品的紧密程度
        """)

    with col_graph:
        with st.spinner('🕸️ 正在使用 NetworkX 计算商业生态引力场... '):
            G = nx.Graph()
            
            # ====================================================
            # 🧠 第二步：根据用户的过滤条件构建网络
            # ====================================================
            is_focus_mode = focus_company != "-- 显示全局星系 --"
            
            for pair, count in co_productions.items():
                comp1, comp2 = pair
                
                # 如果是聚光灯模式，只添加包含目标公司的边；且不限制最低合作次数，展示该公司的所有触角
                if is_focus_mode:
                    if comp1 != focus_company and comp2 != focus_company:
                        continue 
                # 如果是全局模式，则严格执行最低合作次数过滤，防止毛线球
                elif count < min_coops:
                    continue
                    
                # 添加节点 (如果不存在)
                if comp1 not in G:
                    size = 10 + math.log(company_counts[comp1] + 1) * 10
                    # 如果是聚光灯主角，标为醒目的红色并放大
                    if is_focus_mode and comp1 == focus_company:
                        G.add_node(comp1, size=size*1.5, title=f"🌟 {comp1} (核心)\n大片产量: {company_counts[comp1]}", color="#FF3B30")
                    else:
                        G.add_node(comp1, size=size, title=f"{comp1}\n大片产量: {company_counts[comp1]}", color="#FF9500") 
                        
                if comp2 not in G:
                    size = 10 + math.log(company_counts[comp2] + 1) * 10
                    if is_focus_mode and comp2 == focus_company:
                        G.add_node(comp2, size=size*1.5, title=f"🌟 {comp2} (核心)\n大片产量: {company_counts[comp2]}", color="#FF3B30")
                    else:
                        G.add_node(comp2, size=size, title=f"{comp2}\n大片产量: {company_counts[comp2]}", color="#FF9500")
                        
                # 添加边
                G.add_edge(comp1, comp2, value=count, title=f"联合出品: {count} 次")
                    
            # ====================================================
            # 🖼️ 第三步：渲染引擎
            # ====================================================
            if len(G.nodes) == 0:
                st.info("当前筛选条件太严格，或者该公司暂无符合条件的合作方。请尝试放宽条件。")
            else:
                # 危险警告：全局模式下节点还是太多
                if not is_focus_mode and len(G.nodes) > 300:
                    st.warning("⚠️ 当前全局星系节点极多，物理引擎可能会产生轻微卡顿。建议使用左侧的【聚光灯模式】查看特定公司！")
                
                nt = Network(height='600px', width='100%', bgcolor='rgba(0,0,0,0)', font_color='#1D1D1F')
                nt.from_nx(G)
                
                # 调整物理引擎：聚光灯模式下让周围的节点散得更开
                if is_focus_mode:
                    nt.barnes_hut(gravity=-5000, central_gravity=0.1, spring_length=250, damping=0.09)
                else:
                    nt.barnes_hut(gravity=-3000, central_gravity=0.15, spring_length=200, damping=0.09)
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
                    nt.save_graph(tmp_file.name)
                    HtmlFile = open(tmp_file.name, 'r', encoding='utf-8')
                    source_code = HtmlFile.read() 
                    st.components.v1.html(source_code, height=620)