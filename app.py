import streamlit as st
import google.generativeai as genai

# --- 1. 基礎設定 ---
st.set_page_config(page_title="我的 AI 萬能助手", page_icon="🚀")
api_key = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)

# --- 2. 設定模型 (含搜尋與上傳支援) ---
def get_model():
    # 這裡使用最新正確的搜尋語法
    tools = [{"google_search_retrieval": {"dynamic_retrieval_config": {"mode": "dynamic", "dynamic_threshold": 0.3}}}]
    
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash-latest",
        system_instruction="你是一個具備檔案分析與網路搜尋能力的 AI。當使用者上傳檔案時，請先分析檔案內容再回答。",
        tools=tools
    )
    return model

# 初始化對話
if "chat_session" not in st.session_state:
    st.session_state.chat_session = get_model().start_chat(history=[])

st.title("Gemini Pro 萬能助手 (支援檔案) 📂")

# --- 3. 側邊欄：上傳功能 ---
with st.sidebar:
    st.header("檔案上傳")
    uploaded_file = st.file_uploader("選擇圖片、PDF 或文字檔", type=["png", "jpg", "jpeg", "pdf", "txt"])
    if uploaded_file:
        st.success(f"已偵測到檔案: {uploaded_file.name}")

# --- 4. 顯示對話紀錄 ---
for message in st.session_state.chat_session.history:
    with st.chat_message("user" if message.role == "user" else "model"):
        st.markdown(message.parts[0].text)

# --- 5. 處理輸入與檔案 ---
user_input = st.chat_input("請輸入問題或針對檔案提問...")

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)
    
    with st.chat_message("model"):
        with st.spinner("分析中..."):
            try:
                content_list = [user_input]
                
                # 如果有上傳檔案，將檔案轉為 Gemini 可讀格式
                if uploaded_file:
                    file_data = uploaded_file.read()
                    content_list.append({
                        "mime_type": uploaded_file.type,
                        "data": file_data
                    })
                
                # 發送包含文字與檔案的請求
                response = st.session_state.chat_session.send_message(content_list)
                st.markdown(response.text)
                
                # 顯示搜尋來源
                if response.candidates[0].grounding_metadata.search_entry_point:
                    st.divider()
                    st.caption("🔍 網路搜尋來源：")
                    st.markdown(response.candidates[0].grounding_metadata.search_entry_point.rendered_content)
            except Exception as e:
                st.error(f"發生錯誤：{e}")



