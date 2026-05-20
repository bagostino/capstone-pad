"""
Capstone Findings Dashboard — E-Commerce Revenue Analysis
Streamlit app based on capstone_starter_notebook.ipynb
"""

import streamlit as st
import polars as pl
import polars.selectors as cs
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from pathlib import Path

# ── Brand palette (mirrors ESG_Python Update/Scripts/brand_colors.py) ──────────
BRAND_PALETTE = [
    "#002A41",  # 0 Dark Navy
    "#9C6E02",  # 1 Dark Gold
    "#035D6D",  # 2 Teal
    "#7F7F7F",  # 3 Grey
    "#025785",  # 4 Blue
    "#B3872D",  # 5 Light Gold
    "#067E92",  # 6 Mid Teal
    "#ACACAA",  # 7 Light Grey
]


def palette_colors(categories: list[str]) -> dict[str, str]:
    """Return a {category: hex} map using brand colors positionally."""
    return {cat: BRAND_PALETTE[i % len(BRAND_PALETTE)] for i, cat in enumerate(categories)}


# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="E-Commerce Revenue Analysis",
    layout="wide",
    page_icon="📊",
)

DATA_PATH = Path(__file__).parent / "data" / "raw" / "capstone_dataset.csv"


# ── Data loading & cleaning ────────────────────────────────────────────────────
@st.cache_data
def load_and_clean() -> pl.DataFrame:
    df = pl.read_csv(DATA_PATH, try_parse_dates=True)

    df = (
        df
        # fill missing discount with 0 (no discount applied)
        .with_columns(pl.col("discount_applied").fill_null(0.0))
        # derived columns
        .with_columns([
            # estimated revenue after discount
            (pl.col("product_price") * pl.col("quantity") * (1 - pl.col("discount_applied")))
            .alias("estimated_revenue"),
            # month label for time-series
            pl.col("date").dt.strftime("%Y-%m").alias("month"),
            # weekend flag (5=Sat, 6=Sun)
            pl.col("date").dt.weekday().is_in([5, 6]).cast(pl.Int8).alias("is_weekend"),
            # binary discount flag
            (pl.col("discount_applied") > 0).cast(pl.Int8).alias("binary_discount"),
            # revenue per unit
            (pl.col("total_revenue") / pl.col("quantity")).alias("revenue_per_unit"),
            # VIP flag
            (pl.col("customer_segment") == "VIP").cast(pl.Int8).alias("is_vip"),
        ])
    )
    return df


# ── Load data ──────────────────────────────────────────────────────────────────
with st.spinner("Loading data..."):
    try:
        df = load_and_clean()
    except Exception as e:
        st.error(f"Could not load dataset: {e}")
        st.stop()

# ── Sidebar filters ────────────────────────────────────────────────────────────
st.sidebar.title("Filters")

all_segments = sorted(df["customer_segment"].unique().to_list())
selected_segments = st.sidebar.multiselect(
    "Customer Segment", all_segments, default=all_segments
)

all_categories = sorted(df["product_category"].unique().to_list())
selected_categories = st.sidebar.multiselect(
    "Product Category", all_categories, default=all_categories
)

all_channels = sorted(df["marketing_channel"].unique().to_list())
selected_channels = st.sidebar.multiselect(
    "Marketing Channel", all_channels, default=all_channels
)

all_regions = sorted(df["region"].unique().to_list())
selected_regions = st.sidebar.multiselect(
    "Region", all_regions, default=all_regions
)

discount_filter = st.sidebar.radio(
    "Discount Status", ["All", "Discounted Only", "No Discount Only"], index=0
)

# Apply filters
dff = df.filter(
    pl.col("customer_segment").is_in(selected_segments)
    & pl.col("product_category").is_in(selected_categories)
    & pl.col("marketing_channel").is_in(selected_channels)
    & pl.col("region").is_in(selected_regions)
)
if discount_filter == "Discounted Only":
    dff = dff.filter(pl.col("binary_discount") == 1)
elif discount_filter == "No Discount Only":
    dff = dff.filter(pl.col("binary_discount") == 0)

# ── Title & KPIs ───────────────────────────────────────────────────────────────
st.title("📊 E-Commerce Revenue Analysis")
st.caption("Capstone findings — FY 2025 transaction data  |  Audience: CFO, CMO, Head of Sales")

total_rev = dff["total_revenue"].sum()
avg_rev = dff["total_revenue"].mean()
txn_count = len(dff)
discount_pct = dff["binary_discount"].mean() * 100
return_rate = dff["returned"].mean() * 100

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Revenue", f"${total_rev:,.0f}")
k2.metric("Avg Rev / Transaction", f"${avg_rev:,.0f}")
k3.metric("Transactions", f"{txn_count:,}")
k4.metric("Discount Rate", f"{discount_pct:.1f}%")
k5.metric("Return Rate", f"{return_rate:.1f}%")

st.divider()

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Revenue Overview",
    "💸 Discount Strategy",
    "👤 Customer Segments",
    "📣 Marketing Channels",
    "🔬 Modeling & Correlation",
])


# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — Revenue Overview
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    st.subheader("Revenue Overview")
    col_left, col_right = st.columns(2)

    # Histogram of revenue distribution
    with col_left:
        fig_hist = px.histogram(
            dff,
            x="total_revenue",
            nbins=20,
            title="Distribution of Total Revenue per Transaction",
            labels={"total_revenue": "Total Revenue ($)"},
            color_discrete_sequence=[BRAND_PALETTE[0]],
        )
        fig_hist.update_layout(bargap=0.05, showlegend=False)
        st.plotly_chart(fig_hist, use_container_width=True)
        st.caption(
            "**Insight:** Strong right skew — a small number of large transactions "
            "($1k–$2.5k) drive a disproportionate share of revenue."
        )

    # Monthly revenue trend
    with col_right:
        monthly = (
            dff.group_by("month")
            .agg(pl.col("total_revenue").sum().alias("revenue"))
            .sort("month")
        )
        fig_trend = px.line(
            monthly,
            x="month",
            y="revenue",
            title="Monthly Revenue Trend",
            labels={"month": "Month", "revenue": "Total Revenue ($)"},
            color_discrete_sequence=[BRAND_PALETTE[2]],
            markers=True,
        )
        fig_trend.update_xaxes(tickangle=45)
        st.plotly_chart(fig_trend, use_container_width=True)

    # Weekend vs Weekday
    st.subheader("Weekday vs. Weekend")
    weekend_summary = (
        dff.group_by("is_weekend")
        .agg([
            pl.len().alias("transactions"),
            pl.col("total_revenue").sum().alias("total_revenue"),
            pl.col("total_revenue").mean().alias("avg_revenue"),
        ])
        .with_columns(
            pl.when(pl.col("is_weekend") == 1)
            .then(pl.lit("Weekend"))
            .otherwise(pl.lit("Weekday"))
            .alias("Day Type")
        )
        .sort("is_weekend")
    )

    wk_col1, wk_col2 = st.columns(2)
    with wk_col1:
        color_map = palette_colors(["Weekday", "Weekend"])
        fig_wk_txn = px.bar(
            weekend_summary,
            x="Day Type",
            y="transactions",
            color="Day Type",
            color_discrete_map=color_map,
            title="Transaction Count by Day Type",
            labels={"transactions": "Transactions"},
        )
        fig_wk_txn.update_layout(showlegend=False)
        st.plotly_chart(fig_wk_txn, use_container_width=True)
    with wk_col2:
        fig_wk_rev = px.bar(
            weekend_summary,
            x="Day Type",
            y="avg_revenue",
            color="Day Type",
            color_discrete_map=color_map,
            title="Avg Revenue per Transaction by Day Type",
            labels={"avg_revenue": "Avg Revenue ($)"},
        )
        fig_wk_rev.update_layout(showlegend=False)
        st.plotly_chart(fig_wk_rev, use_container_width=True)
    st.caption(
        "**Finding:** Weekday vs. weekend timing is **not** a meaningful revenue lever. "
        "Values are essentially identical — the company should not invest in weekend-specific campaigns."
    )

    st.dataframe(
        weekend_summary.select(["Day Type", "transactions", "avg_revenue", "total_revenue"])
        .rename({"transactions": "Transactions", "avg_revenue": "Avg Revenue ($)", "total_revenue": "Total Revenue ($)"}),
        use_container_width=True,
        hide_index=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — Discount Strategy
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    st.subheader("Discount Strategy Analysis")
    st.markdown(
        "> **Key Finding:** Discounts are applied to ~67% of transactions and statistically reduce "
        "per-transaction revenue by 23% on average. A two-sample t-test confirmed this gap is "
        "significant (p = 0.0004). Discounts do **not** drive higher purchase volume or larger baskets."
    )

    disc_summary = (
        dff.group_by("binary_discount")
        .agg([
            pl.len().alias("Transactions"),
            pl.col("total_revenue").mean().alias("Avg Revenue ($)"),
            pl.col("total_revenue").median().alias("Median Revenue ($)"),
            pl.col("quantity").mean().alias("Avg Quantity"),
            pl.col("returned").mean().alias("Return Rate"),
        ])
        .with_columns(
            pl.when(pl.col("binary_discount") == 1)
            .then(pl.lit("Discounted"))
            .otherwise(pl.lit("No Discount"))
            .alias("Discount Status")
        )
        .sort("binary_discount")
    )

    d1, d2 = st.columns(2)
    disc_color_map = palette_colors(["No Discount", "Discounted"])

    with d1:
        fig_disc_rev = px.bar(
            disc_summary,
            x="Discount Status",
            y="Avg Revenue ($)",
            color="Discount Status",
            color_discrete_map=disc_color_map,
            title="Avg Revenue: Discounted vs. Non-Discounted",
            text_auto=".0f",
        )
        fig_disc_rev.update_traces(textposition="outside")
        fig_disc_rev.update_layout(showlegend=False)
        st.plotly_chart(fig_disc_rev, use_container_width=True)

    with d2:
        fig_disc_count = px.pie(
            disc_summary,
            names="Discount Status",
            values="Transactions",
            title="Share of Transactions: Discounted vs. Non-Discounted",
            color="Discount Status",
            color_discrete_map=disc_color_map,
            hole=0.4,
        )
        st.plotly_chart(fig_disc_count, use_container_width=True)

    # Discount rate by segment
    st.subheader("Discount Frequency by Customer Segment")
    disc_seg = (
        dff.group_by("customer_segment")
        .agg(
            pl.col("binary_discount").mean().alias("Discount Rate"),
            pl.len().alias("Transactions"),
            pl.col("total_revenue").mean().alias("Avg Revenue ($)"),
        )
        .sort("Discount Rate", descending=True)
    )
    present_segs = disc_seg["customer_segment"].to_list()
    seg_color_map = palette_colors(present_segs)

    fig_disc_seg = px.bar(
        disc_seg,
        x="customer_segment",
        y="Discount Rate",
        color="customer_segment",
        color_discrete_map=seg_color_map,
        title="% of Transactions with a Discount by Segment",
        labels={"customer_segment": "Segment", "Discount Rate": "% with Discount"},
        text_auto=".1%",
    )
    fig_disc_seg.update_layout(showlegend=False, yaxis_tickformat=".0%")
    fig_disc_seg.update_traces(textposition="outside")
    st.plotly_chart(fig_disc_seg, use_container_width=True)
    st.caption(
        "**VIPs receive the most discounts (~73%)** and experience the largest revenue drop when "
        "discounted. The CFO should consider reducing overall discount frequency meaningfully "
        "(proposed: from 67% → ~30%)."
    )

    st.dataframe(
        disc_summary.select(["Discount Status", "Transactions", "Avg Revenue ($)", "Avg Quantity", "Return Rate"])
        .with_columns(pl.col("Return Rate").round(3)),
        use_container_width=True,
        hide_index=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — Customer Segments
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    st.subheader("Customer Segment Analysis")
    st.markdown(
        "> **Surprising Finding:** VIPs make up only ~17% of transactions but appear to generate "
        "meaningful revenue. However, **two independent t-tests confirmed VIP status has no "
        "statistically significant effect** on per-transaction OR annual revenue (p ≈ 0.98). "
        "The VIP designation needs to be audited."
    )

    seg_summary = (
        dff.group_by("customer_segment")
        .agg([
            pl.len().alias("Transactions"),
            pl.col("total_revenue").sum().alias("Total Revenue ($)"),
            pl.col("total_revenue").mean().alias("Avg Revenue ($)"),
            pl.col("total_revenue").median().alias("Median Revenue ($)"),
            pl.col("quantity").mean().alias("Avg Quantity"),
            pl.col("returned").mean().alias("Return Rate"),
        ])
        .sort("Total Revenue ($)", descending=True)
    )

    s1, s2 = st.columns(2)

    seg_order = seg_summary["customer_segment"].to_list()
    seg_color_map = palette_colors(seg_order)

    with s1:
        fig_seg_total = px.bar(
            seg_summary,
            x="customer_segment",
            y="Total Revenue ($)",
            color="customer_segment",
            color_discrete_map=seg_color_map,
            title="Total Revenue by Customer Segment",
            text_auto=".2s",
        )
        fig_seg_total.update_layout(showlegend=False)
        fig_seg_total.update_traces(textposition="outside")
        st.plotly_chart(fig_seg_total, use_container_width=True)

    with s2:
        fig_seg_avg = px.bar(
            seg_summary,
            x="customer_segment",
            y="Avg Revenue ($)",
            color="customer_segment",
            color_discrete_map=seg_color_map,
            title="Avg Revenue per Transaction by Segment",
            text_auto=".0f",
        )
        fig_seg_avg.update_layout(showlegend=False)
        fig_seg_avg.update_traces(textposition="outside")
        st.plotly_chart(fig_seg_avg, use_container_width=True)

    # VIP discount cross-cut
    st.subheader("VIP Revenue Impact of Discounts")
    disc_cross = (
        dff.group_by(["customer_segment", "binary_discount"])
        .agg(
            pl.len().alias("Transactions"),
            pl.col("total_revenue").mean().alias("Avg Revenue ($)"),
            pl.col("quantity").mean().alias("Avg Qty"),
        )
        .with_columns(
            pl.when(pl.col("binary_discount") == 1)
            .then(pl.lit("Discounted"))
            .otherwise(pl.lit("No Discount"))
            .alias("Discount Status")
        )
        .sort(["customer_segment", "binary_discount"])
    )

    disc_cross_color = palette_colors(["No Discount", "Discounted"])
    fig_cross = px.bar(
        disc_cross,
        x="customer_segment",
        y="Avg Revenue ($)",
        color="Discount Status",
        barmode="group",
        color_discrete_map=disc_cross_color,
        title="Avg Revenue per Transaction: Discount × Segment",
        labels={"customer_segment": "Segment"},
        text_auto=".0f",
    )
    fig_cross.update_traces(textposition="outside")
    st.plotly_chart(fig_cross, use_container_width=True)

    st.dataframe(
        seg_summary.with_columns(pl.col("Return Rate").round(3)),
        use_container_width=True,
        hide_index=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — Marketing Channels
# ─────────────────────────────────────────────────────────────────────────────
with tab4:
    st.subheader("Marketing Channel Analysis")
    st.markdown(
        "> **Key Finding:** Marketing channel is the **strongest acquisition lever**. "
        "Paid Search delivers the highest avg revenue per transaction; Social Media offers "
        "the best combination of volume and value. Product category shows almost no variation."
    )

    channel_summary = (
        dff.group_by("marketing_channel")
        .agg([
            pl.len().alias("Transactions"),
            pl.col("total_revenue").mean().alias("Avg Revenue ($)"),
            pl.col("total_revenue").sum().alias("Total Revenue ($)"),
            pl.col("returned").mean().alias("Return Rate"),
        ])
        .sort("Avg Revenue ($)", descending=True)
    )

    ch_order = channel_summary["marketing_channel"].to_list()
    ch_color_map = palette_colors(ch_order)

    c1, c2 = st.columns(2)

    with c1:
        fig_ch_avg = px.bar(
            channel_summary,
            x="Avg Revenue ($)",
            y="marketing_channel",
            color="marketing_channel",
            color_discrete_map=ch_color_map,
            orientation="h",
            title="Avg Revenue per Transaction by Channel",
            labels={"marketing_channel": "Channel"},
            text_auto=".0f",
        )
        fig_ch_avg.update_layout(showlegend=False, yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig_ch_avg, use_container_width=True)

    with c2:
        fig_ch_vol = px.bar(
            channel_summary,
            x="Transactions",
            y="marketing_channel",
            color="marketing_channel",
            color_discrete_map=ch_color_map,
            orientation="h",
            title="Transaction Volume by Channel",
            labels={"marketing_channel": "Channel"},
            text_auto="d",
        )
        fig_ch_vol.update_layout(showlegend=False, yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig_ch_vol, use_container_width=True)

    # Product category
    st.subheader("Product Category Analysis")
    cat_summary = (
        dff.group_by("product_category")
        .agg([
            pl.len().alias("Transactions"),
            pl.col("total_revenue").mean().alias("Avg Revenue ($)"),
            pl.col("total_revenue").sum().alias("Total Revenue ($)"),
        ])
        .sort("Avg Revenue ($)", descending=True)
    )
    cat_order = cat_summary["product_category"].to_list()
    cat_color_map = palette_colors(cat_order)

    fig_cat = px.bar(
        cat_summary,
        x="product_category",
        y="Avg Revenue ($)",
        color="product_category",
        color_discrete_map=cat_color_map,
        title="Avg Revenue per Transaction by Product Category",
        labels={"product_category": "Category"},
        text_auto=".0f",
    )
    fig_cat.update_layout(showlegend=False)
    fig_cat.update_traces(textposition="outside")
    st.plotly_chart(fig_cat, use_container_width=True)
    st.caption(
        "**Product category is not a lever.** Revenue and transaction counts are nearly identical "
        "across all six categories (~$680–$820 avg). The CMO should not change product mix."
    )

    col_ch, col_cat = st.columns(2)
    with col_ch:
        st.dataframe(
            channel_summary.with_columns(pl.col("Return Rate").round(3)),
            use_container_width=True,
            hide_index=True,
        )
    with col_cat:
        st.dataframe(cat_summary, use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 5 — Modeling & Correlation
# ─────────────────────────────────────────────────────────────────────────────
with tab5:
    st.subheader("Correlation Matrix")

    numeric_cols = [
        "product_price", "quantity", "discount_applied", "binary_discount",
        "total_revenue", "customer_satisfaction", "returned", "revenue_per_unit", "is_vip",
    ]

    # Drop rows with nulls in the numeric columns for correlation
    df_corr = dff.select(numeric_cols).drop_nulls()
    corr_pd = df_corr.to_pandas().corr()

    fig_corr = px.imshow(
        corr_pd,
        text_auto=".2f",
        color_continuous_scale=[
            [0.0, BRAND_PALETTE[1]],     # Dark Gold — strong negative
            [0.5, "#FFFFFF"],             # white — zero
            [1.0, BRAND_PALETTE[0]],     # Dark Navy — strong positive
        ],
        zmin=-1,
        zmax=1,
        title="Correlation Matrix — Key Variables",
        aspect="auto",
    )
    fig_corr.update_layout(height=550)
    st.plotly_chart(fig_corr, use_container_width=True)

    st.markdown("""
    **Correlation Matrix Highlights:**
    - **Product price (0.73) and quantity (0.66)** are the strongest positive revenue drivers.
    - **Discounts show a weak negative correlation (−0.17)** — confirms discounting erodes revenue without driving volume.
    - **VIP status has near-zero correlation with per-transaction revenue** — VIPs are not bigger spenders per transaction.
    - **Returns are the weakest correlate with transaction size** — not a factor worth prioritizing.
    """)

    st.divider()
    st.subheader("Linear Regression — Revenue Drivers")
    st.markdown(
        "A linear regression model was fitted on an 80/20 train/test split. "
        "The model achieved **R² ≈ 0.897** on the test set, confirming these five variables "
        "explain ~90% of variation in transaction revenue."
    )

    # Fit regression using numpy (no sklearn dependency required)
    reg_features = ["product_price", "quantity", "discount_applied", "is_vip", "binary_discount"]
    df_model = dff.select(reg_features + ["total_revenue"]).drop_nulls()

    X = df_model.select(reg_features).to_numpy()
    y = df_model["total_revenue"].to_numpy()

    # Add intercept column
    X_b = np.column_stack([np.ones(len(X)), X])
    try:
        coeffs, *_ = np.linalg.lstsq(X_b, y, rcond=None)
        intercept = coeffs[0]
        coef_values = coeffs[1:]
        y_pred = X_b @ coeffs
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - y.mean()) ** 2)
        r2 = 1 - ss_res / ss_tot

        coef_df = pl.DataFrame({
            "Variable": reg_features,
            "Coefficient ($)": [round(float(c), 2) for c in coef_values],
        }).sort("Coefficient ($)", descending=True)

        coef_order = coef_df["Variable"].to_list()
        coef_color_map = palette_colors(coef_order)

        fig_coef = px.bar(
            coef_df,
            x="Variable",
            y="Coefficient ($)",
            color="Variable",
            color_discrete_map=coef_color_map,
            title=f"Regression Coefficients (R² = {r2:.3f})",
            text_auto=".1f",
        )
        fig_coef.add_hline(y=0, line_dash="dash", line_color=BRAND_PALETTE[3])
        fig_coef.update_layout(showlegend=False)
        fig_coef.update_traces(textposition="outside")
        st.plotly_chart(fig_coef, use_container_width=True)

        r2_col, int_col = st.columns(2)
        r2_col.metric("Model R²", f"{r2:.3f}")
        int_col.metric("Intercept ($)", f"{intercept:.2f}")

        st.dataframe(coef_df, use_container_width=True, hide_index=True)
    except Exception as e:
        st.warning(f"Could not compute regression: {e}")

    st.markdown("""
    **Regression Takeaways:**
    - **Quantity and product price are the dominant positive drivers** of revenue.
    - **discount_applied carries the largest negative coefficient** — each percentage point of discount 
      meaningfully reduces transaction revenue.
    - **VIP status coefficient is near zero**, statistically validating that the current VIP designation 
      does not predict higher revenue.
    """)

    st.divider()
    st.subheader("Recommendations Summary")
    st.markdown("""
    | Stakeholder | Recommendation |
    |-------------|----------------|
    | **CFO** | Reduce discount frequency from ~67% → ~30%; test targeted markets before full rollout |
    | **Head of Sales** | Audit VIP designation criteria — current labels do not identify behaviorally differentiated customers |
    | **CMO** | Scale Paid Search and Social Media investment; do not reallocate budgets toward specific product categories |
    | **All** | Do not invest in weekend-specific promotions or staffing — timing is not a meaningful lever |
    """)
