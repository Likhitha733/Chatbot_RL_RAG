import streamlit as st
import os
from config import Config
from rag_engine import RAGEngine
from feedback_manager import FeedbackManager

st.set_page_config(page_title="Agentic AI RAG", layout="wide")

# Initialize Logic
if "rag" not in st.session_state:
    st.session_state.rag = RAGEngine()
    # Auto-init if db missing
    if not os.path.exists(Config.CHROMA_PATH):
         pass 

if "fb_manager" not in st.session_state:
    st.session_state.fb_manager = FeedbackManager()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_query" not in st.session_state:
    st.session_state.last_query = None
if "last_response" not in st.session_state:
    st.session_state.last_response = None

# Sidebar Controls
with st.sidebar:
    st.title("⚙️ RAG Controller")
    if st.button("🔄 Re-Index Database"):
        with st.spinner("Reading PDF & Chunking..."):
            st.session_state.rag.initialize_database(Config.PDF_PATH, force=True)
        st.success("Database Updated!")
    
    st.divider()
    st.subheader("🧠 RL Memory")
    stats = st.session_state.fb_manager.get_stats()
    st.metric("Questions Learned", stats['instructions_learned'])
    
    with st.expander("View Learned Rules"):
        for item in st.session_state.fb_manager.history:
            if item.get('instruction'):
                st.text(f"Q: {item['query']}\nRule: {item['instruction']}")
                st.divider()

# Main Chat
st.title("🤖 Agentic AI Expert")
st.caption("I learn from your feedback. If I miss details, teach me.")

# Render Chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("is_learned"):
            st.caption("✨ Answer improved by previous human feedback")

# Input
if prompt := st.chat_input("Ask about authors, clarity, or retail implementations..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # 1. RL STEP: Check Memory
            learned_instruction = st.session_state.fb_manager.get_instruction_for_query(prompt)
            
            # 2. RAG STEP: Retrieve & Sort
            chunks = st.session_state.rag.vector_store.search(prompt, top_k=Config.TOP_K_RESULTS)
            
            # 3. LLM STEP: Generate
            response_text = st.session_state.rag.answer_query(prompt, chunks, instruction=learned_instruction)
            
            st.markdown(response_text)
            if learned_instruction:
                st.success(f"Applied Learned Rule: {learned_instruction}")
            
    # Save context
    st.session_state.messages.append({
        "role": "assistant", 
        "content": response_text,
        "is_learned": bool(learned_instruction)
    })
    st.session_state.last_query = prompt
    st.session_state.last_response = response_text
    st.rerun()

# Feedback Loop (The "RL" Interface)
if st.session_state.last_response:
    st.divider()
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("✅ Perfect"):
            st.toast("Feedback recorded!")
            st.session_state.last_query = None
            st.rerun()
            
    with col2:
        with st.expander("🛠️ Teach & Improve (RL Feedback)"):
            st.write("If the answer was incomplete, tell me exactly what columns or details to add.")
            with st.form("teach_form"):
                instruction = st.text_area(
                    "Correction Instruction:", 
                    placeholder="Example: 'Present this as a table with columns: Author Name, Experience, and Page Number'"
                )
                if st.form_submit_button("Teach & Regenerate"):
                    # Save the Rule
                    st.session_state.fb_manager.store_feedback(
                        st.session_state.last_query,
                        st.session_state.last_response,
                        "negative",
                        instruction=instruction
                    )
                    st.toast("Rule Learned! Regenerating...")
                    
                    # Force Regenerate
                    st.session_state.messages.pop() # Remove old answer
                    
                    with st.spinner("Applying new rule..."):
                        chunks = st.session_state.rag.vector_store.search(st.session_state.last_query, top_k=Config.TOP_K_RESULTS)
                        new_response = st.session_state.rag.answer_query(st.session_state.last_query, chunks, instruction=instruction)
                        
                        st.session_state.messages.append({"role": "assistant", "content": new_response, "is_learned": True})
                        st.session_state.last_response = new_response
                        st.rerun()