import streamlit as st
import google.generativeai as genai

# 設定頁面
st.set_page_config(page_title="Gemini 萬能助手", layout="wide")

# 讀取金鑰
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("請在 Secrets 中設定 GOOGLE_API_KEY")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# 強制指定一個最容易成功的模型
# 請將這行完整替換，注意包含了 'models/' 和具體版本號 '002'
model = genai.GenerativeModel('models/gemini-1.5-flash-002')

st.title("Gemini 萬能助手 📂")

# 側邊欄上傳檔案
with st.sidebar:
    st.header("檔案上傳")
    uploaded_file = st.file_uploader("選擇檔案 (PDF, TXT, PY, JPG)", type=["pdf", "txt", "py", "jpg", "png"])

# 初始化對話紀錄
if "messages" not in st.session_state:
    st.session_state.messages = []

# 顯示過去對話
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 處理使用者輸入
if prompt := st.chat_input("請輸入問題..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # 準備發送的內容
            request_content = [prompt]
            if uploaded_file:
                # 讀取檔案內容
                file_bytes = uploaded_file.read()
                request_content.append({
                    "mime_type": "text/plain" if uploaded_file.name.endswith(".py") else uploaded_file.type,
                    "data": file_bytes
                })
            
            # 取得回應
            response = model.generate_content(request_content)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            st.error(f"連線失敗，請檢查 API Key 是否正確。錯誤代碼: {e}")


