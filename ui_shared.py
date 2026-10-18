import streamlit as st


def apply_theme():
    st.markdown(
        """
        <style>
        .stApp { background: linear-gradient(180deg, #f7f9fc 0%, #ffffff 35%); }
        .block-container { max-width: 1280px; padding-top: 1.4rem; padding-bottom: 3rem; }
        h1, h2, h3 { letter-spacing: -0.02em; }
        [data-testid="stMetric"] {
            background: white;
            border: 1px solid #e7ebf2;
            padding: 14px 16px;
            border-radius: 14px;
            box-shadow: 0 3px 14px rgba(15, 23, 42, 0.04);
        }
        [data-testid="stSidebar"] { border-right: 1px solid #e7ebf2; }
        .hero {
            padding: 30px 34px;
            border-radius: 20px;
            background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 58%, #0f766e 100%);
            color: white;
            margin-bottom: 22px;
            box-shadow: 0 12px 34px rgba(15, 23, 42, 0.16);
        }
        .hero h1 { color: white; margin: 0 0 8px 0; font-size: 2.25rem; }
        .hero p { color: #dbeafe; margin: 0; font-size: 1.03rem; max-width: 900px; }
        .eyebrow {
            display: inline-block;
            font-size: 0.76rem;
            font-weight: 700;
            letter-spacing: .08em;
            text-transform: uppercase;
            color: #a7f3d0;
            margin-bottom: 10px;
        }
        .module-card {
            background: white;
            border: 1px solid #e7ebf2;
            border-radius: 16px;
            padding: 20px;
            min-height: 178px;
            box-shadow: 0 5px 18px rgba(15, 23, 42, 0.05);
            margin-bottom: 12px;
        }
        .module-card h3 { margin-top: 0; margin-bottom: 8px; font-size: 1.15rem; }
        .module-card p { color: #475569; margin-bottom: 14px; }
        .tag {
            display: inline-block;
            padding: 4px 9px;
            margin: 2px 4px 2px 0;
            border-radius: 999px;
            background: #f1f5f9;
            color: #334155;
            font-size: .76rem;
            font-weight: 600;
        }
        .section-label {
            color: #64748b;
            font-size: .78rem;
            font-weight: 700;
            letter-spacing: .07em;
            text-transform: uppercase;
            margin-bottom: 2px;
        }
        .status-dot { font-size: .9rem; }
        .small-note { color: #64748b; font-size: .88rem; }
        div[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def module_header(eyebrow, title, description):
    st.markdown(
        f"""
        <div class="hero">
            <div class="eyebrow">{eyebrow}</div>
            <h1>{title}</h1>
            <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def card(title, body, tags):
    tag_html = "".join(f'<span class="tag">{t}</span>' for t in tags)
    st.markdown(
        f"""
        <div class="module-card">
            <h3>{title}</h3>
            <p>{body}</p>
            <div>{tag_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
