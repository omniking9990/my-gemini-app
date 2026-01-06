import streamlit as st
import google.generativeai as genai

# 設定頁面
st.set_page_config(page_title="Gemini 萬能助手", layout="wide")

# 檢查密鑰是否存在
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("請在 Secrets 中設定 GOOGLE_API_KEY")
    st.stop()

# 配置 API
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# --- 修改重點：使用絕對通用的模型名稱 ---
# 如果連這個都 404，代表 API Key 的區域權限有問題
model = genai.GenerativeModel('gemini-1.5-flash') 

st.title("Gemini 萬能助手 📂")

# 側邊欄檔案上傳
with st.sidebar:
    st.header("檔案上傳")
    uploaded_file = st.file_uploader("選擇檔案", type=["pdf", "txt", "py", "jpg", "png"])

# 初始化對話
if "messages" not in st.session_state:
    st.session_state.messages = []

# 顯示對話內容
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 處理輸入
if prompt := st.chat_input("請輸入問題..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # 構建發送內容
            content = [prompt]
            if uploaded_file:
                # 重新讀取檔案
                bytes_data = uploaded_file.getvalue()
                content.append({
                    "mime_type": "text/plain" if uploaded_file.name.endswith(".py") else uploaded_file.type,
                    "data": bytes_data
                })
            
            # 呼叫模型
            response = model.generate_content(content)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            # 顯示具體錯誤，幫助我們判斷是否為 Key 的問題
            st.error(f"連線異常：{e}")
