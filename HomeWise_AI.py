import streamlit as st
import json
import os
from datetime import datetime, date
import calendar
from groq import Groq
from fpdf import FPDF
import tempfile

# ─── API Key (Secure for deployment) ─────────────────────────────────────────
try:
    # For Streamlit Cloud deployment
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    try:
        # For local development
        from dotenv import load_dotenv
        load_dotenv()
        GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    except:
        GROQ_API_KEY = ""
# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="HomeWise AI",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --primary: #1a3c34;
    --accent: #e8a838;
    --accent2: #c45c2a;
    --bg: #f5f0e8;
    --card: #fffdf7;
    --text: #1a1a1a;
    --muted: #6b6b5a;
    --border: #d4c9a8;
    --success: #2d6a4f;
    --warning: #e8a838;
    --danger: #c45c2a;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--bg);
    color: var(--text);
}

/* Hide Streamlit defaults */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1rem; padding-bottom: 2rem; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--primary) !important;
    border-right: none;
}
[data-testid="stSidebar"] * { color: #f5f0e8 !important; }
[data-testid="stSidebar"] .stButton button {
    background: rgba(232,168,56,0.15) !important;
    border: 1px solid rgba(232,168,56,0.4) !important;
    color: var(--accent) !important;
    border-radius: 8px;
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    letter-spacing: 0.5px;
    transition: all 0.2s;
    width: 100%;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: rgba(232,168,56,0.3) !important;
}

/* Header */
.app-header {
    background: linear-gradient(135deg, var(--primary) 0%, #2d5a4e 100%);
    color: #f5f0e8;
    padding: 2rem 2.5rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.app-header::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(232,168,56,0.2) 0%, transparent 70%);
    border-radius: 50%;
}
.app-header h1 {
    font-family: 'Playfair Display', serif;
    font-size: 2.5rem;
    font-weight: 900;
    margin: 0;
    letter-spacing: -1px;
}
.app-header p {
    margin: 0.4rem 0 0;
    opacity: 0.75;
    font-size: 1rem;
    font-weight: 300;
}

/* Chat messages */
.chat-container {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.5rem;
    min-height: 400px;
    max-height: 550px;
    overflow-y: auto;
    margin-bottom: 1rem;
}
.msg-user {
    background: var(--primary);
    color: #f5f0e8;
    padding: 0.75rem 1.2rem;
    border-radius: 18px 18px 4px 18px;
    margin: 0.6rem 0 0.6rem 20%;
    font-size: 0.95rem;
    line-height: 1.5;
    box-shadow: 0 2px 8px rgba(26,60,52,0.15);
}
.msg-ai {
    background: #f0ebe0;
    color: var(--text);
    padding: 0.85rem 1.2rem;
    border-radius: 4px 18px 18px 18px;
    margin: 0.6rem 20% 0.6rem 0;
    font-size: 0.95rem;
    line-height: 1.6;
    border-left: 3px solid var(--accent);
}
.msg-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    margin-bottom: 0.3rem;
    opacity: 0.6;
}

/* Cards */
.feature-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem;
    margin-bottom: 0.8rem;
    transition: box-shadow 0.2s;
}
.feature-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.08); }
.feature-card h4 {
    font-family: 'Playfair Display', serif;
    font-size: 1.1rem;
    margin: 0 0 0.4rem;
    color: var(--primary);
}

/* Cost card */
.cost-card {
    background: linear-gradient(135deg, #1a3c34 0%, #2d5a4e 100%);
    color: #f5f0e8;
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
    text-align: center;
}
.cost-card .cost-value {
    font-family: 'Playfair Display', serif;
    font-size: 2.5rem;
    font-weight: 900;
    color: var(--accent);
}
.cost-card .cost-label { font-size: 0.85rem; opacity: 0.7; margin-top: 0.3rem; }

/* Calendar */
.cal-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 4px;
    margin-top: 0.5rem;
}
.cal-header { background: var(--primary); color: #f5f0e8; font-size: 0.7rem; font-weight: 600; text-align: center; padding: 6px 2px; border-radius: 4px; }
.cal-day { background: var(--card); border: 1px solid var(--border); font-size: 0.75rem; text-align: center; padding: 6px 2px; border-radius: 4px; cursor: pointer; }
.cal-day.has-task { background: #fff3cd; border-color: var(--accent); font-weight: 600; color: var(--accent2); }
.cal-day.today { background: var(--primary); color: #f5f0e8; font-weight: 700; }
.cal-day.empty { background: transparent; border: none; }

/* Task badge */
.task-badge {
    display: inline-block;
    background: var(--accent);
    color: var(--primary);
    font-size: 0.7rem;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 20px;
    margin: 2px;
}
.task-badge.urgent { background: var(--danger); color: white; }
.task-badge.done { background: var(--success); color: white; }

/* Tip box */
.tip-box {
    background: linear-gradient(135deg, #fff8e7 0%, #fef3d0 100%);
    border: 1px solid var(--accent);
    border-radius: 10px;
    padding: 1rem 1.25rem;
    margin: 0.6rem 0;
    font-size: 0.9rem;
}
.tip-box .tip-title { font-weight: 700; color: var(--accent2); margin-bottom: 0.3rem; }

/* Buttons */
.stButton button {
    background: var(--primary) !important;
    color: #f5f0e8 !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.5rem !important;
    transition: all 0.2s !important;
}
.stButton button:hover {
    background: #2d5a4e !important;
    box-shadow: 0 4px 12px rgba(26,60,52,0.3) !important;
    transform: translateY(-1px);
}

/* Section title */
.section-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--primary);
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid var(--accent);
}

/* Input */
.stTextInput input, .stTextArea textarea, .stSelectbox select {
    border: 1.5px solid var(--border) !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 2px rgba(26,60,52,0.1) !important;
}

/* Divider */
hr { border: none; border-top: 1px solid var(--border); margin: 1.5rem 0; }

/* Metrics */
.metric-row { display: flex; gap: 1rem; margin: 1rem 0; }
.metric-box {
    flex: 1;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem;
    text-align: center;
}
.metric-box .m-val { font-family: 'Playfair Display', serif; font-size: 1.8rem; font-weight: 700; color: var(--primary); }
.metric-box .m-lbl { font-size: 0.75rem; color: var(--muted); margin-top: 0.2rem; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #f0ebe0; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ─── Groq Client ───────────────────────────────────────────────────────────────
@st.cache_resource
def get_groq_client():
    return Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """You are HomeWise AI, an expert home maintenance assistant with 20+ years of experience as a licensed contractor and home inspector.

Your expertise covers:
- Plumbing (pipes, faucets, water heaters, drainage)
- Electrical (wiring, outlets, panels, lighting)
- HVAC (heating, ventilation, air conditioning, filters)
- Roofing & exterior (shingles, gutters, siding, waterproofing)
- Structural (foundations, walls, floors, framing)
- Appliances (diagnosis, repair tips, maintenance)
- Seasonal maintenance (winterizing, spring checks, etc.)
- DIY guidance with safety warnings
- Energy efficiency improvements
- Pest prevention

When responding:
1. Be specific and actionable — give real step-by-step instructions
2. Always mention safety first for electrical/gas tasks
3. Recommend when to call a professional vs DIY
4. Estimate difficulty level: Beginner / Intermediate / Professional Only
5. Mention tools needed for DIY tasks
6. Be conversational but authoritative
7. If asked about cost, give realistic ranges (materials + labor)

You have a warm, helpful personality — like a knowledgeable neighbor who genuinely wants to help."""

# ─── Session State ─────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "messages": [],
        "tasks": [],
        "active_tab": "chat",
        "home_profile": {
            "type": "House",
            "year_built": 2000,
            "size_sqft": 1500,
            "location": "Midwest"
        }
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ─── Helpers ───────────────────────────────────────────────────────────────────
def ask_groq(messages, system=SYSTEM_PROMPT):
    client = get_groq_client()
    formatted = [{"role": "system", "content": system}] + messages
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=formatted,
        temperature=0.7,
        max_tokens=1024
    )
    return resp.choices[0].message.content

def estimate_cost(task, location, home_type):
    prompt = f"""Provide a detailed cost estimate for: "{task}"
Home: {home_type}, Location: {location}
Return a JSON object with these exact keys:
{{
  "task": "task name",
  "diy_cost": {{"min": number, "max": number, "unit": "USD"}},
  "pro_cost": {{"min": number, "max": number, "unit": "USD"}},
  "time_hours": {{"diy": number, "pro": number}},
  "difficulty": "Beginner|Intermediate|Advanced|Professional Only",
  "materials": ["item1", "item2"],
  "tools": ["tool1", "tool2"],
  "tips": "brief money-saving tip",
  "urgency": "Low|Medium|High|Critical"
}}
Return ONLY the JSON, no other text."""
    client = get_groq_client()
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=600
    )
    raw = resp.choices[0].message.content.strip()
    # Clean JSON
    if "```" in raw:
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())

def get_seasonal_tips(season, home_profile):
    prompt = f"""Give 6 essential home maintenance tasks for {season} for a {home_profile['year_built']} {home_profile['type']} in {home_profile['location']}.
Return JSON array:
[{{"task": "task name", "description": "2 sentence description", "priority": "High|Medium|Low", "estimated_hours": number, "estimated_cost": number}}]
ONLY JSON, no other text."""
    client = get_groq_client()
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=800
    )
    raw = resp.choices[0].message.content.strip()
    if "```" in raw:
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())

def export_pdf(chat_history, tasks, cost_data=None):
    # Create PDF with Unicode support
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(20, 20, 20)
    
    # Helper function to clean text of problematic characters
    def clean_text(text):
        """Replace problematic characters with safe alternatives"""
        if not isinstance(text, str):
            text = str(text)
        
        replacements = {
            "—": "-",      # em dash to regular dash
            "–": "-",      # en dash to regular dash  
            "’": "'",      # curly apostrophe to straight
            "‘": "'",      # curly apostrophe to straight
            "“": '"',      # curly quote to straight
            "”": '"',      # curly quote to straight
            "…": "...",    # ellipsis to three dots
            "•": "-",      # bullet to dash
            "®": "(R)",    # registered symbol
            "™": "(TM)",   # trademark symbol
            "°": "deg",    # degree symbol
            "¢": "cent",   # cent symbol
            "£": "GBP",    # pound symbol
            "€": "EUR",    # euro symbol
            "¥": "JPY",    # yen symbol
            "©": "(c)",    # copyright symbol
            "✓": "[OK]",   # checkmark
            "✅": "[DONE]", # checkmark emoji
            "❌": "[X]",    # x mark
            "⭐": "*",      # star
            "•": "-",      # bullet point
        }
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        
        # Remove any other non-ASCII characters (keep only ASCII)
        text = ''.join(char for char in text if ord(char) < 128 or char in ' \n\t.,!?;:()[]{}"\'-')
        return text

    # Header with background
    pdf.set_fill_color(26, 60, 52)
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_y(15)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(232, 168, 56)
    pdf.cell(0, 10, "HomeWise AI - Maintenance Report", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(200, 200, 180)
    pdf.cell(0, 8, f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", ln=True, align="C")
    pdf.ln(15)

    # Chat History
    if chat_history:
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(26, 60, 52)
        pdf.cell(0, 10, "Chat History", ln=True)
        pdf.set_draw_color(232, 168, 56)
        pdf.set_line_width(0.5)
        pdf.line(20, pdf.get_y(), 190, pdf.get_y())
        pdf.ln(4)

        for msg in chat_history:
            role = "You" if msg["role"] == "user" else "HomeWise AI"
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(100, 100, 80)
            pdf.cell(0, 6, role.upper(), ln=True)

            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(30, 30, 30)
            content = msg["content"]
            
            # Clean the content of problematic characters
            content = clean_text(content)
            
            # Remove markdown symbols for cleaner PDF
            for sym in ["**", "*", "##", "#", "```", "__"]:
                content = content.replace(sym, "")
            
            # Split long content into chunks if needed
            pdf.multi_cell(0, 6, content[:2000])  # Limit length
            pdf.ln(3)

    # Tasks
    if tasks:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(26, 60, 52)
        pdf.cell(0, 10, "Maintenance Calendar Tasks", ln=True)
        pdf.set_draw_color(232, 168, 56)
        pdf.line(20, pdf.get_y(), 190, pdf.get_y())
        pdf.ln(4)

        for task in tasks:
            status_icon = "[DONE]" if task.get("done") else "[PENDING]"
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(26, 60, 52)
            
            title = clean_text(task.get('title', 'Untitled'))
            pdf.cell(0, 7, f"{status_icon} {title}", ln=True)
            
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(80, 80, 70)
            due_date = clean_text(task.get('due', 'TBD'))
            priority = clean_text(task.get('priority', 'Medium'))
            cost = task.get('cost', 0)
            pdf.cell(0, 6, f"Due: {due_date}  |  Priority: {priority}  |  Est. Cost: ${cost:,}", ln=True)
            
            if task.get("notes"):
                pdf.set_text_color(100, 100, 90)
                notes = clean_text(task["notes"])
                pdf.multi_cell(0, 5, notes)
            pdf.ln(2)

    # Cost summary
    if cost_data:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(26, 60, 52)
        pdf.cell(0, 10, "Cost Estimate Details", ln=True)
        pdf.set_draw_color(232, 168, 56)
        pdf.line(20, pdf.get_y(), 190, pdf.get_y())
        pdf.ln(4)
        
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(30, 30, 30)
        
        task_name = clean_text(cost_data.get('task', ''))
        pdf.multi_cell(0, 6, f"Task: {task_name}")
        
        # Safely get nested values
        diy_min = cost_data.get('diy_cost', {}).get('min', 0)
        diy_max = cost_data.get('diy_cost', {}).get('max', 0)
        pdf.cell(0, 6, f"DIY Cost: ${diy_min:,} - ${diy_max:,}", ln=True)
        
        pro_min = cost_data.get('pro_cost', {}).get('min', 0)
        pro_max = cost_data.get('pro_cost', {}).get('max', 0)
        pdf.cell(0, 6, f"Pro Cost: ${pro_min:,} - ${pro_max:,}", ln=True)
        
        difficulty = clean_text(cost_data.get('difficulty', ''))
        pdf.cell(0, 6, f"Difficulty: {difficulty}", ln=True)
        
        urgency = clean_text(cost_data.get('urgency', ''))
        pdf.cell(0, 6, f"Urgency: {urgency}", ln=True)
        
        if cost_data.get("materials"):
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 7, "Materials Needed:", ln=True)
            pdf.set_font("Helvetica", "", 10)
            for m in cost_data["materials"]:
                material = clean_text(m)
                pdf.cell(0, 6, f"  - {material}", ln=True)
        
        if cost_data.get("tools"):
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 7, "Tools Required:", ln=True)
            pdf.set_font("Helvetica", "", 10)
            for t in cost_data["tools"]:
                tool = clean_text(t)
                pdf.cell(0, 6, f"  - {tool}", ln=True)
        
        if cost_data.get("tips"):
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 7, "Money-Saving Tip:", ln=True)
            pdf.set_font("Helvetica", "", 10)
            tip = clean_text(cost_data["tips"])
            pdf.multi_cell(0, 6, tip)

    # Footer on last page
    pdf.set_y(-20)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(150, 150, 130)
    pdf.cell(0, 8, "HomeWise AI - Your Intelligent Home Maintenance Companion", ln=True, align="C")

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(tmp.name)
    return tmp.name



# ─── Main Content ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <h1>🏠 HomeWise AI</h1>
    <p>Your intelligent home maintenance companion — powered by Groq & Llama 3.3</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["💬 Chat Assistant", "💰 Cost Estimator", "📅 Maintenance Calendar", "🌿 Seasonal Tips", "📄 Export Report"])

# ════════════════════════════════════════════════════════════════════
# TAB 1: CHAT
# ════════════════════════════════════════════════════════════════════
with tab1:
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown('<div class="section-title">Chat with HomeWise AI</div>', unsafe_allow_html=True)

        # Chat display
        if not st.session_state.messages:
            st.markdown("""
            <div style="background:var(--card);border:1px solid var(--border);border-radius:16px;padding:3rem 2rem;text-align:center;opacity:0.6;">
                <div style="font-size:3rem;">🏠</div>
                <div style="font-family:'Playfair Display',serif;font-size:1.1rem;margin-top:0.5rem;">Ask me anything about your home!</div>
                <div style="font-size:0.85rem;margin-top:0.5rem;">Plumbing · Electrical · HVAC · Roofing · Appliances · DIY Tips</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    st.markdown(f'<div class="msg-user"><div class="msg-label">You</div>{msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    content = msg["content"].replace("\n", "<br>")
                    st.markdown(f'<div class="msg-ai"><div class="msg-label">🏠 HomeWise AI</div>{content}</div>', unsafe_allow_html=True)

        # Input
        with st.form("chat_form", clear_on_submit=True):
            cols = st.columns([5, 1])
            with cols[0]:
                user_input = st.text_input("", placeholder="e.g. My toilet keeps running, how do I fix it?", label_visibility="collapsed")
            with cols[1]:
                submitted = st.form_submit_button("Send →")

        if submitted and user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.spinner("HomeWise AI is thinking..."):
                try:
                    response = ask_groq(st.session_state.messages)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    st.error(f"Error: {e}")
            st.rerun()

        if st.session_state.messages:
            if st.button("🗑️ Clear Chat"):
                st.session_state.messages = []
                st.rerun()

    with col2:
        st.markdown('<div class="section-title" style="font-size:1.1rem;">💡 Suggested Questions</div>', unsafe_allow_html=True)
        suggestions = [
            "How do I unclog a drain without chemicals?",
            "Why is my circuit breaker tripping?",
            "How often should I change HVAC filters?",
            "What causes drywall cracks?",
            "How do I stop a leaking faucet?",
            "Signs my roof needs replacing?",
            "How to improve home energy efficiency?",
            "What's the ideal water heater temp?",
        ]
        for s in suggestions:
            if st.button(s, key=f"sug_{s}", help="Click to ask this"):
                st.session_state.messages.append({"role": "user", "content": s})
                with st.spinner("Thinking..."):
                    try:
                        response = ask_groq(st.session_state.messages)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                    except Exception as e:
                        st.error(f"Error: {e}")
                st.rerun()

# ════════════════════════════════════════════════════════════════════
# TAB 2: COST ESTIMATOR
# ════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">💰 AI Cost Estimator</div>', unsafe_allow_html=True)
    st.markdown("Get instant AI-powered cost estimates for any home repair or maintenance task.")

    col1, col2 = st.columns([2, 1])
    with col1:
        cost_task = st.text_input("What task do you need estimated?",
                                   placeholder="e.g. Replace water heater, Fix roof leak, Repaint living room...")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        estimate_btn = st.button("💰 Get Estimate", key="est_btn")

    if estimate_btn and cost_task:
        with st.spinner("Calculating costs..."):
            try:
                data = estimate_cost(cost_task, st.session_state.home_profile["location"],
                                    st.session_state.home_profile["type"])
                st.session_state["last_cost_data"] = data

                # Cost cards
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"""
                    <div class="cost-card">
                        <div style="font-size:0.85rem; opacity:0.7; margin-bottom:0.5rem;">🔨 DIY COST</div>
                        <div class="cost-value">${data['diy_cost']['min']:,} – ${data['diy_cost']['max']:,}</div>
                        <div class="cost-label">~{data['time_hours']['diy']} hours of your time</div>
                    </div>
                    """, unsafe_allow_html=True)
                with c2:
                    st.markdown(f"""
                    <div class="cost-card" style="background: linear-gradient(135deg, #7a3a1e 0%, #c45c2a 100%);">
                        <div style="font-size:0.85rem; opacity:0.7; margin-bottom:0.5rem;">👷 PROFESSIONAL COST</div>
                        <div class="cost-value">${data['pro_cost']['min']:,} – ${data['pro_cost']['max']:,}</div>
                        <div class="cost-label">~{data['time_hours']['pro']} hours turnaround</div>
                    </div>
                    """, unsafe_allow_html=True)

                # Details
                col_a, col_b, col_c = st.columns(3)
                urgency_color = {"Low": "#2d6a4f", "Medium": "#e8a838", "High": "#c45c2a", "Critical": "#8b0000"}.get(data.get("urgency","Low"), "#666")
                with col_a:
                    st.markdown(f"""<div class="feature-card"><h4>⚡ Difficulty</h4><span class="task-badge">{data.get('difficulty','N/A')}</span></div>""", unsafe_allow_html=True)
                with col_b:
                    st.markdown(f"""<div class="feature-card"><h4>🚨 Urgency</h4><span style="background:{urgency_color};color:white;padding:3px 10px;border-radius:20px;font-size:0.75rem;font-weight:700;">{data.get('urgency','Low')}</span></div>""", unsafe_allow_html=True)
        
                # Add to calendar
                if st.button("📅 Add to Maintenance Calendar"):
                    st.session_state.tasks.append({
                        "title": cost_task,
                        "due": str(date.today()),
                        "priority": data.get("urgency", "Medium"),
                        "cost": data['pro_cost']['min'],
                        "notes": f"DIY: ${data['diy_cost']['min']}-${data['diy_cost']['max']} | Pro: ${data['pro_cost']['min']}-${data['pro_cost']['max']}",
                        "done": False
                    })
                    st.success("✅ Added to your maintenance calendar!")

            except json.JSONDecodeError:
                st.error("Could not parse cost estimate. Try rephrasing your task.")
            except Exception as e:
                st.error(f"Error: {e}")

# ════════════════════════════════════════════════════════════════════
# TAB 3: MAINTENANCE CALENDAR
# ════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-title">📅 Maintenance Calendar</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("#### ➕ Add New Task")
        with st.form("task_form"):
            t_title = st.text_input("Task Title", placeholder="e.g. Clean gutters")
            t_col1, t_col2 = st.columns(2)
            with t_col1:
                t_due = st.date_input("Due Date", value=date.today())
                t_priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
            with t_col2:
                t_cost = st.number_input("Est. Cost ($)", min_value=0, value=0, step=10)
                t_category = st.selectbox("Category", ["Plumbing", "Electrical", "HVAC", "Roofing", "Exterior", "Interior", "Appliances", "Safety", "Other"])
            t_notes = st.text_area("Notes", height=80, placeholder="Optional notes...")
            add_task = st.form_submit_button("Add Task")

        if add_task and t_title:
            st.session_state.tasks.append({
                "title": t_title,
                "due": str(t_due),
                "priority": t_priority,
                "cost": t_cost,
                "category": t_category,
                "notes": t_notes,
                "done": False,
                "created": str(date.today())
            })
            st.success(f"✅ '{t_title}' added!")
            st.rerun()

        # Calendar view
        st.markdown("#### 📆 This Month")
        today = date.today()
        cal = calendar.monthcalendar(today.year, today.month)
        task_dates = {t["due"][:10] for t in st.session_state.tasks}

        days_header = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        header_html = "".join([f'<div class="cal-header">{d}</div>' for d in days_header])

        days_html = ""
        for week in cal:
            for day in week:
                if day == 0:
                    days_html += '<div class="cal-day empty"></div>'
                else:
                    d_str = f"{today.year}-{today.month:02d}-{day:02d}"
                    cls = "cal-day"
                    if day == today.day:
                        cls += " today"
                    elif d_str in task_dates:
                        cls += " has-task"
                    days_html += f'<div class="{cls}">{day}</div>'

        st.markdown(f'<div class="cal-grid">{header_html}{days_html}</div>', unsafe_allow_html=True)

    with col2:
        st.markdown("#### 📋 Task List")

        if not st.session_state.tasks:
            st.markdown("""<div style="text-align:center;padding:2rem;opacity:0.5;"><div style="font-size:2rem;">📋</div><div>No tasks yet. Add your first maintenance task!</div></div>""", unsafe_allow_html=True)
        else:
            # Sort by due date
            sorted_tasks = sorted(st.session_state.tasks, key=lambda x: (x.get("done", False), x.get("due", "9999")))

            # Stats
            done_count = sum(1 for t in st.session_state.tasks if t.get("done"))
            total_count = len(st.session_state.tasks)
            total_cost = sum(t.get("cost", 0) for t in st.session_state.tasks if not t.get("done"))

            st.markdown(f"""
            <div style="display:flex;gap:0.8rem;margin-bottom:1rem;">
                <div style="flex:1;background:var(--card);border:1px solid var(--border);border-radius:8px;padding:0.8rem;text-align:center;">
                    <div style="font-size:1.4rem;font-weight:800;color:var(--primary);">{total_count}</div>
                    <div style="font-size:0.7rem;color:var(--muted);">TOTAL TASKS</div>
                </div>
                <div style="flex:1;background:var(--card);border:1px solid var(--border);border-radius:8px;padding:0.8rem;text-align:center;">
                    <div style="font-size:1.4rem;font-weight:800;color:#2d6a4f;">{done_count}</div>
                    <div style="font-size:0.7rem;color:var(--muted);">COMPLETED</div>
                </div>
                <div style="flex:1;background:var(--card);border:1px solid var(--border);border-radius:8px;padding:0.8rem;text-align:center;">
                    <div style="font-size:1.4rem;font-weight:800;color:var(--accent2);">${total_cost:,}</div>
                    <div style="font-size:0.7rem;color:var(--muted);">PENDING COST</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            for i, task in enumerate(sorted_tasks):
                orig_i = st.session_state.tasks.index(task)
                priority_color = {"Low": "#2d6a4f", "Medium": "#e8a838", "High": "#c45c2a", "Critical": "#8b0000"}.get(task.get("priority"), "#666")
                done_style = "opacity:0.5; text-decoration:line-through;" if task.get("done") else ""

                with st.expander(f"{'✅' if task.get('done') else '⏳'} {task['title']}", expanded=not task.get("done")):
                    st.markdown(f"""
                    <div style="{done_style}">
                        <span class="task-badge" style="background:{priority_color};color:white;">{task.get('priority','Medium')}</span>
                        <span class="task-badge">{task.get('category','Other')}</span>
                        <div style="margin-top:0.5rem; font-size:0.85rem; color:var(--muted);">
                            📅 Due: {task.get('due','TBD')} &nbsp;|&nbsp; 💰 Est: ${task.get('cost',0):,}
                        </div>
                        {f"<div style='font-size:0.85rem; margin-top:0.4rem;'>{task['notes']}</div>" if task.get('notes') else ""}
                    </div>
                    """, unsafe_allow_html=True)

                    bcol1, bcol2 = st.columns(2)
                    with bcol1:
                        label = "↩️ Mark Pending" if task.get("done") else "✅ Mark Done"
                        if st.button(label, key=f"done_{i}"):
                            st.session_state.tasks[orig_i]["done"] = not task.get("done")
                            st.rerun()
                    with bcol2:
                        if st.button("🗑️ Delete", key=f"del_{i}"):
                            st.session_state.tasks.pop(orig_i)
                            st.rerun()

# ════════════════════════════════════════════════════════════════════
# TAB 4: SEASONAL TIPS
# ════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-title">🌿 Seasonal Maintenance Guide</div>', unsafe_allow_html=True)
    st.markdown("Get AI-generated maintenance checklists tailored to your home and season.")

    col1, col2 = st.columns([1, 3])
    with col1:
        season = st.selectbox("Select Season", ["🌸 Spring", "☀️ Summer", "🍂 Fall", "❄️ Winter"])
        gen_btn = st.button("Generate Guide", key="season_btn")

    with col2:
        season_icons = {"🌸 Spring": "🌸", "☀️ Summer": "☀️", "🍂 Fall": "🍂", "❄️ Winter": "❄️"}
        season_desc = {
            "🌸 Spring": "Post-winter recovery, exterior inspections, and HVAC prep",
            "☀️ Summer": "Cooling efficiency, outdoor maintenance, and storm prep",
            "🍂 Fall": "Pre-winter weatherization and heating system checks",
            "❄️ Winter": "Freeze protection, indoor maintenance, and safety checks"
        }
        st.markdown(f"""
        <div class="tip-box">
            <div class="tip-title">{season} — {season_desc.get(season,'')}</div>
            Home: {st.session_state.home_profile['year_built']} {st.session_state.home_profile['type']} · {st.session_state.home_profile['size_sqft']:,} sq ft · {st.session_state.home_profile['location']}
        </div>
        """, unsafe_allow_html=True)

    if gen_btn:
        with st.spinner(f"Generating {season} maintenance guide..."):
            try:
                season_clean = season.split(" ", 1)[1]
                tips = get_seasonal_tips(season_clean, st.session_state.home_profile)
                st.session_state["seasonal_tips"] = tips
                st.session_state["seasonal_season"] = season
            except Exception as e:
                st.error(f"Error: {e}")

    if "seasonal_tips" in st.session_state:
        tips = st.session_state["seasonal_tips"]
        season_shown = st.session_state.get("seasonal_season", "")

        st.markdown(f"### {season_shown} Maintenance Checklist")

        add_all = st.button("📅 Add All to Calendar")

        cols = st.columns(2)
        for i, tip in enumerate(tips):
            priority_color = {"High": "#c45c2a", "Medium": "#e8a838", "Low": "#2d6a4f"}.get(tip.get("priority"), "#666")
            with cols[i % 2]:
                st.markdown(f"""
                <div class="feature-card">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                        <h4>{tip['task']}</h4>
                        <span style="background:{priority_color};color:white;padding:2px 8px;border-radius:12px;font-size:0.7rem;font-weight:700;white-space:nowrap;">{tip.get('priority','Medium')}</span>
                    </div>
                    <p style="font-size:0.87rem;color:var(--muted);margin:0.3rem 0 0.6rem;line-height:1.5;">{tip['description']}</p>
                    <div style="font-size:0.8rem;color:var(--muted);">
                        ⏱ {tip.get('estimated_hours',1)}h &nbsp;|&nbsp; 💰 ~${tip.get('estimated_cost',0):,}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        if add_all:
            s_clean = season_shown.split(" ", 1)[1] if " " in season_shown else season_shown
            for tip in tips:
                st.session_state.tasks.append({
                    "title": tip["task"],
                    "due": str(date.today()),
                    "priority": tip.get("priority", "Medium"),
                    "cost": tip.get("estimated_cost", 0),
                    "category": "Other",
                    "notes": tip.get("description", ""),
                    "done": False,
                    "created": str(date.today())
                })
            st.success(f"✅ Added {len(tips)} {s_clean} tasks to your calendar!")
            st.rerun()

# ════════════════════════════════════════════════════════════════════
# TAB 5: EXPORT REPORT
# ════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-title">📄 Export Maintenance Report</div>', unsafe_allow_html=True)
    st.markdown("Generate a professional PDF report with your chat history, tasks, and cost estimates.")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("#### What to include:")
        inc_chat = st.checkbox("💬 Chat History", value=True)
        inc_tasks = st.checkbox("📅 Maintenance Tasks", value=True)
        inc_cost = st.checkbox("💰 Latest Cost Estimate", value=True)

        st.markdown("---")
        st.markdown("#### Report Preview")
        chat_count = len(st.session_state.messages)
        task_count = len(st.session_state.tasks)
        has_cost = "last_cost_data" in st.session_state

        export_btn = st.button("📥 Generate PDF Report", key="export_btn")

    
    if export_btn:
        chat_to_export = st.session_state.messages if inc_chat else []
        tasks_to_export = st.session_state.tasks if inc_tasks else []
        cost_to_export = st.session_state.get("last_cost_data") if inc_cost else None

        if not chat_to_export and not tasks_to_export and not cost_to_export:
            st.warning("Nothing to export! Start chatting or add tasks first.")
        else:
            with st.spinner("Generating your PDF report..."):
                try:
                    pdf_path = export_pdf(chat_to_export, tasks_to_export, cost_to_export)
                    with open(pdf_path, "rb") as f:
                        pdf_bytes = f.read()
                    filename = f"HomeWise_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
                    st.download_button(
                        label="⬇️ Download PDF Report",
                        data=pdf_bytes,
                        file_name=filename,
                        mime="application/pdf"
                    )
                    st.success("✅ Report generated! Click above to download.")
                    os.unlink(pdf_path)
                except Exception as e:
                    st.error(f"PDF generation error: {e}")

# ─── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<hr>
<div style="text-align:center;font-size:0.8rem;color:#999;padding:0.5rem;">
    <strong style="color:var(--primary);">HomeWise AI</strong> — Powered by Groq & Llama 3.3 · Built with Streamlit<br>
    <span style="opacity:0.6;">Always consult a licensed professional for electrical, gas, and structural work.</span>
</div>
""", unsafe_allow_html=True)