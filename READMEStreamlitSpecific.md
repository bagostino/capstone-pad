# Streamlit Dashboard — E-Commerce Revenue Analysis

## Overview

This repository includes an interactive Streamlit dashboard (`app.py`) that presents the key findings from my capstone analysis in a visual, executive-ready format.

---

## How to Run

From the root of this repository:

```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

---

## App Structure

The dashboard is organized into five tabs:

| Tab | Content |
|-----|---------|
| **Revenue Overview** | Revenue distribution histogram, monthly trend line, weekday vs. weekend comparison |
| **Discount Strategy** | Avg revenue by discount status, discount frequency pie chart, discount rate by customer segment |
| **Customer Segments** | Total and avg revenue by segment, VIP × discount cross-cut chart |
| **Marketing Channels** | Avg revenue and transaction volume by channel, product category revenue comparison |
| **Modeling & Correlation** | Interactive correlation heatmap, linear regression coefficient chart, full recommendations summary table |

A sidebar allows filtering by customer segment, product category, marketing channel, region, and discount status. All charts and KPIs update dynamically with filter selections.

---

## A Note on How This Was Built — For the Instructor

The original analysis notebook (`notebooks/capstone_starter_notebook.ipynb`) was written entirely by me. All problem framing, data cleaning decisions, EDA, statistical tests, and written insights are my own work.

The Streamlit dashboard (`app.py`) was built with the assistance of **GitHub Copilot Chat** inside VS Code. I use Streamlit professionally at work and am familiar with it, so I knew exactly what I wanted to produce — I used Copilot as a coding assistant to help me build it efficiently.

Specifically, I prompted Copilot to:
- **Read through my entire notebook** without touching or editing it
- **Build a complete, interactive Streamlit app** that surfaced my main findings visually
- Use **Plotly** for all charts (which is the standard I use at work)
- Reflect the **actual insights and recommendations** from my analysis — not generate new ones

I explicitly instructed Copilot not to modify the original notebook at any point. The analytical thinking, conclusions, and recommendations in both the notebook and the dashboard are mine. Copilot translated them into a working front-end application.

This reflects how AI coding tools are actually used in professional data roles — not to replace analytical thinking, but to accelerate implementation of well-defined deliverables.
