import streamlit as st
import google.generativeai as genai

# 設定頁面標題
st.set_page_config(page_title="Gemini 萬能助手", layout="wide")

# 1. 安全讀取 Secrets
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("請在 Streamlit Secrets 中設定 GOOGLE_API_KEY")
    st.stop()

# 2. 設定 API
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# 3. 指定最通用的模型名稱 (Gemini 1.5 Flash 是目前最穩定的)
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"模型啟動失敗: {e}")
    st.stop()

st.title("Gemini 萬能助手 📂")

# 側邊欄：上傳你的劇本檔
with st.sidebar:
    st.header("檔案中心")
    uploaded_file = st.file_uploader("選擇檔案 (PDF, TXT, PY)", type=["pdf", "txt", "py"])

# 4. 初始化對話紀錄
if "messages" not in st.session_state:
    st.session_state.messages = []

# 顯示聊天歷程
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 5. 處理輸入
if prompt := st.chat_input("請輸入問題..."):
    # 儲存使用者問題
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # 準備發送給 AI 的內容
            content_to_send = [prompt]
            
            # 如果有上傳檔案，將檔案內容加入對話
            if uploaded_file:
                # 取得檔案內容並判斷類型
                file_bytes = uploaded_file.getvalue()
                mime_type = "text/plain" if uploaded_file.name.endswith(".py") else uploaded_file.type
                content_to_send.append({
                    "mime_type": mime_type,
                    "data": file_bytes
                })
            
            # 呼叫 Gemini
            response = model.generate_content(content_to_send)
            
            # 顯示與儲存回答
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            st.error(f"連線失敗，可能是 API Key 權限問題。錯誤訊息：{e}")
