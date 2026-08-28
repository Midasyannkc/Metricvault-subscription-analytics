import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

plt.rcParams["font.size"] = 11
KPI_DIR = "../data/computed_kpis"

arr_trend = pd.read_csv(f"{KPI_DIR}/arr_mrr_trend.csv", parse_dates=["snapshot_month"])
movements = pd.read_csv(f"{KPI_DIR}/mrr_movements_by_month.csv", parse_dates=["movement_month"])
recon = pd.read_csv(f"{KPI_DIR}/finance_reconciliation.csv", parse_dates=["month"])
retention = pd.read_csv(f"{KPI_DIR}/nrr_logo_retention_cohorts.csv", parse_dates=["cohort_month"])

money_fmt = mticker.FuncFormatter(lambda x, _: f"${x/1000:,.0f}k")

# 1. ARR growth trend
fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(arr_trend["snapshot_month"], arr_trend["arr_usd"], marker="o", markersize=3, color="#3B6FA0", linewidth=2)
ax.set_title("ARR Growth (18-Month History)")
ax.set_ylabel("ARR (USD)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1e6:.1f}M" if x >= 1e6 else f"${x/1000:.0f}k"))
ax.grid(alpha=0.2)
fig.tight_layout()
fig.savefig("arr_growth_trend.png", dpi=150)
plt.close(fig)

# 2. Latest-month MRR bridge (waterfall)
latest_month = movements["movement_month"].max()
bridge = movements[movements["movement_month"] == latest_month].set_index("movement_type")["mrr_delta"]
starting_mrr = arr_trend.set_index("snapshot_month").loc[
    arr_trend["snapshot_month"].sort_values().iloc[-2], "total_mrr_usd"
]
order = ["new", "expansion", "reactivation", "contraction", "churned"]
deltas = [bridge.get(k, 0) for k in order]
ending_mrr = starting_mrr + sum(deltas)

labels = ["Starting\nMRR"] + [k.title() for k in order] + ["Ending\nMRR"]
values = [starting_mrr] + deltas + [ending_mrr]

fig, ax = plt.subplots(figsize=(10, 5.5))
cumulative = starting_mrr
colors = []
bottoms = [0]
heights = [starting_mrr]
colors.append("#5A5A5A")
for d in deltas:
    if d >= 0:
        bottoms.append(cumulative)
        heights.append(d)
        colors.append("#2E8B57")
    else:
        bottoms.append(cumulative + d)
        heights.append(-d)
        colors.append("#C0504D")
    cumulative += d
bottoms.append(0)
heights.append(ending_mrr)
colors.append("#3B6FA0")

bars = ax.bar(labels, heights, bottom=bottoms, color=colors, width=0.6)
for bar, bottom, height, val in zip(bars, bottoms, heights, values):
    label_y = bottom + height + max(values) * 0.02
    ax.text(bar.get_x() + bar.get_width() / 2, label_y, f"${val:,.0f}", ha="center", fontsize=9)
ax.set_title(f"MRR Bridge, {pd.Timestamp(latest_month).strftime('%B %Y')}")
ax.set_ylabel("MRR (USD)")
ax.yaxis.set_major_formatter(money_fmt)
fig.tight_layout()
fig.savefig("mrr_bridge_waterfall.png", dpi=150)
plt.close(fig)

# 3. Finance reconciliation variance
fig, ax = plt.subplots(figsize=(9, 5))
colors = ["#C0504D" if s != "PASS" else "#2E8B57" for s in recon["control_status"]]
ax.bar(recon["month"].dt.strftime("%Y-%m"), recon["variance_pct"] * 100, color=colors, width=0.6)
ax.axhline(2, color="gray", linestyle="--", linewidth=1)
ax.axhline(-2, color="gray", linestyle="--", linewidth=1, label="2% control threshold")
ax.set_title("Finance Reconciliation Variance by Month")
ax.set_ylabel("Variance (%)")
plt.setp(ax.get_xticklabels(), rotation=60, ha="right", fontsize=8)
ax.legend(loc="lower left", fontsize=9)
fig.tight_layout()
fig.savefig("finance_reconciliation_variance.png", dpi=150)
plt.close(fig)

# 4. NRR & Logo Retention by cohort
fig, ax = plt.subplots(figsize=(9, 5))
ax2 = ax.twinx()
ax.bar(retention["cohort_month"].dt.strftime("%Y-%m"), retention["net_revenue_retention"] * 100, color="#3B6FA0", alpha=0.75, width=0.6, label="Net Revenue Retention")
ax2.plot(retention["cohort_month"].dt.strftime("%Y-%m"), retention["logo_retention"] * 100, color="#E4832A", marker="o", linewidth=2, label="Logo Retention")
ax.axhline(100, color="gray", linestyle="--", linewidth=1)
ax.set_ylabel("Net Revenue Retention (%)")
ax2.set_ylabel("Logo Retention (%)")
ax.set_title("6-Month Cohort Retention: NRR vs. Logo Retention")
plt.setp(ax.get_xticklabels(), rotation=45, ha="right", fontsize=8)
lines1, labels1 = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax.legend(lines1 + lines2, labels1 + labels2, loc="lower right", fontsize=9)
fig.tight_layout()
fig.savefig("retention_cohorts.png", dpi=150)
plt.close(fig)

print("Charts written: arr_growth_trend.png, mrr_bridge_waterfall.png, finance_reconciliation_variance.png, retention_cohorts.png")
