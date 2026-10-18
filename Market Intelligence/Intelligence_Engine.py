import os
import re
import json
import sqlite3
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

DATABASE_FILE = "intelligence.db"
INPUT_FILE = "news_articles.csv"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "")


# =========================================================
# DATABASE
# =========================================================

def initialize_database():

    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS intelligence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT,
            title TEXT,
            url TEXT UNIQUE,
            article_text TEXT,
            relevant INTEGER,
            primary_theme TEXT,
            secondary_themes TEXT,
            business_area TEXT,
            maturity TEXT,
            significance TEXT,
            technology TEXT,
            partners TEXT,
            summary TEXT,
            why_it_matters TEXT,
            analysis_mode TEXT,
            analyzed_at TEXT
        )
    """)

    conn.commit()

    # Add analysis_mode if using an older database
    cursor.execute(
        "PRAGMA table_info(intelligence)"
    )

    columns = [
        row[1]
        for row in cursor.fetchall()
    ]

    if "analysis_mode" not in columns:

        cursor.execute(
            """
            ALTER TABLE intelligence
            ADD COLUMN analysis_mode TEXT
            """
        )

    conn.commit()
    conn.close()


# =========================================================
# ALREADY PROCESSED?
# =========================================================

def already_analyzed(url):

    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id
        FROM intelligence
        WHERE url = ?
        """,
        (url,)
    )

    result = cursor.fetchone()

    conn.close()

    return result is not None


# =========================================================
# ARTICLE RETRIEVAL
# =========================================================

def fetch_article_text(url):

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64)"
        )
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=20
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    for tag in soup([
        "script",
        "style",
        "nav",
        "footer",
        "header",
        "form",
        "aside"
    ]):
        tag.decompose()

    paragraphs = []

    for tag in soup.find_all(
        ["h1", "h2", "h3", "p"]
    ):

        text = tag.get_text(
            " ",
            strip=True
        )

        if len(text) > 30:
            paragraphs.append(text)

    return " ".join(paragraphs)[:15000]


# =========================================================
# RULE-BASED FALLBACK ANALYZER
# =========================================================

def analyze_with_rules(
    company,
    title,
    article_text
):

    text = (
        title + " " + article_text
    ).lower()

    themes = []

    theme_rules = {

        "AGENTIC_AI": [
            "agentic ai",
            "ai agent",
            "ai agents"
        ],

        "GENERATIVE_AI": [
            "generative ai",
            "genai",
            "large language model",
            "llm",
            "copilot"
        ],

        "AI_ML": [
            "artificial intelligence",
            "machine learning",
            "predictive analytics",
            "ai-powered"
        ],

        "AUTONOMOUS_OPERATIONS": [
            "autonomous operations",
            "autonomous control",
            "closed-loop",
            "remote operations"
        ],

        "ROBOTICS": [
            "robot",
            "robotics",
            "robotic"
        ],

        "DRONES": [
            "drone",
            "drones",
            "uav"
        ],

        "DIGITAL_TWIN": [
            "digital twin",
            "digital twins"
        ],

        "COMPUTER_VISION": [
            "computer vision",
            "visual inspection"
        ],

        "DATA_CLOUD": [
            "data platform",
            "cloud",
            "industrial data",
            "edge computing"
        ],

        "TECHNOLOGY_STRATEGY": [
            "digital transformation",
            "technology strategy",
            "strategic partnership"
        ]
    }

    for theme, keywords in theme_rules.items():

        if any(
            keyword in text
            for keyword in keywords
        ):
            themes.append(theme)

    relevant = len(themes) > 0

    primary_theme = (
        themes[0]
        if themes
        else "OTHER"
    )

    secondary_themes = (
        themes[1:]
        if len(themes) > 1
        else []
    )


    # =====================================================
    # MATURITY
    # =====================================================

    if any(word in text for word in [
        "enterprise-wide",
        "enterprise wide",
        "across the company",
        "company-wide"
    ]):

        maturity = "ENTERPRISE_ADOPTION"

    elif any(word in text for word in [
        "scaled",
        "scale-up",
        "rollout",
        "across multiple",
        "expanded deployment"
    ]):

        maturity = "SCALE_UP"

    elif any(word in text for word in [
        "deployed",
        "deployment",
        "operational",
        "implemented"
    ]):

        maturity = "DEPLOYMENT"

    elif any(word in text for word in [
        "pilot",
        "trial",
        "proof of concept",
        "poc"
    ]):

        maturity = "PILOT"

    elif any(word in text for word in [
        "developing",
        "development",
        "build",
        "building"
    ]):

        maturity = "DEVELOPMENT"

    elif any(word in text for word in [
        "partnership",
        "collaboration",
        "agreement",
        "memorandum",
        "mou"
    ]):

        maturity = "PARTNERSHIP"

    elif any(word in text for word in [
        "announced",
        "launches",
        "launched",
        "introduces"
    ]):

        maturity = "ANNOUNCEMENT"

    else:

        maturity = "UNKNOWN"


    # =====================================================
    # BUSINESS AREA
    # =====================================================

    business_area = []

    area_rules = {

        "Upstream": [
            "upstream",
            "subsurface",
            "reservoir",
            "drilling",
            "well"
        ],

        "Production": [
            "production",
            "operations"
        ],

        "Maintenance": [
            "maintenance",
            "asset integrity",
            "inspection"
        ],

        "Processing": [
            "gas processing",
            "refinery",
            "processing plant"
        ],

        "Supply Chain": [
            "supply chain",
            "logistics"
        ]
    }

    for area, keywords in area_rules.items():

        if any(
            keyword in text
            for keyword in keywords
        ):
            business_area.append(area)


    # =====================================================
    # SIGNIFICANCE
    # =====================================================

    score = 0

    if "AGENTIC_AI" in themes:
        score += 3

    if "AUTONOMOUS_OPERATIONS" in themes:
        score += 3

    if "ROBOTICS" in themes:
        score += 2

    if maturity in [
        "DEPLOYMENT",
        "SCALE_UP",
        "ENTERPRISE_ADOPTION"
    ]:
        score += 3

    elif maturity == "PILOT":
        score += 2

    elif maturity == "PARTNERSHIP":
        score += 1

    if score >= 5:
        significance = "HIGH"

    elif score >= 2:
        significance = "MEDIUM"

    else:
        significance = "LOW"


    # =====================================================
    # SIMPLE SUMMARY
    # =====================================================

    summary = (
        f"{company} reported a technology development "
        f"related to {primary_theme.replace('_', ' ').title()}."
    )

    why_it_matters = (
        f"The development is classified as {maturity} "
        f"and has {significance.lower()} strategic significance."
    )


    return {

        "relevant":
            relevant,

        "primary_theme":
            primary_theme,

        "secondary_themes":
            secondary_themes,

        "business_area":
            business_area,

        "maturity":
            maturity,

        "significance":
            significance,

        "technology":
            primary_theme.replace(
                "_",
                " "
            ).title(),

        "partners":
            [],

        "summary":
            summary,

        "why_it_matters":
            why_it_matters,

        "analysis_mode":
            "RULE_BASED"
    }


# =========================================================
# OPTIONAL LLM ANALYZER
# =========================================================

def analyze_with_llm(
    company,
    title,
    article_text
):

    if (
        not OPENAI_API_KEY
        or not OPENAI_MODEL
    ):

        raise RuntimeError(
            "LLM configuration not available"
        )

    from openai import OpenAI

    client = OpenAI(
        api_key=OPENAI_API_KEY
    )

    prompt = f"""
You are an oil and gas technology intelligence analyst.

Company:
{company}

Title:
{title}

Article:
{article_text}

Analyze the development.

Return ONLY valid JSON:

{{
    "relevant": true,
    "primary_theme": "",
    "secondary_themes": [],
    "business_area": [],
    "maturity": "",
    "significance": "",
    "technology": "",
    "partners": [],
    "summary": "",
    "why_it_matters": ""
}}

Maturity must be one of:

ANNOUNCEMENT
PARTNERSHIP
DEVELOPMENT
PILOT
DEPLOYMENT
SCALE_UP
ENTERPRISE_ADOPTION
UNKNOWN

Significance must be:

LOW
MEDIUM
HIGH

Do not invent information.
"""

    response = client.responses.create(
        model=OPENAI_MODEL,
        input=prompt
    )

    text = response.output_text.strip()

    text = re.sub(
        r"^```json",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"```$",
        "",
        text
    )

    analysis = json.loads(
        text.strip()
    )

    analysis[
        "analysis_mode"
    ] = "LLM"

    return analysis


# =========================================================
# HYBRID ANALYZER
# =========================================================

def analyze_article(
    company,
    title,
    article_text
):

    try:

        print(
            "Trying GenAI analysis..."
        )

        analysis = analyze_with_llm(
            company,
            title,
            article_text
        )

        print(
            "LLM analysis successful."
        )

        return analysis

    except Exception as e:

        print(
            "LLM unavailable:"
        )

        print(
            str(e)
        )

        print(
            "Using rule-based fallback..."
        )

        return analyze_with_rules(
            company,
            title,
            article_text
        )


# =========================================================
# SAVE TO SQLITE
# =========================================================

def save_to_database(
    company,
    title,
    url,
    article_text,
    analysis
):

    conn = sqlite3.connect(
        DATABASE_FILE
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR REPLACE INTO intelligence (

            company,
            title,
            url,
            article_text,
            relevant,
            primary_theme,
            secondary_themes,
            business_area,
            maturity,
            significance,
            technology,
            partners,
            summary,
            why_it_matters,
            analysis_mode,
            analyzed_at

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,

        (
            company,
            title,
            url,
            article_text,

            int(
                analysis.get(
                    "relevant",
                    False
                )
            ),

            analysis.get(
                "primary_theme",
                ""
            ),

            json.dumps(
                analysis.get(
                    "secondary_themes",
                    []
                )
            ),

            json.dumps(
                analysis.get(
                    "business_area",
                    []
                )
            ),

            analysis.get(
                "maturity",
                "UNKNOWN"
            ),

            analysis.get(
                "significance",
                "LOW"
            ),

            analysis.get(
                "technology",
                ""
            ),

            json.dumps(
                analysis.get(
                    "partners",
                    []
                )
            ),

            analysis.get(
                "summary",
                ""
            ),

            analysis.get(
                "why_it_matters",
                ""
            ),

            analysis.get(
                "analysis_mode",
                "UNKNOWN"
            ),

            datetime.now().isoformat(
                timespec="seconds"
            )
        )
    )

    conn.commit()
    conn.close()


# =========================================================
# PROCESS ARTICLES
# =========================================================

def process_articles():

    initialize_database()

    articles = pd.read_csv(
        INPUT_FILE
    )

    print(
        f"\nLoaded {len(articles)} candidate items."
    )

    for index, row in articles.iterrows():

        company = str(
            row["company"]
        )

        title = str(
            row["title"]
        )

        url = str(
            row["url"]
        )

        print(
            "\n=================================="
        )

        print(
            f"[{index + 1}/{len(articles)}]"
        )

        print(company)

        print(
            title[:150]
        )

        if already_analyzed(url):

            print(
                "Already analyzed - skipping."
            )

            continue

        try:

            print(
                "Fetching article..."
            )

            article_text = fetch_article_text(
                url
            )

            if len(article_text) < 100:

                print(
                    "Insufficient content."
                )

                continue

            analysis = analyze_article(
                company,
                title,
                article_text
            )

            print(
                "Theme:",
                analysis["primary_theme"]
            )

            print(
                "Maturity:",
                analysis["maturity"]
            )

            print(
                "Significance:",
                analysis["significance"]
            )

            print(
                "Analysis mode:",
                analysis["analysis_mode"]
            )

            save_to_database(
                company,
                title,
                url,
                article_text,
                analysis
            )

            print(
                "Saved to database."
            )

        except Exception as e:

            print(
                "FAILED:",
                e
            )


# =========================================================
# DATABASE SUMMARY
# =========================================================

def show_summary():

    conn = sqlite3.connect(
        DATABASE_FILE
    )

    df = pd.read_sql_query(
        """
        SELECT

            company,
            title,
            primary_theme,
            maturity,
            significance,
            analysis_mode,
            summary

        FROM intelligence

        WHERE relevant = 1

        ORDER BY

        CASE significance

            WHEN 'HIGH'
                THEN 3

            WHEN 'MEDIUM'
                THEN 2

            ELSE 1

        END DESC
        """,
        conn
    )

    conn.close()

    print(
        "\n=================================="
    )

    print(
        "TECHNOLOGY INTELLIGENCE DATABASE"
    )

    print(
        "=================================="
    )

    if df.empty:

        print(
            "No intelligence stored."
        )

    else:

        print(
            df.to_string(
                index=False
            )
        )


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    process_articles()

    show_summary()