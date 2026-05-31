# Amazon Product Portfolio Intelligence
## AI-Driven Consumer Sentiment Analysis & Business Intelligence Dashboard
Overview

This project applies Artificial Intelligence, Natural Language Processing (NLP), and Business Analytics techniques to analyze Amazon consumer reviews and transform customer feedback into strategic business insights.

Using over 4,385 consumer reviews from the Datafiniti Amazon Reviews dataset, the project combines:

Market Performance Analysis
Sentiment Analysis using NLTK VADER
Product Health Scoring
Theme Discovery & Keyword Analysis
Business Intelligence Dashboards
Executive Reporting

The objective is to demonstrate how customer-generated data can be converted into actionable recommendations for product managers and business decision-makers.

Project Objectives
Analyze customer satisfaction across Amazon products.
Measure sentiment using NLP techniques.
Identify positive and negative customer themes.
Evaluate product performance through a custom Product Health Score.
Generate executive-level business insights.
Build an interactive Streamlit dashboard for decision-making.
Dataset

Dataset Used:

Datafiniti Amazon Consumer Reviews Dataset

https://www.kaggle.com/datasets/datafiniti/consumer-reviews-of-amazon-products

Contains:

Product Information
Categories
Brands
Customer Ratings
Customer Reviews

Records analyzed:

4,385 Reviews
23 Products
Multiple Product Categories


Technologies Used:
```
# Programming
  Python
# Data Analysis
  Pandas
  NumPy
# Visualization
  Matplotlib
  Seaborn
  Plotly
# Natural Language Processing
  NLTK
  VADER Sentiment Analyzer
# Dashboard Development
  Streamlit
```

Project Structure:
```
Nike_Project/
│
├── Datafiniti_Amazon_Consumer_Reviews_of_Amazon_Products.csv
├── analysis.py
├── dashboard.py
├── requirements.txt
│
├── outputs/
│   ├── charts/
│   ├── executive_summary.txt
│   ├── insights_report.txt
│
├── consulting_report.md
│
└── README.md
```

Key Features:

Data Cleaning
  Duplicate removal
  Missing value handling
  Rating standardization
  Automated column detection
Market Analysis
  Average Rating by Category
  Average Rating by Brand
  Most Reviewed Products
  Rating Distribution
  
Sentiment Analysis
  Using NLTK VADER:
    Positive Reviews
    Neutral Reviews
    Negative Reviews
    Sentiment Score Calculation
    
Theme Discovery
  Identification of:
    Top Positive Keywords
    Top Negative Keywords
    Word Frequency Trends


Product Health Intelligence

Custom Formula:

Health Score =
( Average Rating × 0.60 )
+
( Positive Sentiment % × 0.40 )


Classification:

  Scale
  Fix
  Drop


Trend Analysis:
  Rating vs Sentiment
  Category vs Satisfaction
  Brand vs Satisfaction

  
Interactive Dashboard

The Streamlit dashboard provides:

Executive Overview
  KPI Cards
  Ratings Distribution
  Sentiment Distribution
  Product Performance
Product Health Matrix
  Scale Products
  Fix Products
  Drop Products
Thematic Insights
  Positive Themes
  Negative Themes
  Customer Voice Analysis
  
Strategic Recommendations
  Business-focused recommendations generated from review intelligence and sentiment patterns.

Key Findings
  Average Rating: 4.60 / 5
  Positive Sentiment: 90.35%
  Negative Sentiment: 5.27%
  Products Analyzed: 23
  Reviews Processed: 4,385

Major positive themes:
  Great
  Love
  Easy
  Alexa
  Kindle

Major pain points:
  Battery
  Charging
  Apps
  Device Reliability

  
Generated Outputs:

The project automatically generates:

Reports
Executive Summary Report
Insights Report
Strategic Consulting Report
Visualizations
Rating Distribution
Sentiment Distribution
Category Performance
Brand Performance
Product Health Matrix
Keyword Analysis Charts


Installation:

Clone the repository:

```
git clone https://github.com/your-username/amazon-product-portfolio-intelligence.git
```

Install dependencies:

```
pip install -r requirements.txt
```

Download NLTK resources:

```
python -c "import nltk; nltk.download('vader_lexicon'); nltk.download('punkt'); nltk.download('stopwords')"
```

Run analysis:

```
python analysis.py
```

Launch dashboard:

```
streamlit run dashboard.py
```


Academic Context

Course: MGNM523 – Business Applications of Artificial Intelligence

Programme: MBA (Data Science & Artificial Intelligence)

This project demonstrates the application of AI-driven sentiment analysis and business intelligence techniques for strategic decision-making using real-world consumer review data.

Author

Subrata Roy
MBA (Data Science & Artificial Intelligence)
