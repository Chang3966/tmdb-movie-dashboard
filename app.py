import streamlit as st
import pandas as pd
import sys
import os
from openai import OpenAI

# 确保能找到 data_utils
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from data_utils import load_data, render_sidebar, apply_apple_glass_style 

# 全局页面配置 (这必须是 Streamlit 命令的第一句)
st.set_page_config(page_title="TMDB 数据看板", page_icon="🎬", layout="wide")

# ====================================================
# ✨ 第 1 步：一键全局注入 Apple 液态玻璃框美容代码！
# ====================================================
apply_apple_glass_style()

# ====================================================
# 🚀 第 2 步：加载数据并在首页挂载高级侧边栏
# ====================================================
with st.spinner("正在准备数据引擎..."):
    df, _ = load_data()

# 渲染超级侧边栏，并接收过滤后的数据结果
df_filtered = render_sidebar(df)

# ====================================================
# 📝 第 3 步：首页主视觉与文案
# ====================================================
st.title("🎬 欢迎来到 TMDB 电影数据分析系统")
st.markdown("---")

st.markdown("""
### 👈 请通过左侧导航栏探索以下核心模块：

* **📊 数据概览**：查看宏观电影数量、评分、类型与时长分布，以及流行趋势。
* **💰 商业分析**：深度挖掘预算与票房的关系，计算投资回报率 (ROI)，分析好莱坞影视巨头。
* **🤖 探索与推荐**：利用机器学习算法，根据您的喜好智能推荐相似电影，并附带动态海报画廊。
* **🕸️ 巨头合作网**：探索好莱坞巨头（华纳、迪士尼等）是如何抱团取暖的（物理引擎动态星系图）。
""")

# 动态交互提示：让首页立刻“活”起来！
st.success(f"💡 **当前数据池状态**：您已通过左侧边栏的条件，成功筛选出 **{len(df_filtered):,}** 部核心影片！切换到其他页面即可直接对这些数据进行可视化分析。")

st.markdown("""
> **🌟 数据集与工程说明**: 
> 本系统的数据底座源自 TMDB 庞大的 **百万级** 电影数据库。为了保障绝佳的网页交互与云端“秒开”体验，同时确保数据的专业合规（引入社区投票验证机制并剔除无效短片），我们在数据清洗阶段进行了严格的降维过滤，为您精炼并呈现了全球最具分析价值的 **190,000+** 部核心影视佳作。
""")

st.markdown("---")

# ====================================================
# 🧠 第 4 步：终极杀器 —— 本地结构化数据 Agent
# ====================================================
st.header("🧠 终极数据 Agent (结构化 RAG 体验)")
st.info("💡 **高阶演示**：这是企业级的数据 Agent 原型！它不仅懂通用知识，还能根据你左侧栏筛选出的 **动态数据集**，实时编写 Python 代码为你进行极度精确的跨纬度运算。")

# Agent 驱动配置区
with st.expander("⚙️ 唤醒 Agent (需在此输入 API Key)"):
    col1, col2 = st.columns(2)
    with col1:
        model_provider = st.selectbox("🤖 选择大模型引擎", ["DeepSeek", "Kimi", "通义千问"])
    with col2:
        api_key_input = st.text_input("🔑 填入 API Key", type="password")
        
    if model_provider == "DeepSeek":
        base_url = "https://api.deepseek.com"
        model_name = "deepseek-chat"
    elif model_provider == "Kimi":
        base_url = "https://api.moonshot.cn/v1"
        model_name = "moonshot-v1-8k"
    else:
        base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        model_name = "qwen-plus"

# 聊天输入框
user_query = st.chat_input("试着问：目前这个库里票房最高的前三部电影是哪几部？")

if user_query:
    if not api_key_input:
        st.error("⚠️ 请先在上方展开面板中输入您的 API Key 唤醒大脑！")
    else:
        client = OpenAI(api_key=api_key_input, base_url=base_url)
        
        with st.chat_message("user"):
            st.markdown(user_query)
            
        with st.chat_message("assistant"):
            # 使用 st.status 创建一个极具科技感的“思考过程”折叠面板！
            with st.status("🧠 Agent 正在启动数据引擎...", expanded=True) as status:
                try:
                    # 环节 1：Schema 注入
                    st.write("🔍 正在扫描本地 DataFrame 结构与当前过滤条件...")
                    schema = df_filtered.dtypes.to_string()
                    sample = df_filtered.head(2).to_string()
                    
                    sys_prompt = f"""
                    你是一个顶级的 Pandas 数据科学家。目前内存中有一个名为 `df` 的 DataFrame。
                    它的列名和数据类型如下：\n{schema}\n\n前2行样例：\n{sample}\n
                    用户的需求是：{user_query}
                    
                    请编写 Python 代码来完成这个分析。要求：
                    1. 只输出代码，不要包裹 ```python 和 ``` 标签，不要有任何多余的解释文字！
                    2. 将最终的分析答案赋值给一个名为 `result` 的变量。
                    3. 请确保使用的列名在上面的 Schema 中是真实存在的。
                    """
                    
                    # 环节 2：LLM 编写代码
                    st.write("💻 大模型正在根据您的需求编写专属 Python 挖掘脚本...")
                    response = client.chat.completions.create(
                        model=model_name,
                        messages=[{"role": "system", "content": sys_prompt}]
                    )
                    
                    code = response.choices[0].message.content.replace('```python', '').replace('```', '').strip()
                    st.code(code, language='python')
                    
                    # 环节 3：本地沙盒极其危险但炫酷的 Exec 执行
                    st.write("⚡ 正在本地沙盒执行代码并计算数据结果...")
                    local_vars = {'df': df_filtered, 'pd': pd}
                    exec(code, {}, local_vars)
                    raw_result = local_vars.get('result', "未能提取出 result 变量")
                    st.write(f"✅ 底层计算完成，原始数据包：{str(raw_result)[:100]}...")
                    
                    # 环节 4：二次总结润色
                    st.write("👄 正在交由大模型进行拟人化口语输出...")
                    summary_res = client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": "你是一个资深、幽默的电影数据分析师。请把下面干瘪的数据结果，转化成一段精彩的人话告诉用户。直接给结论，禁止啰嗦。"},
                            {"role": "user", "content": f"用户问题：{user_query} \n代码计算出来的精准数据：{raw_result}"}
                        ]
                    )
                    final_answer = summary_res.choices[0].message.content
                    
                    status.update(label="✅ Agent 分析与推演完成！", state="complete", expanded=False)
                    
                except Exception as e:
                    final_answer = f"非常抱歉，Agent 在编写数据清洗代码时发生了语法崩溃。可能是您问的问题超出了当前表结构的维度。\n\n**Debug 信息:** `{e}`"
                    status.update(label="❌ Agent 计算引发了异常", state="error", expanded=False)
            
            # 将最终润色好的答案大方地展示出来
            st.markdown(final_answer)