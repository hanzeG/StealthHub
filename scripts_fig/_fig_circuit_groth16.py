import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.lines import Line2D

# Data provided
C = [1320, 3960, 9240, 19800, 40920, 83160, 167640, 336600,
     678, 2034, 4746, 10170, 21018, 42714, 86106, 172890,
     240, 720, 1680, 3600, 7440, 15120, 30480, 61200,
     240, 720, 1680, 3600, 7440, 15120, 30480, 61200,
     228, 684, 1596, 3420, 7068, 14364, 28956, 58140]

setup_runtime = [2.65, 6.62, 14.47, 21.68, 28.04, 36.99, 50.49, 93.86,
                 12.26, 15.19, 27.82, 49.63, 112.01, 228.15, 511.6, 3475.97,
                 1.97, 4.83, 10.5, 19.25, 31.27, 54.04, 67.36, 79.05,
                 1.86, 4.3, 9.23, 17.5, 27.15, 41.07, 57.48, 71.47,
                 7.63, 21.1, 36.98, 39.98, 46.34, 82.83, 145.87, 283.62]

prove_runtime = [0.55, 0.82, 1.34, 2.13, 3.73, 6.97, 13.37, 26.15,
                 0.59, 0.9, 1.58, 2.86, 5.22, 9.9, 19.46, 38.27,
                 0.42, 0.48, 0.61, 0.71, 1, 1.54, 2.42, 4.5,
                 0.43, 0.48, 0.56, 0.73, 1, 1.66, 2.57, 4.45,
                 0.47, 0.54, 0.63, 0.87, 1.4, 2.18, 3.79, 6.79]

verify_runtime = [0.37, 0.36, 0.36, 0.36, 0.41, 0.37, 0.38, 0.37,
                  0.37, 0.37, 0.36, 0.44, 0.36, 0.36, 0.37, 0.36,
                  0.37, 0.36, 0.37, 0.36, 0.41, 0.4, 0.43, 0.43,
                  0.36, 0.37, 0.36, 0.38, 0.36, 0.36, 0.37, 0.38,
                  0.36, 0.43, 0.43, 0.36, 0.36, 0.36, 0.42, 0.41]

# New variable: assign a name label to every 8 rows (total 40 rows = 5 groups)
names = ["MiMC"] * 8 + ["GMiMC"] * 8 + ["Poseidon"] * 8 + ["Poseidon2"] * 8 + ["Neptune"] * 8

# Assemble the data into a DataFrame
df = pd.DataFrame({
    'C': C,
    'setup': setup_runtime,
    'prove': prove_runtime,
    'verify': verify_runtime,
    'name': names
})

# Reshape the DataFrame into long format while keeping the 'name' column
df_long = df.melt(id_vars=['C', 'name'], value_vars=['setup', 'prove', 'verify'],
                  var_name='Metric', value_name='Runtime')

# Apply logarithmic transformations
df_long['log2_C'] = np.log2(df_long['C'])
df_long['log10_Runtime'] = np.log10(df_long['Runtime'])

# Set a clean aesthetic style
sns.set(style="whitegrid", context="talk")

# Define styles for name groups: each with a distinct color and marker shape.
# For example: deep blue square, deep purple triangle, dark green diamond, dark red circle, dark cyan inverted triangle.
name_styles = {
    "MiMC":      {"color": "#00008B", "marker": "s"},  # dark blue square
    "GMiMC":     {"color": "#800080", "marker": "^"},  # deep purple triangle
    "Poseidon":  {"color": "#006400", "marker": "D"},  # dark green diamond
    "Poseidon2": {"color": "#8B0000", "marker": "o"},  # dark red circle
    "Neptune":   {"color": "#008B8B", "marker": "v"}   # dark cyan triangle_down
}

# Define line style variations for each metric.
metric_line_styles = {
    "setup": "-",   # solid line
    "prove": "--",  # dashed line
    "verify": ":"   # dotted line
}

# Create the figure and axis
fig, ax = plt.subplots(figsize=(10, 6))

# Plot the discrete points and connect them with lines.
# For each combination of name and Metric, use the name's color and marker,
# and use the metric's line style for connecting lines.
for (name, metric), group in df_long.groupby(['name', 'Metric']):
    group = group.sort_values('log2_C')
    style = name_styles[name]
    line_style = metric_line_styles[metric]
    ax.plot(group['log2_C'], group['log10_Runtime'],
            color=style["color"],
            marker=style["marker"],
            linestyle=line_style,
            linewidth=1.5,
            markersize=8)

# Set axis labels and title
ax.set_xlabel("Exponent (log₂ C)", fontsize=14)
ax.set_ylabel("Runtime (seconds, 10^x)", fontsize=14)
ax.set_title("Runtime Metrics vs C by Name Groups\n(Marker Style & Color for Name; Line Style for Metric)", fontsize=16)

# Format the y-axis ticks to display in scientific notation (10^n)
def y_formatter(val, pos):
    return r"$10^{%d}$" % int(val)
y_min = np.floor(df_long['log10_Runtime'].min())
y_max = np.ceil(df_long['log10_Runtime'].max())
y_ticks = np.arange(y_min, y_max + 1, 1)
ax.set_yticks(y_ticks)
ax.yaxis.set_major_formatter(FuncFormatter(y_formatter))

# Create custom legend handles for name groups (showing color and marker)
names_order = ["MiMC", "GMiMC", "Poseidon", "Poseidon2", "Neptune"]
name_handles = [Line2D([], [], marker=name_styles[n]["marker"], color=name_styles[n]["color"],
                       linestyle='None', markersize=8, label=n) for n in names_order]

# Create custom legend handles for metrics (showing line style)
metric_handles = [Line2D([], [], color='black', linestyle=metric_line_styles[m], marker='',
                           linewidth=2, label=m) for m in ["setup", "prove", "verify"]]

# Add the legends to the plot.
legend_names = ax.legend(handles=name_handles, title="Name Group", loc='upper left', fontsize=12, title_fontsize=13)
legend_metrics = ax.legend(handles=metric_handles, title="Metric", loc='upper right', fontsize=12, title_fontsize=13)
ax.add_artist(legend_names)

plt.tight_layout()
plt.show()