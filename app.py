"""
app.py  –  Automata-Based Cybersecurity Analyzer
Run: streamlit run app.py
"""

import streamlit as st
import pandas as pd

from automata_engine import (
    build_password_dfa,
    build_sql_injection_nfa,
    run_sql_nfa,
    EPSILON,
)

# ─────────────────────────────────────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Automata Cybersecurity Analyzer",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

/* ── Root Variables ── */
:root {
    --bg-primary:   #0d1117;
    --bg-secondary: #161b22;
    --bg-card:      #1c2230;
    --accent-cyan:  #00e5ff;
    --accent-green: #00e676;
    --accent-red:   #ff1744;
    --accent-amber: #ffc400;
    --accent-purple:#7c4dff;
    --accent-blue:  #448aff;
    --text-primary: #e6edf3;
    --text-muted:   #8b949e;
    --border:       #30363d;
    --glow-cyan:    0 0 20px rgba(0,229,255,0.3);
    --glow-green:   0 0 20px rgba(0,230,118,0.3);
    --glow-red:     0 0 20px rgba(255,23,68,0.3);
}

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: var(--bg-primary);
    color: var(--text-primary);
}

.stApp { background-color: var(--bg-primary); }

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #161b22 0%, #0d1117 100%);
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] .stRadio > label {
    color: var(--text-muted);
    font-size: 0.80rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

/* ── Custom hero banner ── */
.hero-banner {
    background: linear-gradient(135deg, #0d1117 0%, #161b22 40%, #1a1f2e 100%);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.hero-banner::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(0,229,255,0.06) 0%, transparent 70%);
    pointer-events: none;
}
.hero-title {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(90deg, var(--accent-cyan), var(--accent-purple));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    line-height: 1.2;
}
.hero-subtitle {
    color: var(--text-muted);
    font-size: 0.95rem;
    margin-top: 0.5rem;
}

/* ── Cards ── */
.card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.card-title {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--text-muted);
    margin-bottom: 0.75rem;
}

/* ── Status badges ── */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.35rem 0.9rem;
    border-radius: 999px;
    font-size: 0.82rem;
    font-weight: 600;
    letter-spacing: 0.03em;
}
.badge-success {
    background: rgba(0,230,118,0.12);
    color: var(--accent-green);
    border: 1px solid rgba(0,230,118,0.3);
    box-shadow: var(--glow-green);
}
.badge-danger {
    background: rgba(255,23,68,0.12);
    color: var(--accent-red);
    border: 1px solid rgba(255,23,68,0.3);
    box-shadow: var(--glow-red);
}
.badge-warning {
    background: rgba(255,196,0,0.12);
    color: var(--accent-amber);
    border: 1px solid rgba(255,196,0,0.3);
}
.badge-info {
    background: rgba(0,229,255,0.10);
    color: var(--accent-cyan);
    border: 1px solid rgba(0,229,255,0.3);
}

/* ── Strength meter ── */
.strength-bar-outer {
    background: var(--border);
    border-radius: 999px;
    height: 8px;
    margin: 0.4rem 0 0.8rem;
    overflow: hidden;
}
.strength-bar-inner {
    height: 100%;
    border-radius: 999px;
    transition: width 0.4s ease;
}

/* ── Criteria checklist ── */
.criteria-item {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.4rem 0;
    font-size: 0.88rem;
    border-bottom: 1px solid rgba(48,54,61,0.5);
}
.criteria-item:last-child { border-bottom: none; }

/* ── Monospace trace ── */
.trace-line {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: var(--text-muted);
    padding: 0.2rem 0.5rem;
    border-left: 2px solid var(--border);
    margin-bottom: 2px;
}
.trace-line.accepted {
    border-left-color: var(--accent-green);
    color: var(--accent-green);
}
.trace-line.dead {
    border-left-color: var(--accent-red);
    color: var(--accent-red);
}

/* ── Metric tiles ── */
.metric-row {
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
    flex-wrap: wrap;
}
.metric-tile {
    flex: 1;
    min-width: 130px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem;
    text-align: center;
}
.metric-value {
    font-size: 1.6rem;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
    color: var(--accent-cyan);
}
.metric-label {
    font-size: 0.72rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 0.2rem;
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background-color: var(--bg-secondary) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-primary) !important;
    border-radius: 8px !important;
    font-family: 'JetBrains Mono', monospace !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--accent-cyan) !important;
    box-shadow: 0 0 0 3px rgba(0,229,255,0.15) !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, var(--accent-cyan) 0%, var(--accent-purple) 100%) !important;
    color: #000 !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6rem 2rem !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: var(--glow-cyan) !important;
}

/* ── DataFrame ── */
[data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-secondary);
    border-radius: 10px 10px 0 0;
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: var(--text-muted);
    border-radius: 8px;
    font-size: 0.85rem;
    padding: 0.6rem 1.2rem;
}
.stTabs [aria-selected="true"] {
    color: var(--accent-cyan) !important;
    background: rgba(0,229,255,0.1) !important;
}

/* ── Expanders ── */
[data-testid="stExpander"] {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 10px;
}

/* ── Attack pattern pill ── */
.attack-pill {
    display: inline-block;
    background: rgba(255,23,68,0.15);
    border: 1px solid rgba(255,23,68,0.4);
    color: var(--accent-red);
    border-radius: 6px;
    padding: 0.2rem 0.7rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    margin: 0.2rem;
}

/* ── Section divider ── */
.section-divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 1.5rem 0;
}

/* ── Sidebar logo ── */
.sidebar-logo {
    text-align: center;
    padding: 1rem 0 1.5rem;
}
.sidebar-logo-icon {
    font-size: 2.5rem;
    display: block;
}
.sidebar-logo-text {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: var(--text-muted);
    margin-top: 0.3rem;
}

/* ── Info box ── */
.info-box {
    background: rgba(0,229,255,0.05);
    border: 1px solid rgba(0,229,255,0.2);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    font-size: 0.85rem;
    color: var(--text-muted);
    margin-bottom: 1rem;
}
.info-box code {
    background: rgba(0,229,255,0.1);
    padding: 0.1rem 0.4rem;
    border-radius: 4px;
    color: var(--accent-cyan);
    font-family: 'JetBrains Mono', monospace;
}

/* ── State node ── */
.state-node {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 36px; height: 36px;
    border-radius: 50%;
    background: var(--bg-secondary);
    border: 2px solid var(--border);
    font-size: 0.7rem;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
}
.state-node.active { border-color: var(--accent-cyan); color: var(--accent-cyan); background: rgba(0,229,255,0.1); }
.state-node.accept { border-color: var(--accent-green); color: var(--accent-green); background: rgba(0,230,118,0.08); }
.state-node.dead   { border-color: var(--accent-red);  color: var(--accent-red);  background: rgba(255,23,68,0.08); }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar Navigation
# ─────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <span class="sidebar-logo-icon">🔐</span>
        <div style="font-size:1rem;font-weight:700;color:#e6edf3;margin-top:0.4rem;">FLAT Analyzer</div>
        <div class="sidebar-logo-text">Automata · Cybersecurity</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    page = st.radio(
        "Navigation",
        ["🏠  Overview",
         "🔑  Password Validator",
         "🚨  SQL Injection Detector",
         "🔄  NFA → DFA Conversion",
         "📚  Theory Reference"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.72rem;color:#8b949e;padding:0.5rem 0;line-height:1.6;">
    <b style="color:#e6edf3;">Formal Language Concepts</b><br><br>
    • Deterministic Finite Automata (DFA)<br>
    • Non-Deterministic Finite Automata (NFA)<br>
    • ε-Closure Computation<br>
    • Subset Construction<br>
    • Regular Languages<br>
    • Pattern Recognition
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Cached automata instances
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_resource
def get_password_dfa():
    return build_password_dfa(min_length=8)

@st.cache_resource
def get_sql_nfa():
    return build_sql_injection_nfa()


# ═════════════════════════════════════════════════════════════════════════════
# PAGE: Overview
# ═════════════════════════════════════════════════════════════════════════════

if page == "🏠  Overview":
    st.markdown("""
    <div class="hero-banner">
        <h1 class="hero-title">Automata-Based Cybersecurity Analyzer</h1>
        <div class="hero-subtitle">Applying Formal Languages &amp; Automata Theory to real-world security challenges</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    tile_data = [
        (col1, "DFA States", "180+", "Password validation automaton"),
        (col2, "NFA Patterns", "12", "SQL injection signatures"),
        (col3, "Regex Classes", "5", "Uppercase · Lowercase · Digit · Special · Other"),
        (col4, "Automata Models", "2", "DFA + NFA with ε-closure"),
    ]
    for col, label, val, desc in tile_data:
        with col:
            st.markdown(f"""
            <div class="metric-tile">
                <div class="metric-value">{val}</div>
                <div class="metric-label">{label}</div>
                <div style="font-size:0.68rem;color:#555e6b;margin-top:0.4rem;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("### 🎯 Project Objectives")
        objectives = [
            ("Apply FLAT in cybersecurity", "Bridge theory and practice"),
            ("DFA for password validation", "Deterministic, efficient, exact rules"),
            ("NFA for attack detection", "Flexible, multi-pattern matching"),
            ("ε-closure computation", "Foundation for NFA simulation"),
            ("NFA → DFA conversion", "Subset construction demonstration"),
        ]
        for title, desc in objectives:
            st.markdown(f"""
            <div class="criteria-item">
                <span style="color:#00e5ff;font-size:1rem;">◈</span>
                <div><b style="color:#e6edf3;">{title}</b>
                <div style="font-size:0.78rem;color:#8b949e;">{desc}</div></div>
            </div>
            """, unsafe_allow_html=True)

    with col_r:
        st.markdown("### 🏗️ System Architecture")
        st.markdown("""
        <div class="info-box">
        <b style="color:#e6edf3;">Data Flow</b><br><br>
        <code>User Input</code> → <code>Automata Engine</code> → <code>Analysis Result</code> → <code>Security Feedback</code>
        <br><br>
        <b style="color:#e6edf3;">Modules</b>
        <ul style="margin:0.5rem 0 0;padding-left:1.2rem;line-height:1.9;">
          <li>Password Validation DFA — 5-tuple (Q, Σ, δ, q₀, F)</li>
          <li>SQL Injection NFA — ε-transitions, multi-pattern</li>
          <li>Automata Simulation — state trace, step-by-step</li>
          <li>NFA → DFA Converter — subset construction</li>
          <li>Theory Reference — formal definitions</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 📖 Abstract")
    st.markdown("""
    <div class="card">
    <p style="color:#c9d1d9;line-height:1.8;font-size:0.9rem;">
    This project demonstrates the practical application of <b>Formal Languages and Automata Theory (FLAT)</b>
    in cybersecurity. Password strength is verified using a <b>Deterministic Finite Automaton (DFA)</b>
    that encodes character-class rules as a state machine. SQL-injection–like attack patterns are detected
    using a <b>Non-Deterministic Finite Automaton (NFA)</b> with ε-closure computation.
    The project also performs <b>NFA-to-DFA conversion</b> via the subset construction method,
    illustrating automata equivalence.
    </p>
    </div>
    """, unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE: Password Validator
# ═════════════════════════════════════════════════════════════════════════════

elif page == "🔑  Password Validator":
    st.markdown("""
    <div class="hero-banner">
        <h1 class="hero-title">Password Strength Validator</h1>
        <div class="hero-subtitle">Powered by Deterministic Finite Automaton (DFA)</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
    The DFA encodes 5 acceptance rules as a <em>bitmask × length</em> state space.<br>
    State = <code>(length_bucket, criteria_mask)</code> — accepted iff <code>length ≥ 8</code>
    <b>AND</b> all 4 character-class bits are set.
    </div>
    """, unsafe_allow_html=True)

    dfa = get_password_dfa()

    col_input, col_rules = st.columns([3, 2])

    with col_input:
        password = st.text_input(
            "Enter a password to analyze",
            type="password",
            placeholder="Type your password…",
            help="The DFA will process each character and determine acceptance.",
        )
        show_password = st.checkbox("👁 Reveal password", value=False)
        if show_password and password:
            st.code(password, language=None)

    with col_rules:
        st.markdown("**Acceptance Criteria (DFA Rules)**")
        rules = [
            ("Minimum 8 characters", "Length ≥ 8"),
            ("At least one UPPERCASE letter", "A-Z"),
            ("At least one lowercase letter", "a-z"),
            ("At least one digit", "0-9"),
            ("At least one special char", "! @ # $ % ^ & * _ -"),
        ]
        for rule, detail in rules:
            st.markdown(f"""
            <div class="criteria-item">
                <span style="color:#448aff;">▸</span>
                <div><span style="color:#e6edf3;">{rule}</span>
                <span style="color:#8b949e;font-size:0.75rem;"> — {detail}</span></div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    if password:
        accepted, trace, strength = dfa.run(password)

        # ── Result banner ──
        if accepted:
            st.markdown("""
            <div style="background:rgba(0,230,118,0.07);border:1px solid rgba(0,230,118,0.3);
                        border-radius:12px;padding:1rem 1.5rem;margin-bottom:1rem;
                        box-shadow:0 0 20px rgba(0,230,118,0.15);">
                <span style="font-size:1.5rem;">✅</span>
                <span style="font-size:1.1rem;font-weight:700;color:#00e676;margin-left:0.5rem;">
                  Password ACCEPTED by DFA</span>
                <div style="color:#8b949e;font-size:0.82rem;margin-top:0.3rem;">
                  The input string reached an accepting state — it belongs to the defined regular language.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:rgba(255,23,68,0.07);border:1px solid rgba(255,23,68,0.3);
                        border-radius:12px;padding:1rem 1.5rem;margin-bottom:1rem;
                        box-shadow:0 0 20px rgba(255,23,68,0.15);">
                <span style="font-size:1.5rem;">❌</span>
                <span style="font-size:1.1rem;font-weight:700;color:#ff1744;margin-left:0.5rem;">
                  Password REJECTED by DFA</span>
                <div style="color:#8b949e;font-size:0.82rem;margin-top:0.3rem;">
                  The DFA did not reach an accepting state — the string does not satisfy all rules.</div>
            </div>
            """, unsafe_allow_html=True)

        # ── Strength meter ──
        level_colors = {
            "Very Weak": "#ff1744", "Weak": "#ff6d00", "Fair": "#ffc400",
            "Good": "#69f0ae", "Strong": "#00e676", "Very Strong": "#00e5ff",
        }
        score = strength["score"]
        level = strength["level"]
        bar_color = level_colors.get(level, "#00e5ff")
        bar_pct = int(score / 5 * 100)

        st.markdown(f"""
        <div class="card">
          <div class="card-title">Strength Assessment</div>
          <div style="display:flex;align-items:center;gap:1rem;margin-bottom:0.5rem;">
            <div class="strength-bar-outer" style="flex:1;">
              <div class="strength-bar-inner" style="width:{bar_pct}%;background:{bar_color};"></div>
            </div>
            <span style="color:{bar_color};font-weight:700;font-size:0.9rem;white-space:nowrap;">{level}</span>
          </div>
        """, unsafe_allow_html=True)

        crit = strength["criteria"]
        crit_labels = {
            "min_length_8":  ("Minimum 8 characters", f"Current: {len(password)} chars"),
            "has_uppercase": ("Uppercase letter",      "A-Z"),
            "has_lowercase": ("Lowercase letter",      "a-z"),
            "has_digit":     ("Digit",                 "0-9"),
            "has_special":   ("Special character",     "! @ # $ % ^ & * _ -"),
        }
        for key, met in crit.items():
            label, hint = crit_labels[key]
            icon = "✅" if met else "❌"
            color = "#00e676" if met else "#ff1744"
            st.markdown(f"""
            <div class="criteria-item">
                <span>{icon}</span>
                <span style="color:{color};">{label}</span>
                <span style="color:#555e6b;font-size:0.75rem;margin-left:auto;">{hint}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # ── DFA Trace ──
        with st.expander("🔬 DFA Execution Trace (step-by-step)", expanded=False):
            st.markdown(f"""
            <div class="info-box">
            The DFA processed <code>{len(password)}</code> characters through
            <code>{len(trace)}</code> state transitions.
            Each row shows: symbol → category → from-state → to-state.
            </div>
            """, unsafe_allow_html=True)

            trace_rows = []
            for t in trace:
                if t["symbol"] == "START":
                    trace_rows.append({
                        "Step": 0,
                        "Symbol": "—",
                        "Category": "—",
                        "From State": "—",
                        "To State": t["to"],
                        "Status": "▶ START",
                    })
                else:
                    status = "✅ OK" if t.get("accepted") else ("💀 DEAD" if t["to"] == "DEAD" else "⏩")
                    trace_rows.append({
                        "Step": t["step"],
                        "Symbol": t["symbol"],
                        "Category": t.get("category", "—"),
                        "From State": t["from"],
                        "To State": t["to"],
                        "Status": status,
                    })

            df_trace = pd.DataFrame(trace_rows)
            st.dataframe(df_trace, use_container_width=True, hide_index=True)

        # ── DFA formal definition ──
        with st.expander("📐 DFA Formal Definition", expanded=False):
            st.markdown(f"""
            **DFA 5-tuple:**  M = (Q, Σ, δ, q₀, F)

            | Component | Value |
            |-----------|-------|
            | **Q** (states) | Tuples `(length_bucket, criteria_mask)` where length ∈ [0..8], mask ∈ [0..15] → 144 states + DEAD |
            | **Σ** (alphabet) | `{{upper, lower, digit, special, other}}` (5 character categories) |
            | **δ** (transition) | `δ((l, m), cat)` → `(min(l+1, 8),  m | bit(cat))` |
            | **q₀** (start) | `(0, 0b0000)` — zero length, no criteria met |
            | **F** (accept) | `{{(8, 0b1111)}}` — length saturated AND all 4 criteria bits set |

            **Language Accepted:**  
            L = {{ w ∈ Σ* | |w| ≥ 8 ∧ w contains upper ∧ lower ∧ digit ∧ special }}
            """)

    else:
        st.markdown("""
        <div style="text-align:center;padding:3rem;color:#8b949e;">
            <div style="font-size:3rem;margin-bottom:1rem;">🔑</div>
            <div>Enter a password above to begin DFA analysis</div>
            <div style="font-size:0.8rem;margin-top:0.5rem;">Try: <code>MyP@ss123</code> (strong) or <code>password</code> (weak)</div>
        </div>
        """, unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE: SQL Injection Detector
# ═════════════════════════════════════════════════════════════════════════════

elif page == "🚨  SQL Injection Detector":
    st.markdown("""
    <div class="hero-banner">
        <h1 class="hero-title">SQL Injection Attack Detector</h1>
        <div class="hero-subtitle">Powered by Non-Deterministic Finite Automaton (NFA) with ε-closure</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
    The NFA models 12 SQL-injection signature patterns as parallel chains from a shared start state q₀.
    ε-transitions allow the automaton to non-deterministically attempt all patterns simultaneously.
    The input is <b>case-insensitive</b> (lowercased before processing).
    </div>
    """, unsafe_allow_html=True)

    nfa = get_sql_nfa()

    # Sample attack payloads
    col_input, col_samples = st.columns([3, 2])

    with col_input:
        user_input = st.text_area(
            "Enter SQL query / user input to analyze",
            height=140,
            placeholder="e.g.  SELECT * FROM users WHERE id='1' OR '1'='1'",
            help="The NFA will scan for known SQL injection patterns.",
        )

    with col_samples:
        st.markdown("**Quick Sample Payloads**")
        samples = {
            "Classic Tautology": "admin' OR '1'='1",
            "UNION-based": "1 UNION SELECT username, password FROM users",
            "DROP Attack": "1; DROP TABLE users; --",
            "Time-based Blind": "1; SLEEP(5)--",
            "Safe input": "SELECT * FROM products WHERE price > 10",
            "Normal login": "username=john&password=secure123",
        }
        for label, payload in samples.items():
            if st.button(f"▶ {label}", key=f"sample_{label}", use_container_width=True):
                st.session_state["sql_payload"] = payload

    # Allow sample injection
    if "sql_payload" in st.session_state and not user_input:
        user_input = st.session_state["sql_payload"]
        st.info(f"Loaded sample: `{user_input}`")

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    if user_input.strip():
        detected, matched, trace = run_sql_nfa(nfa, user_input)

        # Result banner
        if detected:
            st.markdown(f"""
            <div style="background:rgba(255,23,68,0.08);border:1px solid rgba(255,23,68,0.35);
                        border-radius:12px;padding:1rem 1.5rem;margin-bottom:1rem;
                        box-shadow:0 0 20px rgba(255,23,68,0.2);">
                <span style="font-size:1.5rem;">🚨</span>
                <span style="font-size:1.1rem;font-weight:700;color:#ff1744;margin-left:0.5rem;">
                  ATTACK DETECTED — NFA reached accepting state</span>
                <div style="margin-top:0.5rem;">
                  {''.join(f'<span class="attack-pill">{p}</span>' for p in matched)}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:rgba(0,230,118,0.07);border:1px solid rgba(0,230,118,0.3);
                        border-radius:12px;padding:1rem 1.5rem;margin-bottom:1rem;">
                <span style="font-size:1.5rem;">✅</span>
                <span style="font-size:1.1rem;font-weight:700;color:#00e676;margin-left:0.5rem;">
                  Input appears SAFE — no SQL injection patterns detected</span>
                <div style="color:#8b949e;font-size:0.82rem;margin-top:0.3rem;">
                  The NFA did not reach any accepting state for the known attack signatures.</div>
            </div>
            """, unsafe_allow_html=True)

        # Stats
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.markdown(f"""
            <div class="metric-tile">
                <div class="metric-value">{len(user_input)}</div>
                <div class="metric-label">Characters Processed</div>
            </div>""", unsafe_allow_html=True)
        with col_b:
            st.markdown(f"""
            <div class="metric-tile">
                <div class="metric-value" style="color:{'#ff1744' if detected else '#00e676'};">
                    {len(matched)}</div>
                <div class="metric-label">Patterns Matched</div>
            </div>""", unsafe_allow_html=True)
        with col_c:
            st.markdown(f"""
            <div class="metric-tile">
                <div class="metric-value">{len(trace)}</div>
                <div class="metric-label">NFA Transitions</div>
            </div>""", unsafe_allow_html=True)

        # ε-Closure demo
        with st.expander("📐 ε-Closure Computation", expanded=True):
            st.markdown("""
            **ε-Closure of start state q₀:**

            The NFA uses ε-transitions from q₀ to reach the beginning of every pattern chain
            *without consuming* any input symbol. This is the foundational concept of NFA simulation.
            """)
            ec = nfa.epsilon_closure_single(nfa.start_state)
            st.markdown(f"""
            <div class="info-box">
            <b>ε-closure({{q₀}}) = </b><code>{{{', '.join(sorted(ec))}}}</code>
            <br><br>
            The closure contains <b>{len(ec)} states</b>.
            Since there are no ε-transitions from q₀ in this NFA, the closure is just
            <code>{{q₀}}</code> itself — the NFA starts at q₀ and transitions on actual input symbols.
            </div>
            """, unsafe_allow_html=True)

        # NFA trace
        with st.expander("🔬 NFA Execution Trace", expanded=False):
            st.markdown(f"""
            <div class="info-box">
            The NFA simultaneously tracks <b>multiple active states</b> at each step.
            Showing first {min(50, len(trace))} steps of {len(trace)} total.
            </div>
            """, unsafe_allow_html=True)
            trace_rows = [
                {
                    "Step": t["step"],
                    "Symbol": t["symbol"],
                    "Active States": str(t["states"]),
                    "# States": len(t["states"]),
                    "Attack Found": "🚨 YES" if t["accepted"] else "—",
                }
                for t in trace[:50]
            ]
            st.dataframe(pd.DataFrame(trace_rows), use_container_width=True, hide_index=True)

        # Pattern dictionary
        with st.expander("📖 SQL Injection Pattern Dictionary", expanded=False):
            patterns_info = [
                ("' OR '1'='1",   "Classic tautology bypass"),
                ("' OR 1=1",      "Alternative tautology"),
                ("UNION SELECT",  "Data extraction via UNION"),
                ("DROP TABLE",    "Destructive DDL injection"),
                ("--",            "Comment-based bypass"),
                ("1=1",           "Embedded tautology"),
                (";",             "Statement termination"),
                ("xp_",           "SQL Server extended procedure"),
                ("SLEEP(",        "Time-based blind injection"),
                ("EXEC(",         "Stored procedure execution"),
                ("INSERT INTO",   "Data insertion"),
                ("DELETE FROM",   "Data deletion"),
            ]
            df_pats = pd.DataFrame(patterns_info, columns=["Pattern", "Attack Type"])
            st.dataframe(df_pats, use_container_width=True, hide_index=True)

        # NFA formal definition
        with st.expander("📐 NFA Formal Definition", expanded=False):
            st.markdown(f"""
            **NFA 5-tuple:**  N = (Q, Σ, δ, q₀, F)

            | Component | Description |
            |-----------|-------------|
            | **Q** | q₀ (start) + one chain of states per pattern character |
            | **Σ** | Lowercase ASCII characters used in the 12 attack signatures |
            | **δ** | Character-by-character transitions per pattern chain; q₀ self-loops on all symbols |
            | **q₀** | Shared start state — entry point for all 12 pattern chains |
            | **F** | Terminal state of each pattern chain (12 accepting states total) |
            | **ε-transitions** | None explicit — NFA achieves non-determinism via q₀ self-loop |

            **Key property:** Because q₀ has a self-loop on every symbol, the NFA can start
            matching any pattern at *any position* in the input string — this provides
            **substring matching** without explicit ε-prefix transitions.
            """)
    else:
        st.markdown("""
        <div style="text-align:center;padding:3rem;color:#8b949e;">
            <div style="font-size:3rem;margin-bottom:1rem;">🚨</div>
            <div>Enter SQL input above or click a sample payload</div>
        </div>
        """, unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE: NFA → DFA Conversion
# ═════════════════════════════════════════════════════════════════════════════

elif page == "🔄  NFA → DFA Conversion":
    st.markdown("""
    <div class="hero-banner">
        <h1 class="hero-title">NFA → DFA Conversion</h1>
        <div class="hero-subtitle">Subset Construction (Powerset Construction) Method</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
    The <b>subset construction algorithm</b> converts any NFA into an equivalent DFA.
    Each DFA state corresponds to a <em>set</em> of NFA states reachable under the same input.
    This demonstrates that DFAs and NFAs recognize the same class of languages — the <b>Regular Languages</b>.
    </div>
    """, unsafe_allow_html=True)

    # ── Build a small illustrative NFA ──────────────────────────────────────
    st.markdown("### 🧪 Interactive NFA → DFA Converter")
    st.markdown("Use the **custom example NFA** below or switch to a pre-built one:")

    example_choice = st.selectbox("Select NFA Example", [
        "Example 1 — Ends with 'ab' (over {a,b})",
        "Example 2 — Contains 'aa' (over {a,b})",
        "Example 3 — Starts with '0' or ends with '1' (over {0,1})",
    ])

    from automata_engine import NFA, EPSILON
    from collections import defaultdict

    def example_nfa_1():
        """Accepts strings over {a,b} ending with 'ab'."""
        states = {"q0", "q1", "q2"}
        alphabet = {"a", "b"}
        transitions = {
            ("q0", "a"): {"q0", "q1"},
            ("q0", "b"): {"q0"},
            ("q1", "b"): {"q2"},
        }
        return NFA(states, alphabet, transitions, "q0", {"q2"})

    def example_nfa_2():
        """Accepts strings over {a,b} containing 'aa'."""
        states = {"q0", "q1", "q2"}
        alphabet = {"a", "b"}
        transitions = {
            ("q0", "a"): {"q0", "q1"},
            ("q0", "b"): {"q0"},
            ("q1", "a"): {"q2"},
            ("q2", "a"): {"q2"},
            ("q2", "b"): {"q2"},
        }
        return NFA(states, alphabet, transitions, "q0", {"q2"})

    def example_nfa_3():
        """Accepts strings over {0,1} starting with 0 or ending with 1."""
        states = {"q0", "q1", "q2", "q3"}
        alphabet = {"0", "1"}
        transitions = {
            ("q0", EPSILON): {"q1", "q2"},
            ("q1", "0"):     {"q1"},
            ("q1", "1"):     {"q1", "q3"},
            ("q2", "0"):     {"q2"},
        }
        return NFA(states, alphabet, transitions, "q0", {"q1", "q3"})

    nfa_map = {
        "Example 1 — Ends with 'ab' (over {a,b})":           example_nfa_1(),
        "Example 2 — Contains 'aa' (over {a,b})":            example_nfa_2(),
        "Example 3 — Starts with '0' or ends with '1' (over {0,1})": example_nfa_3(),
    }

    demo_nfa = nfa_map[example_choice]
    dfa_converted, state_map = demo_nfa.to_dfa()

    col_nfa, col_dfa = st.columns(2)

    with col_nfa:
        st.markdown("#### Original NFA")
        nfa_rows = demo_nfa.get_transitions_table()
        if nfa_rows:
            st.dataframe(pd.DataFrame(nfa_rows), use_container_width=True, hide_index=True)
        else:
            st.info("No transitions defined.")
        st.markdown(f"""
        <div class="card">
          <div class="card-title">NFA Summary</div>
          <div class="criteria-item"><span style="color:#00e5ff;">▸</span> <b>States:</b> <code>{sorted(demo_nfa.states)}</code></div>
          <div class="criteria-item"><span style="color:#00e5ff;">▸</span> <b>Alphabet:</b> <code>{sorted(demo_nfa.alphabet)}</code></div>
          <div class="criteria-item"><span style="color:#00e5ff;">▸</span> <b>Start:</b> <code>{demo_nfa.start_state}</code></div>
          <div class="criteria-item"><span style="color:#00e5ff;">▸</span> <b>Accept:</b> <code>{sorted(demo_nfa.accept_states)}</code></div>
        </div>
        """, unsafe_allow_html=True)

    with col_dfa:
        st.markdown("#### Converted DFA")
        dfa_rows = dfa_converted.get_transitions_table()
        if dfa_rows:
            st.dataframe(pd.DataFrame(dfa_rows), use_container_width=True, hide_index=True)
        st.markdown(f"""
        <div class="card">
          <div class="card-title">DFA Summary</div>
          <div class="criteria-item"><span style="color:#00e676;">▸</span> <b>States:</b> <code>{sorted(dfa_converted.states)}</code></div>
          <div class="criteria-item"><span style="color:#00e676;">▸</span> <b>Alphabet:</b> <code>{sorted(dfa_converted.alphabet)}</code></div>
          <div class="criteria-item"><span style="color:#00e676;">▸</span> <b>Start:</b> <code>{dfa_converted.start_state}</code></div>
          <div class="criteria-item"><span style="color:#00e676;">▸</span> <b>Accept:</b> <code>{sorted(dfa_converted.accept_states)}</code></div>
          <div class="criteria-item"><span style="color:#00e676;">▸</span> <b>Total States:</b> <code>{len(dfa_converted.states)}</code> (from NFA's {len(demo_nfa.states)})</div>
        </div>
        """, unsafe_allow_html=True)

    # State mapping
    with st.expander("🗺️ DFA State ↔ NFA State-Set Mapping", expanded=True):
        mapping_rows = [
            {
                "DFA State": ds,
                "NFA State Set": str(sorted(ns)),
                "Is Accepting": "✅ YES" if ds in dfa_converted.accept_states else "—",
                "Is Start": "▶ START" if ds == dfa_converted.start_state else "—",
            }
            for ds, ns in sorted(state_map.items())
        ]
        st.dataframe(pd.DataFrame(mapping_rows), use_container_width=True, hide_index=True)

    # ε-closure table
    with st.expander("📐 ε-Closure Table for All NFA States", expanded=False):
        ec_rows = []
        for s in sorted(demo_nfa.states):
            ec = demo_nfa.epsilon_closure_single(s)
            ec_rows.append({"State": s, "ε-closure": str(sorted(ec))})
        st.dataframe(pd.DataFrame(ec_rows), use_container_width=True, hide_index=True)

    # Equivalence verification
    st.markdown("### ✅ Equivalence Verification")
    st.markdown("Test that the original NFA and converted DFA give **identical results**:")

    test_str = st.text_input("Enter test string", placeholder="e.g. ab or aab or 01")
    if test_str:
        nfa_acc, nfa_trace = demo_nfa.run(test_str)
        dfa_acc, dfa_trace = dfa_converted.run(test_str)
        match = nfa_acc == dfa_acc

        col_n, col_d, col_eq = st.columns(3)
        with col_n:
            st.markdown(f"""
            <div class="metric-tile">
                <div class="metric-value" style="color:{'#00e676' if nfa_acc else '#ff1744'};">
                    {'✅' if nfa_acc else '❌'}</div>
                <div class="metric-label">NFA Result</div>
                <div style="font-size:0.72rem;color:#8b949e;">{'ACCEPTED' if nfa_acc else 'REJECTED'}</div>
            </div>""", unsafe_allow_html=True)
        with col_d:
            st.markdown(f"""
            <div class="metric-tile">
                <div class="metric-value" style="color:{'#00e676' if dfa_acc else '#ff1744'};">
                    {'✅' if dfa_acc else '❌'}</div>
                <div class="metric-label">DFA Result</div>
                <div style="font-size:0.72rem;color:#8b949e;">{'ACCEPTED' if dfa_acc else 'REJECTED'}</div>
            </div>""", unsafe_allow_html=True)
        with col_eq:
            st.markdown(f"""
            <div class="metric-tile">
                <div class="metric-value" style="color:{'#00e5ff' if match else '#ff1744'};">
                    {'⚖️' if match else '⚠️'}</div>
                <div class="metric-label">Equivalent?</div>
                <div style="font-size:0.72rem;color:{'#00e5ff' if match else '#ff1744'};">
                    {'YES — automata are equivalent' if match else 'NO — mismatch!'}</div>
            </div>""", unsafe_allow_html=True)

        if match:
            st.success("✅ Both automata agree on this string — confirming equivalence!")
        else:
            st.error("⚠️ Results differ — this should not happen with correct conversion.")


# ═════════════════════════════════════════════════════════════════════════════
# PAGE: Theory Reference
# ═════════════════════════════════════════════════════════════════════════════

elif page == "📚  Theory Reference":
    st.markdown("""
    <div class="hero-banner">
        <h1 class="hero-title">Theory Reference</h1>
        <div class="hero-subtitle">Formal Languages & Automata Theory — Core Concepts</div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📌 DFA", "📌 NFA", "📌 ε-Closure", "📌 Regular Languages", "📌 Pumping Lemma"
    ])

    with tab1:
        st.markdown("""
        ## Deterministic Finite Automaton (DFA)

        A DFA is formally defined as a 5-tuple:

        > **M = (Q, Σ, δ, q₀, F)**

        | Symbol | Meaning |
        |--------|---------|
        | **Q** | Finite set of states |
        | **Σ** | Finite input alphabet |
        | **δ : Q × Σ → Q** | Total transition function |
        | **q₀ ∈ Q** | Initial (start) state |
        | **F ⊆ Q** | Set of accepting (final) states |

        ### Key Properties
        - **Deterministic**: For each state and input symbol, there is exactly **one** next state.
        - **Total function**: `δ` is defined for every `(state, symbol)` pair (undefined → dead state).
        - **No ε-transitions**: Every transition consumes exactly one input symbol.
        - **Efficient**: O(n) time to process a string of length n.

        ### In This Project
        ```
        Password DFA:
          Q  = { (length_bucket, criteria_mask) | length ∈ [0..8], mask ∈ [0..15] } ∪ { DEAD }
          Σ  = { upper, lower, digit, special, other }
          δ  = (length, mask) × symbol → (min(length+1,8), mask | bit(symbol))
          q₀ = (0, 0b0000)
          F  = { (8, 0b1111) }
        ```
        """)

    with tab2:
        st.markdown("""
        ## Non-Deterministic Finite Automaton (NFA)

        An NFA is formally defined as a 5-tuple:

        > **N = (Q, Σ, δ, q₀, F)**

        | Symbol | Meaning |
        |--------|---------|
        | **Q** | Finite set of states |
        | **Σ** | Finite input alphabet (not including ε) |
        | **δ : Q × (Σ ∪ {ε}) → 2^Q** | Transition function returning a **set** of next states |
        | **q₀ ∈ Q** | Initial state |
        | **F ⊆ Q** | Set of accepting states |

        ### Key Differences from DFA
        - **Non-deterministic**: Multiple possible next states for a given input.
        - **ε-transitions**: Can change state without consuming any input.
        - **Accepts if**: At least **one** computation path leads to an accepting state.

        ### NFA Simulation (used in this project)
        The NFA is simulated by tracking the **set of all currently possible states**:
        ```
        current_states = ε-closure({q₀})
        for each symbol in input:
            next = ∪{ δ(s, symbol) | s ∈ current_states }
            current_states = ε-closure(next)
        accept if current_states ∩ F ≠ ∅
        ```

        ### In This Project
        ```
        SQL Injection NFA:
          12 pattern chains emanating from shared q₀
          q₀ self-loops enable substring matching anywhere in input
          Each chain's terminal state ∈ F
        ```
        """)

    with tab3:
        st.markdown("""
        ## ε-Closure

        The **ε-closure** of a state `q` is the set of all states reachable from `q`
        using **zero or more ε-transitions** (i.e., without consuming any input).

        ### Formal Definition
        ```
        ε-closure({q}) = { r ∈ Q | q →*_ε r }
        ```

        ### Algorithm
        ```python
        def epsilon_closure(state_set):
            closure = set(state_set)
            stack = list(state_set)
            while stack:
                s = stack.pop()
                for t in δ(s, ε):          # all ε-successors
                    if t not in closure:
                        closure.add(t)
                        stack.append(t)
            return frozenset(closure)
        ```

        ### Complexity
        - **Time**: O(|Q| + |transitions|) using BFS/DFS
        - **Space**: O(|Q|)

        ### Role in NFA-to-DFA Conversion
        ε-closure is called at every step of the subset construction to ensure
        all states reachable via ε are included in the current DFA "macro-state".
        """)

    with tab4:
        st.markdown("""
        ## Regular Languages

        A language L is **regular** if and only if it is recognized by some DFA
        (equivalently: some NFA, or some regular expression).

        ### The Chomsky Hierarchy
        | Type | Language Class | Machine |
        |------|---------------|---------|
        | Type 0 | Recursively Enumerable | Turing Machine |
        | Type 1 | Context-Sensitive | Linear Bounded Automaton |
        | Type 2 | Context-Free | Pushdown Automaton |
        | **Type 3** | **Regular** | **DFA / NFA** |

        ### Closure Properties
        Regular languages are closed under:
        - **Union**: L₁ ∪ L₂
        - **Concatenation**: L₁ · L₂
        - **Kleene Star**: L*
        - **Complement**: L̄
        - **Intersection**: L₁ ∩ L₂

        ### Why Regular Languages for Security?
        Password validation rules and attack signature matching are **pattern matching** problems.
        Their constraints (character classes, fixed keyword sequences) define **regular languages**,
        making DFA/NFA the ideal — and theoretically optimal — recognizer.

        ### Limitations
        Some security patterns are **not** regular:
        - Balanced brackets `( ... )` → Context-Free
        - Matching repeated strings `ww` → Not even Context-Free
        These require pushdown automata or more powerful models.
        """)

    with tab5:
        st.markdown("""
        ## Pumping Lemma for Regular Languages

        The Pumping Lemma is used to **prove a language is NOT regular**.

        ### Statement
        If L is a regular language, then there exists a **pumping length** p ≥ 1 such that
        for every string w ∈ L with |w| ≥ p, we can write w = xyz where:

        1. |y| ≥ 1
        2. |xy| ≤ p
        3. For all i ≥ 0: xyⁱz ∈ L ("pumping" y any number of times stays in L)

        ### How to Use It (Proof by Contradiction)
        1. Assume L is regular with pumping length p
        2. Choose a specific string w ∈ L with |w| ≥ p
        3. Show that for **every** possible split w = xyz satisfying conditions 1 and 2,
           there exists some i where xyⁱz ∉ L
        4. This contradicts the lemma → L is **not** regular

        ### Relevance to This Project
        The Pumping Lemma explains the **limitations** of our cybersecurity analyzer:

        | Detectable (Regular) | Not Detectable (Non-Regular) |
        |----------------------|------------------------------|
        | Fixed SQL keywords | Arbitrarily nested queries |
        | Password character classes | Matching open/close tags |
        | Substring patterns | Counting occurrences exactly |
        | Simple tautologies | Context-dependent semantics |

        > This is why real-world SQL injection prevention uses **parser-based** approaches
        > (like parameterized queries) in addition to pattern matching.
        """)

    st.markdown("---")
    st.markdown("### 📚 References")
    refs = [
        ("Hopcroft, Motwani, Ullman", "Introduction to Automata Theory, Languages, and Computation", "Pearson, 3rd Ed."),
        ("Mishra, K. L. P.", "Theory of Computer Science: Automata, Languages and Computation", "PHI Learning"),
        ("Sipser, M.", "Introduction to the Theory of Computation", "Cengage Learning, 3rd Ed."),
        ("OWASP", "SQL Injection Prevention Cheat Sheet", "owasp.org"),
    ]
    for author, title, pub in refs:
        st.markdown(f"""
        <div class="criteria-item">
            <span style="color:#448aff;">📖</span>
            <div><b style="color:#e6edf3;">{author}</b> — <em style="color:#c9d1d9;">{title}</em>
            <div style="font-size:0.75rem;color:#8b949e;">{pub}</div></div>
        </div>
        """, unsafe_allow_html=True)
