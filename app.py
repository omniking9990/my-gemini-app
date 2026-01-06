import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Gemini 萬能助手", layout="wide")

if "GOOGLE_API_KEY" not in st.secrets:
    st.error("請在 Secrets 中設定 GOOGLE_API_KEY")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# --- [核心修改] 自動搜尋可用模型名稱 ---
@st.cache_resource
def find_available_model():
    try:
        # 列出所有可用的模型
        for m in genai.list_models():
            # 優先尋找支援生成內容且名稱包含 1.5 的模型
            if 'generateContent' in m.supported_generation_methods:
                if "1.5-flash" in m.name or "1.5-pro" in m.name:
                    return m.name
        return None
    except Exception as e:
        st.error(f"無法列出模型清單：{e}")
        return None

target_model_name = find_available_model()

if not target_model_name:
    st.error("你的 API Key 目前似乎沒有可用的 Gemini 模型權限。")
    st.stop()

# 顯示目前使用的模型名稱（除錯用）
st.caption(f"🚀 目前運作模型：{target_model_name}")

model = genai.GenerativeModel(target_model_name)

# --- 以下維持對話功能 ---
st.title("Gemini 萬能助手 📂")

with st.sidebar:
    st.header("檔案上傳")
    uploaded_file = st.file_uploader("選擇檔案", type=["pdf", "txt", "py", "jpg", "png"])

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("請輸入問題..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            content = [prompt]
            if uploaded_file:
                bytes_data = uploaded_file.getvalue()
                content.append({
                    "mime_type": "text/plain" if uploaded_file.name.endswith(".py") else uploaded_file.type,
                    "data": bytes_data
                })
            
            response = model.generate_content(content)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            st.error(f"連線異常：{e}")
