const pptxgen = require("pptxgenjs");

const NAVY = "1F2A44";
const BLUE = "3B6FA0";
const GREEN = "2E8B57";
const RED = "C0504D";
const GRAY = "5A5A5A";
const WHITE = "FFFFFF";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";

function titleSlide() {
  const s = pres.addSlide();
  s.background = { color: NAVY };
  s.addText("MetricVault", {
    x: 0.8, y: 1.7, w: 11.7, h: 1.3, fontSize: 48, bold: true, color: WHITE, fontFace: "Arial",
  });
  s.addText("Subscription Revenue Data Product", {
    x: 0.8, y: 2.75, w: 11.7, h: 0.7, fontSize: 24, color: "AFC3DC", fontFace: "Arial",
  });
  s.addText("dbt + MetricFlow + LookML + Dagster + Snowflake + Tableau, with a real SOX reconciliation control", {
    x: 0.8, y: 3.55, w: 11.7, h: 0.5, fontSize: 14, color: "9FCBB0", fontFace: "Arial",
  });
  s.addText("Every pipeline stage in this deck actually ran. dbt build: 40/40 tests passing. Dagster: full asset graph, RUN_SUCCESS.", {
    x: 0.8, y: 4.2, w: 11.7, h: 0.5, fontSize: 12, color: "F0C199", fontFace: "Arial", italic: true,
  });
  s.addText("Christian Kouadio Kouassi", { x: 0.8, y: 6.6, w: 6, h: 0.4, fontSize: 12, color: "6FA396", fontFace: "Arial" });
}

function sectionHeader(title, kicker) {
  const s = pres.addSlide();
  s.background = { color: WHITE };
  s.addText(kicker.toUpperCase(), { x: 0.8, y: 0.55, w: 8, h: 0.4, fontSize: 13, color: BLUE, bold: true, fontFace: "Arial", charSpacing: 1 });
  s.addText(title, { x: 0.8, y: 0.95, w: 11.5, h: 0.85, fontSize: 28, bold: true, color: NAVY, fontFace: "Arial" });
  return s;
}

function bulletBlock(s, items, opts) {
  const o = Object.assign({ x: 0.8, y: 2.0, w: 11.5, h: 4.6, fontSize: 16 }, opts);
  s.addText(
    items.map((t, i) => ({ text: t, options: { bullet: { code: "2022" }, breakLine: i !== items.length - 1, paraSpaceAfter: 14 } })),
    { x: o.x, y: o.y, w: o.w, h: o.h, fontSize: o.fontSize, color: NAVY, fontFace: "Arial", valign: "top", margin: 0 }
  );
}

titleSlide();

{
  const s = sectionHeader("The Problem", "Context");
  bulletBlock(s, [
    "A subscription company's revenue metrics get defined multiple times: a BI calculated field, an analyst's ad hoc SQL, Finance's spreadsheet, and they quietly drift apart.",
    "Because the company is public, the numbers this pipeline produces directly support financial reporting, so accuracy, lineage, and Finance reconciliation aren't optional.",
    "The role: own the shared transformation and metric layer everything else depends on, not a pipeline role, not a dashboard role.",
  ]);
}

{
  const s = sectionHeader("Where the Data Comes From", "Data Source");
  bulletBlock(s, [
    "Synthetic data shaped to mirror real Stripe API objects exactly: Customer, Subscription, Invoice, Charge, Refund, plan-change events.",
    "18-month history, documented growth/churn model: 4,503 customers, ~27,000 invoices, ~3.2% monthly churn.",
    "Finance's independently-recorded ledger (NetSuite GL stand-in) is generated separately, with deterministic noise, so reconciliation results are real and reproducible.",
  ]);
}

{
  const s = sectionHeader("What We're Testing For", "Hypothesis");
  bulletBlock(s, [
    "Whether MRR movement classification, the genuinely hard part of subscription analytics, can be built as governed dbt logic both MetricFlow and LookML read identically.",
    "Whether an independent Finance reconciliation catches real variance rather than trivially always passing.",
    "It does: 2 of 18 months fail the 2% control threshold, tied to a documented one-time adjustment, not silently absorbed.",
  ]);
}

{
  const s = sectionHeader("Certified Metrics, One Definition Each", "Semantic Layer");
  bulletBlock(s, [
    "Primary: dbt Semantic Layer / MetricFlow, ARR, MRR, NRR, Logo Retention, Paying Customers, and every MRR movement type, each with exactly one definition.",
    "Secondary: LookML, a migration-period mirror for existing Looker consumers, wired to the same certified mart tables, never independently defined.",
    "Verified: semantic_layer_refresh validated 9 metrics against their underlying measures, live, in the Dagster run.",
  ]);
}

{
  const s = sectionHeader("Stack & Why It Fits", "Architecture");
  const rows = [
    ["Layer", "Tool", "Why"],
    ["Ingestion", "Stripe-shaped extract + Dagster", "Matches target ingestion + orchestration stack"],
    ["Warehouse", "Snowflake (verified via DuckDB)", "Runnable and testable without a live account"],
    ["Transformation", "dbt (staging \u2192 intermediate \u2192 marts)", "Version control, tests, CI, documentation"],
    ["Semantic layer", "MetricFlow (primary) + LookML (migration)", "Certified metrics, one source of truth"],
    ["Orchestration", "Dagster", "Real asset graph + SOX asset check"],
    ["BI", "Tableau", "Executive ARR/MRR bridge, retention, reconciliation"],
  ];
  s.addTable(rows, {
    x: 0.8, y: 1.9, w: 11.5, h: 4.3, fontSize: 12.5, fontFace: "Arial",
    border: { type: "solid", color: "DDDDDD", pt: 1 }, autoPage: false, color: NAVY, fill: { color: WHITE }, valign: "middle", rowH: 0.58,
  });
}

{
  const s = sectionHeader("The SOX Control, Live", "Compliance");
  bulletBlock(s, [
    "fct_finance_reconciliation compares data-team ARR against Finance's independently-recorded ledger, every month, automatically.",
    "The Dagster asset check ran for real and correctly flagged two months by name and exact variance, without blocking the pipeline.",
    "Access control, change management, and this reconciliation are each documented and mapped to a specific SOX ITGC control objective in sox/.",
  ]);
}

{
  const s = sectionHeader("Results", "KPI Snapshot");
  s.addImage({ path: "../charts/arr_growth_trend.png", x: 0.5, y: 1.85, w: 5.9, h: 3.28 });
  s.addImage({ path: "../charts/mrr_bridge_waterfall.png", x: 6.55, y: 1.85, w: 6.0, h: 3.44 });
  bulletBlock(s, [
    "ARR grew from ~$100K to $2.79M over 18 months, 2,888 active paying customers.",
    "114.3% average Net Revenue Retention, 95.3% average Logo Retention across 6-month cohorts.",
    "40/40 dbt tests passing. Dagster: full asset graph RUN_SUCCESS.",
  ], { y: 5.4, h: 1.7, fontSize: 13 });
}

{
  const s = sectionHeader("Reconciliation & Retention", "KPI Snapshot, Continued");
  s.addImage({ path: "../charts/finance_reconciliation_variance.png", x: 0.5, y: 1.85, w: 5.9, h: 3.44 });
  s.addImage({ path: "../charts/retention_cohorts.png", x: 6.55, y: 1.85, w: 6.0, h: 3.44 });
  s.addText(
    "16 of 18 months reconcile within the 2% control threshold; the two flagged months (Jul 2025, Mar 2026) trace to a documented one-time GL adjustment, exactly what this control is designed to catch.",
    { x: 0.8, y: 5.5, w: 11.5, h: 0.9, fontSize: 12, color: GRAY, italic: true, fontFace: "Arial" }
  );
}

pres.writeFile({ fileName: "kpi_walkthrough.pptx" }).then(() => {
  console.log("Deck written: kpi_walkthrough.pptx");
});
