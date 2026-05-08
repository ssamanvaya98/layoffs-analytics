# Navigating the Shift — Tech Layoffs Visual Analytics
**IIT Delhi | Entry 2025EEY7601 | Soumya Samanvaya**

---

## 🚀 Quick Start (3 steps)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate synthetic data (or drop real CSVs into /data/)
python generate_data.py

# 3. Run the app
streamlit run app.py
```

The app opens at **http://localhost:8501**

---

## 📁 Project Structure

```
layoffs_app/
├── app.py               ← Main Streamlit application
├── generate_data.py     ← Synthetic dataset generator
├── requirements.txt     ← Python dependencies
├── README.md
└── data/
    ├── layoffs_global.csv   ← Global dataset (Kaggle/layoffs.fyi format)
    └── layoffs_india.csv    ← India-specific dataset
```

---

## 🔄 Replacing with Real Data

Drop your real CSVs into `/data/` with these columns:

### `layoffs_global.csv`
| Column | Type | Description |
|--------|------|-------------|
| `company` | str | Company name |
| `location` | str | HQ city |
| `industry` | str | Industry sector |
| `total_laid_off` | float | # employees laid off |
| `percentage_laid_off` | float | Fraction (0.0–1.0) |
| `date` | YYYY-MM-DD | Event date |
| `stage` | str | Funding stage |
| `country` | str | Full country name |
| `funds_raised_millions` | float | Funds in $M |

### `layoffs_india.csv`
Same as above but with an extra `city` column (Bengaluru, NCR Delhi, etc.)

---

## 📊 Features

| Tab | Visualization |
|-----|--------------|
| 🌍 Global Map | Choropleth + Top-10 bar chart |
| 🇮🇳 India Hub | Bubble geo-map + area chart per city |
| 🏭 Industry | Sunburst + Donut + Funding stage bar |
| 📅 Temporal | Monthly trend + rolling avg + animated choropleth + heatmap |
| ⚖️ Comparison | Side-by-side line chart + KPI cards + radar chart |

All charts are **fully interactive** (zoom, pan, hover, filter).

---

## 🎛️ Sidebar Controls

- **Year range slider** (2020–2026)
- **Industry multi-select**
- **Funding stage multi-select**
- **Comparison mode**: Company vs Company or City vs City

---

## 📦 Data Sources (for final submission)

1. **Kaggle (Swaptr)** — https://www.kaggle.com/datasets/swaptr/layoffs-2022
2. **Layoffs.fyi** — https://layoffs.fyi (manual export)
3. **Indian Layoffs Tracker** — https://github.com/search?q=india+layoffs+dataset
