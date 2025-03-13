import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.lines import Line2D

# Load JSON data
with open('data/dep_lsb.json', 'r') as f:
    data = json.load(f)

# Convert data to NumPy arrays
right_gas = np.array(data["rightMerkleTreeGas"], dtype=int)
incremental_gas = np.array(data["incrementalMerkleTreeGas"], dtype=int)
n_values = np.arange(1, len(right_gas) + 1)

# Compute means
mean_right = np.mean(right_gas)
mean_incremental = np.mean(incremental_gas)

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

color1 = "#FFA07A"
color11 = "#20B2AA"
color12 = "#87CEEB"
color13 = "#9370DB"

color2 = "#20B2AA"
color3 = "#FFF8DC"
color4 = "#FFC8B0"
color5 = "#40C0B0"

# Create masks and group data
mask = right_gas < incremental_gas
n_group1 = n_values[mask]
right_group1 = right_gas[mask]
incremental_group1 = incremental_gas[mask]

n_group2 = n_values[~mask]
right_group2 = right_gas[~mask]
incremental_group2 = incremental_gas[~mask]

# Plot group 1: right gas < incremental gas
# plt.vlines(n_group1, right_group1, incremental_group1, color=color4, linewidth=0.5, alpha=0.1, zorder=1)  # Lower z-order
plt.scatter(n_group1, right_group1, color=color1, s=1, alpha=0.5, zorder=2,rasterized=True)  # Higher z-order
plt.scatter(n_group1, incremental_group1, color=color12, s=1, alpha=0.5, zorder=2,rasterized=True)  # Higher z-order

# Plot group 2: right gas ≥ incremental gas
# plt.vlines(n_group2, right_group2, incremental_group2, color=color5, linewidth=0.5, alpha=0.1, zorder=1)  # Lower z-order
plt.scatter(n_group2, right_group2, color=color2, s=1, alpha=0.5, zorder=2,rasterized=True)  # Higher z-order
plt.scatter(n_group2, incremental_group2, color=color2, s=1, alpha=0.5, zorder=2,rasterized=True)  # Higher z-order

# Plot average lines with reduced thickness
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

# Custom legend displaying the colour coding
# legend_elements = [
#     Line2D([0], [0], marker='o', color='w', label='RMT < IMT Gas Used',
#            markerfacecolor=color1, markersize=5),
#     Line2D([0], [0], marker='o', color='w', label='RMT ≥ IMT Gas Used',
#            markerfacecolor=color2, markersize=5)
# ]
# Custom legend displaying the colour coding (using lines instead of dots)
# legend_elements = [
#     Line2D([0], [0], marker='o', color='w', label='RMT < IMT Gas Used',
#            markerfacecolor=color1, markersize=5),
#     Line2D([0], [0], marker='o', color='w', label='RMT ≥ IMT Gas Used',
#            markerfacecolor=color2, markersize=5)
# ]
# plt.legend(handles=legend_elements, loc='lower right', framealpha=0.5)  # 50% transparency

import matplotlib.ticker as mticker
ax = plt.gca()
ax.xaxis.set_major_formatter(mticker.FormatStrFormatter('%.1e'))
# ax.set_xlabel('Index', fontweight='bold')
# ax.xaxis.set_label_coords(-0.06, -0.12)

ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.1e'))
ax.set_ylabel('Gas Used', rotation=0)
ax.yaxis.set_label_coords(-0.07, 0.95)

plt.tight_layout()

plt.savefig("figure/dep_lsb.pdf", format='pdf', bbox_inches='tight', transparent=True)

plt.show()

