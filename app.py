import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS

# --- 1. 基礎設定 ---
st.set_page_config(page_title="Llama 3 超級助手", page_icon="⚡", layout="wide")

# 檢查金鑰
if "GROQ_API_KEY" not in st.secrets:
    st.error("請在 Secrets 中設定 GROQ_API_KEY")
    st.stop()

# 初始化 Groq 客戶端
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 2. 定義強大的搜尋功能 (免費且即時) ---
def search_web(query):
    try:
        results = DDGS().text(query, max_results=3)
        if results:
            summary = "\n".join([f"- {r['title']}: {r['body']} (來源: {r['href']})" for r in results])
            return summary
        return "無搜尋結果。"
    except Exception as e:
        return f"搜尋錯誤: {e}"

# --- 3. 初始化記憶體 ---
if "messages" not in st.session_state:
    # 這裡設定「第一則指令」，無論對話多長，AI 永遠會記得這條
    st.session_state.messages = [
        {"role": "system", "content": "你是一個深度思考的 AI 助手。你必須具備以下特質：\n1. 每次回答前，必須先分析使用者的問題是否需要網路資訊。\n2. 你的回答必須基於事實。\n3. 無論對話進行多久，你都必須嚴格遵守使用者的第一條指令設定。"}
    ]

# --- 4. 介面設計 ---
st.title("Llama 3.3 x 即時搜尋 ⚡")
st.caption("🚀 模型：Meta Llama-3.3-70B | 搜尋：DuckDuckGo")

# 顯示歷史對話 (不顯示系統指令，只顯示對話)
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# --- 5. 處理輸入與思考 ---
if prompt := st.chat_input("請輸入問題..."):
    # 1. 顯示使用者問題
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. AI 思考與搜尋
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # 步驟 A: 搜尋網路資料
        with st.status("🔍 正在搜尋網路並深度分析...", expanded=False) as status:
            search_results = search_web(prompt)
            status.write(f"已獲取網路資料：\n{search_results}")
            status.update(label="✅ 分析完成", state="complete")
        
        # 步驟 B: 組合最終提示詞 (包含歷史紀錄 + 搜尋結果)
        # 為了確保記憶力，我們將搜尋結果作為當前的背景知識傳入
        full_context_prompt = f"使用者問題：{prompt}\n\n參考的網路即時資訊：\n{search_results}\n\n請根據以上資訊與歷史對話進行深度回答："
        
        # 暫時替換最後一條訊息內容給 AI 看 (包含搜尋結果)，但不存入歷史以免混亂
        messages_for_ai = st.session_state.messages[:-1] + [{"role": "user", "content": full_context_prompt}]

        try:
            # 步驟 C: 呼叫 Llama 模型
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages_for_ai,
                temperature=0.7,
                max_tokens=4096,
                stream=True,
            )
            
            # 串流輸出回答
            full_response = ""
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
            # 3. 儲存 AI 回答
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"發生錯誤：{e}")
