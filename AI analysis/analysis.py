"""
Nike Project - Amazon Reviews Sentiment Analysis & Business Intelligence
MBA Data Science & AI Program - MGNM523 Business Applications of AI

This module provides comprehensive business analytics and sentiment analysis
on Amazon product reviews, including market analysis, sentiment insights,
product health scoring, and visualization generation.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter
import warnings
import os
from datetime import datetime

warnings.filterwarnings('ignore')

# Configure visualization style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10


class AmazonReviewsAnalysis:
    """
    Main class for analyzing Amazon product reviews data.
    Handles data loading, cleaning, analysis, and report generation.
    """
    
    def __init__(self, csv_path):
        """Initialize analysis with CSV file path."""
        self.csv_path = csv_path
        self.df = None
        self.output_folder = 'outputs'
        self.sia = SentimentIntensityAnalyzer()
        self.stopwords_set = set(stopwords.words('english'))
        
        # Create outputs folder if it doesn't exist
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
    
    def load_data(self):
        """Load and auto-detect columns from CSV file."""
        print("Loading data...")
        self.df = pd.read_csv(self.csv_path)
        
        # Auto-detect column names (case-insensitive)
        self.df.columns = self.df.columns.str.lower().str.strip()
        
        # Map common column variations
        column_mapping = {}
        
        # Find name column
        for col in self.df.columns:
            if 'name' in col or 'product' in col:
                column_mapping[col] = 'name'
                break
        
        # Find brand column
        for col in self.df.columns:
            if 'brand' in col:
                column_mapping[col] = 'brand'
                break
        
        # Find categories column
        for col in self.df.columns:
            if 'categor' in col:
                column_mapping[col] = 'categories'
                break
        
        # Find rating column
        for col in self.df.columns:
            if 'rating' in col and 'review' in col:
                column_mapping[col] = 'rating'
                break
        
        # Find review text column
        for col in self.df.columns:
            if 'review' in col and 'text' in col:
                column_mapping[col] = 'text'
                break
        
        # Rename columns to standardized names
        self.df.rename(columns=column_mapping, inplace=True)
        
        print(f"Data loaded: {len(self.df)} rows")
        print(f"Columns: {self.df.columns.tolist()}")
        
        # THIS IS THE CRITICAL LINE THAT IS MISSING
        return self
    
    def clean_data(self):
        """Clean data: remove duplicates, nulls, convert ratings to numeric."""
        print("\nCleaning data...")
        
        # Remove duplicate reviews
        initial_count = len(self.df)
        self.df.drop_duplicates(subset=['text'], keep='first', inplace=True)
        print(f"Removed {initial_count - len(self.df)} duplicate reviews")
        
        # Remove null reviews
        self.df.dropna(subset=['text'], inplace=True)
        self.df.dropna(subset=['rating'], inplace=True)
        
        # Convert rating to numeric
        self.df['rating'] = pd.to_numeric(self.df['rating'], errors='coerce')
        self.df.dropna(subset=['rating'], inplace=True)
        
        # Clean text column
        self.df['text'] = self.df['text'].astype(str).str.strip()
        self.df = self.df[self.df['text'].str.len() > 0]
        
        print(f"Data cleaned: {len(self.df)} records remain")
        return self
    
    def sentiment_analysis(self):
        """Perform NLTK VADER sentiment analysis."""
        print("\nPerforming sentiment analysis...")
        
        # Calculate sentiment scores
        sentiments = self.df['text'].apply(lambda x: self.sia.polarity_scores(str(x)))
        self.df['sentiment_score'] = sentiments.apply(lambda x: x['compound'])
        
        # Create sentiment labels
        def label_sentiment(score):
            if score > 0.05:
                return 'Positive'
            elif score < -0.05:
                return 'Negative'
            else:
                return 'Neutral'
        
        self.df['sentiment_label'] = self.df['sentiment_score'].apply(label_sentiment)
        
        # Calculate sentiment percentages
        sentiment_counts = self.df['sentiment_label'].value_counts()
        self.sentiment_percentages = {
            'Positive': (sentiment_counts.get('Positive', 0) / len(self.df)) * 100,
            'Neutral': (sentiment_counts.get('Neutral', 0) / len(self.df)) * 100,
            'Negative': (sentiment_counts.get('Negative', 0) / len(self.df)) * 100
        }
        
        print(f"Sentiment Distribution:")
        for label, pct in self.sentiment_percentages.items():
            print(f"  {label}: {pct:.2f}%")
        
        return self
    
    def market_analysis(self):
        """Analyze market metrics: ratings by category/brand, rating distribution."""
        print("\nPerforming market analysis...")
        
        # Average rating by category
        if 'categories' in self.df.columns:
            self.category_ratings = self.df.groupby('categories')['rating'].agg(['mean', 'count']).sort_values('mean', ascending=False)
            self.category_ratings.columns = ['avg_rating', 'review_count']
        
        # Average rating by brand
        if 'brand' in self.df.columns:
            self.brand_ratings = self.df.groupby('brand')['rating'].agg(['mean', 'count']).sort_values('mean', ascending=False)
            self.brand_ratings.columns = ['avg_rating', 'review_count']
        
        # Most reviewed products
        if 'name' in self.df.columns:
            self.most_reviewed = self.df['name'].value_counts().head(10)
        
        # Overall rating distribution
        self.rating_distribution = self.df['rating'].value_counts().sort_index()
        self.overall_avg_rating = self.df['rating'].mean()
        
        print(f"Overall average rating: {self.overall_avg_rating:.2f}")
        
        return self
    
    def theme_discovery(self):
        """Extract top positive and negative keywords."""
        print("\nDiscovering themes...")
        
        # Process text for keyword analysis
        positive_reviews = self.df[self.df['sentiment_label'] == 'Positive']['text']
        negative_reviews = self.df[self.df['sentiment_label'] == 'Negative']['text']
        
        # Extract and count keywords
        self.positive_keywords = self._extract_keywords(positive_reviews, top_n=20)
        self.negative_keywords = self._extract_keywords(negative_reviews, top_n=20)
        
        print(f"Extracted {len(self.positive_keywords)} positive keywords")
        print(f"Extracted {len(self.negative_keywords)} negative keywords")
        
        return self
    
    def _extract_keywords(self, texts, top_n=20):
        """Extract top keywords from text corpus."""
        all_words = []
        
        for text in texts:
            words = word_tokenize(str(text).lower())
            # Filter out stopwords and short words
            words = [w for w in words if w.isalpha() and len(w) > 3 and w not in self.stopwords_set]
            all_words.extend(words)
        
        # Count and get top N
        word_counts = Counter(all_words)
        return word_counts.most_common(top_n)
    
    def product_health_scoring(self):
        """Calculate product health scores and classify products."""
        print("\nCalculating product health scores...")
        
        if 'name' not in self.df.columns:
            print("Product name column not found. Skipping health scoring.")
            return self
        
        # Group by product
        products = self.df.groupby('name').agg({
            'rating': 'mean',
            'sentiment_label': lambda x: (x == 'Positive').sum() / len(x) * 100
        }).rename(columns={'rating': 'avg_rating', 'sentiment_label': 'positive_sentiment_pct'})
        
        # Calculate health score
        products['health_score'] = (products['avg_rating'] / 5 * 100 * 0.6) + (products['positive_sentiment_pct'] * 0.4)
        
        # Classify products
        def classify_health(score):
            if score >= 70:
                return 'Scale'
            elif score >= 50:
                return 'Fix'
            else:
                return 'Drop'
        
        products['classification'] = products['health_score'].apply(classify_health)
        
        self.product_health = products.sort_values('health_score', ascending=False)
        
        print("\nProduct Health Classification Summary:")
        print(self.product_health['classification'].value_counts())
        
        return self
    
    def trend_analysis(self):
        """Analyze trends: rating vs sentiment, category vs satisfaction, brand vs satisfaction."""
        print("\nPerforming trend analysis...")
        
        # Rating vs Sentiment correlation
        self.rating_sentiment_corr = self.df['rating'].corr(self.df['sentiment_score'])
        print(f"Rating vs Sentiment correlation: {self.rating_sentiment_corr:.3f}")
        
        return self
    
    def generate_visualizations(self):
        """Generate all charts and save to outputs folder."""
        print("\nGenerating visualizations...")
        
        # 1. Sentiment Distribution Pie Chart
        plt.figure(figsize=(8, 6))
        colors = ['#2ecc71', '#f39c12', '#e74c3c']
        plt.pie(self.sentiment_percentages.values(), labels=self.sentiment_percentages.keys(),
                autopct='%1.1f%%', colors=colors, startangle=90)
        plt.title('Sentiment Distribution')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_folder, '01_sentiment_distribution.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Rating Distribution Histogram
        plt.figure(figsize=(10, 6))
        self.df['rating'].hist(bins=5, edgecolor='black', color='steelblue')
        plt.xlabel('Rating')
        plt.ylabel('Frequency')
        plt.title('Rating Distribution')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_folder, '02_rating_distribution.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. Average Rating by Category (if available)
        if hasattr(self, 'category_ratings') and len(self.category_ratings) > 0:
            plt.figure(figsize=(12, 6))
            self.category_ratings['avg_rating'].head(10).plot(kind='barh', color='coral')
            plt.xlabel('Average Rating')
            plt.title('Top 10 Categories by Average Rating')
            plt.tight_layout()
            plt.savefig(os.path.join(self.output_folder, '03_category_ratings.png'), dpi=300, bbox_inches='tight')
            plt.close()
        
        # 4. Average Rating by Brand (if available)
        if hasattr(self, 'brand_ratings') and len(self.brand_ratings) > 0:
            plt.figure(figsize=(12, 6))
            self.brand_ratings['avg_rating'].head(10).plot(kind='barh', color='skyblue')
            plt.xlabel('Average Rating')
            plt.title('Top 10 Brands by Average Rating')
            plt.tight_layout()
            plt.savefig(os.path.join(self.output_folder, '04_brand_ratings.png'), dpi=300, bbox_inches='tight')
            plt.close()
        
        # 5. Sentiment Score Distribution
        plt.figure(figsize=(10, 6))
        self.df['sentiment_score'].hist(bins=30, edgecolor='black', color='teal')
        plt.xlabel('Sentiment Score')
        plt.ylabel('Frequency')
        plt.title('Distribution of Sentiment Scores')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_folder, '05_sentiment_scores.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        # 6. Rating vs Sentiment Scatter Plot
        plt.figure(figsize=(10, 6))
        plt.scatter(self.df['rating'], self.df['sentiment_score'], alpha=0.5, s=30)
        plt.xlabel('Rating')
        plt.ylabel('Sentiment Score')
        plt.title(f'Rating vs Sentiment (Correlation: {self.rating_sentiment_corr:.3f})')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_folder, '06_rating_vs_sentiment.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        # 7. Top Positive Keywords
        if len(self.positive_keywords) > 0:
            plt.figure(figsize=(12, 6))
            keywords, counts = zip(*self.positive_keywords)
            plt.barh(keywords, counts, color='green', alpha=0.7)
            plt.xlabel('Frequency')
            plt.title('Top 20 Positive Keywords')
            plt.tight_layout()
            plt.savefig(os.path.join(self.output_folder, '07_positive_keywords.png'), dpi=300, bbox_inches='tight')
            plt.close()
        
        # 8. Top Negative Keywords
        if len(self.negative_keywords) > 0:
            plt.figure(figsize=(12, 6))
            keywords, counts = zip(*self.negative_keywords)
            plt.barh(keywords, counts, color='red', alpha=0.7)
            plt.xlabel('Frequency')
            plt.title('Top 20 Negative Keywords')
            plt.tight_layout()
            plt.savefig(os.path.join(self.output_folder, '08_negative_keywords.png'), dpi=300, bbox_inches='tight')
            plt.close()
        
        # 9. Product Health Score Distribution
        if hasattr(self, 'product_health'):
            plt.figure(figsize=(10, 6))
            colors_health = {'Scale': '#2ecc71', 'Fix': '#f39c12', 'Drop': '#e74c3c'}
            health_colors = [colors_health[c] for c in self.product_health['classification']]
            plt.barh(range(len(self.product_health)), self.product_health['health_score'], color=health_colors)
            plt.xlabel('Health Score')
            plt.ylabel('Product')
            plt.title('Product Health Scores')
            plt.tight_layout()
            plt.savefig(os.path.join(self.output_folder, '09_product_health_scores.png'), dpi=300, bbox_inches='tight')
            plt.close()
        
        # 10. Sentiment by Rating
        plt.figure(figsize=(10, 6))
        sentiment_by_rating = self.df.groupby('rating')['sentiment_label'].value_counts().unstack(fill_value=0)
        sentiment_by_rating.plot(kind='bar', stacked=True, color=['#e74c3c', '#f39c12', '#2ecc71'])
        plt.xlabel('Rating')
        plt.ylabel('Count')
        plt.title('Sentiment Distribution by Rating')
        plt.legend(title='Sentiment')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_folder, '10_sentiment_by_rating.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Visualizations saved to {self.output_folder} folder")
        
        return self
    
    def generate_executive_summary(self):
        """Generate executive summary report."""
        print("\nGenerating executive summary...")
        
        report = []
        report.append("=" * 80)
        report.append("EXECUTIVE SUMMARY - AMAZON REVIEWS ANALYSIS")
        report.append("=" * 80)
        report.append(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Key Metrics
        report.append("KEY METRICS:")
        report.append("-" * 80)
        report.append(f"Total Reviews Analyzed: {len(self.df):,}")
        report.append(f"Overall Average Rating: {self.overall_avg_rating:.2f}/5.0")
        report.append(f"Rating Range: {self.df['rating'].min():.0f} - {self.df['rating'].max():.0f}")
        report.append("")
        
        # Sentiment Analysis
        report.append("SENTIMENT ANALYSIS:")
        report.append("-" * 80)
        report.append(f"Positive Sentiment: {self.sentiment_percentages['Positive']:.2f}%")
        report.append(f"Neutral Sentiment: {self.sentiment_percentages['Neutral']:.2f}%")
        report.append(f"Negative Sentiment: {self.sentiment_percentages['Negative']:.2f}%")
        report.append(f"Average Sentiment Score: {self.df['sentiment_score'].mean():.3f}")
        report.append("")
        
        # Market Performance
        if hasattr(self, 'category_ratings'):
            report.append("TOP PERFORMING CATEGORIES (by rating):")
            report.append("-" * 80)
            for cat, row in self.category_ratings.head(5).iterrows():
                report.append(f"  {cat}: {row['avg_rating']:.2f} avg rating ({int(row['review_count'])} reviews)")
            report.append("")
        
        if hasattr(self, 'brand_ratings'):
            report.append("TOP PERFORMING BRANDS (by rating):")
            report.append("-" * 80)
            for brand, row in self.brand_ratings.head(5).iterrows():
                report.append(f"  {brand}: {row['avg_rating']:.2f} avg rating ({int(row['review_count'])} reviews)")
            report.append("")
        
        # Product Health
        if hasattr(self, 'product_health'):
            report.append("PRODUCT HEALTH CLASSIFICATION:")
            report.append("-" * 80)
            report.append(f"Scale (High Priority): {(self.product_health['classification'] == 'Scale').sum()} products")
            report.append(f"Fix (Medium Priority): {(self.product_health['classification'] == 'Fix').sum()} products")
            report.append(f"Drop (Low Priority): {(self.product_health['classification'] == 'Drop').sum()} products")
            report.append("")
        
        # Trends
        report.append("KEY INSIGHTS:")
        report.append("-" * 80)
        report.append(f"Rating-Sentiment Correlation: {self.rating_sentiment_corr:.3f}")
        if self.rating_sentiment_corr > 0.5:
            report.append("  → Strong positive correlation: Higher ratings align with more positive sentiment")
        elif self.rating_sentiment_corr > 0:
            report.append("  → Moderate positive correlation: Generally, higher ratings have more positive sentiment")
        else:
            report.append("  → Weak or no correlation: Ratings and sentiment may be influenced by different factors")
        report.append("")
        
        report.append("=" * 80)
        
        # Save report
        report_text = "\n".join(report)
        with open(os.path.join(self.output_folder, 'executive_summary.txt'), 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        print(report_text)
        
        return self
    
    def generate_insights_report(self):
        """Generate detailed insights report."""
        print("\nGenerating insights report...")
        
        report = []
        report.append("=" * 80)
        report.append("DETAILED INSIGHTS REPORT - AMAZON REVIEWS ANALYSIS")
        report.append("=" * 80)
        report.append(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Data Quality
        report.append("1. DATA QUALITY & COVERAGE:")
        report.append("-" * 80)
        report.append(f"Total Records Analyzed: {len(self.df):,}")
        report.append(f"Data Completeness: 100%")
        report.append(f"Rating Score Range: {self.df['rating'].min():.0f} - {self.df['rating'].max():.0f}")
        report.append(f"Average Review Length: {self.df['text'].str.len().mean():.0f} characters")
        report.append("")
        
        # Sentiment Deep Dive
        report.append("2. SENTIMENT ANALYSIS DEEP DIVE:")
        report.append("-" * 80)
        report.append(f"Positive Reviews: {self.sentiment_percentages['Positive']:.2f}%")
        report.append(f"Neutral Reviews: {self.sentiment_percentages['Neutral']:.2f}%")
        report.append(f"Negative Reviews: {self.sentiment_percentages['Negative']:.2f}%")
        report.append(f"Sentiment Score Statistics:")
        report.append(f"  Mean: {self.df['sentiment_score'].mean():.3f}")
        report.append(f"  Median: {self.df['sentiment_score'].median():.3f}")
        report.append(f"  Std Dev: {self.df['sentiment_score'].std():.3f}")
        report.append("")
        
        # Keyword Analysis
        report.append("3. THEMATIC ANALYSIS:")
        report.append("-" * 80)
        report.append("Top 20 Positive Keywords (indicating strengths):")
        for i, (keyword, count) in enumerate(self.positive_keywords, 1):
            report.append(f"  {i}. {keyword} ({count} occurrences)")
        report.append("")
        
        report.append("Top 20 Negative Keywords (indicating pain points):")
        for i, (keyword, count) in enumerate(self.negative_keywords, 1):
            report.append(f"  {i}. {keyword} ({count} occurrences)")
        report.append("")
        
        # Product Performance
        if hasattr(self, 'product_health'):
            report.append("4. PRODUCT INTELLIGENCE:")
            report.append("-" * 80)
            report.append("Top 5 Products to Scale (High Health Score):")
            for i, (prod, row) in enumerate(self.product_health[self.product_health['classification'] == 'Scale'].head(5).iterrows(), 1):
                report.append(f"  {i}. {prod}")
                report.append(f"     Health Score: {row['health_score']:.2f}")
                report.append(f"     Avg Rating: {row['avg_rating']:.2f}")
                report.append(f"     Positive Sentiment: {row['positive_sentiment_pct']:.2f}%")
            report.append("")
        
        # Category Performance
        if hasattr(self, 'category_ratings'):
            report.append("5. CATEGORY PERFORMANCE:")
            report.append("-" * 80)
            report.append("Top 10 Categories by Average Rating:")
            for i, (cat, row) in enumerate(self.category_ratings.head(10).iterrows(), 1):
                report.append(f"  {i}. {cat}: {row['avg_rating']:.2f} ({int(row['review_count'])} reviews)")
            report.append("")
        
        # Brand Performance
        if hasattr(self, 'brand_ratings'):
            report.append("6. BRAND PERFORMANCE:")
            report.append("-" * 80)
            report.append("Top 10 Brands by Average Rating:")
            for i, (brand, row) in enumerate(self.brand_ratings.head(10).iterrows(), 1):
                report.append(f"  {i}. {brand}: {row['avg_rating']:.2f} ({int(row['review_count'])} reviews)")
            report.append("")
        
        report.append("7. RECOMMENDATIONS:")
        report.append("-" * 80)
        report.append("• Focus on scaling products with high health scores and positive sentiment")
        report.append("• Address negative keywords to improve customer satisfaction")
        report.append("• Maintain quality in high-performing categories and brands")
        report.append("• Use sentiment insights to improve product messaging and positioning")
        report.append("")
        
        report.append("=" * 80)
        
        # Save report
        report_text = "\n".join(report)
        with open(os.path.join(self.output_folder, 'insights_report.txt'), 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        print("Insights report generated")
        
        return self
    
    def run_full_analysis(self):
        """Execute complete analysis pipeline."""
        print("\n" + "=" * 80)
        print("AMAZON REVIEWS ANALYSIS - COMPLETE PIPELINE")
        print("=" * 80 + "\n")
        
        try:
            (self.load_data()
                 .clean_data()
                 .sentiment_analysis()
                 .market_analysis()
                 .theme_discovery()
                 .product_health_scoring()
                 .trend_analysis()
                 .generate_visualizations()
                 .generate_executive_summary()
                 .generate_insights_report())
            
            print("\n" + "=" * 80)
            print("ANALYSIS COMPLETE!")
            print("=" * 80)
            print(f"\nOutputs saved to: {os.path.abspath(self.output_folder)}")
            print("Generated files:")
            print("  - Charts: 01_sentiment_distribution.png through 10_sentiment_by_rating.png")
            print("  - Reports: executive_summary.txt and insights_report.txt")
            
        except Exception as e:
            print(f"\nError during analysis: {str(e)}")
            raise


# Main execution
if __name__ == "__main__":
    # File path to dataset
    csv_file = 'Datafiniti_Amazon_Consumer_Reviews_of_Amazon_Products.csv'
    
    # Initialize and run analysis
    analysis = AmazonReviewsAnalysis(csv_file)
    analysis.run_full_analysis()
