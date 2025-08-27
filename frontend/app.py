# app.py
import streamlit as st
import asyncio
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ------------------------------------------------------------------
#  1️⃣  Import the modules we just created
# ------------------------------------------------------------------
from backend.data_processing import DataProcessing   # ← your data‑processing logic
from backend.rag_engine import ask                   # ← ask() from the snippet above

# ------------------------------------------------------------------
#  2️⃣  Load config – it’s also used by the data‑processor
# ------------------------------------------------------------------
config_path = "config/config.json"
st.session_state.data_ready = True
# ------------------------------------------------------------------
#  3️⃣  Run the data‑processor once (and *block* until it finishes)
# ------------------------------------------------------------------
if "data_ready" not in st.session_state:
    st.write("🚀  Initialising the vector store … this may take a moment …")
    # the method is async; we run it synchronously in Streamlit by awaiting it
    asyncio.run(DataProcessing.launch_processing())
    st.session_state.data_ready = True
    st.success("✅  Vector store ready!")

# ------------------------------------------------------------------
#  4️⃣  Streamlit UI
# ------------------------------------------------------------------
st.title("📚  PDF‑Powered Q&A")

# 4.1  Question input
user_question = st.text_input(
    label="Ask me anything …",
    placeholder="What is RAM?",
    key="question_input",
)

# 4.2  Send / Reset buttons
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("Send", type="primary", key="send_btn"):
        if not user_question.strip():
            st.warning("Please type a question first.")
        else:
            # 4.3  Run the chain
            answer, docs = ask(user_question)

            # 4.4  Store in session_state for later reuse
            st.session_state.answer = answer
            st.session_state.docs   = docs
            st.session_state.question = user_question

with col2:
    if st.button("Clear", type="secondary", key="clear_btn"):
        st.session_state.pop("answer", None)
        st.session_state.pop("docs", None)
        st.session_state.pop("question", None)

# ------------------------------------------------------------------
#  5️⃣  Show the answer
# ------------------------------------------------------------------
if "answer" in st.session_state:
    st.subheader("💬  Answer")
    st.write(st.session_state.answer)

    # ------------------------------------------------------------------
    #  5.1  Show source documents (titles + chunks)
    # ------------------------------------------------------------------
    st.subheader("📖  Source Documents")
    for i, source in enumerate(st.session_state.docs):
        title = source if source else f"Document {i+1}"
        
        # Use an expander so the UI stays tidy
        with st.expander(label=f"{i+1}. {title}", expanded=False):
            st.info(f"Source: {title}")
            st.write("This document was used to generate the answer above.")
