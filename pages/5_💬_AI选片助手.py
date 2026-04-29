import streamlit as st
from openai import OpenAI
import sys
import os
import time

# 确保能正确导入上一级主目录的 data_utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data_utils import apply_apple_glass_style

st.set_page_config(page_title="AI 选片助手", page_icon="💬", layout="wide")

# ====================================================
# ✨ 注入 Apple 毛玻璃液态框全局样式
# ====================================================
apply_apple_glass_style()

# ====================================================
# 🔑 侧边栏：国内大模型 API 密钥配置区
# ====================================================
st.sidebar.header("⚙️ 助手配置")

# 以下拉框的形式，让你随时切换不同的国内大模型！
model_provider = st.sidebar.selectbox(
    "🤖 选择大模型引擎",
    ["DeepSeek (深度求索)", "Kimi (月之暗面)", "通义千问 (阿里云)"]
)

api_key_input = st.sidebar.text_input(
    f"🔑 填入您的 {model_provider} API Key", 
    type="password", 
    help="本站不会存储您的密钥。请前往对应官网免费申请。"
)

if model_provider == "DeepSeek (深度求索)":
    st.sidebar.markdown("[👉 点击申请 DeepSeek API](https://platform.deepseek.com/)")
    base_url = "https://api.deepseek.com"
    model_name = "deepseek-chat"
elif model_provider == "Kimi (月之暗面)":
    st.sidebar.markdown("[👉 点击申请 Kimi API](https://platform.moonshot.cn/)")
    base_url = "https://api.moonshot.cn/v1"
    model_name = "moonshot-v1-8k"
else:
    st.sidebar.markdown("[👉 点击申请 通义千问 API](https://dashscope.console.aliyun.com/)")
    base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    model_name = "qwen-plus"

st.title("💬 AI 智能选片助手 (极速版)")

if not api_key_input:
    st.warning(f"👈 请先在左侧边栏输入您的 **{model_provider} API Key** 唤醒大脑！")
    st.info("💡 **国内直连，拒绝卡顿！** 本项目现已全面接入国内顶尖大模型生态，零延迟、更懂中文语境。")
    st.stop()

# ====================================================
# 🧠 初始化 OpenAI 兼容客户端
# ====================================================
try:
    client = OpenAI(
        api_key=api_key_input,
        base_url=base_url  # 核心魔法：把请求地址指向国内厂商的服务器！
    )
except Exception as e:
    st.error("初始化客户端失败，请检查配置。")
    st.stop()

st.info(f"🧠 当前驱动大脑：**{model_provider}** | 状态：🟢 极速直连中")

# ====================================================
# 💬 页面 UI 与聊天逻辑 (极致丝滑打字机)
# ====================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

# 渲染历史聊天记录
for message in st.session_state.messages:
    # 不显示系统提示词
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.chat_input("例如：帮我找几部类似于神偷奶爸的温馨搞笑的少儿电影"):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # 组装给大模型的历史对话（包含系统人设）
            system_msg = {"role": "system", "content": "你是一个极其专业的资深电影专家。请废话少说，直接推荐3部电影，每部一句话理由。"}
            # 只取最近几轮对话防止 tokens 爆炸
            chat_history = [system_msg] + st.session_state.messages[-5:] 

            # 🚀 核心修改：在这里加入 st.spinner，并把发起请求到打字输出的代码，全部往右缩进一格！
            with st.spinner("⏳ 大脑飞速运转中，正在跨越光年为您检索电影宇宙..."):
                
                # 发起国内直连请求！
                response = client.chat.completions.create(
                    model=model_name,
                    messages=chat_history,
                    stream=True  # 依然开启流式输出
                )
                
                # 国内模型的文字切片解析方式略有不同
                def stream_generator():
                    for chunk in response:
                        # 获取国内模型传回的文字碎片
                        content = chunk.choices[0].delta.content
                        if content:
                            for char in content:
                                yield char
                                time.sleep(0.005) # 丝滑打字感
                                
                full_response = st.write_stream(stream_generator)
            
            # 🚀 注意这里：打字完毕后，退出 spinner 的缩进（退回一格），保存聊天记录
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error("呼叫国内大脑失败... 请检查 API Key 是否正确，或当前账户是否有余额。")
            st.caption(f"详细错误信息：{e}")