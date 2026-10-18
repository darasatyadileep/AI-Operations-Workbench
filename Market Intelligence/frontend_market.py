import streamlit as st
import requests
import pandas as pd
import json


API_BASE = "http://127.0.0.1:8004"


st.set_page_config(
    page_title="Oil & Gas Technology Intelligence",
    layout="wide"
)


st.title(
    "Oil & Gas Technology Intelligence"
)

st.caption(
    "Agentic market intelligence across major oil & gas "
    "companies — AI, robotics, autonomous operations, "
    "digital twins and emerging technologies."
)


# =========================================================
# LOAD DATA
# =========================================================

try:

    response = requests.get(
        f"{API_BASE}/intelligence",
        timeout=20
    )

    response.raise_for_status()

    data = response.json()

except Exception as e:

    st.error(
        "Unable to connect to the Technology Intelligence API."
    )

    st.code(str(e))

    st.stop()


df = pd.DataFrame(data)


# =========================================================
# EMPTY DATABASE
# =========================================================

if df.empty:

    st.warning(
        "No intelligence items are stored yet."
    )

    st.stop()


# =========================================================
# TOP METRICS
# =========================================================

total_items = len(df)

high_items = (
    df["significance"]
    .eq("HIGH")
    .sum()
)

company_count = (
    df["company"]
    .nunique()
)

theme_count = (
    df["primary_theme"]
    .nunique()
)


c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Intelligence Items",
    total_items
)

c2.metric(
    "High Significance",
    int(high_items)
)

c3.metric(
    "Companies",
    company_count
)

c4.metric(
    "Technology Themes",
    theme_count
)


st.divider()


# =========================================================
# FILTERS
# =========================================================

st.subheader(
    "Intelligence Explorer"
)

f1, f2, f3 = st.columns(3)


companies = sorted(
    df["company"]
    .dropna()
    .unique()
)

themes = sorted(
    df["primary_theme"]
    .dropna()
    .unique()
)

significance_options = [
    "HIGH",
    "MEDIUM",
    "LOW"
]


with f1:

    company_filter = st.multiselect(
        "Company",
        companies
    )


with f2:

    theme_filter = st.multiselect(
        "Technology Theme",
        themes
    )


with f3:

    significance_filter = (
        st.multiselect(
            "Significance",
            significance_options
        )
    )


filtered = df.copy()


if company_filter:

    filtered = filtered[
        filtered["company"]
        .isin(company_filter)
    ]


if theme_filter:

    filtered = filtered[
        filtered["primary_theme"]
        .isin(theme_filter)
    ]


if significance_filter:

    filtered = filtered[
        filtered["significance"]
        .isin(significance_filter)
    ]


# =========================================================
# EXECUTIVE VIEW
# =========================================================

st.subheader(
    "Executive Intelligence"
)


significance_order = {
    "HIGH": 3,
    "MEDIUM": 2,
    "LOW": 1
}


filtered["importance"] = (
    filtered["significance"]
    .map(significance_order)
    .fillna(0)
)


executive_df = (
    filtered
    .sort_values(
        "importance",
        ascending=False
    )
)


for _, row in executive_df.iterrows():

    with st.container():

        left, right = st.columns(
            [4, 1]
        )

        with left:

            st.markdown(
                f"### {row['company']}"
            )

            st.write(
                row["title"]
            )

        with right:

            st.metric(
                "Significance",
                row["significance"]
            )

        st.write(
            "**Theme:**",
            row["primary_theme"]
        )

        st.write(
            "**Maturity:**",
            row["maturity"]
        )

        if row.get("summary"):

            st.write(
                "**Summary:**",
                row["summary"]
            )

        if row.get(
            "why_it_matters"
        ):

            st.write(
                "**Why it matters:**",
                row["why_it_matters"]
            )

        st.caption(
            "Analysis mode: "
            + str(
                row["analysis_mode"]
            )
        )

        if row.get("url"):

            st.link_button(
                "Open source",
                row["url"]
            )

        st.divider()


# =========================================================
# ANALYTICS
# =========================================================

st.subheader(
    "Industry Signals"
)


chart1, chart2 = st.columns(2)


with chart1:

    st.write(
        "#### Technology Themes"
    )

    theme_counts = (
        filtered[
            "primary_theme"
        ]
        .value_counts()
    )

    st.bar_chart(
        theme_counts
    )


with chart2:

    st.write(
        "#### Maturity"
    )

    maturity_counts = (
        filtered[
            "maturity"
        ]
        .value_counts()
    )

    st.bar_chart(
        maturity_counts
    )


# =========================================================
# COMPANY ACTIVITY
# =========================================================

st.subheader(
    "Company Activity"
)


company_counts = (
    filtered["company"]
    .value_counts()
)

st.bar_chart(
    company_counts
)


# =========================================================
# DATA TABLE
# =========================================================

with st.expander(
    "View Intelligence Database"
):

    columns_to_show = [
        "company",
        "title",
        "primary_theme",
        "maturity",
        "significance",
        "analysis_mode"
    ]

    st.dataframe(
        filtered[
            columns_to_show
        ],
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# ARCHITECTURE / HOW IT WORKS
# =========================================================

with st.expander(
    "How the Technology Intelligence Agent works"
):

    st.markdown(
        """
        **1. Source Registry**  
        Maintains a curated universe of oil & gas companies
        and technology sources.

        **2. Collection**  
        The collector scans registered sources and identifies
        technology-related candidate items.

        **3. Relevance Filtering**  
        Deterministic rules remove unrelated material.

        **4. Intelligence Analysis**  
        A GenAI model can classify the technology, business
        area, maturity, strategic significance and implications.
        When the LLM service is unavailable, the prototype can
        use an explicitly labelled rule-based fallback.

        **5. Persistent Memory**  
        Results are stored in SQLite, creating a historical
        technology-intelligence repository.

        **6. Benchmarking**  
        Stored intelligence can be compared by company,
        technology theme and maturity.

        **7. Executive Interface**  
        The dashboard surfaces the most strategically important
        developments rather than simply displaying news.
        """
    )