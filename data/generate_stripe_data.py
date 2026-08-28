"""
Synthetic subscription billing data, generated to mirror Stripe's real
API object shapes exactly (Customer, Subscription, Invoice, Charge,
Refund), field names and relationships included, so the staging layer
downstream maps one-to-one onto what a real Stripe webhook/API sync
would land in the RAW schema.

Not connected to a real Stripe account. No real customer or payment
data. Generated with a documented growth/churn model over an 18-month
history so MRR movement classification (new/expansion/contraction/
churn/reactivation) has real, non-trivial patterns to detect.

Run: python generate_stripe_data.py
Output: stripe_customers.csv, stripe_subscriptions.csv,
        stripe_plan_changes.csv, stripe_invoices.csv,
        stripe_charges.csv, stripe_refunds.csv
"""
import csv
import random
from datetime import date, timedelta

random.seed(101)

# Stripe Price/Plan objects: (plan_id, nickname, monthly_amount_usd, interval)
PLANS = [
    ("price_free", "Free", 0, "month"),
    ("price_starter_m", "Starter Monthly", 9, "month"),
    ("price_starter_y", "Starter Annual", 90, "year"),   # ~$7.50/mo equivalent
    ("price_pro_m", "Pro Monthly", 29, "month"),
    ("price_pro_y", "Pro Annual", 290, "year"),
    ("price_business_m", "Business Monthly", 99, "month"),
    ("price_business_y", "Business Annual", 990, "year"),
    ("price_enterprise_m", "Enterprise Monthly", 299, "month"),
]
PLAN_MRR = {p[0]: (p[2] if p[3] == "month" else round(p[2] / 12, 2)) for p in PLANS}
PLAN_LOOKUP = {p[0]: p for p in PLANS}

COUNTRIES = ["US", "US", "US", "GB", "CA", "DE", "AU", "IN", "FR"]
SIGNUP_CHANNELS = ["organic", "paid_search", "referral", "content", "partner"]

START_MONTH = date(2025, 1, 1)
END_MONTH = date(2026, 6, 1)  # 18 months of history
N_MONTHS = 18


def month_add(d, n):
    month = d.month - 1 + n
    year = d.year + month // 12
    month = month % 12 + 1
    return date(year, month, 1)


def random_day_in_month(month_start):
    days_in_month = (month_add(month_start, 1) - month_start).days
    return month_start + timedelta(days=random.randint(0, days_in_month - 1))


def main():
    customers = []
    subscriptions = []
    plan_changes = []
    invoices = []
    charges = []
    refunds = []

    customer_seq = 1
    subscription_seq = 1
    invoice_seq = 1
    charge_seq = 1
    refund_seq = 1

    active_subs = {}  # customer_id -> current subscription dict

    # base new-signups-per-month grows over time (simple growth curve),
    # with a monthly churn probability applied to existing active subs
    base_signups = 180

    for month_idx in range(N_MONTHS):
        month_start = month_add(START_MONTH, month_idx)
        growth_factor = 1 + month_idx * 0.045
        new_signups_this_month = int(base_signups * growth_factor * random.uniform(0.9, 1.1))

        # ---- churn existing active subscriptions ----
        for cust_id, sub in list(active_subs.items()):
            monthly_churn_prob = 0.032 if sub["plan_id"] != "price_enterprise_m" else 0.015
            if random.random() < monthly_churn_prob:
                cancel_date = random_day_in_month(month_start)
                subscriptions.append({
                    **sub, "status": "canceled",
                    "canceled_at": cancel_date.isoformat(),
                })
                del active_subs[cust_id]

        # ---- expansion / contraction: plan changes on a subset of active subs ----
        for cust_id, sub in list(active_subs.items()):
            if random.random() < 0.04:  # 4% chance of a plan change this month
                old_plan_id = sub["plan_id"]
                old_mrr = PLAN_MRR[old_plan_id]
                # 65% of changes are upgrades, 35% downgrades
                plan_ids = list(PLAN_MRR.keys())
                if random.random() < 0.65:
                    candidates = [p for p in plan_ids if PLAN_MRR[p] > old_mrr]
                else:
                    candidates = [p for p in plan_ids if 0 < PLAN_MRR[p] < old_mrr]
                if candidates:
                    new_plan_id = random.choice(candidates)
                    change_date = random_day_in_month(month_start)
                    plan_changes.append({
                        "change_id": f"pc_{len(plan_changes)+1:06d}",
                        "subscription_id": sub["subscription_id"],
                        "customer_id": cust_id,
                        "change_date": change_date.isoformat(),
                        "old_plan_id": old_plan_id,
                        "new_plan_id": new_plan_id,
                        "old_mrr": old_mrr,
                        "new_mrr": PLAN_MRR[new_plan_id],
                    })
                    sub["plan_id"] = new_plan_id

        # ---- new signups this month ----
        for _ in range(new_signups_this_month):
            cust_id = f"cus_{customer_seq:06d}"
            customer_seq += 1
            signup_date = random_day_in_month(month_start)
            customers.append({
                "customer_id": cust_id,
                "created": signup_date.isoformat(),
                "country": random.choice(COUNTRIES),
                "signup_channel": random.choice(SIGNUP_CHANNELS),
            })

            # weighted plan selection, most signups start small
            plan_weights = [0.20, 0.28, 0.05, 0.22, 0.04, 0.12, 0.02, 0.07]
            plan_id = random.choices([p[0] for p in PLANS], weights=plan_weights)[0]

            sub_id = f"sub_{subscription_seq:06d}"
            subscription_seq += 1
            sub = {
                "subscription_id": sub_id,
                "customer_id": cust_id,
                "plan_id": plan_id,
                "status": "active",
                "start_date": signup_date.isoformat(),
                "canceled_at": "",
            }
            active_subs[cust_id] = sub

        # ---- invoices + charges for every active sub this month ----
        for cust_id, sub in active_subs.items():
            plan = PLAN_LOOKUP[sub["plan_id"]]
            if plan[2] == 0:
                continue  # free plan, no invoice
            period_start = month_start
            period_end = month_add(month_start, 1)
            amount_due = plan[2]

            inv_id = f"in_{invoice_seq:06d}"
            invoice_seq += 1
            payment_failed = random.random() < 0.015
            invoices.append({
                "invoice_id": inv_id,
                "customer_id": cust_id,
                "subscription_id": sub["subscription_id"],
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
                "amount_due": amount_due,
                "amount_paid": 0 if payment_failed else amount_due,
                "status": "open" if payment_failed else "paid",
                "created": random_day_in_month(month_start).isoformat(),
            })

            if not payment_failed:
                charge_id = f"ch_{charge_seq:06d}"
                charge_seq += 1
                charges.append({
                    "charge_id": charge_id,
                    "invoice_id": inv_id,
                    "customer_id": cust_id,
                    "amount": amount_due,
                    "status": "succeeded",
                    "created": invoices[-1]["created"],
                })
                # small chance of a partial/full refund
                if random.random() < 0.008:
                    refund_amount = round(amount_due * random.choice([0.5, 1.0]), 2)
                    refunds.append({
                        "refund_id": f"re_{refund_seq:06d}",
                        "charge_id": charge_id,
                        "amount": refund_amount,
                        "reason": random.choice(["requested_by_customer", "duplicate", "fraudulent"]),
                        "created": invoices[-1]["created"],
                    })
                    refund_seq += 1

        # ---- reactivations: some churned customers come back ----
        churned_customer_ids = [c["customer_id"] for c in customers if c["customer_id"] not in active_subs]
        if churned_customer_ids and random.random() < 0.6:
            reactivating = random.sample(churned_customer_ids, k=min(3, len(churned_customer_ids)))
            for cust_id in reactivating:
                if random.random() < 0.25 and cust_id not in active_subs:
                    plan_id = random.choice(["price_starter_m", "price_pro_m"])
                    sub_id = f"sub_{subscription_seq:06d}"
                    subscription_seq += 1
                    reactivate_date = random_day_in_month(month_start)
                    active_subs[cust_id] = {
                        "subscription_id": sub_id, "customer_id": cust_id, "plan_id": plan_id,
                        "status": "active", "start_date": reactivate_date.isoformat(), "canceled_at": "",
                    }

    # close out remaining active subscriptions as still-active at end of window
    for sub in active_subs.values():
        subscriptions.append(sub)

    def write_csv(rows, path):
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

    write_csv(customers, "stripe_customers.csv")
    write_csv(subscriptions, "stripe_subscriptions.csv")
    write_csv(plan_changes, "stripe_plan_changes.csv")
    write_csv(invoices, "stripe_invoices.csv")
    write_csv(charges, "stripe_charges.csv")
    write_csv(refunds, "stripe_refunds.csv")

    print(f"customers: {len(customers)}")
    print(f"subscriptions (all states, incl. canceled history rows): {len(subscriptions)}")
    print(f"plan_changes: {len(plan_changes)}")
    print(f"invoices: {len(invoices)}")
    print(f"charges: {len(charges)}")
    print(f"refunds: {len(refunds)}")
    print(f"active subscriptions at end of window: {len(active_subs)}")


if __name__ == "__main__":
    main()
