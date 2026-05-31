"""
=============================================================================
Nike Project — Amazon Reviews Intelligence Dashboard
MBA Data Science & AI | MGNM523 Business Applications of AI
=============================================================================

INSTALLATION REQUIREMENTS (run once before launching):
    pip install streamlit plotly pandas numpy nltk scikit-learn

NLTK DATA (run once in Python):
    import nltk
    nltk.download('vader_lexicon')
    nltk.download('stopwords')
    nltk.download('punkt')

USAGE:
    streamlit run dashboard.py
=============================================================================
"""

# ---------------------------------------------------------------------------
# Standard imports
# ---------------------------------------------------------------------------
import os
import re
import warnings
from pathlib import Path
from collections import Counter
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Page configuration — MUST be the very first Streamlit call
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Amazon Product Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS — consulting / dark-glass aesthetic
# ---------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Global reset ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* ── App background ── */
.stApp {
    background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 50%, #0f1525 100%);
    color: #e8e8f0;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: rgba(15, 15, 40, 0.95);
    border-right: 1px solid rgba(99, 102, 241, 0.25);
}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stMultiSelect label,
section[data-testid="stSidebar"] p {
    color: #a5b4fc !important;
    font-weight: 500;
}

/* ── Tab styling ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.04);
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
    border: 1px solid rgba(99, 102, 241, 0.2);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    color: #94a3b8 !important;
    font-weight: 500;
    font-size: 14px;
    padding: 10px 24px;
    background: transparent;
    border: none !important;
    transition: all 0.25s ease;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: #ffffff !important;
    box-shadow: 0 4px 20px rgba(99, 102, 241, 0.45);
}

/* ── KPI card ── */
.kpi-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(99, 102, 241, 0.25);
    border-radius: 16px;
    padding: 24px 20px;
    text-align: center;
    backdrop-filter: blur(12px);
    transition: transform 0.2s, box-shadow 0.2s;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #6366f1, #8b5cf6, #06b6d4);
    border-radius: 16px 16px 0 0;
}
.kpi-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 40px rgba(99, 102, 241, 0.3);
}
.kpi-icon  { font-size: 2rem; margin-bottom: 8px; }
.kpi-label { font-size: 12px; color: #94a3b8; letter-spacing: 1px;
             text-transform: uppercase; font-weight: 600; margin-bottom: 6px; }
.kpi-value { font-size: 2.2rem; font-weight: 800;
             background: linear-gradient(135deg, #e2e8f0, #a5b4fc);
             -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.kpi-delta { font-size: 12px; color: #10b981; margin-top: 4px; font-weight: 500; }

/* ── Section headings ── */
.section-title {
    font-size: 20px;
    font-weight: 700;
    color: #e2e8f0;
    margin: 28px 0 16px 0;
    padding-left: 12px;
    border-left: 4px solid #6366f1;
    letter-spacing: 0.3px;
}
.section-subtitle {
    font-size: 13px;
    color: #64748b;
    margin-top: -10px;
    margin-bottom: 18px;
    padding-left: 16px;
}

/* ── Recommendation boxes ── */
.rec-card {
    border-radius: 14px;
    padding: 20px 22px;
    margin-bottom: 14px;
    border-left: 4px solid transparent;
    backdrop-filter: blur(10px);
}
.rec-scale  { background: rgba(16,185,129,0.10); border-color: #10b981; }
.rec-fix    { background: rgba(245,158,11,0.10);  border-color: #f59e0b; }
.rec-drop   { background: rgba(239,68,68,0.10);   border-color: #ef4444; }
.rec-title  { font-size: 15px; font-weight: 700; margin-bottom: 6px; }
.rec-body   { font-size: 13px; color: #94a3b8; line-height: 1.7; }
.badge {
    display: inline-block; border-radius: 6px; padding: 2px 10px;
    font-size: 11px; font-weight: 700; letter-spacing: 0.5px; margin-right: 4px;
}
.badge-scale { background: rgba(16,185,129,0.25);  color: #10b981; }
.badge-fix   { background: rgba(245,158,11,0.25);  color: #f59e0b; }
.badge-drop  { background: rgba(239,68,68,0.25);   color: #ef4444; }

/* ── Executive summary card ── */
.exec-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 16px;
    padding: 28px 32px;
    line-height: 1.9;
    color: #cbd5e1;
    font-size: 14px;
}
.exec-card h4 {
    color: #a5b4fc;
    font-size: 13px;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-top: 18px;
    margin-bottom: 4px;
}
.exec-highlight { color: #f1f5f9; font-weight: 700; }

/* ── Health pill badges in tables ── */
.pill {
    display: inline-block; border-radius: 20px; padding: 3px 12px;
    font-size: 11px; font-weight: 700;
}
.pill-scale { background: #064e3b; color: #34d399; }
.pill-fix   { background: #451a03; color: #fbbf24; }
.pill-drop  { background: #450a0a; color: #f87171; }

/* ── Metric delta overrides ── */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(99,102,241,0.2) !important;
    border-radius: 12px !important;
    padding: 16px !important;
}

/* ── Divider ── */
hr { border-color: rgba(99,102,241,0.2) !important; }

/* ── Hide default streamlit footer ── */
footer { visibility: hidden; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# NLTK setup
# ---------------------------------------------------------------------------
@st.cache_resource
def _ensure_nltk():
    for resource, path in [
        ("vader_lexicon", "sentiment/vader_lexicon.zip"),
        ("stopwords",     "corpora/stopwords"),
        ("punkt",         "tokenizers/punkt"),
    ]:
        try:
            nltk.data.find(path)
        except LookupError:
            nltk.download(resource, quiet=True)

_ensure_nltk()


# ---------------------------------------------------------------------------
# Data loading & preprocessing
# ---------------------------------------------------------------------------
CSV_NAME = "Datafiniti_Amazon_Consumer_Reviews_of_Amazon_Products.csv"
NEEDED_COLS = ["name", "brand", "categories", "reviews.rating", "reviews.text", "reviews.title"]


@st.cache_data(show_spinner="Loading dataset…")
def load_data(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path, usecols=NEEDED_COLS, low_memory=False)
    df = df.rename(columns={
        "name":           "product_name",
        "reviews.rating": "rating",
        "reviews.text":   "review",
        "reviews.title":  "review_title",
    })

    # ── ratings ──
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df = df.dropna(subset=["review", "rating"])
    df["review"] = df["review"].astype(str).str.strip()
    df = df[df["review"].str.len() > 0]

    # ── main category (first item in comma-separated string) ──
    df["main_category"] = (
        df["categories"]
        .fillna("Unknown")
        .astype(str)
        .apply(lambda x: x.split(",")[0].strip())
    )

    # ── clean brand / product name ──
    df["brand"]        = df["brand"].fillna("Unknown").astype(str).str.strip()
    df["product_name"] = df["product_name"].fillna("Unknown").astype(str).str.strip()

    # ── remove duplicates ──
    df = df.drop_duplicates(subset=["review"])
    df = df.reset_index(drop=True)
    return df


@st.cache_data(show_spinner="Running sentiment analysis…")
def add_sentiment(df: pd.DataFrame) -> pd.DataFrame:
    sia = SentimentIntensityAnalyzer()
    df = df.copy()
    df["sentiment_score"] = df["review"].apply(
        lambda x: sia.polarity_scores(x)["compound"]
    )
    df["sentiment_label"] = df["sentiment_score"].apply(
        lambda s: "Positive" if s > 0.05 else ("Negative" if s < -0.05 else "Neutral")
    )
    return df


# ---------------------------------------------------------------------------
# Metric helpers
# ---------------------------------------------------------------------------
def compute_kpis(df: pd.DataFrame) -> dict:
    return {
        "avg_rating":    df["rating"].mean() if len(df) else 0,
        "positive_pct":  (df["sentiment_label"] == "Positive").mean() * 100 if len(df) else 0,
        "num_products":  df["product_name"].nunique(),
        "num_reviews":   len(df),
    }


def product_metrics(df: pd.DataFrame) -> pd.DataFrame:
    grp = (
        df.groupby("product_name", sort=False)
        .agg(
            avg_rating    = ("rating",          "mean"),
            review_count  = ("review",          "count"),
            positive_pct  = ("sentiment_label", lambda x: (x == "Positive").mean() * 100),
            avg_sentiment = ("sentiment_score", "mean"),
        )
        .reset_index()
    )
    grp["rating_pct"]   = grp["avg_rating"] / 5.0 * 100
    grp["health_score"] = grp["rating_pct"] * 0.6 + grp["positive_pct"] * 0.4
    grp["health_class"] = grp["health_score"].apply(
        lambda h: "Scale" if h >= 70 else ("Fix" if h >= 50 else "Drop")
    )
    return grp.sort_values("health_score", ascending=False)


def category_metrics(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("main_category", sort=False)
        .agg(
            avg_rating   = ("rating",          "mean"),
            review_count = ("review",          "count"),
            positive_pct = ("sentiment_label", lambda x: (x == "Positive").mean() * 100),
        )
        .reset_index()
        .sort_values("review_count", ascending=False)
    )


def brand_metrics(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("brand", sort=False)
        .agg(
            avg_rating   = ("rating",          "mean"),
            review_count = ("review",          "count"),
            positive_pct = ("sentiment_label", lambda x: (x == "Positive").mean() * 100),
        )
        .reset_index()
        .sort_values("review_count", ascending=False)
    )


def extract_keywords(texts: pd.Series, top_n: int = 15) -> list[tuple]:
    stop = set(stopwords.words("english")) | {
        "would", "could", "also", "really", "get", "got", "one", "like",
        "just", "even", "much", "little", "thing", "make", "way", "good",
        "great", "love", "bought", "product", "amazon",
    }
    words = []
    for t in texts:
        tokens = re.findall(r"\b[a-z]{4,}\b", str(t).lower())
        words.extend(w for w in tokens if w not in stop)
    return Counter(words).most_common(top_n)


# ---------------------------------------------------------------------------
# Plotly helpers — shared theme
# ---------------------------------------------------------------------------
PLOTLY_LAYOUT = dict(
    font_family   = "Inter, sans-serif",
    font_color    = "#cbd5e1",
    paper_bgcolor = "rgba(0,0,0,0)",
    plot_bgcolor  = "rgba(0,0,0,0)",
    margin        = dict(l=20, r=20, t=40, b=20),
    legend        = dict(
        bgcolor      = "rgba(255,255,255,0.05)",
        bordercolor  = "rgba(99,102,241,0.3)",
        borderwidth  = 1,
        font_size    = 12,
    ),
)

PALETTE = px.colors.qualitative.Bold
COLOR_SENTIMENT = {
    "Positive": "#10b981",
    "Neutral":  "#f59e0b",
    "Negative": "#ef4444",
}
COLOR_HEALTH = {
    "Scale": "#10b981",
    "Fix":   "#f59e0b",
    "Drop":  "#ef4444",
}


def styled_fig(fig: go.Figure) -> go.Figure:
    fig.update_layout(**PLOTLY_LAYOUT)
    fig.update_xaxes(
        gridcolor   = "rgba(99,102,241,0.12)",
        zerolinecolor = "rgba(99,102,241,0.2)",
        tickfont_color = "#94a3b8",
    )
    fig.update_yaxes(
        gridcolor   = "rgba(99,102,241,0.12)",
        zerolinecolor = "rgba(99,102,241,0.2)",
        tickfont_color = "#94a3b8",
    )
    return fig


# ---------------------------------------------------------------------------
# Chart builders
# ---------------------------------------------------------------------------
def fig_ratings_dist(df: pd.DataFrame) -> go.Figure:
    counts = (
        df["rating"].value_counts().sort_index().reindex([1, 2, 3, 4, 5], fill_value=0)
    )
    stars   = [f"{'★'*int(r)} ({int(r)})" for r in counts.index]
    colours = ["#ef4444", "#f97316", "#f59e0b", "#84cc16", "#10b981"]

    fig = go.Figure(go.Bar(
        x            = stars,
        y            = counts.values,
        marker_color = colours,
        text         = counts.values,
        textposition = "outside",
        textfont     = dict(color="#e2e8f0", size=12),
        hovertemplate = "<b>%{x}</b><br>Reviews: %{y}<extra></extra>",
    ))
    fig.update_layout(
        title        = "Ratings Distribution",
        title_font   = dict(size=16, color="#e2e8f0"),
        showlegend   = False,
        yaxis_title  = "Number of Reviews",
        xaxis_title  = "Star Rating",
        bargap       = 0.35,
    )
    return styled_fig(fig)


def fig_sentiment_donut(df: pd.DataFrame) -> go.Figure:
    vc = df["sentiment_label"].value_counts()
    labels = vc.index.tolist()
    values = vc.values.tolist()
    colors = [COLOR_SENTIMENT.get(l, "#6366f1") for l in labels]

    fig = go.Figure(go.Pie(
        labels           = labels,
        values           = values,
        hole             = 0.62,
        marker_colors    = colors,
        textfont_size    = 13,
        hovertemplate    = "<b>%{label}</b><br>%{value} reviews (%{percent})<extra></extra>",
        textinfo         = "percent+label",
    ))
    fig.update_layout(
        title       = "Sentiment Distribution",
        title_font  = dict(size=16, color="#e2e8f0"),
        annotations = [dict(
            text      = f"{(df['sentiment_label']=='Positive').mean()*100:.0f}%<br><span style='font-size:11px;fill:#94a3b8'>Positive</span>",
            x=0.5, y=0.5, font_size=18, showarrow=False,
            font_color="#10b981",
        )],
        showlegend  = True,
        legend_orientation = "h",
    )
    return styled_fig(fig)


def fig_top_products(pm: pd.DataFrame, n: int = 10) -> go.Figure:
    top = pm.nlargest(n, "review_count").iloc[::-1]   # ascending for horizontal
    colours = [COLOR_HEALTH[h] for h in top["health_class"]]

    # Truncate long product names
    labels = top["product_name"].apply(lambda s: (s[:55] + "…") if len(s) > 58 else s)

    fig = go.Figure(go.Bar(
        y            = labels,
        x            = top["review_count"],
        orientation  = "h",
        marker_color = colours,
        text         = top["review_count"],
        textposition = "outside",
        textfont     = dict(color="#e2e8f0", size=11),
        customdata   = list(zip(
            top["avg_rating"].round(2),
            top["positive_pct"].round(1),
            top["health_class"],
        )),
        hovertemplate = (
            "<b>%{y}</b><br>"
            "Reviews: %{x}<br>"
            "Avg Rating: %{customdata[0]}/5<br>"
            "Positive: %{customdata[1]}%<br>"
            "Health: %{customdata[2]}<extra></extra>"
        ),
    ))
    fig.update_layout(
        title       = f"Top {n} Products by Review Volume",
        title_font  = dict(size=16, color="#e2e8f0"),
        xaxis_title = "Number of Reviews",
        height      = 420,
        showlegend  = False,
    )
    return styled_fig(fig)


def fig_category_perf(cm: pd.DataFrame) -> go.Figure:
    top = cm.head(12)

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(
        name         = "Review Count",
        x            = top["main_category"],
        y            = top["review_count"],
        marker_color = "#6366f1",
        opacity      = 0.85,
        hovertemplate = "<b>%{x}</b><br>Reviews: %{y}<extra></extra>",
    ), secondary_y=False)

    fig.add_trace(go.Scatter(
        name         = "Avg Rating",
        x            = top["main_category"],
        y            = top["avg_rating"],
        mode         = "lines+markers",
        line         = dict(color="#f59e0b", width=2.5),
        marker       = dict(size=8, color="#f59e0b"),
        hovertemplate = "<b>%{x}</b><br>Avg Rating: %{y:.2f}<extra></extra>",
    ), secondary_y=True)

    fig.update_layout(
        title       = "Category Performance — Review Volume & Avg Rating",
        title_font  = dict(size=16, color="#e2e8f0"),
        hovermode   = "x unified",
        height      = 400,
        xaxis_tickangle = -35,
    )
    fig.update_yaxes(title_text="Review Count",  secondary_y=False, title_font_color="#6366f1")
    fig.update_yaxes(title_text="Average Rating", secondary_y=True,  title_font_color="#f59e0b")
    return styled_fig(fig)


def fig_brand_perf(bm: pd.DataFrame) -> go.Figure:
    top = bm.head(10)
    fig = px.scatter(
        top,
        x          = "avg_rating",
        y          = "positive_pct",
        size       = "review_count",
        color      = "brand",
        text       = "brand",
        size_max   = 60,
        color_discrete_sequence = PALETTE,
        labels     = {
            "avg_rating":   "Average Rating",
            "positive_pct": "Positive Sentiment %",
            "brand":        "Brand",
        },
        hover_data = {"review_count": True, "avg_rating": ":.2f", "positive_pct": ":.1f"},
    )
    fig.update_traces(textposition="top center", textfont_size=11)
    fig.update_layout(
        title      = "Brand Performance — Rating vs Sentiment",
        title_font = dict(size=16, color="#e2e8f0"),
        height     = 420,
    )
    return styled_fig(fig)


def fig_health_matrix(pm: pd.DataFrame) -> go.Figure:
    fig = go.Figure()

    # Background quadrant shading
    for (x0, x1, y0, y1, col) in [
        (70, 105, 70, 105, "rgba(16,185,129,0.06)"),   # top-right  → Scale
        (0,  70,  70, 105, "rgba(245,158,11,0.06)"),   # top-left   → Fix
        (70, 105, 0,  70,  "rgba(245,158,11,0.06)"),   # bot-right  → Fix
        (0,  70,  0,  70,  "rgba(239,68,68,0.06)"),    # bot-left   → Drop
    ]:
        fig.add_shape(type="rect", x0=x0, x1=x1, y0=y0, y1=y1,
                      fillcolor=col, line_width=0, layer="below")

    # Reference lines
    for val, axis in [(70, "x"), (70, "y")]:
        fig.add_shape(
            type="line",
            **({f"{axis}0": val, f"{axis}1": val,
                "y0" if axis=="x" else "x0": 0,
                "y1" if axis=="x" else "x1": 100}),
            line=dict(color="rgba(148,163,184,0.4)", dash="dash", width=1.5),
        )

    # Quadrant labels
    annotations = [
        dict(x=87, y=95, text="<b>SCALE ✅</b>",    font_color="#10b981", font_size=13),
        dict(x=35, y=95, text="<b>FIX ⚠️</b>",      font_color="#f59e0b", font_size=13),
        dict(x=87, y=40, text="<b>FIX ⚠️</b>",      font_color="#f59e0b", font_size=13),
        dict(x=35, y=40, text="<b>DROP ❌</b>",      font_color="#ef4444", font_size=13),
    ]

    for cls in ["Scale", "Fix", "Drop"]:
        sub = pm[pm["health_class"] == cls]
        if sub.empty:
            continue
        labels = sub["product_name"].apply(
            lambda s: (s[:40] + "…") if len(s) > 43 else s
        )
        fig.add_trace(go.Scatter(
            x            = sub["rating_pct"],
            y            = sub["positive_pct"],
            mode         = "markers",
            name         = cls,
            marker       = dict(
                color   = COLOR_HEALTH[cls],
                size    = np.clip(sub["review_count"] / sub["review_count"].max() * 40, 8, 40),
                opacity = 0.85,
                line    = dict(color="rgba(255,255,255,0.2)", width=1),
            ),
            text         = labels,
            hovertemplate = (
                "<b>%{text}</b><br>"
                "Rating Score: %{x:.1f}%<br>"
                "Positive Sentiment: %{y:.1f}%<br>"
                "<extra></extra>"
            ),
        ))

    fig.update_layout(
        title        = "Product Health Matrix — Rating vs Positive Sentiment",
        title_font   = dict(size=16, color="#e2e8f0"),
        xaxis_title  = "Rating Score (% of max 5★)",
        yaxis_title  = "Positive Sentiment %",
        xaxis_range  = [0, 105],
        yaxis_range  = [0, 105],
        height       = 540,
        annotations  = [dict(showarrow=False, **a) for a in annotations],
        legend       = dict(title="Classification", orientation="h", y=-0.12),
    )
    return styled_fig(fig)


def fig_keywords(kws: list[tuple], title: str, color: str) -> go.Figure:
    words, counts = zip(*kws) if kws else ([], [])
    fig = go.Figure(go.Bar(
        x            = list(counts)[::-1],
        y            = list(words)[::-1],
        orientation  = "h",
        marker       = dict(
            color    = color,
            opacity  = 0.85,
            line     = dict(color="rgba(255,255,255,0.1)", width=0.5),
        ),
        text         = list(counts)[::-1],
        textposition = "outside",
        textfont     = dict(color="#e2e8f0", size=11),
        hovertemplate = "<b>%{y}</b><br>Occurrences: %{x}<extra></extra>",
    ))
    fig.update_layout(
        title       = title,
        title_font  = dict(size=15, color="#e2e8f0"),
        xaxis_title = "Occurrences",
        height      = 400,
        showlegend  = False,
    )
    return styled_fig(fig)


# ---------------------------------------------------------------------------
# KPI card HTML helper
# ---------------------------------------------------------------------------
def kpi_card(icon: str, label: str, value: str, delta: str = "") -> str:
    delta_html = f'<div class="kpi-delta">{delta}</div>' if delta else ""
    return f"""
    <div class="kpi-card">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>"""


# ---------------------------------------------------------------------------
# Executive summary builder
# ---------------------------------------------------------------------------
def build_exec_summary(kpis: dict, cm: pd.DataFrame, pm: pd.DataFrame, df: pd.DataFrame) -> str:
    top_cats = cm.head(3)["main_category"].tolist()
    scale_n  = (pm["health_class"] == "Scale").sum()
    fix_n    = (pm["health_class"] == "Fix").sum()
    drop_n   = (pm["health_class"] == "Drop").sum()
    pos_kws  = extract_keywords(df[df["sentiment_label"] == "Positive"]["review"], 5)
    neg_kws  = extract_keywords(df[df["sentiment_label"] == "Negative"]["review"], 5)
    top_pos  = ", ".join(w for w, _ in pos_kws)
    top_neg  = ", ".join(w for w, _ in neg_kws)

    return f"""
    <div class="exec-card">
        <h4>📋 Report Overview</h4>
        This intelligence brief summarises consumer sentiment and product performance
        for <span class="exec-highlight">{kpis['num_reviews']:,} Amazon reviews</span>
        spanning <span class="exec-highlight">{kpis['num_products']}</span> distinct products.
        The analysis leverages NLTK VADER sentiment scoring and a composite health model
        to drive portfolio strategy.

        <h4>📊 Key Performance Indicators</h4>
        The dataset carries an overall average star rating of
        <span class="exec-highlight">{kpis['avg_rating']:.2f} / 5.0</span> with
        <span class="exec-highlight">{kpis['positive_pct']:.1f}%</span> of reviews classified as
        positive — indicating a <em>high customer satisfaction baseline</em>.

        <h4>🏷️ Category Landscape</h4>
        The top three volume categories are
        <span class="exec-highlight">{", ".join(top_cats)}</span>.
        These segments collectively account for the majority of review activity
        and should be prioritised in product investment decisions.

        <h4>🏆 Portfolio Health Breakdown</h4>
        Product health scoring (60% ratings weight + 40% sentiment weight) classifies
        the portfolio as follows:
        &nbsp;✅ <span class="exec-highlight">{scale_n} products to Scale</span>
        &nbsp;⚠️ <span class="exec-highlight">{fix_n} products to Fix</span>
        &nbsp;❌ <span class="exec-highlight">{drop_n} products to Drop</span>.

        <h4>💬 Voice of the Customer</h4>
        Positive reviews emphasise: <span class="exec-highlight">{top_pos}</span>.<br>
        Negative reviews surface: <span class="exec-highlight">{top_neg}</span>.
        Addressing the pain points identified in negative reviews could materially
        reduce churn and lift Net Promoter Score.

        <h4>📅 Report Generated</h4>
        {datetime.now().strftime("%d %B %Y, %H:%M")}
    </div>
    """


# ---------------------------------------------------------------------------
# Business recommendations
# ---------------------------------------------------------------------------
def build_recommendations(pm: pd.DataFrame, df: pd.DataFrame) -> str:
    scale_prods = pm[pm["health_class"] == "Scale"].head(3)["product_name"].tolist()
    fix_prods   = pm[pm["health_class"] == "Fix"].head(3)["product_name"].tolist()
    drop_prods  = pm[pm["health_class"] == "Drop"].head(3)["product_name"].tolist()

    neg_kws = extract_keywords(df[df["sentiment_label"] == "Negative"]["review"], 7)
    pain_pts = ", ".join(f"<em>{w}</em>" for w, _ in neg_kws)

    scale_list = (
        "<br>".join(f"&nbsp;• {p[:70]}…" if len(p) > 70 else f"&nbsp;• {p}" for p in scale_prods)
        if scale_prods else "&nbsp;• No products meet Scale criteria in the current filter."
    )
    fix_list = (
        "<br>".join(f"&nbsp;• {p[:70]}…" if len(p) > 70 else f"&nbsp;• {p}" for p in fix_prods)
        if fix_prods else "&nbsp;• No products meet Fix criteria in the current filter."
    )
    drop_list = (
        "<br>".join(f"&nbsp;• {p[:70]}…" if len(p) > 70 else f"&nbsp;• {p}" for p in drop_prods)
        if drop_prods else "&nbsp;• No products meet Drop criteria in the current filter."
    )

    html = f"""
    <div class="rec-card rec-scale">
        <div class="rec-title">
            <span class="badge badge-scale">SCALE</span>
            Amplify Market Position &amp; Investment
        </div>
        <div class="rec-body">
            These products demonstrate superior ratings and high positive sentiment.
            Prioritise marketing spend, expand inventory, and explore premium pricing.<br><br>
            {scale_list}
        </div>
    </div>

    <div class="rec-card rec-fix">
        <div class="rec-title">
            <span class="badge badge-fix">FIX</span>
            Address Quality Gaps &amp; Customer Pain Points
        </div>
        <div class="rec-body">
            Mid-tier performers with untapped potential. Customer pain-points surfaced
            in negative reviews include: {pain_pts}.<br>
            Tactical improvements in product reliability, packaging, and after-sales support
            are recommended.<br><br>
            {fix_list}
        </div>
    </div>

    <div class="rec-card rec-drop">
        <div class="rec-title">
            <span class="badge badge-drop">DROP</span>
            Phase Out or Re-position Underperformers
        </div>
        <div class="rec-body">
            Low ratings and negative sentiment indicate structural product issues.
            Consider markdown promotions, product repositioning, or discontinuation
            to protect brand equity.<br><br>
            {drop_list}
        </div>
    </div>
    """
    return html


# ---------------------------------------------------------------------------
# Sidebar — filters
# ---------------------------------------------------------------------------
def render_sidebar(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/Amazon_logo.svg/320px-Amazon_logo.svg.png",
        width=140,
    )
    st.sidebar.markdown(
        "<br><div style='font-size:18px;font-weight:700;color:#a5b4fc;'>📊 Filters</div>",
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("---")

    # Category filter
    cats = sorted(df["main_category"].dropna().unique().tolist())
    selected_cats = st.sidebar.multiselect(
        "Category",
        options    = cats,
        default    = [],
        help       = "Leave empty to include all categories",
    )

    # Brand filter
    brands = sorted(df["brand"].dropna().unique().tolist())
    selected_brands = st.sidebar.multiselect(
        "Brand",
        options = brands,
        default = [],
        help    = "Leave empty to include all brands",
    )

    # Rating filter
    st.sidebar.markdown("---")
    min_r, max_r = st.sidebar.slider(
        "Minimum Rating",
        min_value = 1.0,
        max_value = 5.0,
        value     = (1.0, 5.0),
        step      = 0.5,
    )

    # Apply filters
    filt = df.copy()
    if selected_cats:
        filt = filt[filt["main_category"].isin(selected_cats)]
    if selected_brands:
        filt = filt[filt["brand"].isin(selected_brands)]
    filt = filt[(filt["rating"] >= min_r) & (filt["rating"] <= max_r)]

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        f"<div style='color:#64748b;font-size:12px;'>"
        f"Showing <b style='color:#a5b4fc'>{len(filt):,}</b> of "
        f"<b style='color:#a5b4fc'>{len(df):,}</b> reviews</div>",
        unsafe_allow_html=True,
    )
    st.sidebar.markdown(
        "<br><div style='color:#374151;font-size:11px;text-align:center;'>"
        "MBA Data Science &amp; AI<br>MGNM523 Business Applications of AI</div>",
        unsafe_allow_html=True,
    )
    return filt


# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------
def main():
    # ── Header ──────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center;padding:32px 0 8px 0;">
        <div style="font-size:42px;font-weight:800;
             background:linear-gradient(135deg,#6366f1,#8b5cf6,#06b6d4);
             -webkit-background-clip:text;-webkit-text-fill-color:transparent;
             letter-spacing:-1px;line-height:1.15;">
            Amazon Product Intelligence Dashboard
        </div>
        <div style="color:#64748b;font-size:15px;margin-top:8px;font-weight:400;">
            Consumer Review Analytics &nbsp;·&nbsp; Sentiment Intelligence &nbsp;·&nbsp; Portfolio Strategy
        </div>
    </div>
    <hr style="margin:12px 0 28px 0;">
    """, unsafe_allow_html=True)

    # ── Load CSV ─────────────────────────────────────────────────────────────
    base     = Path(__file__).resolve().parent
    csv_path = base / CSV_NAME

    if not csv_path.exists():
        st.error(f"❌ Dataset not found at `{csv_path}`.\n\n"
                 "Place `Datafiniti_Amazon_Consumer_Reviews_of_Amazon_Products.csv` "
                 "in the same folder as `dashboard.py` and reload.")
        st.stop()

    df_raw  = load_data(str(csv_path))
    df_full = add_sentiment(df_raw)

    # ── Sidebar / filtering ──────────────────────────────────────────────────
    df = render_sidebar(df_full)

    if len(df) == 0:
        st.warning("⚠️ No data matches the current filters. Please broaden your selection.")
        st.stop()

    # ── Compute metrics ───────────────────────────────────────────────────────
    kpis = compute_kpis(df)
    pm   = product_metrics(df)
    cm   = category_metrics(df)
    bm   = brand_metrics(df)

    # ── KPI Cards ──────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    cards = [
        (c1, "⭐", "Average Rating",      f"{kpis['avg_rating']:.2f} / 5.0",   "Overall satisfaction"),
        (c2, "😊", "Positive Sentiment",  f"{kpis['positive_pct']:.1f}%",      "VADER compound > 0.05"),
        (c3, "📦", "Distinct Products",   f"{kpis['num_products']:,}",          "In filtered dataset"),
        (c4, "💬", "Total Reviews",       f"{kpis['num_reviews']:,}",           "After de-duplication"),
    ]
    for col, icon, label, value, delta in cards:
        col.markdown(kpi_card(icon, label, value, delta), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tabs ─────────────────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs([
        "🏠  Executive Overview",
        "🧮  Product Health Matrix",
        "🔍  Thematic Insights",
    ])

    # ═══════════════════════════════════════════════════════════════════════
    # TAB 1 — Executive Overview
    # ═══════════════════════════════════════════════════════════════════════
    with tab1:

        # Row 1: Ratings + Sentiment side by side
        st.markdown('<div class="section-title">📈 Ratings & Sentiment Overview</div>',
                    unsafe_allow_html=True)
        rc1, rc2 = st.columns([1.2, 1], gap="large")
        with rc1:
            st.plotly_chart(fig_ratings_dist(df), use_container_width=True)
        with rc2:
            st.plotly_chart(fig_sentiment_donut(df), use_container_width=True)

        st.markdown("---")

        # Row 2: Top Products
        st.markdown('<div class="section-title">🏆 Top Products by Review Volume</div>',
                    unsafe_allow_html=True)
        st.markdown(
            '<div class="section-subtitle">'
            'Bar colour indicates health classification — '
            '<span style="color:#10b981">■ Scale</span> &nbsp;'
            '<span style="color:#f59e0b">■ Fix</span> &nbsp;'
            '<span style="color:#ef4444">■ Drop</span></div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(fig_top_products(pm, n=10), use_container_width=True)

        st.markdown("---")

        # Row 3: Category + Brand performance
        st.markdown('<div class="section-title">📊 Category & Brand Performance</div>',
                    unsafe_allow_html=True)
        pc1, pc2 = st.columns([1.2, 1], gap="large")
        with pc1:
            st.plotly_chart(fig_category_perf(cm), use_container_width=True)
        with pc2:
            st.plotly_chart(fig_brand_perf(bm), use_container_width=True)

        st.markdown("---")

        # Executive Summary
        st.markdown('<div class="section-title">📋 Executive Summary</div>',
                    unsafe_allow_html=True)
        st.markdown(
            build_exec_summary(kpis, cm, pm, df),
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # Business Recommendations
        st.markdown('<div class="section-title">💡 Business Recommendations</div>',
                    unsafe_allow_html=True)
        st.markdown(
            build_recommendations(pm, df),
            unsafe_allow_html=True,
        )

    # ═══════════════════════════════════════════════════════════════════════
    # TAB 2 — Product Health Matrix
    # ═══════════════════════════════════════════════════════════════════════
    with tab2:
        st.markdown('<div class="section-title">🧮 Product Health Matrix</div>',
                    unsafe_allow_html=True)
        st.markdown(
            '<div class="section-subtitle">'
            'Each bubble represents a product. Size ∝ review volume. '
            'Thresholds: Scale ≥ 70 health score, Fix 50–70, Drop &lt; 50</div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(fig_health_matrix(pm), use_container_width=True)

        st.markdown("---")

        # Classification tables in sub-tabs
        st.markdown('<div class="section-title">📂 Product Classification Details</div>',
                    unsafe_allow_html=True)

        t_scale, t_fix, t_drop = st.tabs(["✅ Scale", "⚠️ Fix", "❌ Drop"])

        display_cols = {
            "product_name": "Product",
            "avg_rating":   "Avg Rating",
            "positive_pct": "Positive %",
            "review_count": "Reviews",
            "health_score": "Health Score",
        }

        def fmt_table(cls: str) -> pd.DataFrame:
            sub = pm[pm["health_class"] == cls].copy()
            sub["avg_rating"]   = sub["avg_rating"].round(2)
            sub["positive_pct"] = sub["positive_pct"].round(1)
            sub["health_score"] = sub["health_score"].round(1)
            sub["product_name"] = sub["product_name"].apply(
                lambda s: (s[:80] + "…") if len(s) > 83 else s
            )
            return sub[list(display_cols.keys())].rename(columns=display_cols)

        with t_scale:
            tdf = fmt_table("Scale")
            if tdf.empty:
                st.info("No products classified as Scale under the current filter.")
            else:
                st.success(f"**{len(tdf)} products** recommended for scaling.")
                st.dataframe(tdf, use_container_width=True, hide_index=True)

        with t_fix:
            tdf = fmt_table("Fix")
            if tdf.empty:
                st.info("No products classified as Fix under the current filter.")
            else:
                st.warning(f"**{len(tdf)} products** require quality or experience improvements.")
                st.dataframe(tdf, use_container_width=True, hide_index=True)

        with t_drop:
            tdf = fmt_table("Drop")
            if tdf.empty:
                st.info("No products classified as Drop under the current filter.")
            else:
                st.error(f"**{len(tdf)} products** are underperformers — consider discontinuation.")
                st.dataframe(tdf, use_container_width=True, hide_index=True)

        # Summary donut
        st.markdown("---")
        st.markdown('<div class="section-title">🥧 Portfolio Health Breakdown</div>',
                    unsafe_allow_html=True)

        hcounts = pm["health_class"].value_counts()
        hfig = go.Figure(go.Pie(
            labels        = hcounts.index.tolist(),
            values        = hcounts.values.tolist(),
            hole          = 0.55,
            marker_colors = [COLOR_HEALTH.get(l, "#6366f1") for l in hcounts.index],
            textinfo      = "percent+label",
            textfont_size = 14,
            hovertemplate = "<b>%{label}</b><br>%{value} products (%{percent})<extra></extra>",
        ))
        hfig.update_layout(
            title       = "Portfolio Health Composition",
            title_font  = dict(size=16, color="#e2e8f0"),
            showlegend  = True,
            height      = 360,
        )
        _, hcol, _ = st.columns([1, 1.4, 1])
        hcol.plotly_chart(styled_fig(hfig), use_container_width=True)

    # ═══════════════════════════════════════════════════════════════════════
    # TAB 3 — Thematic Insights
    # ═══════════════════════════════════════════════════════════════════════
    with tab3:
        st.markdown('<div class="section-title">🔑 Keyword Themes by Sentiment</div>',
                    unsafe_allow_html=True)
        st.markdown(
            '<div class="section-subtitle">'
            'Top keywords extracted from positive and negative reviews (stopwords removed)</div>',
            unsafe_allow_html=True,
        )

        pos_reviews = df[df["sentiment_label"] == "Positive"]["review"]
        neg_reviews = df[df["sentiment_label"] == "Negative"]["review"]

        pos_kws = extract_keywords(pos_reviews, 15)
        neg_kws = extract_keywords(neg_reviews, 15)

        kc1, kc2 = st.columns(2, gap="large")
        with kc1:
            if pos_kws:
                st.plotly_chart(
                    fig_keywords(pos_kws, "🟢 Top Positive Keywords", "#10b981"),
                    use_container_width=True,
                )
            else:
                st.info("Insufficient positive reviews for keyword extraction.")
        with kc2:
            if neg_kws:
                st.plotly_chart(
                    fig_keywords(neg_kws, "🔴 Top Negative Keywords", "#ef4444"),
                    use_container_width=True,
                )
            else:
                st.info("Insufficient negative reviews for keyword extraction.")

        st.markdown("---")

        # Sentiment by Rating stacked bar
        st.markdown('<div class="section-title">📊 Sentiment Distribution by Star Rating</div>',
                    unsafe_allow_html=True)

        sent_by_rat = (
            df.groupby(["rating", "sentiment_label"])
            .size()
            .reset_index(name="count")
        )
        sbr_fig = px.bar(
            sent_by_rat,
            x              = "rating",
            y              = "count",
            color          = "sentiment_label",
            color_discrete_map = COLOR_SENTIMENT,
            barmode        = "stack",
            labels         = {"rating": "Star Rating", "count": "Review Count",
                              "sentiment_label": "Sentiment"},
            text_auto      = False,
        )
        sbr_fig.update_layout(
            title      = "Sentiment Distribution Across Star Ratings",
            title_font = dict(size=16, color="#e2e8f0"),
            height     = 380,
            xaxis      = dict(tickvals=[1, 2, 3, 4, 5]),
        )
        st.plotly_chart(styled_fig(sbr_fig), use_container_width=True)

        st.markdown("---")

        # Sentiment score histogram
        st.markdown('<div class="section-title">📉 Sentiment Score Distribution</div>',
                    unsafe_allow_html=True)

        ss_fig = px.histogram(
            df,
            x          = "sentiment_score",
            nbins      = 40,
            color      = "sentiment_label",
            color_discrete_map = COLOR_SENTIMENT,
            labels     = {"sentiment_score": "VADER Compound Score",
                          "count":           "Number of Reviews"},
            opacity    = 0.8,
        )
        ss_fig.update_layout(
            title      = "Distribution of VADER Sentiment Scores",
            title_font = dict(size=16, color="#e2e8f0"),
            height     = 360,
            barmode    = "overlay",
        )
        ss_fig.add_vline(x=0.05,  line_dash="dash", line_color="#10b981",
                         annotation_text="Positive threshold",
                         annotation_font_color="#10b981")
        ss_fig.add_vline(x=-0.05, line_dash="dash", line_color="#ef4444",
                         annotation_text="Negative threshold",
                         annotation_font_color="#ef4444")
        st.plotly_chart(styled_fig(ss_fig), use_container_width=True)

        st.markdown("---")

        # Raw sample data
        with st.expander("🗂️ Browse Filtered Review Data", expanded=False):
            sample_cols = ["product_name", "brand", "main_category",
                           "rating", "sentiment_label", "sentiment_score", "review"]
            st.dataframe(
                df[sample_cols]
                .rename(columns={
                    "product_name":    "Product",
                    "brand":           "Brand",
                    "main_category":   "Category",
                    "rating":          "Rating",
                    "sentiment_label": "Sentiment",
                    "sentiment_score": "Score",
                    "review":          "Review Text",
                })
                .sort_values("Rating", ascending=False)
                .reset_index(drop=True),
                use_container_width=True,
                height=400,
            )

    # ── Footer ──────────────────────────────────────────────────────────────
    st.markdown("""
    <hr>
    <div style="text-align:center;color:#374151;font-size:12px;padding:12px 0;">
        Amazon Product Intelligence Dashboard &nbsp;·&nbsp;
        MBA Data Science &amp; AI &nbsp;·&nbsp; MGNM523 Business Applications of AI<br>
        Sentiment powered by NLTK VADER &nbsp;·&nbsp;
        Thresholds: compound &gt; 0.05 = Positive; &lt; −0.05 = Negative; else Neutral
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    main()
