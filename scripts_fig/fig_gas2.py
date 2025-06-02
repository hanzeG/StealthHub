import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.lines import Line2D
import matplotlib.ticker as mticker
import os

# Load JSON data
base_dir = os.path.dirname(os.path.abspath(__file__))
input_data_path = os.path.join(base_dir, '../data/16_gas_used.json')
output_data_path = os.path.join(base_dir, '../figure/16_gas_used.pdf')
with open(input_data_path, 'r') as f:
    data = json.load(f)

# Convert data to NumPy arrays
mmr_gas = np.array(data["mmrGas"], dtype=int)
incremental_gas = np.array(data["imtGas"], dtype=int)
n_values = np.arange(1, len(mmr_gas) + 1)

# Compute means
mean_mmr = np.mean(mmr_gas)
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
color1 = "#FFA07A"
color2 = "#20B2AA"
color3 = "#FFF8DC"
color4 = "#FFC8B0"
color5 = "#40C0B0"

# Create masks and group data
mask = mmr_gas < incremental_gas
n_group1 = n_values[mask]
mmr_group1 = mmr_gas[mask]
incremental_group1 = incremental_gas[mask]

n_group2 = n_values[~mask]
mmr_group2 = mmr_gas[~mask]
incremental_group2 = incremental_gas[~mask]

# Plot group 1: mmr gas < incremental gas
plt.vlines(n_group1, mmr_group1, incremental_group1, color=color4, linewidth=0.5, alpha=0.1, zorder=1,rasterized=True)
plt.scatter(n_group1, mmr_group1, color=color1, s=1, alpha=0.5, zorder=2,rasterized=True)
plt.scatter(n_group1, incremental_group1, color=color1, s=1, alpha=0.5, zorder=2,rasterized=True)

# Plot group 2: mmr gas ≥ incremental gas
plt.vlines(n_group2, mmr_group2, incremental_group2, color=color5, linewidth=0.5, alpha=0.1, zorder=1,rasterized=True)
plt.scatter(n_group2, mmr_group2, color=color2, s=1, alpha=0.5, zorder=2,rasterized=True)
plt.scatter(n_group2, incremental_group2, color=color2, s=1, alpha=0.5, zorder=2,rasterized=True)

# Plot average lines with reduced thickness
plt.axhline(y=mean_mmr, color=color3, linestyle='dashdot', linewidth=0.5)
plt.axhline(y=mean_incremental, color=color3, linestyle='dashdot', linewidth=0.5)

# Add text labels for the average lines (displaying label and value side by side)
plt.text(n_values[-1] + 0.06 * len(n_values), mean_mmr, f'Mean:\n{mean_mmr:.2e}',
         color='black', va='center', fontsize=9)
plt.text(n_values[-1] + 0.06 * len(n_values), mean_incremental, f'Mean:\n{mean_incremental:.2e}',
         color='black', va='center', fontsize=9)

# Use scientific notation for tick labels
plt.ticklabel_format(axis='x', style='scientific', scilimits=(0, 0))
plt.ticklabel_format(axis='y', style='scientific', scilimits=(0, 0))

# Custom legend displaying the colour coding
# legend_elements = [
#     Line2D([0, 1], [0, 0], color=color1, linestyle='-', linewidth=2, label='LSBT < IMT gas used'),
#     Line2D([0, 1], [0, 0], color=color2, linestyle='-', linewidth=2, label='LSBT ≥ IMT gas used')
# ]
legend_elements = [
    Line2D([0], [0], color='w', marker='o', markerfacecolor=color1, markersize=5, label='MMR < IMT gas used'),
    Line2D([0], [0], color='w', marker='o', markerfacecolor=color2, markersize=5, label='MMR ≥ IMT gas used')
]
plt.legend(handles=legend_elements, loc='lower right', framealpha=0.5)

# Set scientific notation format for tick labels
ax = plt.gca()
ax.xaxis.set_major_formatter(mticker.FormatStrFormatter('%.1e'))
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.1e'))

# Set axis labels with adjusted coordinates and horizontal y-axis label
# ax.set_xlabel('Index')
# ax.xaxis.set_label_coords(-0.06, -0.12)
ax.set_ylabel('Gas Used', rotation=0)
ax.yaxis.set_label_coords(-0.07, 0.95)

plt.tight_layout()

plt.savefig(output_data_path, format='pdf', bbox_inches='tight', transparent=True)
plt.show()