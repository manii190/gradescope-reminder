import streamlit as st
import asyncio
import base64
from datetime import datetime, timedelta
from collections import defaultdict
import pandas as pd
import altair as alt
from assignments import get_all_assignments

st.set_page_config(
    page_title="Gradescope Command Center",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)


def get_base64_image(f):
    try:
        with open(f, "rb") as fh:
            return base64.b64encode(fh.read()).decode()
    except FileNotFoundError:
        return ""

day_bg   = get_base64_image("uofa_day.jpeg")
night_bg = get_base64_image("uofa_night.jpeg")

if "dark" not in st.session_state:
    st.session_state.dark = True

_bg  = night_bg if st.session_state.dark else day_bg
_dim = "linear-gradient(rgba(0,0,0,0.52),rgba(0,0,0,0.60))" if st.session_state.dark \
       else "linear-gradient(rgba(0,0,0,0.28),rgba(0,0,0,0.36))"

bg_css = f"""
.stApp {{
    background-image: {_dim}, url("data:image/jpeg;base64,{_bg}");
    background-size:cover; background-position:center; background-attachment:fixed; color:#fff;
}}
header[data-testid="stHeader"] {{ background: transparent !important; background-color: transparent !important; }}
[data-testid="stToolbar"] {{ background: transparent !important; }}
div[data-testid="stDecoration"] {{ background: transparent !important; display: none !important; }}
""" if _bg else ""

st.markdown(f"""
<style>
{bg_css}

/* ══════════════════════════════════════════════
   SIDEBAR — dark glass, icon + label tiles
══════════════════════════════════════════════ */
[data-testid="stSidebar"] {{
    background: rgba(10, 8, 16, 0.82) !important;
    backdrop-filter: blur(32px) !important;
    -webkit-backdrop-filter: blur(32px) !important;
    border-right: 0.5px solid rgba(255,255,255,0.07) !important;
    width: 96px !important;
    min-width: 96px !important;
}}
[data-testid="stSidebar"] * {{ color: #ffffff !important; }}

/* Center column layout */
[data-testid="stSidebar"] > div > div > div {{
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    padding: 10px 0 !important;
    gap: 2px !important;
}}

/* All nav buttons — tall rounded tiles showing emoji + tiny label */
[data-testid="stSidebar"] .stButton > button {{
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 16px !important;
    width: 64px !important;
    height: 64px !important;
    padding: 6px 4px !important;
    margin: 2px auto !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 13px !important;
    line-height: 1.3 !important;
    box-shadow: none !important;
    transition: background 0.15s ease, border-color 0.15s ease !important;
    white-space: normal !important;
    word-break: break-word !important;
}}
[data-testid="stSidebar"] .stButton > button p {{
    font-size: 11px !important;
    line-height: 1.2 !important;
    margin: 0 !important;
    color: rgba(255,255,255,0.55) !important;
    text-align: center !important;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
    background: rgba(255,255,255,0.10) !important;
    border-color: rgba(255,255,255,0.20) !important;
}}
[data-testid="stSidebar"] .stButton > button:hover p {{
    color: rgba(255,255,255,0.9) !important;
}}

/* Active — red glow ring */
[data-testid="stSidebar"] .stButton > button[kind="primary"] {{
    background: rgba(171,5,32,0.22) !important;
    border: 1px solid rgba(171,5,32,0.65) !important;
    box-shadow: 0 0 14px rgba(171,5,32,0.28) !important;
}}
[data-testid="stSidebar"] .stButton > button[kind="primary"] p {{
    color: rgba(255,200,210,0.9) !important;
}}

/* Sync button — red tile */
.sync-btn > button {{
    background: rgba(171,5,32,0.28) !important;
    border: 1px solid rgba(171,5,32,0.55) !important;
    border-radius: 16px !important;
    width: 64px !important;
    height: 64px !important;
    padding: 6px 4px !important;
    margin: 2px auto !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 13px !important;
}}
.sync-btn > button p {{
    font-size: 11px !important;
    color: rgba(255,180,190,0.8) !important;
    margin: 0 !important;
    text-align: center !important;
}}
.sync-btn > button:hover {{
    background: rgba(171,5,32,0.48) !important;
}}

/* Progress bar */
[data-testid="stProgress"] > div > div {{
    background: linear-gradient(90deg,#AB0520,#ff4466) !important;
    border-radius: 999px !important;
}}
[data-testid="stProgress"] {{
    background: rgba(255,255,255,0.08) !important;
    border-radius: 999px !important;
    width: 64px !important;
}}

/* Sidebar progress text */
[data-testid="stSidebar"] div[style*="font-size:11px"] {{
    font-size: 9px !important;
    text-align: center !important;
    color: rgba(255,255,255,0.30) !important;
    display: none !important;
}}

/* Toggle */
[data-testid="stToggle"] label {{
    font-size: 11px !important;
    color: rgba(255,255,255,0.35) !important;
}}

/* ══════════════════════════════════════════════
   LAYOUT
══════════════════════════════════════════════ */
.block-container {{
    padding-top: 1.6rem;
    max-width: 1200px;
    background: transparent !important;
}}

.main, .main > div,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
[data-testid="block-container"],
[data-testid="stVerticalBlock"],
[data-testid="stVerticalBlockBorderWrapper"],
section[data-testid="stSidebar"] + div,
.stMainBlockContainer,
.element-container {{
    background: transparent !important;
    background-color: transparent !important;
}}

/* ══════════════════════════════════════════════
   GLASS CARDS
══════════════════════════════════════════════ */
.glass {{
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.16);
    backdrop-filter: blur(28px);
    -webkit-backdrop-filter: blur(28px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.20), inset 0 1px 0 rgba(255,255,255,0.10);
    border-radius: 20px;
    padding: 26px 30px;
    margin-bottom: 18px;
}}

/* ══════════════════════════════════════════════
   PAGE TITLE
══════════════════════════════════════════════ */
.page-title {{
    font-size: clamp(24px,3.5vw,40px);
    font-weight: 900; letter-spacing:-0.8px;
    background: linear-gradient(110deg, #ff8a8a, #ffffff 55%, #b8d4ff);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    margin-bottom: 2px;
}}
.page-subtitle {{
    color: rgba(255,255,255,0.48);
    font-size: 14px; font-weight:400; margin-bottom:24px;
}}

/* ══════════════════════════════════════════════
   METRIC BOXES
══════════════════════════════════════════════ */
[data-testid="stMetric"] {{
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.16) !important;
    backdrop-filter: blur(28px) !important;
    border-radius: 18px !important;
    padding: 20px 16px !important;
    transition: transform 0.16s ease !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.18) !important;
}}
[data-testid="stMetric"]:hover {{ transform: translateY(-2px) !important; }}
[data-testid="stMetricLabel"] {{
    color: rgba(255,255,255,0.50) !important;
    font-size: 11px !important; font-weight:700 !important;
    letter-spacing:0.09em !important; text-transform:uppercase !important;
}}
[data-testid="stMetricValue"] {{
    color: #ffffff !important; font-size:26px !important; font-weight:800 !important;
}}

/* ══════════════════════════════════════════════
   ASSIGNMENT CARDS
══════════════════════════════════════════════ */
.acard {{
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.15);
    backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px);
    box-shadow: 0 4px 20px rgba(0,0,0,0.16);
    border-radius: 18px; padding: 20px 24px; margin-bottom:12px;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}}
.acard:hover {{ transform:translateY(-2px); box-shadow:0 10px 32px rgba(0,0,0,0.24); }}
.acard-title {{
    font-size:17px; font-weight:800; color:#fff;
    letter-spacing:-0.2px; margin-bottom:7px;
    text-shadow: 0 1px 4px rgba(0,0,0,0.28);
}}
.acard-urgent {{ border-color:rgba(255,90,110,0.40) !important; background:rgba(255,50,70,0.08) !important; }}
.acard-done   {{ opacity:0.55; }}

/* ══════════════════════════════════════════════
   ALERT STRIP
══════════════════════════════════════════════ */
.alert-strip {{
    background: rgba(255,50,70,0.12);
    border: 1px solid rgba(255,90,110,0.38);
    backdrop-filter: blur(22px); border-radius:14px;
    padding:14px 20px; margin-bottom:10px;
    display:flex; align-items:center; gap:12px;
}}

/* ══════════════════════════════════════════════
   BADGES
══════════════════════════════════════════════ */
.badge {{
    display:inline-block; padding:3px 11px; border-radius:999px;
    font-weight:700; font-size:11px; letter-spacing:0.03em; margin:3px 4px 7px 0;
}}
.badge-red    {{ background:rgba(255,80,100,0.18); border:1px solid rgba(255,120,140,0.45); color:#ffd6dd; }}
.badge-white  {{ background:rgba(255,255,255,0.11); border:1px solid rgba(255,255,255,0.26); color:rgba(255,255,255,0.85); }}
.badge-green  {{ background:rgba(52,211,153,0.14); border:1px solid rgba(52,211,153,0.36); color:#a7f3d0; }}
.badge-orange {{ background:rgba(251,146,60,0.16); border:1px solid rgba(251,146,60,0.38); color:#fed7aa; }}
.badge-blue   {{ background:rgba(96,165,250,0.14); border:1px solid rgba(96,165,250,0.36); color:#bfdbfe; }}

/* ══════════════════════════════════════════════
   META / LABELS
══════════════════════════════════════════════ */
.meta {{ color:rgba(255,255,255,0.62); font-size:13px; line-height:1.7; margin:1px 0; }}
.section-label {{
    font-size:10px; font-weight:700; letter-spacing:0.12em;
    text-transform:uppercase; color:rgba(255,255,255,0.38);
    margin:24px 0 10px 0;
}}

/* ══════════════════════════════════════════════
   MAIN CONTENT BUTTONS
══════════════════════════════════════════════ */
.main-area .stButton > button,
.stLinkButton > a {{
    background: rgba(255,255,255,0.09) !important;
    border: 1px solid rgba(255,255,255,0.20) !important;
    color: rgba(255,255,255,0.80) !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    padding: 6px 14px !important;
    box-shadow: none !important;
    transition: all 0.14s ease !important;
}}
.stLinkButton > a:hover {{
    background: rgba(255,255,255,0.16) !important;
    color: #fff !important;
}}

/* ══════════════════════════════════════════════
   PROGRESS BAR (main area)
══════════════════════════════════════════════ */
[data-testid="stProgress"] > div > div {{
    background: linear-gradient(90deg,#AB0520,#ff8fa3) !important;
    border-radius:999px !important;
}}
[data-testid="stProgress"] {{
    background: rgba(255,255,255,0.09) !important; border-radius:999px !important;
}}

/* ══════════════════════════════════════════════
   MISC
══════════════════════════════════════════════ */
hr {{ border-color:rgba(255,255,255,0.08) !important; margin:16px 0 !important; }}

[data-testid="stTextInput"] input {{
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.18) !important;
    color: #fff !important; border-radius:12px !important;
}}

[data-testid="stSelectbox"] > div > div {{
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.18) !important;
    border-radius:12px !important; color:#fff !important;
}}

[data-testid="stDataFrame"] {{
    background: rgba(255,255,255,0.05) !important;
    border-radius:14px !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
}}

[data-testid="stAlert"] {{
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.14) !important;
    border-radius: 14px !important; color:#fff !important;
}}

@media screen and (max-width:768px) {{
    .acard-title {{ font-size:15px; }}
    .meta {{ font-size:12px; }}
    [data-testid="stMetricValue"] {{ font-size:20px !important; }}
}}
</style>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────────
def parse_due(raw):
    if not raw: return None
    raw = raw.strip()
    for fmt in ["%b %d at %I:%M%p","%b %d at %I:%M %p","%B %d at %I:%M%p","%B %d at %I:%M %p"]:
        try: return datetime.strptime(raw + f" {datetime.now().year}", fmt + " %Y")
        except ValueError: pass
    return None

def countdown_text(due):
    if not due: return "No date"
    diff = due - datetime.now()
    if diff.total_seconds() < 0: return "Past due"
    d, s = diff.days, diff.seconds
    h, m = s // 3600, (s % 3600) // 60
    if d > 0:  return f"{d}d {h}h {m}m"
    if h > 0:  return f"{h}h {m}m"
    return f"{m}m"

def safe_name(t): return t.split("\n")[0].strip() if t else ""

def urgency(due):
    if not due: return "badge-white", "No date"
    secs = (due - datetime.now()).total_seconds()
    if secs < 0:          return "badge-red",    "Past due"
    if secs < 86400:      return "badge-red",    f"⚠️ {countdown_text(due)}"
    if secs < 86400 * 3:  return "badge-orange", f"⏳ {countdown_text(due)}"
    return "badge-green", f"✅ {countdown_text(due)}"

def load_assignments():
    with st.spinner("Syncing with Gradescope..."):
        raw = asyncio.run(get_all_assignments())
    out = []
    for a in raw:
        due = parse_due(a.get("due_date_raw",""))
        a["due_dt"]       = due
        a["course_clean"] = safe_name(a.get("course_short","Course"))
        a["done"]         = "submitted" in (a.get("status","")).lower()
        out.append(a)
    return sorted(out, key=lambda x: x["due_dt"] or datetime.max)


# ── Session state ──────────────────────────────────────────────────────────────
for key, val in [("assignments",[]),("page","Dashboard"),("search",""),
                 ("pinned",set()),("notes",{})]:
    if key not in st.session_state:
        st.session_state[key] = val


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    # Logo tile
    st.markdown("""
    <div style="width:64px;height:64px;border-radius:18px;
                background:rgba(171,5,32,0.22);border:1px solid rgba(171,5,32,0.50);
                display:flex;flex-direction:column;align-items:center;justify-content:center;
                font-size:28px;margin:8px auto 10px auto;line-height:1;">
        📚
    </div>
    """, unsafe_allow_html=True)

    # Sync button
    st.markdown('<div class="sync-btn">', unsafe_allow_html=True)
    if st.button("🔄\nSync", key="sync_gradescope_main", use_container_width=False):
        st.session_state.assignments = load_assignments()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='width:64px;margin:6px auto;border-top:0.5px solid rgba(255,255,255,0.08);'></div>",
                unsafe_allow_html=True)

    # Nav pages — emoji + short label
    pages = [
        ("🏠", "Dashboard",   "Home"),
        ("📋", "Assignments", "Tasks"),
        ("📅", "Calendar",    "Cal"),
        ("📊", "Analytics",   "Stats"),
        ("📌", "Pinned",      "Pinned"),
        ("🗒️", "Notes",       "Notes"),
    ]

    for icon, name, short in pages:
        is_active = st.session_state.page == name
        btn_type  = "primary" if is_active else "secondary"
        if st.button(f"{icon}\n{short}", key=f"nav_{name}", use_container_width=False, type=btn_type):
            st.session_state.page = name
            st.rerun()

    st.markdown("<div style='width:64px;margin:6px auto;border-top:0.5px solid rgba(255,255,255,0.08);'></div>",
                unsafe_allow_html=True)

    # Progress
    n    = len(st.session_state.assignments)
    done = sum(1 for a in st.session_state.assignments if a.get("done"))
    if n:
        pct = round(done / n * 100)
        st.progress(pct / 100)
        st.markdown(
            f"<div style='font-size:9px;color:rgba(255,255,255,0.28);text-align:center;margin-top:4px;'>"
            f"{pct}%</div>",
            unsafe_allow_html=True
        )

    # Dark mode toggle
    prev_dark = st.session_state.dark
    new_dark  = st.toggle("🌙 Dark", value=st.session_state.dark, key="dark_toggle")
    if new_dark != prev_dark:
        st.session_state.dark = new_dark
        st.rerun()


# ── Shared vars ────────────────────────────────────────────────────────────────
assignments = st.session_state.assignments
now         = datetime.now()
due_week    = [a for a in assignments if a.get("due_dt") and 0 <= (a["due_dt"]-now).days <= 7]
due_24h     = [a for a in assignments if a.get("due_dt") and timedelta(0) <= (a["due_dt"]-now) <= timedelta(hours=24)]
past_due    = [a for a in assignments if a.get("due_dt") and a["due_dt"] < now]
pinned_ids  = st.session_state.pinned


# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "Dashboard":
    st.markdown('<div class="page-title">🏠 Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Your full assignment overview</div>', unsafe_allow_html=True)

    if not assignments:
        st.markdown("""
        <div class="glass" style="text-align:center;padding:56px 32px;">
            <div style="font-size:48px;margin-bottom:14px;">📭</div>
            <div style="font-size:19px;font-weight:700;margin-bottom:6px;">Nothing loaded yet</div>
            <div style="color:rgba(255,255,255,0.45);font-size:14px;">
                Hit <b>🔄</b> in the sidebar to sync your assignments.
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        c1,c2,c3,c4,c5 = st.columns(5)
        with c1: st.metric("Total",         len(assignments))
        with c2: st.metric("Due This Week",  len(due_week))
        with c3: st.metric("Due in 24h",     len(due_24h))
        with c4: st.metric("Past Due",       len(past_due))
        with c5: st.metric("Submitted",      sum(1 for a in assignments if a.get("done")))

        if due_24h:
            st.markdown('<div class="section-label">🚨 Urgent — due in 24 hours</div>', unsafe_allow_html=True)
            for a in due_24h:
                st.markdown(f"""
                <div class="alert-strip">
                    <span style="font-size:24px;">⚠️</span>
                    <div style="flex:1;">
                        <div style="font-weight:800;font-size:15px;">{a["name"]}</div>
                        <div class="meta">📚 {a["course_clean"]} · 📅 {a["due_date_raw"]}</div>
                    </div>
                    <span class="badge badge-red">{countdown_text(a["due_dt"])}</span>
                </div>""", unsafe_allow_html=True)

        if past_due:
            st.markdown('<div class="section-label">❌ Past due</div>', unsafe_allow_html=True)
            for a in past_due:
                st.markdown(f"""
                <div class="acard acard-urgent" style="opacity:0.7;">
                    <div class="acard-title">{a["name"]}</div>
                    <span class="badge badge-red">Past due</span>
                    <div class="meta">📚 {a["course_clean"]} · 📅 {a["due_date_raw"]}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown('<div class="section-label">📅 Due this week</div>', unsafe_allow_html=True)
        if due_week:
            cols = st.columns(min(len(due_week), 3))
            for i, a in enumerate(due_week[:6]):
                bc, bt = urgency(a["due_dt"])
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class="acard">
                        <div class="acard-title">{a["name"]}</div>
                        <span class="badge {bc}">{bt}</span>
                        <div class="meta">📚 {a["course_clean"]}</div>
                        <div class="meta">📅 {a["due_date_raw"]}</div>
                    </div>""", unsafe_allow_html=True)
        else:
            st.info("Nothing due this week. You're all caught up! 🎉")


# ══════════════════════════════════════════════════════════════════════════════
# ASSIGNMENTS
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "Assignments":
    st.markdown('<div class="page-title">📋 Assignments</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">All open assignments with search and filters</div>', unsafe_allow_html=True)

    if not assignments:
        st.info("Hit 🔄 in the sidebar to sync.")
    else:
        col_s, col_c, col_sort, col_hide = st.columns([3,2,2,1])
        with col_s:
            search = st.text_input("🔍 Search", placeholder="Search assignment name...", label_visibility="collapsed")
        with col_c:
            courses = ["All courses"] + sorted(set(a["course_clean"] for a in assignments))
            course_filter = st.selectbox("Course", courses, label_visibility="collapsed")
        with col_sort:
            sort_by = st.selectbox("Sort", ["Due date","Course","Name"], label_visibility="collapsed")
        with col_hide:
            hide_done = st.checkbox("Hide done", value=False)

        filtered = assignments[:]
        if search:
            filtered = [a for a in filtered if search.lower() in a["name"].lower()]
        if course_filter != "All courses":
            filtered = [a for a in filtered if a["course_clean"] == course_filter]
        if hide_done:
            filtered = [a for a in filtered if not a.get("done")]
        if sort_by == "Course": filtered.sort(key=lambda x: x["course_clean"])
        if sort_by == "Name":   filtered.sort(key=lambda x: x["name"])

        st.markdown(f'<div class="section-label">{len(filtered)} assignments</div>', unsafe_allow_html=True)

        for a in filtered:
            bc, bt     = urgency(a["due_dt"])
            urgent_cls = "acard-urgent" if a in due_24h else ""
            done_cls   = "acard-done"   if a.get("done") else ""
            pin_icon   = "📌" if id(a) in pinned_ids else "📍"

            st.markdown(f"""
            <div class="acard {urgent_cls} {done_cls}">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:6px;">
                    <div class="acard-title">{a["name"]}</div>
                    <span class="badge {bc}">{bt}</span>
                </div>
                <div class="meta">📚 <b>{a["course_clean"]}</b></div>
                <div class="meta">📅 Due: {a["due_date_raw"] or "No date"}</div>
                <div class="meta">✅ Status: {a.get("status","Unknown")}</div>
            </div>""", unsafe_allow_html=True)

            col_btn1, col_btn2, col_btn3, _ = st.columns([1,1,1,5])
            with col_btn1:
                if a.get("link"):
                    st.link_button("Open →", a["link"])
            with col_btn2:
                if st.button(f"{pin_icon} Pin", key=f"pin_{id(a)}"):
                    if id(a) in st.session_state.pinned:
                        st.session_state.pinned.discard(id(a))
                    else:
                        st.session_state.pinned.add(id(a))
                    st.rerun()
            with col_btn3:
                if st.button("🗒️ Note", key=f"note_btn_{id(a)}"):
                    st.session_state[f"show_note_{id(a)}"] = not st.session_state.get(f"show_note_{id(a)}", False)
                    st.rerun()

            if st.session_state.get(f"show_note_{id(a)}", False):
                note = st.text_area("Your note", value=st.session_state.notes.get(id(a),""),
                                    key=f"note_area_{id(a)}", height=80)
                st.session_state.notes[id(a)] = note


# ══════════════════════════════════════════════════════════════════════════════
# CALENDAR
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "Calendar":
    st.markdown('<div class="page-title">📅 Calendar</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Assignments grouped by day</div>', unsafe_allow_html=True)

    if not assignments:
        st.info("Hit 🔄 in the sidebar to sync.")
    else:
        dated   = [a for a in assignments if a.get("due_dt")]
        no_date = [a for a in assignments if not a.get("due_dt")]

        groups = defaultdict(list)
        for a in dated:
            groups[a["due_dt"].date()].append(a)

        for day in sorted(groups):
            items    = groups[day]
            is_today = day == now.date()
            is_tmrw  = day == (now + timedelta(days=1)).date()
            tag      = ("TODAY" if is_today else "TOMORROW" if is_tmrw else "")
            tag_html = f'<span class="badge badge-red" style="margin-left:10px;">{tag}</span>' if tag else ""
            day_label = datetime.combine(day, datetime.min.time()).strftime("%A, %B %d")

            st.markdown(f"""
            <div style="font-size:16px;font-weight:800;color:#fff;margin:26px 0 10px 0;
                        display:flex;align-items:center;">
                📆 {day_label} {tag_html}
            </div>""", unsafe_allow_html=True)

            cols = st.columns(min(len(items), 3))
            for i, a in enumerate(items):
                bc, bt = urgency(a["due_dt"])
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class="acard">
                        <div style="font-size:11px;color:rgba(255,255,255,0.42);font-weight:700;
                                    letter-spacing:0.07em;text-transform:uppercase;margin-bottom:5px;">
                            {a["due_dt"].strftime("%I:%M %p")}
                        </div>
                        <div class="acard-title">{a["name"]}</div>
                        <span class="badge {bc}">{bt}</span>
                        <div class="meta">📚 {a["course_clean"]}</div>
                    </div>""", unsafe_allow_html=True)

        if no_date:
            st.markdown('<div class="section-label">No due date</div>', unsafe_allow_html=True)
            for a in no_date:
                st.markdown(f"""
                <div class="acard">
                    <div class="acard-title">{a["name"]}</div>
                    <div class="meta">📚 {a["course_clean"]}</div>
                </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# ANALYTICS
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "Analytics":
    st.markdown('<div class="page-title">📊 Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Workload breakdown and deadline trends</div>', unsafe_allow_html=True)

    if not assignments:
        st.info("Hit 🔄 in the sidebar to sync.")
    else:
        ca, cb = st.columns(2)

        with ca:
            st.markdown('<div class="section-label">Assignments per course</div>', unsafe_allow_html=True)
            df1 = (pd.DataFrame([{"Course": a["course_clean"]} for a in assignments])
                   .groupby("Course").size().reset_index(name="Count"))
            c1 = alt.Chart(df1).mark_bar(cornerRadiusTopLeft=7,cornerRadiusTopRight=7,color="#c0392b"
                ).encode(
                    x=alt.X("Course:N", axis=alt.Axis(labelColor="#aaa",titleColor="#aaa",labelAngle=-20)),
                    y=alt.Y("Count:Q",  axis=alt.Axis(labelColor="#aaa",titleColor="#aaa")),
                    tooltip=["Course","Count"]
                ).properties(height=240).configure_view(fill="transparent").configure(background="transparent")
            st.altair_chart(c1, use_container_width=True)

        with cb:
            st.markdown('<div class="section-label">Deadlines — next 14 days</div>', unsafe_allow_html=True)
            df2 = pd.DataFrame([
                {"Day": a["due_dt"].strftime("%b %d"), "Count": 1}
                for a in assignments if a.get("due_dt") and 0 <= (a["due_dt"]-now).days <= 14
            ])
            if not df2.empty:
                df2 = df2.groupby("Day").sum().reset_index()
                c2 = alt.Chart(df2).mark_bar(cornerRadiusTopLeft=6,cornerRadiusTopRight=6,color="#e07b7b"
                    ).encode(
                        x=alt.X("Day:N", axis=alt.Axis(labelColor="#aaa",titleColor="#aaa",labelAngle=-20)),
                        y=alt.Y("Count:Q", axis=alt.Axis(labelColor="#aaa",titleColor="#aaa")),
                        tooltip=["Day","Count"]
                    ).properties(height=240).configure_view(fill="transparent").configure(background="transparent")
                st.altair_chart(c2, use_container_width=True)
            else:
                st.info("No assignments in the next 14 days.")

        st.markdown('<div class="section-label">Workload summary</div>', unsafe_allow_html=True)
        rows = []
        for course in sorted(set(a["course_clean"] for a in assignments)):
            ci = [a for a in assignments if a["course_clean"] == course]
            rows.append({
                "Course":     course,
                "Total open": len(ci),
                "This week":  sum(1 for a in ci if a in due_week),
                "Due in 24h": sum(1 for a in ci if a in due_24h),
                "Submitted":  sum(1 for a in ci if a.get("done")),
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# PINNED
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "Pinned":
    st.markdown('<div class="page-title">📌 Pinned</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Assignments you flagged for quick access</div>', unsafe_allow_html=True)

    pinned = [a for a in assignments if id(a) in pinned_ids]
    if not pinned:
        st.markdown("""
        <div class="glass" style="text-align:center;padding:48px 32px;">
            <div style="font-size:40px;margin-bottom:12px;">📍</div>
            <div style="font-size:17px;font-weight:700;margin-bottom:6px;">No pinned assignments</div>
            <div style="color:rgba(255,255,255,0.45);font-size:13px;">
                Go to Assignments and click 📍 Pin on any assignment.
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        for a in pinned:
            bc, bt = urgency(a["due_dt"])
            st.markdown(f"""
            <div class="acard">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:6px;">
                    <div class="acard-title">📌 {a["name"]}</div>
                    <span class="badge {bc}">{bt}</span>
                </div>
                <div class="meta">📚 {a["course_clean"]}</div>
                <div class="meta">📅 {a["due_date_raw"] or "No date"}</div>
            </div>""", unsafe_allow_html=True)
            col1, col2, _ = st.columns([1,1,6])
            with col1:
                if a.get("link"): st.link_button("Open →", a["link"])
            with col2:
                if st.button("Unpin", key=f"unpin_{id(a)}"):
                    st.session_state.pinned.discard(id(a))
                    st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# NOTES
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "Notes":
    st.markdown('<div class="page-title">🗒️ Notes</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Your notes for each assignment, all in one place</div>', unsafe_allow_html=True)

    noted          = {aid: note for aid, note in st.session_state.notes.items() if note.strip()}
    id_to_assignment = {id(a): a for a in assignments}

    if not noted:
        st.markdown("""
        <div class="glass" style="text-align:center;padding:48px 32px;">
            <div style="font-size:40px;margin-bottom:12px;">🗒️</div>
            <div style="font-size:17px;font-weight:700;margin-bottom:6px;">No notes yet</div>
            <div style="color:rgba(255,255,255,0.45);font-size:13px;">
                Go to Assignments and click 🗒️ Note on any assignment.
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        for aid, note in noted.items():
            a = id_to_assignment.get(aid)
            if not a: continue
            bc, bt = urgency(a["due_dt"])
            st.markdown(f"""
            <div class="acard">
                <div class="acard-title">🗒️ {a["name"]}</div>
                <span class="badge {bc}">{bt}</span>
                <div class="meta">📚 {a["course_clean"]} · 📅 {a["due_date_raw"] or "No date"}</div>
                <div style="margin-top:10px;padding:12px 14px;background:rgba(255,255,255,0.07);
                            border-radius:10px;font-size:14px;color:rgba(255,255,255,0.82);
                            line-height:1.6;white-space:pre-wrap;">{note}</div>
            </div>""", unsafe_allow_html=True)