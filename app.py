import streamlit as st
import google.generativeai as genai
import os

# --- 設定頁面標題與手機排版 ---
st.set_page_config(page_title="我的 AI 助理", page_icon="🧠", layout="centered")

# --- 1. 取得 API Key (安全性設定) ---
# 我們稍後會在 Streamlit 網站後台設定這個密鑰，這樣才安全
api_key = st.secrets["GOOGLE_API_KEY"]

# --- 2. 設定 AI 模型邏輯 (教學重點) ---
def configure_model():
    genai.configure(api_key=api_key)
    
    # [核心功能] 設定永久記憶指令 (System Instruction)
    # 這段文字就像是植入 AI 大腦的晶片，無論聊了 200 句還是 1000 句，
    # 它永遠會記得這段規則，並且權重最高。
    sys_instruction = """
    你是一個擁有強大搜尋能力與邏輯的 AI 助理。
    請嚴格遵守以下規則：
    1. 你的思考模式必須模擬 Gemini Pro 的高智商邏輯。
    2. 回答任何問題前，必須判斷是否需要事實佐證。若需要，必須使用 Google Search 工具。
    3. 你的回答必須與 Google 搜尋結果的事實完全一致，不可產生幻覺。
    4. 永遠保持冷靜、專業的語氣。
    """
    
    # [核心功能] 啟用 Google 搜尋工具 (Grounding)
    tools = [
    {"google_search_retrieval": {
        "dynamic_retrieval_config": {
            "mode": "dynamic",
            "dynamic_threshold": 0.3
        }
    }}
]
    
    # 建立模型
    # 注意：這裡使用 gemini-1.5-pro，它是目前免費版最強的模型
    # 未來若有 3.0，直接把名字改成 "gemini-3.0-pro" 即可
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        system_instruction=sys_instruction,
        tools=tools
    )
    return model

# --- 3. 處理記憶體 (Session State) ---
# Streamlit 每次刷新畫面都會重跑程式，所以我們要用 Session State 把對話紀錄「存起來」
if "chat_session" not in st.session_state:
    try:
        model = configure_model()
        st.session_state.chat_session = model.start_chat(history=[])
    except Exception as e:
        st.error(f"請先設定 API Key 才能開始使用。錯誤訊息: {e}")

# --- 4. 打造聊天介面 (UI) ---
st.title("Gemini Pro 搜尋增強版 🚀")

# 顯示過去的對話紀錄
if "chat_session" in st.session_state:
    for message in st.session_state.chat_session.history:
        role = "user" if message.role == "user" else "model"
        with st.chat_message(role):
            st.markdown(message.parts[0].text)

# --- 5. 接收指令與回答 ---
user_input = st.chat_input("請輸入你的指令...")

if user_input and "chat_session" in st.session_state:
    # 顯示你的問題
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # AI 思考並回答
    with st.chat_message("model"):
        with st.spinner("正在搜尋網路資料並思考中..."): # 顯示思考轉圈圈
            try:
                # 發送訊息給 AI
                response = st.session_state.chat_session.send_message(user_input)
                
                # 顯示 AI 的文字
                st.markdown(response.text)
                
                # [核心功能] 顯示搜尋來源 (Grounding Metadata)
                # 這是為了證明它真的有去查資料
                if response.candidates[0].grounding_metadata.search_entry_point:
                    st.divider()
                    st.caption("🔍 參考資料來源：")
                    st.markdown(response.candidates[0].grounding_metadata.search_entry_point.rendered_content)
                    
            except Exception as e:
                st.error(f"發生錯誤：{e}")

