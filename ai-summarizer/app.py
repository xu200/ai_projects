import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="AI Text Summarizer", page_icon="📝", layout="centered")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input(
        "DeepSeek API Key",
        type="password",
        placeholder="sk-...",
        help="Get your key at platform.deepseek.com",
    )
    st.divider()
    summary_length = st.select_slider(
        "Summary Length",
        options=["Very Short", "Short", "Medium", "Detailed"],
        value="Medium",
    )
    summary_lang = st.selectbox(
        "Output Language",
        ["Same as input", "Chinese", "English", "Japanese"],
        index=0,
    )
    st.divider()
    st.caption("Powered by DeepSeek API")


def get_client():
    if not api_key:
        return None
    return OpenAI(api_key=api_key, base_url="https://api.deepseek.com")


LENGTH_MAP = {
    "Very Short": "1-2 sentences",
    "Short": "3-5 sentences",
    "Medium": "a short paragraph (about 100 words)",
    "Detailed": "2-3 paragraphs (about 200 words)",
}


def summarize(client, text, length, lang):
    lang_instruction = ""
    if lang != "Same as input":
        lang_instruction = f"\nIMPORTANT: Write the summary in {lang}."

    prompt = f"""Summarize the following text in {LENGTH_MAP[length]}.
Keep the key points and main ideas. Be concise and accurate.{lang_instruction}

Text to summarize:
\"\"\"
{text}
\"\"\"

Summary:"""

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "system",
                "content": "You are a professional text summarizer. Provide clear, accurate, and concise summaries.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()


def count_words(text):
    return len(text.split())


def count_chars(text):
    return len(text)


# Main UI
st.title("📝 AI Text Summarizer")
st.caption("Paste any text and let AI generate a concise summary for you!")

text_input = st.text_area(
    "Paste your text here:",
    height=250,
    placeholder="Paste a long article, essay, report, or any text you want to summarize...",
)

# Stats
if text_input:
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Characters", f"{count_chars(text_input):,}")
    with col2:
        st.metric("Words", f"{count_words(text_input):,}")

if st.button("🚀 Summarize", type="primary", use_container_width=True):
    client = get_client()
    if not client:
        st.error("Please enter your DeepSeek API Key in the sidebar.")
    elif not text_input or len(text_input.strip()) < 50:
        st.error("Please enter at least 50 characters of text to summarize.")
    else:
        with st.spinner("AI is summarizing..."):
            try:
                result = summarize(client, text_input, summary_length, summary_lang)
            except Exception as e:
                st.error(f"Error: {e}")
                result = None

        if result:
            st.divider()
            st.subheader("📋 Summary")
            st.write(result)

            # Show compression ratio
            original_len = count_chars(text_input)
            summary_len = count_chars(result)
            ratio = round((1 - summary_len / original_len) * 100)
            st.divider()
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Original", f"{original_len} chars")
            with c2:
                st.metric("Summary", f"{summary_len} chars")
            with c3:
                st.metric("Compressed", f"{ratio}%")
