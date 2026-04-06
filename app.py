import streamlit as st

from rule_engine.rule_engine import analyze_question, get_vague_words
from ml_model.ml_predictor import AmbiguityMLPredictor

st.set_page_config(
    page_title="AmbiQ — Question Clarity Analyzer",
    page_icon="🔍",
    layout="wide"
)

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
    * { font-family: 'Inter', sans-serif; box-sizing: border-box; }

    /* ── Base ── */
    .stApp {
        background: #f0f2f8;
        color: #1e1e2e;
    }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding: 2rem 3rem 4rem; max-width: 1080px; }

    /* ── Hero ── */
    .hero {
        text-align: center;
        padding: 2.8rem 1rem 1.8rem;
    }
    .hero-badge {
        display: inline-block;
        background: #ede9fe;
        color: #6d28d9;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.13em;
        text-transform: uppercase;
        padding: 0.28rem 0.9rem;
        border-radius: 20px;
        margin-bottom: 1rem;
        border: 1px solid #ddd6fe;
    }
    .hero h1 {
        font-size: 2.6rem;
        font-weight: 800;
        background: linear-gradient(120deg, #4f46e5 0%, #7c3aed 55%, #0ea5e9 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0 0 0.7rem;
        line-height: 1.15;
    }
    .hero p {
        color: #6b7280;
        font-size: 1rem;
        margin: 0;
    }

    /* ── Input card ── */
    .input-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 1.6rem 1.8rem;
        margin: 1.6rem 0 1.2rem;
        box-shadow: 0 2px 12px rgba(79,70,229,0.06);
    }
    .input-label {
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #9ca3af;
        margin-bottom: 0.6rem;
    }
    div[data-testid="stTextInput"] input {
        background: #f9fafb !important;
        border: 1.5px solid #e0e7ff !important;
        border-radius: 12px !important;
        color: #1e1e2e !important;
        font-size: 1rem !important;
        padding: 0.75rem 1rem !important;
        transition: border-color 0.2s, box-shadow 0.2s;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99,102,241,0.12) !important;
        background: #fff !important;
    }
    div[data-testid="stTextInput"] input::placeholder { color: #c4c9d4 !important; }

    /* ── Card ── */
    .card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 1.4rem 1.6rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 8px rgba(0,0,0,0.04);
        transition: box-shadow 0.2s;
    }
    .card:hover { box-shadow: 0 4px 20px rgba(99,102,241,0.1); }
    .card-title {
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #9ca3af;
        margin-bottom: 1rem;
    }

    /* ── Metric grid ── */
    .metric-grid   { display: grid; grid-template-columns: repeat(4,1fr); gap: 0.7rem; }
    .metric-grid-2 { display: grid; grid-template-columns: repeat(2,1fr); gap: 0.7rem; }
    .metric-tile {
        background: #f9fafb;
        border: 1px solid #f0f0f5;
        border-radius: 12px;
        padding: 0.85rem 0.6rem;
        text-align: center;
    }
    .metric-tile .m-label {
        font-size: 0.63rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #9ca3af;
        margin-bottom: 0.35rem;
    }
    .metric-tile .m-value {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1e1e2e;
    }
    .m-value.clear { color: #059669; }
    .m-value.ambig { color: #dc2626; }

    /* ── Intent pill ── */
    .intent-pill {
        display: inline-block;
        padding: 0.22rem 0.75rem;
        border-radius: 20px;
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.07em;
        text-transform: uppercase;
    }
    .pill-booking       { background: #e0f2fe; color: #0369a1; }
    .pill-purchase      { background: #ede9fe; color: #6d28d9; }
    .pill-task          { background: #dcfce7; color: #15803d; }
    .pill-informational { background: #fef9c3; color: #a16207; }
    .pill-unknown       { background: #f3f4f6; color: #6b7280; }

    /* ── Rule items ── */
    .rule-item {
        background: #f9fafb;
        border: 1px solid #f0f0f5;
        border-left: 3px solid #818cf8;
        border-radius: 8px;
        padding: 0.55rem 0.85rem;
        margin: 0.35rem 0;
        font-size: 0.84rem;
        color: #4b5563;
        line-height: 1.45;
    }

    /* ── Vague word highlight ── */
    .vague-word {
        background: #fee2e2;
        color: #b91c1c;
        border-radius: 5px;
        padding: 1px 5px;
        font-weight: 600;
        border: 1px solid #fecaca;
    }

    /* ── Verdict ── */
    .verdict {
        border-radius: 14px;
        padding: 1.1rem 2rem;
        text-align: center;
        font-size: 1.05rem;
        font-weight: 700;
        margin: 1rem 0;
    }
    .verdict-clear {
        background: #f0fdf4;
        border: 1.5px solid #86efac;
        color: #15803d;
    }
    .verdict-ambiguous {
        background: #fff1f2;
        border: 1.5px solid #fca5a5;
        color: #b91c1c;
    }

    /* ── Confidence bar ── */
    .conf-bar-wrap { margin-top: 1rem; }
    .conf-bar-label {
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #9ca3af;
        margin-bottom: 0.4rem;
    }
    .conf-bar-track {
        background: #f0f0f5;
        border-radius: 99px;
        height: 6px;
        overflow: hidden;
    }
    .conf-bar-fill {
        height: 100%;
        border-radius: 99px;
        background: linear-gradient(90deg, #6366f1, #8b5cf6);
    }

    /* ── Clarify header ── */
    .clarify-header {
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #9ca3af;
        margin: 1.4rem 0 0.6rem;
    }

    /* ── Button ── */
    div[data-testid="stButton"] > button {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        padding: 0.55rem 1.4rem !important;
        transition: opacity 0.2s !important;
        box-shadow: 0 2px 8px rgba(99,102,241,0.25) !important;
    }
    div[data-testid="stButton"] > button:hover { opacity: 0.88 !important; }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: #ffffff !important;
        border-right: 1px solid #e5e7eb !important;
    }
    section[data-testid="stSidebar"] > div { padding: 1.6rem 1.1rem; }
    .sb-logo {
        font-size: 1.1rem;
        font-weight: 800;
        background: linear-gradient(120deg, #4f46e5, #7c3aed);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1.6rem;
    }
    .sb-section {
        font-size: 0.63rem;
        font-weight: 700;
        letter-spacing: 0.13em;
        text-transform: uppercase;
        color: #d1d5db;
        margin: 1.2rem 0 0.5rem;
        padding-bottom: 0.3rem;
        border-bottom: 1px solid #f3f4f6;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button {
        background: #f9fafb !important;
        border: 1px solid #f0f0f5 !important;
        color: #4b5563 !important;
        border-radius: 8px !important;
        font-size: 0.8rem !important;
        font-weight: 400 !important;
        text-align: left !important;
        padding: 0.42rem 0.8rem !important;
        width: 100% !important;
        margin-bottom: 0.25rem !important;
        box-shadow: none !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
        background: #ede9fe !important;
        border-color: #ddd6fe !important;
        color: #6d28d9 !important;
        opacity: 1 !important;
    }

    /* ── Footer ── */
    .footer {
        text-align: center;
        color: #d1d5db;
        font-size: 0.75rem;
        margin-top: 3rem;
        padding-top: 1.5rem;
        border-top: 1px solid #f0f0f5;
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
if "selected_question" not in st.session_state:
    st.session_state.selected_question = ""

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

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class='hero'>
    <div class='hero-badge'>NLP + Machine Learning</div>
    <h1>Question Clarity Analyzer</h1>
    <p>Instantly detect whether a question is <strong>clear</strong> or <strong>ambiguous</strong> using hybrid rule-based NLP and ML</p>
</div>
""", unsafe_allow_html=True)

# ── Input ──────────────────────────────────────────────────────────────────────
st.markdown("<div class='input-card'><div class='input-label'>Your Question</div>", unsafe_allow_html=True)
question = st.text_input(
    "question_input",
    value=st.session_state.selected_question,
    placeholder="e.g.  Book it   /   What is machine learning?   /   Send that file",
    label_visibility="collapsed"
)
st.markdown("</div>", unsafe_allow_html=True)

# ── Analysis ───────────────────────────────────────────────────────────────────
if question and question.strip():

    rule_result = analyze_question(question)
    ml_result   = ml_predictor.predict(question)

    pill_class = {
        "booking": "pill-booking",
        "purchase": "pill-purchase",
        "task": "pill-task",
        "informational": "pill-informational",
    }.get(rule_result.intent, "pill-unknown")

    # Ambiguity highlight
    vague_words = get_vague_words(question)
    if vague_words:
        highlighted = question
        for w in set(vague_words):
            highlighted = highlighted.replace(w, f"<span class='vague-word'>{w}</span>")
        st.markdown(f"""
        <div class='card'>
            <div class='card-title'>🖊 Ambiguity Highlight</div>
            <p style='font-size:1.05rem; margin:0 0 0.4rem; color:#1e1e2e'>{highlighted}</p>
            <p style='font-size:0.75rem; color:#9ca3af; margin:0'>Highlighted words are vague references detected via WordNet analysis.</p>
        </div>
        """, unsafe_allow_html=True)

    # ── Two-column cards ───────────────────────────────────────────────────────
    col1, col2 = st.columns(2, gap="medium")

    rule_color = "clear" if rule_result.label == "Clear" else "ambig"
    ml_color   = "clear" if ml_result["label"] == "Clear" else "ambig"

    with col1:
        st.markdown(f"""
        <div class='card'>
            <div class='card-title'>🔍 Rule-Based NLP</div>
            <div class='metric-grid'>
                <div class='metric-tile'>
                    <div class='m-label'>Decision</div>
                    <div class='m-value {rule_color}'>{rule_result.label}</div>
                </div>
                <div class='metric-tile'>
                    <div class='m-label'>Intent</div>
                    <div class='m-value' style='font-size:0.85rem'>
                        <span class='intent-pill {pill_class}'>{rule_result.intent}</span>
                    </div>
                </div>
                <div class='metric-tile'>
                    <div class='m-label'>Score</div>
                    <div class='m-value'>{rule_result.score}</div>
                </div>
                <div class='metric-tile'>
                    <div class='m-label'>Threshold</div>
                    <div class='m-value'>{rule_result.threshold}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class='card'>
            <div class='card-title'>🤖 ML Model</div>
            <div class='metric-grid'>
                <div class='metric-tile'>
                    <div class='m-label'>Prediction</div>
                    <div class='m-value {ml_color}'>{ml_result['label']}</div>
                </div>
                <div class='metric-tile'>
                    <div class='m-label'>Confidence</div>
                    <div class='m-value'>{ml_result['confidence']:.1f}%</div>
                </div>
                <div class='metric-tile'>
                    <div class='m-label'>Clear</div>
                    <div class='m-value'>{ml_result['probabilities']['clear']:.1f}%</div>
                </div>
                <div class='metric-tile'>
                    <div class='m-label'>Ambiguous</div>
                    <div class='m-value'>{ml_result['probabilities']['ambiguous']:.1f}%</div>
                </div>
            </div>
            <div class='conf-bar-wrap'>
                <div class='conf-bar-label'>Ambiguity Confidence</div>
                <div class='conf-bar-track'>
                    <div class='conf-bar-fill' style='width:{int(ml_result["probabilities"]["ambiguous"])}%'></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Triggered rules ────────────────────────────────────────────────────────
    if rule_result.triggered_rules:
        rules_html = "".join(
            f"<div class='rule-item'>▸ {r.reason}</div>"
            for r in rule_result.triggered_rules
        )
        st.markdown(f"""
        <div class='card'>
            <div class='card-title'>📋 Triggered Rules</div>
            {rules_html}
        </div>
        """, unsafe_allow_html=True)

    # ── Final verdict ──────────────────────────────────────────────────────────
    is_ambiguous = (
        rule_result.label == "Ambiguous"
        if rule_result.intent in ["booking", "purchase", "task"]
        else rule_result.label == "Ambiguous" or ml_result["is_ambiguous"]
    )

    if is_ambiguous:
        st.markdown("<div class='verdict verdict-ambiguous'>⚠️ &nbsp; This question is <strong>AMBIGUOUS</strong> — key details are missing</div>", unsafe_allow_html=True)

        triggered_names = {r.name for r in rule_result.triggered_rules}
        clarification_inputs = {}

        st.markdown("<div class='clarify-header'>💬 Clarify the missing details</div>", unsafe_allow_html=True)

        if "MissingRequiredObject" in triggered_names or "ActionWithoutObject" in triggered_names or "TaskWithVagueObject" in triggered_names:
            if rule_result.intent == "booking":
                clarification_inputs["object"] = st.text_input("📌 What do you want to book?", placeholder="e.g. hotel, flight, table")
            elif rule_result.intent == "purchase":
                clarification_inputs["object"] = st.text_input("📌 What do you want to order/buy?", placeholder="e.g. pizza, laptop")
            else:
                clarification_inputs["object"] = st.text_input("📌 What is the target of this action?", placeholder="e.g. the report, the file")

        if "MissingRequiredDateTime" in triggered_names or "MissingTime" in triggered_names:
            clarification_inputs["datetime"] = st.text_input("📅 When?", placeholder="e.g. tomorrow at 3pm, next Monday")

        if "MissingRequiredLocation" in triggered_names or "MissingLocation" in triggered_names:
            clarification_inputs["location"] = st.text_input("📍 Where?", placeholder="e.g. Hyderabad, Room 101, online")

        if "MissingRequiredQuantity" in triggered_names:
            clarification_inputs["quantity"] = st.text_input("🔢 How many?", placeholder="e.g. 2, a dozen")

        if "VaguePronoun" in triggered_names or "TaskWithVagueObject" in triggered_names:
            clarification_inputs["vague"] = st.text_input("❓ What does 'it / this / that' refer to?", placeholder="e.g. the invoice, my laptop")

        filled = {k: v for k, v in clarification_inputs.items() if v and v.strip()}

        if filled and st.button("🔄 Re-analyze with clarifications"):
            refined_question = f"{question} {' '.join(filled.values())}"
            refined_rule = analyze_question(refined_question)
            refined_ml   = ml_predictor.predict(refined_question)

            r_rule_color = "clear" if refined_rule.label == "Clear" else "ambig"
            r_ml_color   = "clear" if refined_ml["label"] == "Clear" else "ambig"

            st.markdown(f"""
            <div class='card' style='margin-top:1rem'>
                <div class='card-title'>🔁 Re-Analysis Result</div>
                <p style='font-size:0.82rem; color:#9ca3af; margin:0 0 1rem'>
                    Refined: <span style='color:#4b5563; font-weight:500'>{refined_question}</span>
                </p>
                <div class='metric-grid-2'>
                    <div class='metric-tile'>
                        <div class='m-label'>Rule Engine</div>
                        <div class='m-value {r_rule_color}'>{refined_rule.label}</div>
                    </div>
                    <div class='metric-tile'>
                        <div class='m-label'>ML Model ({refined_ml['confidence']:.0f}% conf.)</div>
                        <div class='m-value {r_ml_color}'>{refined_ml['label']}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            original_triggered = {r.name for r in rule_result.triggered_rules}
            refined_triggered   = {r.name for r in refined_rule.triggered_rules}
            resolved_all_params = not (original_triggered & refined_triggered)

            refined_ambiguous = (
                not resolved_all_params and refined_rule.label == "Ambiguous"
                if refined_rule.intent in ["booking", "purchase", "task"]
                else refined_rule.label == "Ambiguous" or refined_ml["is_ambiguous"]
            )

            if refined_ambiguous:
                st.markdown("<div class='verdict verdict-ambiguous'>⚠️ &nbsp; Still <strong>AMBIGUOUS</strong> — please provide more details</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='verdict verdict-clear'>✅ &nbsp; Question is now <strong>CLEAR</strong> after clarification!</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='verdict verdict-clear'>✅ &nbsp; This question is <strong>CLEAR</strong></div>", unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("<div class='footer'>AmbiQ &nbsp;·&nbsp; NLP + ML &nbsp;·&nbsp; Question Ambiguity Detection</div>", unsafe_allow_html=True)
