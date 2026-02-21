import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

import model


st.set_page_config(page_title="Personal Finance Simulator", layout="wide")
st.title("💸 Personal Finance Simulator (Roth + 401k + Brokerage)")

st.sidebar.header("Your Inputs")

initial_wealth = st.sidebar.number_input("Initial wealth ($)", 0, 50_000_000, 10_000, step=1000)
years = st.sidebar.slider("Years", 1, 60, 30)
n_sims = st.sidebar.slider("Simulations", 200, 50_000, 5000, step=200)

expected_return = st.sidebar.slider("Return per year", -0.20, 0.30, 0.08, step=0.01)

initial_income = st.sidebar.number_input("Initial income ($/yr)", 0, 2_000_000, 60_000, step=1000)
income_growth = st.sidebar.slider("Income growth (per year)", -0.10, 0.20, 0.03, step=0.01)

initial_expenses = st.sidebar.number_input("Initial expenses ($/yr)", 0, 2_000_000, 45_000, step=1000)
expense_inflation = st.sidebar.slider("Expense inflation (per year)", -0.05, 0.20, 0.03, step=0.01)

st.sidebar.subheader("Roth IRA")
roth_contrib = st.sidebar.number_input("Roth contribution ($/yr)", 0, 50_000, 7000, step=500)
roth_years = st.sidebar.slider("Contribute for how many years?", 0, years, min(10, years))

st.sidebar.subheader("401(k)")
k401_employee_pct = st.sidebar.slider("Your 401k contribution (% of salary)", 0.0, 0.30, 0.08, step=0.01)
k401_match_pct = st.sidebar.slider("Employer match (% of your contrib)", 0.0, 1.0, 0.50, step=0.05)

st.sidebar.subheader("General investments (brokerage)")
taxable_contrib = st.sidebar.number_input("Brokerage contribution ($/yr)", 0, 500_000, 3000, step=500)

seed = st.sidebar.number_input("Random seed", 0, 1_000_000, 42, step=1)

with st.sidebar.expander("Advanced (optional realism)"):
    return_vol = st.sidebar.slider("Return volatility (σ)", 0.0, 0.60, 0.15, step=0.01)
    st.caption("Set σ = 0 for deterministic growth (same return every year).")

run = st.sidebar.button("Run simulation")


@st.cache_data(show_spinner=False)
def run_sim(
    initial_wealth,
    years,
    n_sims,
    expected_return,
    return_vol,
    seed,
    initial_income,
    income_growth,
    initial_expenses,
    expense_inflation,
    roth_contrib,
    roth_years,
    k401_employee_pct,
    k401_match_pct,
    taxable_contrib,
):
    return model.simulate_personal_finances(
        initial_wealth=initial_wealth,
        years=years,
        n_sims=n_sims,
        expected_return=expected_return,
        return_vol=return_vol,
        seed=seed,
        initial_income=initial_income,
        income_growth=income_growth,
        initial_expenses=initial_expenses,
        expense_inflation=expense_inflation,
        roth_contrib=roth_contrib,
        roth_years=roth_years,
        k401_employee_pct=k401_employee_pct,
        k401_match_pct=k401_match_pct,
        taxable_contrib=taxable_contrib,
    )


if run:
    out = run_sim(
        initial_wealth=initial_wealth,
        years=years,
        n_sims=n_sims,
        expected_return=expected_return,
        return_vol=return_vol,
        seed=seed,
        initial_income=initial_income,
        income_growth=income_growth,
        initial_expenses=initial_expenses,
        expense_inflation=expense_inflation,
        roth_contrib=roth_contrib,
        roth_years=roth_years,
        k401_employee_pct=k401_employee_pct,
        k401_match_pct=k401_match_pct,
        taxable_contrib=taxable_contrib,
    )

    total = out["total"]
    roth = out["roth"]
    k401 = out["k401"]
    taxable = out["taxable"]

    final_total = total[-1, :]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Mean final total", f"${np.mean(final_total):,.0f}")
    c2.metric("Median final total", f"${np.median(final_total):,.0f}")
    c3.metric("5th percentile", f"${np.percentile(final_total, 5):,.0f}")
    c4.metric("95th percentile", f"${np.percentile(final_total, 95):,.0f}")

    st.subheader("Total wealth paths (sample)")
    fig = plt.figure(figsize=(10, 5))
    for i in range(min(80, n_sims)):
        plt.plot(total[:, i], alpha=0.25)
    plt.xlabel("Year")
    plt.ylabel("Total wealth ($)")
    st.pyplot(fig)

    st.subheader("Average account balances")
    avg_roth = roth.mean(axis=1)
    avg_k401 = k401.mean(axis=1)
    avg_taxable = taxable.mean(axis=1)

    fig2 = plt.figure(figsize=(10, 5))
    plt.plot(avg_roth, label="Roth IRA")
    plt.plot(avg_k401, label="401(k)")
    plt.plot(avg_taxable, label="Brokerage")
    plt.plot((avg_roth + avg_k401 + avg_taxable), label="Total", linewidth=2)
    plt.xlabel("Year")
    plt.ylabel("Average balance ($)")
    plt.legend()
    st.pyplot(fig2)

    st.caption("Note: This simplified model ignores taxes, contribution limits, and match caps (we can add those next).")
else:
    st.info("Set your inputs in the sidebar, then click **Run simulation**.")


