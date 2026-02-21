import numpy as np
import matplotlib.pyplot as plt
from model import simulate_markov_cashflow_wealth

wealth, states, income, expenses, unemployed = simulate_markov_cashflow_wealth()

# Plot wealth paths
plt.figure(figsize=(10, 6))
for i in range(50):
    plt.plot(wealth[:, i], alpha=0.35)
plt.title("Wealth with Income & Expenses (Markov Economy)")
plt.xlabel("Year")
plt.ylabel("Wealth")
plt.show()

final_wealth = wealth[-1, :]
print("Mean Final Wealth:", np.mean(final_wealth))
print("Median Final Wealth:", np.median(final_wealth))
print("5th percentile (downside):", np.percentile(final_wealth, 5))
print("P(final < initial):", np.mean(final_wealth < wealth[0, 0]))

# Some extra realism metrics
bad_fraction = np.mean(states == 1)
unemp_rate = np.mean(unemployed[1:, :])  # ignore year 0
print("Fraction of time in Bad economy:", bad_fraction)
print("Unemployment frequency:", unemp_rate)

# Average cashflow over time (across sims)
avg_income = np.mean(income, axis=1)
avg_exp = np.mean(expenses, axis=1)

plt.figure(figsize=(10, 5))
plt.plot(avg_income, label="Avg Income")
plt.plot(avg_exp, label="Avg Expenses")
plt.title("Average Income vs Expenses")
plt.xlabel("Year")
plt.ylabel("Dollars")
plt.legend()
plt.show()






