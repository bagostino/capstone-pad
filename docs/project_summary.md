 ## 11. Final Project Summary


**1. Problem Statement**
This project analyzed transaction-level data for an e-commerce company to identify the top customer, product, and pricing levers the company should prioritize in FY 2026 to maximize revenue growth without eroding margin. The analysis was prepared for the CFO, CMO, and Head of Sales to inform the upcoming year's growth strategy.

**2. Dataset Used**
A 500-row, 13-column transaction dataset spanning one full year (January 2025 through January 2026). Each row represents a single transaction and includes customer identifiers and segments, product category and price, transaction quantity, discount status, marketing channel, region, total revenue, customer satisfaction, and return status. The dataset was cleaned and supplemented with five derived columns (month, is_weekend, revenue_per_unit, binary_discount, is_vip) to support the analysis. I never ended up using month.

**3. Main Analysis Steps**
- Data inspection and cleaning, including datetime conversion, missing value handling, and verification of categorical labels
- Visual single factor analysis of revenue drivers and customer segmentation 
- Group-based analysis across customer segments, product categories, marketing channels, weekday vs. weekend, and the cross-cut of VIP and discount status
- Relationship analysis using a correlation matrix and two t-tests
- Linear regression and then a train/test split
- Predictive modeling using linear regression to quantify the dollar impact of each variable on revenue

**4. Key Insights**
- The current discount strategy is the company's largest issue. Discounts are applied to 67% of transactions and statistically reduce revenue without increasing volume.
- The current VIP designation does not capture behaviorally differentiated customers. Two independent statistical tests confirmed that VIP status has no measurable effect on revenue (by transaction or in overall volume).
- Marketing channel is the strongest acquisition lever. Product category showed no meaningful variation.
- Weekday timing does not matter. Weekday vs. weekend timing is not a meaningful revenue lever.

**5. Recommendations**
- **CFO:** Reduce overall discount frequency, particularly for VIP-labeled customers who are being discounted the most.
- **Head of Sales:** Audit how the VIP designation is being assigned and revisit the classification. The current label does not capture genuinely high-value customers.
- **CMO:** Scale investment in Paid Search and Social Media as the highest-yield acquisition channels. Do not change product category mix.

**6. Limitations**
- Single-year dataset; multi-year data would strengthen findings and surface seasonality
- Train / test split could be repeated, in more depth and visualized and explored in more detail
- The VIP designation recommended above requires access to the original criteria used to assign the designation
- Single year is by far the biggest limitation. The VIP status is likely driven by multi-year relationship, so that needs to be tested on longer time horizon data before throwing out the designation.

**7. Future Work**
- Test discounts overall and with VIP customers to save revenue
- Redefine VIP criteria using behavioral data
- Rerun VIP statistical relationship on data with longer time horizon  
