import streamlit as st

from rule_engine.rule_engine import analyze_question, get_vague_words
from ml_model.ml_predictor import AmbiguityMLPredictor
from chatbot import get_answer

st.set_page_config(
    page_title="AmbiQ — Question Clarity Analyzer",
    page_icon="🔍",
    layout="wide"
)

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
    * { font-family: 'Inter', sans-serif; box-sizing: border-box; }

    .stApp { background: #f0f2f8; color: #1e1e2e; }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding: 1.5rem 3rem 2rem; max-width: 1080px; }

    /* ── Hero ── */
    .hero { text-align: center; padding: 2rem 1rem 1.2rem; }
    .hero-badge {
        display: inline-block; background: #ede9fe; color: #6d28d9;
        font-size: 0.7rem; font-weight: 700; letter-spacing: 0.13em;
        text-transform: uppercase; padding: 0.28rem 0.9rem;
        border-radius: 20px; margin-bottom: 0.8rem; border: 1px solid #ddd6fe;
    }
    .hero h1 {
        font-size: 2.2rem; font-weight: 800;
        background: linear-gradient(120deg, #4f46e5 0%, #7c3aed 55%, #0ea5e9 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text; margin: 0 0 0.5rem; line-height: 1.15;
    }
    .hero p { color: #6b7280; font-size: 0.95rem; margin: 0; }

    /* ── Chat container ── */
    .chat-container {
        background: #ffffff; border: 1px solid #e5e7eb;
        border-radius: 20px; padding: 1.5rem;
        min-height: 400px; max-height: 500px;
        overflow-y: auto; margin-bottom: 1rem;
        box-shadow: 0 2px 16px rgba(79,70,229,0.07);
    }

    /* ── Bubbles ── */
    .bubble-row-user { display: flex; justify-content: flex-end; margin: 0.5rem 0; }
    .bubble-row-bot  { display: flex; justify-content: flex-start; margin: 0.5rem 0; align-items: flex-end; gap: 0.5rem; }
    .bubble-user {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: #fff; border-radius: 18px 18px 4px 18px;
        padding: 0.65rem 1rem; max-width: 65%;
        font-size: 0.92rem; line-height: 1.5;
        box-shadow: 0 2px 8px rgba(99,102,241,0.25);
    }
    .bubble-bot {
        background: #f3f4f6; color: #1e1e2e;
        border-radius: 18px 18px 18px 4px;
        padding: 0.65rem 1rem; max-width: 72%;
        font-size: 0.92rem; line-height: 1.6;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }
    .bubble-bot.answer   { background: #f0fdf4; border: 1px solid #bbf7d0; color: #14532d; }
    .bubble-bot.ambiguous{ background: #fff7ed; border: 1px solid #fed7aa; color: #7c2d12; }
    .bubble-bot.clarified{ background: #eff6ff; border: 1px solid #bfdbfe; color: #1e3a5f; }
    .bot-avatar {
        width: 28px; height: 28px; border-radius: 50%;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        display: flex; align-items: center; justify-content: center;
        font-size: 0.75rem; color: white; flex-shrink: 0;
    }

    /* ── Analysis pills ── */
    .analysis-row {
        display: flex; gap: 0.4rem; flex-wrap: wrap;
        margin-top: 0.55rem; padding-top: 0.55rem;
        border-top: 1px solid rgba(0,0,0,0.07);
    }
    .a-pill {
        font-size: 0.63rem; font-weight: 700; padding: 0.15rem 0.55rem;
        border-radius: 20px; letter-spacing: 0.05em; text-transform: uppercase;
    }
    .a-pill.clear  { background: #dcfce7; color: #15803d; }
    .a-pill.ambig  { background: #fee2e2; color: #b91c1c; }
    .a-pill.intent { background: #ede9fe; color: #6d28d9; }
    .a-pill.conf   { background: #e0f2fe; color: #0369a1; }

    /* ── Vague highlight ── */
    .vague-word {
        background: #fee2e2; color: #b91c1c; border-radius: 4px;
        padding: 1px 4px; font-weight: 600; border: 1px solid #fecaca;
    }

    /* ── Input ── */
    .input-label {
        font-size: 0.7rem; font-weight: 700; letter-spacing: 0.1em;
        text-transform: uppercase; color: #9ca3af; margin-bottom: 0.3rem;
    }
    div[data-testid="stTextInput"] input {
        background: #ffffff !important; border: 1.5px solid #e0e7ff !important;
        border-radius: 12px !important; color: #1e1e2e !important;
        font-size: 0.95rem !important; padding: 0.7rem 1rem !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99,102,241,0.12) !important;
    }
    div[data-testid="stTextInput"] input::placeholder { color: #c4c9d4 !important; }

    /* ── Buttons ── */
    div[data-testid="stButton"] > button {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: #fff !important; border: none !important;
        border-radius: 10px !important; font-weight: 600 !important;
        font-size: 0.85rem !important; padding: 0.5rem 1.2rem !important;
        box-shadow: 0 2px 8px rgba(99,102,241,0.25) !important;
    }
    div[data-testid="stButton"] > button:hover { opacity: 0.85 !important; }

    /* ── Clarification card ── */
    .clarify-card {
        background: #fffbeb; border: 1px solid #fde68a;
        border-radius: 14px; padding: 1rem 1.2rem; margin: 0.5rem 0;
    }
    .clarify-title {
        font-size: 0.7rem; font-weight: 700; letter-spacing: 0.1em;
        text-transform: uppercase; color: #92400e; margin-bottom: 0.6rem;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: #ffffff !important; border-right: 1px solid #e5e7eb !important;
    }
    section[data-testid="stSidebar"] > div { padding: 1.4rem 1rem; }
    .sb-logo {
        font-size: 1.05rem; font-weight: 800;
        background: linear-gradient(120deg, #4f46e5, #7c3aed);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text; margin-bottom: 1.4rem;
    }
    .sb-section {
        font-size: 0.62rem; font-weight: 700; letter-spacing: 0.13em;
        text-transform: uppercase; color: #d1d5db;
        margin: 1rem 0 0.4rem; padding-bottom: 0.3rem;
        border-bottom: 1px solid #f3f4f6;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button {
        background: #f9fafb !important; border: 1px solid #f0f0f5 !important;
        color: #4b5563 !important; border-radius: 8px !important;
        font-size: 0.78rem !important; font-weight: 400 !important;
        text-align: left !important; padding: 0.4rem 0.75rem !important;
        width: 100% !important; margin-bottom: 0.22rem !important;
        box-shadow: none !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
        background: #ede9fe !important; border-color: #ddd6fe !important;
        color: #6d28d9 !important; opacity: 1 !important;
    }

    /* ── Footer ── */
    .footer {
        text-align: center; color: #d1d5db; font-size: 0.72rem;
        margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #f0f0f5;
    }
</style>
""", unsafe_allow_html=True)

# ── Load ML model ──────────────────────────────────────────────────────────────
@st.cache_resource
def load_ml_model():
    return AmbiguityMLPredictor(
        "ml_model/ambiguity_model_quora.pkl",
        "ml_model/tfidf_vectorizer_quora.pkl"
    )

ml_predictor = load_ml_model()

# ── Session state ──────────────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "bot", "type": "greeting",
         "text": "👋 Hi! I'm <strong>AmbiQ</strong>. Ask me any question — I'll check if it's clear or ambiguous, and answer it if it's clear!"}
    ]
if "selected_question" not in st.session_state:
    st.session_state.selected_question = ""
if "pending_clarification" not in st.session_state:
    st.session_state.pending_clarification = None

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<div class='sb-logo'>🔍 AmbiQ</div>", unsafe_allow_html=True)

    st.markdown("<div class='sb-section'>✦ Clear Examples</div>", unsafe_allow_html=True)
    for ex in [
        "What is machine learning?",
        "How do I install Python?",
        "Who invented the telephone?",
        "What are the benefits of exercise?",
        "How does photosynthesis work?",
        "What is TF-IDF?",
        "What is logistic regression?",
    ]:
        if st.button(ex, key=f"c_{ex}"):
            st.session_state.selected_question = ex

    st.markdown("<div class='sb-section'>⚠ Ambiguous Examples</div>", unsafe_allow_html=True)
    for ex in [
        "Book it",
        "Send that file",
        "Delete this",
        "Order now",
        "Schedule a meeting",
        "Fix the bug",
    ]:
        if st.button(ex, key=f"a_{ex}"):
            st.session_state.selected_question = ex

    st.markdown("<div class='sb-section'>⚙ Controls</div>", unsafe_allow_html=True)
    if st.button("🗑 Clear Chat"):
        st.session_state.chat_history = [
            {"role": "bot", "type": "greeting",
             "text": "👋 Hi! I'm <strong>AmbiQ</strong>. Ask me any question — I'll check if it's clear or ambiguous, and answer it if it's clear!"}
        ]
        st.session_state.pending_clarification = None
        st.session_state.selected_question = ""
        st.rerun()

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class='hero'>
    <div class='hero-badge'>NLP + Machine Learning + Chatbot</div>
    <h1>AmbiQ — Question Clarity Analyzer</h1>
    <p>Ask anything — I'll detect ambiguity, ask for clarification if needed, and answer when clear.</p>
</div>
""", unsafe_allow_html=True)

# ── Render chat history ────────────────────────────────────────────────────────
def render_chat():
    html = "<div class='chat-container'>"
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            html += f"<div class='bubble-row-user'><div class='bubble-user'>{msg['text']}</div></div>"
        else:
            extra = msg.get("type", "")
            extra_cls = extra if extra in ["answer", "ambiguous", "clarified"] else ""
            pills = ""
            if "analysis" in msg:
                a = msg["analysis"]
                rc = "clear" if a["rule_label"] == "Clear" else "ambig"
                mc = "clear" if a["ml_label"]  == "Clear" else "ambig"
                pills = f"""<div class='analysis-row'>
                    <span class='a-pill {rc}'>Rule: {a['rule_label']}</span>
                    <span class='a-pill {mc}'>ML: {a['ml_label']}</span>
                    <span class='a-pill intent'>{a['intent']}</span>
                    <span class='a-pill conf'>{a['confidence']:.0f}% conf</span>
                </div>"""
            html += f"""<div class='bubble-row-bot'>
                <div class='bot-avatar'>🔍</div>
                <div class='bubble-bot {extra_cls}'>{msg['text']}{pills}</div>
            </div>"""
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

render_chat()

# ── Clarification form ─────────────────────────────────────────────────────────
if st.session_state.pending_clarification:
    pc = st.session_state.pending_clarification
    triggered_names = pc["triggered_names"]
    intent          = pc["intent"]
    original_q      = pc["question"]

    st.markdown("<div class='clarify-card'><div class='clarify-title'>💬 Fill in the missing details to clarify</div>", unsafe_allow_html=True)
    clarification_inputs = {}

    if "MissingRequiredObject" in triggered_names or "ActionWithoutObject" in triggered_names or "TaskWithVagueObject" in triggered_names:
        if intent == "booking":
            clarification_inputs["object"] = st.text_input("📌 What do you want to book?", placeholder="e.g. hotel, flight, table", key="cl_obj")
        elif intent == "purchase":
            clarification_inputs["object"] = st.text_input("📌 What do you want to order/buy?", placeholder="e.g. pizza, laptop", key="cl_obj")
        else:
            clarification_inputs["object"] = st.text_input("📌 What is the target of this action?", placeholder="e.g. the report, the file", key="cl_obj")

    if "MissingRequiredDateTime" in triggered_names or "MissingTime" in triggered_names:
        clarification_inputs["datetime"] = st.text_input("📅 When?", placeholder="e.g. tomorrow at 3pm, next Monday", key="cl_dt")

    if "MissingRequiredLocation" in triggered_names or "MissingLocation" in triggered_names:
        clarification_inputs["location"] = st.text_input("📍 Where?", placeholder="e.g. Hyderabad, Room 101, online", key="cl_loc")

    if "MissingRequiredQuantity" in triggered_names:
        clarification_inputs["quantity"] = st.text_input("🔢 How many?", placeholder="e.g. 2, a dozen", key="cl_qty")

    if "VaguePronoun" in triggered_names or "TaskWithVagueObject" in triggered_names:
        clarification_inputs["vague"] = st.text_input("❓ What does 'it / this / that' refer to?", placeholder="e.g. the invoice, my laptop", key="cl_vague")

    st.markdown("</div>", unsafe_allow_html=True)

    filled = {k: v for k, v in clarification_inputs.items() if v and v.strip()}
    if filled and st.button("🔄 Submit Clarification"):
        refined_q = f"{original_q} {' '.join(filled.values())}"

        st.session_state.chat_history.append({"role": "user", "text": " | ".join(filled.values())})

        refined_rule = analyze_question(refined_q)
        refined_ml   = ml_predictor.predict(refined_q)

        resolved = not (set(triggered_names) & {r.name for r in refined_rule.triggered_rules})
        refined_ambiguous = (
            not resolved and refined_rule.label == "Ambiguous"
            if refined_rule.intent in ["booking", "purchase", "task"]
            else refined_rule.label == "Ambiguous" or refined_ml["is_ambiguous"]
        )

        analysis_meta = {
            "rule_label": refined_rule.label, "ml_label": refined_ml["label"],
            "intent": refined_rule.intent,    "confidence": refined_ml["confidence"]
        }

        if refined_ambiguous:
            st.session_state.chat_history.append({
                "role": "bot", "type": "ambiguous",
                "text": f"⚠️ Still ambiguous. Refined: <em>{refined_q}</em><br>Could you provide more details?",
                "analysis": analysis_meta
            })
        else:
            st.session_state.chat_history.append({
                "role": "bot", "type": "clarified",
                "text": f"✅ Clear now! Refined: <em>{refined_q}</em>",
                "analysis": analysis_meta
            })
            st.session_state.chat_history.append({
                "role": "bot", "type": "answer",
                "text": f"💡 {get_answer(refined_q)}"
            })
            st.session_state.pending_clarification = None

        st.rerun()

# ── Input ──────────────────────────────────────────────────────────────────────
st.markdown("<div class='input-label'>Ask a question</div>", unsafe_allow_html=True)
col_input, col_btn = st.columns([5, 1])
with col_input:
    question = st.text_input(
        "question_input",
        value=st.session_state.selected_question,
        placeholder="e.g. What is machine learning?  /  Book it  /  Send that file",
        label_visibility="collapsed",
        key="main_input"
    )
with col_btn:
    send = st.button("Send ➤")

# ── Process ────────────────────────────────────────────────────────────────────
if (send or st.session_state.selected_question) and question and question.strip():
    st.session_state.selected_question = ""

    st.session_state.chat_history.append({"role": "user", "text": question})

    rule_result = analyze_question(question)
    ml_result   = ml_predictor.predict(question)

    is_ambiguous = (
        rule_result.label == "Ambiguous"
        if rule_result.intent in ["booking", "purchase", "task"]
        else rule_result.label == "Ambiguous" or ml_result["is_ambiguous"]
    )

    vague_words = get_vague_words(question)
    display_q = question
    for w in set(vague_words):
        display_q = display_q.replace(w, f"<span class='vague-word'>{w}</span>")

    analysis_meta = {
        "rule_label": rule_result.label, "ml_label": ml_result["label"],
        "intent": rule_result.intent,    "confidence": ml_result["confidence"]
    }

    if is_ambiguous:
        reasons = " · ".join(r.reason for r in rule_result.triggered_rules)
        st.session_state.chat_history.append({
            "role": "bot", "type": "ambiguous",
            "text": f"⚠️ <em>\"{display_q}\"</em> is <strong>ambiguous</strong>.<br><small style='color:#9a6700'>{reasons}</small>",
            "analysis": analysis_meta
        })
        st.session_state.pending_clarification = {
            "question": question,
            "triggered_names": {r.name for r in rule_result.triggered_rules},
            "intent": rule_result.intent
        }
    else:
        st.session_state.chat_history.append({
            "role": "bot", "type": "clarified",
            "text": "✅ Your question is <strong>clear</strong>!",
            "analysis": analysis_meta
        })
        st.session_state.chat_history.append({
            "role": "bot", "type": "answer",
            "text": f"💡 {get_answer(question)}"
        })
        st.session_state.pending_clarification = None

    st.rerun()

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("<div class='footer'>AmbiQ &nbsp;·&nbsp; NLP + ML + Chatbot &nbsp;·&nbsp; Question Ambiguity Detection</div>", unsafe_allow_html=True)
