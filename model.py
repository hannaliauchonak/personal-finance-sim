import numpy as np

def simulate_personal_finances(
    initial_wealth=10_000,
    years=30,
    n_sims=5000,
    expected_return=0.08,      # "return per year"
    return_vol=0.15,           # optional realism (can set to 0 for deterministic)
    seed=42,

    initial_income=60_000,
    income_growth=0.03,

    initial_expenses=45_000,
    expense_inflation=0.03,

    roth_contrib=7_000,
    roth_years=10,

    k401_employee_pct=0.08,    # 8% of salary
    k401_match_pct=0.50,       # 50% match (simple model)

    taxable_contrib=3_000,     # extra brokerage contribution per year
):
    """
    Each year:
      - Income and expenses grow deterministically (no randomness here for intuition)
      - Contributions go into Roth, 401k, taxable
      - All accounts earn the same market return that year

    Returns dict with arrays shaped (years+1, n_sims):
      total, roth, k401, taxable, income, expenses
    """
    rng = np.random.default_rng(seed)

    # Accounts
    roth = np.zeros((years + 1, n_sims), dtype=float)
    k401 = np.zeros((years + 1, n_sims), dtype=float)
    taxable = np.zeros((years + 1, n_sims), dtype=float)

    # Put initial wealth into taxable by default (intuitive “cash/brokerage bucket”)
    taxable[0, :] = initial_wealth

    # Income/expenses paths (deterministic over time)
    income = np.zeros((years + 1, n_sims), dtype=float)
    expenses = np.zeros((years + 1, n_sims), dtype=float)
    income[0, :] = initial_income
    expenses[0, :] = initial_expenses

    for t in range(1, years + 1):
        income[t, :] = income[t - 1, :] * (1.0 + income_growth)
        expenses[t, :] = expenses[t - 1, :] * (1.0 + expense_inflation)

    # Market returns (shared across accounts)
    if return_vol == 0:
        r = np.full((years, n_sims), expected_return, dtype=float)
    else:
        r = rng.normal(loc=expected_return, scale=return_vol, size=(years, n_sims))

    for t in range(1, years + 1):
        # 1) Grow last year's balances
        roth[t, :] = roth[t - 1, :] * (1.0 + r[t - 1, :])
        k401[t, :] = k401[t - 1, :] * (1.0 + r[t - 1, :])
        taxable[t, :] = taxable[t - 1, :] * (1.0 + r[t - 1, :])

        # 2) Compute contributions for this year (based on THIS year's income)
        sal = income[t, :]
        emp_401 = k401_employee_pct * sal
        match_401 = k401_match_pct * emp_401

        roth_add = roth_contrib if t <= roth_years else 0.0
        roth_add = np.full(n_sims, roth_add, dtype=float)

        taxable_add = np.full(n_sims, taxable_contrib, dtype=float)

        # 3) Basic affordability: contributions can’t exceed (income - expenses)
        # For intuition: we treat 401k employee + roth + taxable as coming out of cashflow.
        cash_available = sal - expenses[t, :]

        planned = emp_401 + roth_add + taxable_add
        # scale down contributions if not affordable
        scale = np.ones(n_sims, dtype=float)
        mask = planned > cash_available
        scale[mask] = np.where(planned[mask] > 0, cash_available[mask] / planned[mask], 0.0)

        emp_401 *= scale
        roth_add *= scale
        taxable_add *= scale

        # 4) Apply contributions
        k401[t, :] += emp_401 + match_401
        roth[t, :] += roth_add
        taxable[t, :] += taxable_add

        # (Optional: if cash_available is negative, we are NOT modeling debt here.
        # You can add debt later if you want.)

    total = roth + k401 + taxable

    return {
        "total": total,
        "roth": roth,
        "k401": k401,
        "taxable": taxable,
        "income": income,
        "expenses": expenses,
    }


