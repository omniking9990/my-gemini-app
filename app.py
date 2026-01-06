import streamlit as st
import google.generativeai as genai

# --- 基礎設定 ---
st.set_page_config(page_title="我的 AI 萬能助手", page_icon="🚀")
api_key = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)

# --- [核心修改] 自動尋找可用模型 ---
@st.cache_resource
def get_working_model():
    # 這裡列出所有可能的名稱，程式會一個一個試
    possible_models = [
        "gemini-1.5-flash",
        "gemini-1.5-flash-002",
        "gemini-1.5-pro",
        "gemini-1.5-pro-002"
    ]
    
    tools = [{"google_search_retrieval": {"dynamic_retrieval_config": {"mode": "dynamic", "dynamic_threshold": 0.3}}}]
    
    for m_name in possible_models:
        try:
            model = genai.GenerativeModel(
                model_name=m_name,
                system_instruction="你是一個具備分析能力與搜尋能力的助理。",
                tools=tools
            )
            # 測試是否真的可用
            model.generate_content("test")
            return model
        except:
            continue
    return None

model = get_working_model()

# --- 初始化對話 ---
if "chat_session" not in st.session_state and model:
    st.session_state.chat_session = model.start_chat(history=[])

st.title("Gemini 萬能助手 📂")

if not model:
    st.error("目前無法連接到任何 Gemini 模型，請檢查你的 API Key 是否有效。")
else:
    # --- 側邊欄：上傳功能 ---
    with st.sidebar:
        st.header("檔案上傳")
        uploaded_file = st.file_uploader("選擇圖片、PDF 或文字檔", type=["png", "jpg", "jpeg", "pdf", "txt", "py"])
        if uploaded_file:
            st.success(f"已上傳: {uploaded_file.name}")

    # --- 顯示對話紀錄 ---
    if "chat_session" in st.session_state:
        for message in st.session_state.chat_session.history:
            with st.chat_message("user" if message.role == "user" else "model"):
                st.markdown(message.parts[0].text)

    # --- 處理輸入 ---
    user_input = st.chat_input("針對檔案提問或聊天...")

    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)
        
        with st.chat_message("model"):
            try:
                content = [user_input]
                if uploaded_file:
                    content.append({"mime_type": "text/plain" if uploaded_file.name.endswith(".py") else uploaded_file.type, 
                                    "data": uploaded_file.read()})
                
                response = st.session_state.chat_session.send_message(content)
                st.markdown(response.text)
            except Exception as e:
                st.error(f"發生錯誤：{e}")
