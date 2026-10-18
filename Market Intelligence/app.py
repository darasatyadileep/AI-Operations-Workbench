import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
import sqlite3
import pandas as pd

DATABASE_FILE = "intelligence.db"

app =
allowed_origins = [x.strip() for x in os.getenv("ALLOWED_ORIGINS","*").split(",") if x.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
 FastAPI(
    title="Oil & Gas Technology Intelligence API"
)


def query_database(sql, params=None):

    conn = sqlite3.connect(DATABASE_FILE)

    df = pd.read_sql_query(
        sql,
        conn,
        params=params
    )

    conn.close()

    return df


@app.get("/")
def home():

    return {
        "message":
        "Oil & Gas Technology Intelligence API running"
    }


@app.get("/intelligence")
def get_intelligence():

    df = query_database("""
        SELECT
            id,
            company,
            title,
            url,
            primary_theme,
            secondary_themes,
            business_area,
            maturity,
            significance,
            technology,
            summary,
            why_it_matters,
            analysis_mode,
            analyzed_at
        FROM intelligence
        WHERE relevant = 1
        ORDER BY analyzed_at DESC
    """)

    return df.to_dict(
        orient="records"
    )


@app.get("/intelligence/summary")
def get_summary():

    df = query_database("""
        SELECT *
        FROM intelligence
        WHERE relevant = 1
    """)

    if df.empty:

        return {
            "total_items": 0,
            "high_significance": 0,
            "companies": 0,
            "themes": 0
        }

    return {
        "total_items":
            len(df),

        "high_significance":
            int(
                (
                    df["significance"]
                    == "HIGH"
                ).sum()
            ),

        "companies":
            int(
                df["company"]
                .nunique()
            ),

        "themes":
            int(
                df["primary_theme"]
                .nunique()
            )
    }


@app.get("/intelligence/companies")
def company_summary():

    df = query_database("""
        SELECT
            company,
            COUNT(*) AS intelligence_items
        FROM intelligence
        WHERE relevant = 1
        GROUP BY company
        ORDER BY intelligence_items DESC
    """)

    return df.to_dict(
        orient="records"
    )


@app.get("/intelligence/themes")
def theme_summary():

    df = query_database("""
        SELECT
            primary_theme,
            COUNT(*) AS intelligence_items
        FROM intelligence
        WHERE relevant = 1
        GROUP BY primary_theme
        ORDER BY intelligence_items DESC
    """)

    return df.to_dict(
        orient="records"
    )
# Live search-enabled AI research (separate from the legacy keyword collector)
from research_api import router as research_router
app.include_router(research_router)
