📊 Ola Ride Insights — EDA Report
1. Booking Status Distribution

Majority of rides are successful (~62k).

Driver cancellations (~18k) outnumber customer cancellations (~10k).

Driver Not Found (~10k) is also significant — signals potential supply-demand mismatch.

Takeaway: Success dominates, but cancellations are non-trivial, especially from drivers.

2. Daily Ride Volume

Ride volume is stable across July, averaging ~3,300 rides/day.

Slight dips mid-month and spikes around 12th & 30th.

End-of-month drop likely due to data cutoff, not demand decline.

3. Rides by Hour of Day

Demand is fairly uniform across hours.

Slight dips between 3–6 AM (low demand).

Evening/late-night demand remains strong, suggesting late-night reliance.

4. Revenue by Payment Method

Cash (~₹19M) dominates, followed by UPI (~₹14M).

Credit/Debit cards are marginal contributors.

Insight: Digital adoption is growing, but cash preference remains strong. UPI is likely to overtake cash soon.

5. Average Ride Distance by Vehicle Type

Longest rides: Prime Sedan, eBike, Bike, Mini (~15–16 km).

Shortest rides: Auto (~7 km) — fits local/last-mile use case.

SUVs slightly shorter than Sedans, possibly linked to group or airport trips.

6. Driver & Customer Ratings




Both skew positively (3.0–5.0 range).

Most ratings cluster near 5.0 → satisfaction bias or rating inflation.

Few low ratings → either genuine high satisfaction or lack of critical feedback.

7. Top 10 Customers by Booking Value

Heavy users spend up to ~₹8,000/month.

These customers should be targeted with retention perks (discounts, loyalty programs).

8. Incomplete Rides & Reasons




Most rides are completed successfully (60k).

~4k incomplete rides + ~39k missing entries → data quality gaps.

Top reasons: Customer demand changes and Vehicle breakdowns.

Takeaway: Address fleet maintenance & improve customer flexibility features.

9. Ride Duration Distribution




Mean ≈ 255 mins (4.2 hrs); Median = 255 mins.

90th percentile = 375 mins (~6.2 hrs) → SLA benchmarking point.

Distribution has long-tail rides (>6 hrs).

Zoomed histogram shows bulk between 150–350 mins.

10. Peak vs Off-Peak Outcomes

Peak (1) has slightly higher cancellations than off-peak (0).

Likely due to driver unavailability or traffic.

Takeaway: Incentivize drivers during peak hours or apply dynamic pricing.

🔄 Cancellation Analysis
By Vehicle Type

Driver cancellations dominate across all vehicle types.

Premium vehicles (Prime Sedan/Plus/SUV) show slightly higher driver cancellations.

Autos/Bikes show balanced cancellation shares.

Takeaway: Premium categories may need incentive tweaks or service-level enforcement.

By Payment Method

Rates are consistent across payment methods.

Cash/UPI dominate → even small changes here impact overall cancellations.

Credit/Debit card volumes are too low for strong insights.

Takeaway: Payment type is not a major driver of cancellations, but monitoring high-volume Cash/UPI is crucial.

By Hour of Day

Driver cancellations dominate at all hours.

Uptick during 7–10 AM and 6–9 PM (commute hours).

Customer cancellations steady → less time-sensitive.

Driver not found is flat → availability issue is consistent.

Takeaway: Focus on driver-side issues during commute hours. Dynamic incentives may help.

👥 Customer Segmentation — Top 5% by Value vs Frequency

Top 5% by Value → slightly longer rides (~14.2 km).

Top 5% by Frequency → consistent shorter/medium rides (~14.0 km).

Both groups rate service ~4.0 (drivers & customers).

Takeaway:

Value segment → revenue maximization, offer premium perks.

Frequency segment → repeat usage, offer loyalty rewards.

📈 Advanced Time Insights
Weekly Ride Volume

Stable at ~23k rides/week across July.

End-of-month drop is a data cutoff issue, not demand decline.

Day of Week

Weekdays (Mon–Wed) peak, especially Tuesday.

Weekends & Thursday–Friday are lower.

Pattern aligns with work commute vs leisure travel.

Takeaway: Ola demand is weekday-driven.
Promotions could boost weekend demand.

⚠️ Outlier & Anomaly Detection
Boxplots




Ride Distance:

IQR = 26 km (Q1 = 0, Q3 = 26).

Upper bound = 65 km.

No extreme distance outliers.

Booking Value:

IQR = 379 (Q1 = 242, Q3 = 621).

Upper bound = ~1189.

Values beyond this (up to 3000) are outliers.

Takeaway:

Distance data looks clean.

Booking values have a long right tail due to premium/surge rides or errors → needs review.
