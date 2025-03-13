import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.lines import Line2D

# Load JSON data
with open('data/dep_agg.json', 'r') as f:
    data = json.load(f)

# Convert data to NumPy arrays
right_gas = np.array(data["S.AGG Dep./ST."], dtype=int)
incremental_gas = np.array(data["Amotised S.AGG Dep./ST."], dtype=int)
# Divide the 'Amotised S.AGG Dep./ST.' values by 32 for plotting purposes
incremental_gas_plot = incremental_gas / 32

# Create an array for the x-axis (leaf indices)
n_values = np.arange(1, len(right_gas) + 1)

# Compute the mean values for both datasets
mean_right = np.mean(right_gas)
mean_incremental = np.mean(incremental_gas_plot)

# Set plot theme and update font sizes for all text elements
sns.set_theme(style="whitegrid", palette="pastel")
plt.rcParams.update({
    'font.size': 9,
    'axes.titlesize': 9,
    'axes.labelsize': 9,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.titlesize': 9
})
plt.figure(figsize=(6, 1.5))


# Define colours
# color1 = "#ADD8E6"  # Light blue for right gas < incremental gas
# color2 = "orange"   # Orange for right gas ≥ incremental gas

# Define colours for the plot elements
color1 = "#FFA07A"   # Colour for S.LSB Dep.
color11 = "#20B2AA"  # Colour for S.AGG Dep./ST.
color12 = "#87CEEB"  # Colour for S.LSB ST.
color13 = "#9370DB"  # Colour for Amotised S.AGG Dep./ST.
color3 = "#FFF8DC"   # Colour for average lines

# Create masks to group the data based on the original condition
mask = right_gas < incremental_gas
n_group1 = n_values[mask]
right_group1 = right_gas[mask]
incremental_group1 = incremental_gas_plot[mask]

n_group2 = n_values[~mask]
right_group2 = right_gas[~mask]
incremental_group2 = incremental_gas_plot[~mask]


# Plot data points for group 1: where right_gas is less than incremental_gas
plt.scatter(n_group1, right_group1, color=color11, s=1, alpha=0.5, zorder=2,rasterized=True)
plt.scatter(n_group1, incremental_group1, color=color13, s=1, alpha=0.5, zorder=2,rasterized=True)

# Plot data points for group 2: where right_gas is greater than or equal to incremental_gas
plt.scatter(n_group2, right_group2, color=color11, s=1, alpha=0.5, zorder=2,rasterized=True)
plt.scatter(n_group2, incremental_group2, color=color13, s=1, alpha=0.5, zorder=2,rasterized=True)

# Plot average lines with a dash-dot style and reduced thickness
plt.axhline(y=mean_right, color=color3, linestyle='dashdot', linewidth=0.5)
plt.axhline(y=mean_incremental, color=color3, linestyle='dashdot', linewidth=0.5)

# Annotate average values with normal black text
plt.text(n_values[-1] + 0.06 * len(n_values), mean_right, f'Mean:\n{mean_right:.2e}', color='black', va='center', fontsize=9)
plt.text(n_values[-1] + 0.06 * len(n_values), mean_incremental, f'Mean:\n{mean_incremental:.2e}', color='black', va='center', fontsize=9)

# Set labels and title
# plt.xlabel("Leaf Index")
# plt.ylabel("Gas Consumption")
# plt.title("Gas Consumption Comparison: Right vs Incremental Merkle Tree")

# Use scientific notation for axes
plt.ticklabel_format(axis='x', style='scientific', scilimits=(0, 0))
plt.ticklabel_format(axis='y', style='scientific', scilimits=(0, 0))

# Create a custom legend with markers indicating each dataset
legend_elements = [
    Line2D([0], [0], marker='o', color='w', label='SH-M Dep.',
           markerfacecolor=color1, markersize=5),
    Line2D([0], [0], marker='o', color='w', label='SH-M ST.',
           markerfacecolor=color12, markersize=5),
    Line2D([0], [0], marker='o', color='w', label='SH-A Dep./ST.',
           markerfacecolor=color11, markersize=5),
    Line2D([0], [0], marker='o', color='w', label='Amotised SH-A Dep./ST.',
           markerfacecolor=color13, markersize=5)
]
plt.legend(handles=legend_elements, loc='lower right', framealpha=0.5)

import matplotlib.ticker as mticker
ax = plt.gca()
ax.xaxis.set_major_formatter(mticker.FormatStrFormatter('%.1e'))
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.1e'))

ax.set_xlabel('Index')
ax.xaxis.set_label_coords(-0.06, -0.12)
# ax.set_ylabel('Gas Used', rotation=0, fontweight='bold')
# ax.yaxis.set_label_coords(-0.07, 0.95)

plt.tight_layout()

plt.savefig("figure/dep_agg.pdf", format='pdf', bbox_inches='tight', transparent=True)

plt.show()

