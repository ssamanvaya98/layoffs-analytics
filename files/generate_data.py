"""
generate_data.py
Generates synthetic layoff data mirroring:
  - Kaggle (Swaptr) dataset structure (2020-2025)
  - layoffs.fyi structure
  - Indian Layoffs Tracker structure

Run once: python generate_data.py
Produces:  data/layoffs_global.csv  &  data/layoffs_india.csv

When you obtain the real CSVs, drop them into /data/ with the same
column names and the app will work without any other changes.
"""

import pandas as pd
import numpy as np
import os

os.makedirs("data", exist_ok=True)
rng = np.random.default_rng(42)

# ── helpers ──────────────────────────────────────────────────────────────────
def rand_dates(start, end, n):
    s = pd.Timestamp(start).value
    e = pd.Timestamp(end).value
    return pd.to_datetime(rng.integers(s, e, n))

# ── reference tables ─────────────────────────────────────────────────────────
COMPANIES = [
    ("Amazon", "USA", "Seattle"), ("Google", "USA", "San Francisco"),
    ("Meta", "USA", "San Francisco"), ("Microsoft", "USA", "Seattle"),
    ("Twitter", "USA", "San Francisco"), ("Salesforce", "USA", "San Francisco"),
    ("Stripe", "USA", "San Francisco"), ("Lyft", "USA", "San Francisco"),
    ("Uber", "USA", "San Francisco"), ("Airbnb", "USA", "San Francisco"),
    ("Netflix", "USA", "Los Angeles"), ("Spotify", "Sweden", "Stockholm"),
    ("Shopify", "Canada", "Ottawa"), ("Coinbase", "USA", "San Francisco"),
    ("Robinhood", "USA", "San Francisco"), ("Snap", "USA", "Los Angeles"),
    ("Pinterest", "USA", "San Francisco"), ("Zoom", "USA", "San Jose"),
    ("Dropbox", "USA", "San Francisco"), ("Box", "USA", "San Francisco"),
    ("Intel", "USA", "Santa Clara"), ("Dell", "USA", "Austin"),
    ("IBM", "USA", "New York"), ("Cisco", "USA", "San Jose"),
    ("SAP", "Germany", "Walldorf"), ("Siemens", "Germany", "Munich"),
    ("HSBC", "UK", "London"), ("Barclays", "UK", "London"),
    ("Philips", "Netherlands", "Amsterdam"), ("Nokia", "Finland", "Espoo"),
    ("ByteDance", "China", "Beijing"), ("Alibaba", "China", "Hangzhou"),
    ("Grab", "Singapore", "Singapore"), ("Sea", "Singapore", "Singapore"),
    ("Gojek", "Indonesia", "Jakarta"), ("Tokopedia", "Indonesia", "Jakarta"),
    ("Flipkart", "India", "Bengaluru"), ("Byju's", "India", "Bengaluru"),
    ("Ola", "India", "Bengaluru"), ("Zomato", "India", "NCR Delhi"),
    ("Paytm", "India", "NCR Delhi"), ("Meesho", "India", "Bengaluru"),
    ("ShareChat", "India", "Bengaluru"), ("Unacademy", "India", "Bengaluru"),
    ("Swiggy", "India", "Bengaluru"), ("PhonePe", "India", "Bengaluru"),
    ("CRED", "India", "Bengaluru"), ("Razorpay", "India", "Bengaluru"),
    ("Dunzo", "India", "Bengaluru"), ("Urban Company", "India", "NCR Delhi"),
    ("Vedantu", "India", "Bengaluru"), ("Lenskart", "India", "NCR Delhi"),
    ("Nykaa", "India", "Mumbai"), ("Cars24", "India", "NCR Delhi"),
    ("InMobi", "India", "Bengaluru"), ("Freshworks", "India", "Chennai"),
    ("Infosys BPM", "India", "Bengaluru"), ("Wipro", "India", "Bengaluru"),
    ("HCL Tech", "India", "NCR Delhi"), ("TCS", "India", "Mumbai"),
]

INDUSTRIES = {
    "FinTech": ["Coinbase", "Robinhood", "Stripe", "Paytm", "PhonePe", "Razorpay", "CRED"],
    "EdTech": ["Byju's", "Unacademy", "Vedantu"],
    "Retail/E-Commerce": ["Amazon", "Flipkart", "Shopify", "Meesho", "Nykaa", "Cars24"],
    "Transportation": ["Uber", "Lyft", "Ola", "Grab", "Gojek"],
    "Food/Delivery": ["Zomato", "Swiggy", "Dunzo"],
    "Social Media": ["Meta", "Twitter", "Snap", "Pinterest", "ShareChat"],
    "Cloud/SaaS": ["Salesforce", "Zoom", "Dropbox", "Box", "Freshworks"],
    "Hardware": ["Intel", "Dell", "IBM", "Cisco", "Nokia", "Philips"],
    "Consumer Tech": ["Netflix", "Spotify", "Airbnb"],
    "IT Services": ["Infosys BPM", "Wipro", "HCL Tech", "TCS", "InMobi"],
    "Other": ["Lenskart", "Urban Company", "HSBC", "Barclays", "SAP",
              "Siemens", "ByteDance", "Alibaba", "Sea", "Tokopedia"],
}

STAGES = ["Seed", "Series A", "Series B", "Series C", "Series D",
          "Series E", "Series F", "Post-IPO", "Private Equity", "Acquired"]

company_to_industry = {c: ind for ind, cs in INDUSTRIES.items() for c in cs}

# ── global dataset ────────────────────────────────────────────────────────────
n_global = 2800
company_rows = [COMPANIES[i % len(COMPANIES)] for i in rng.integers(0, len(COMPANIES), n_global)]
companies, countries, locations = zip(*company_rows)

# date distribution: surge in 2022-23, persistent in 2024-26
date_pool = (
    list(rand_dates("2020-03-01", "2021-12-31", 300)) +
    list(rand_dates("2022-01-01", "2022-12-31", 600)) +
    list(rand_dates("2023-01-01", "2023-12-31", 700)) +
    list(rand_dates("2024-01-01", "2024-12-31", 500)) +
    list(rand_dates("2025-01-01", "2025-12-31", 500)) +
    list(rand_dates("2026-01-01", "2026-04-15", 200))
)
rng.shuffle(date_pool)
dates = date_pool[:n_global]

total_laid_off = rng.integers(50, 15000, n_global).astype(float)
total_laid_off[rng.random(n_global) < 0.08] = np.nan  # ~8% missing

pct_laid_off = np.clip(rng.normal(0.12, 0.08, n_global), 0.01, 1.0).round(2)
pct_laid_off[rng.random(n_global) < 0.10] = np.nan

funds_raised = rng.integers(5, 50000, n_global).astype(float)
funds_raised[rng.random(n_global) < 0.12] = np.nan

global_df = pd.DataFrame({
    "company":          companies,
    "location":         locations,
    "industry":         [company_to_industry.get(c, "Other") for c in companies],
    "total_laid_off":   total_laid_off,
    "percentage_laid_off": pct_laid_off,
    "date":             pd.to_datetime(dates).strftime("%Y-%m-%d"),
    "stage":            rng.choice(STAGES, n_global),
    "country":          countries,
    "funds_raised_millions": funds_raised,
})
global_df.to_csv("data/layoffs_global.csv", index=False)
print(f"✅  data/layoffs_global.csv  ({len(global_df):,} rows)")

# ── india-specific dataset ────────────────────────────────────────────────────
INDIA_COMPANIES = [c for c, country, _ in COMPANIES if country == "India"]
INDIA_CITIES = ["Bengaluru", "NCR Delhi", "Mumbai", "Hyderabad", "Pune", "Chennai"]

n_india = 800
india_companies = rng.choice(INDIA_COMPANIES, n_india)
india_cities    = rng.choice(INDIA_CITIES, n_india, p=[0.40, 0.25, 0.15, 0.10, 0.05, 0.05])

india_date_pool = (
    list(rand_dates("2020-03-01", "2021-12-31", 80)) +
    list(rand_dates("2022-01-01", "2022-12-31", 180)) +
    list(rand_dates("2023-01-01", "2023-12-31", 200)) +
    list(rand_dates("2024-01-01", "2024-12-31", 160)) +
    list(rand_dates("2025-01-01", "2025-12-31", 130)) +
    list(rand_dates("2026-01-01", "2026-04-15", 50))
)
rng.shuffle(india_date_pool)
india_dates = india_date_pool[:n_india]

india_laid_off = rng.integers(20, 5000, n_india).astype(float)
india_laid_off[rng.random(n_india) < 0.08] = np.nan

india_df = pd.DataFrame({
    "company":        india_companies,
    "city":           india_cities,
    "industry":       [company_to_industry.get(c, "Other") for c in india_companies],
    "total_laid_off": india_laid_off,
    "date":           pd.to_datetime(india_dates).strftime("%Y-%m-%d"),
    "country":        "India",
    "stage":          rng.choice(STAGES, n_india),
    "funds_raised_millions": rng.integers(1, 5000, n_india).astype(float),
})
india_df.to_csv("data/layoffs_india.csv", index=False)
print(f"✅  data/layoffs_india.csv   ({len(india_df):,} rows)")
print("\nDone! Replace these CSVs with the real datasets anytime — column names match.")
