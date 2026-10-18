import pandas as pd
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin


# =========================================================
# 1. TECHNOLOGY TAXONOMY
# =========================================================

TECHNOLOGY_THEMES = {

    "AI_ML": [
        "artificial intelligence",
        "machine learning",
        "predictive analytics",
        "ai-powered",
        "ai driven",
        "ai-driven"
    ],

    "GENERATIVE_AI": [
        "generative ai",
        "genai",
        "large language model",
        "llm",
        "copilot"
    ],

    "AGENTIC_AI": [
        "agentic ai",
        "ai agent",
        "ai agents",
        "autonomous agent"
    ],

    "AUTONOMOUS_OPERATIONS": [
        "autonomous operations",
        "autonomous control",
        "closed-loop optimization",
        "closed loop optimization",
        "remote operations"
    ],

    "ROBOTICS": [
        "robot",
        "robots",
        "robotics",
        "robotic inspection"
    ],

    "DRONES": [
        "drone",
        "drones",
        "uav",
        "unmanned aerial"
    ],

    "COMPUTER_VISION": [
        "computer vision",
        "image recognition",
        "visual inspection"
    ],

    "DIGITAL_TWIN": [
        "digital twin",
        "digital twins"
    ],

    "DATA_CLOUD": [
        "cloud",
        "data platform",
        "industrial data",
        "edge computing",
        "data solution"
    ],

    "TECHNOLOGY_STRATEGY": [
        "digital transformation",
        "technology strategy",
        "strategic technology partnership",
        "ai strategy"
    ]
}


# =========================================================
# 2. DETECT TECHNOLOGY THEMES
# =========================================================

def detect_themes(text):

    text_lower = text.lower()

    matched_themes = []

    for theme, keywords in TECHNOLOGY_THEMES.items():

        for keyword in keywords:

            if keyword.lower() in text_lower:

                matched_themes.append(theme)
                break

    return matched_themes


# =========================================================
# 3. CLASSIFY CONTENT TYPE
# =========================================================

def classify_content_type(title, url):

    combined = f"{title} {url}".lower()

    news_keywords = [
        "news",
        "press",
        "release",
        "announces",
        "announced",
        "launches",
        "launched",
        "deploys",
        "deployed",
        "deployment",
        "partnership",
        "collaboration",
        "agreement",
        "signs",
        "signed",
        "pilot",
        "award",
        "investment",
        "expands",
        "introduces"
    ]

    for keyword in news_keywords:

        if keyword in combined:
            return "NEWS"

    return "EVERGREEN"


# =========================================================
# 4. SIMPLE RELEVANCE SCORE
# =========================================================

def calculate_relevance_score(
    themes,
    content_type
):

    score = 0

    # More technology themes = stronger relevance
    score += len(themes) * 2

    # News developments are more valuable than
    # general service/technology pages
    if content_type == "NEWS":
        score += 3

    # Extra importance for selected themes
    high_value_themes = [
        "AGENTIC_AI",
        "AUTONOMOUS_OPERATIONS",
        "ROBOTICS",
        "GENERATIVE_AI"
    ]

    for theme in themes:

        if theme in high_value_themes:
            score += 2

    return score


# =========================================================
# 5. COLLECT LINKS FROM ONE SOURCE
# =========================================================

def collect_from_source(
    company,
    url
):

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/120 Safari/537.36"
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

    items = []

    for link in soup.find_all(
        "a",
        href=True
    ):

        title = link.get_text(
            " ",
            strip=True
        )

        if not title:
            continue

        # Skip extremely short labels
        if len(title) < 4:
            continue

        href = link.get(
            "href",
            ""
        )

        full_url = urljoin(
            url,
            href
        )

        # Detect themes using both
        # title and URL text
        searchable_text = (
            f"{title} {full_url}"
        )

        themes = detect_themes(
            searchable_text
        )

        if not themes:
            continue

        content_type = classify_content_type(
            title,
            full_url
        )

        relevance_score = (
            calculate_relevance_score(
                themes,
                content_type
            )
        )

        items.append({

            "company":
                company,

            "title":
                title,

            "url":
                full_url,

            "themes":
                ", ".join(themes),

            "content_type":
                content_type,

            "relevance_score":
                relevance_score
        })

    return items


# =========================================================
# 6. COLLECT FROM ALL REGISTERED SOURCES
# =========================================================

def collect_all():

    print(
        "\nLoading source registry..."
    )

    sources = pd.read_csv(
        "source_registry.csv"
    )

    all_items = []

    total_sources = len(sources)

    for index, row in sources.iterrows():

        company = row["company"]
        url = row["url"]

        print(
            f"\n[{index + 1}/{total_sources}] "
            f"Collecting: {company}"
        )

        try:

            items = collect_from_source(
                company,
                url
            )

            all_items.extend(
                items
            )

            print(
                f"Found {len(items)} "
                f"technology-related links"
            )

        except Exception as e:

            print(
                f"FAILED: {e}"
            )

    # Convert to dataframe
    result = pd.DataFrame(
        all_items
    )

    if result.empty:

        print(
            "\nNo relevant articles found."
        )

        return result

    # =====================================================
    # 7. CLEAN RESULTS
    # =====================================================

    # Remove duplicate URLs
    result = result.drop_duplicates(
        subset=["url"]
    )

    # Remove duplicate company/title pairs
    result = result.drop_duplicates(
        subset=[
            "company",
            "title"
        ]
    )

    # Sort most relevant first
    result = result.sort_values(
        by=[
            "content_type",
            "relevance_score"
        ],
        ascending=[
            False,
            False
        ]
    )

    # Reset row numbers
    result = result.reset_index(
        drop=True
    )

    # =====================================================
    # 8. SAVE COMPLETE RESULTS
    # =====================================================

    result.to_csv(
        "collected_articles.csv",
        index=False
    )

    # =====================================================
    # 9. SAVE NEWS ONLY
    # =====================================================

    news_only = result[
        result["content_type"]
        == "NEWS"
    ]

    news_only.to_csv(
        "news_articles.csv",
        index=False
    )

    # =====================================================
    # 10. PRINT SUMMARY
    # =====================================================

    print(
        "\n=============================="
    )

    print(
        "COLLECTION COMPLETE"
    )

    print(
        "=============================="
    )

    print(
        "Total relevant links:",
        len(result)
    )

    print(
        "News items:",
        len(news_only)
    )

    print(
        "Evergreen pages:",
        len(result) - len(news_only)
    )

    print(
        "\nResults by company:"
    )

    print(
        result[
            "company"
        ].value_counts()
    )

    print(
        "\nTop results:"
    )

    print(
        result[
            [
                "company",
                "title",
                "themes",
                "content_type",
                "relevance_score"
            ]
        ].head(20)
    )

    return result


# =========================================================
# 11. RUN SCRIPT
# =========================================================

if __name__ == "__main__":

    result = collect_all()