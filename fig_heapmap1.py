import json
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize
import matplotlib.ticker as ticker

# Custom logarithmic normalisation using base 2
class LogNorm2(Normalize):
    def __init__(self, vmin=None, vmax=None, clip=False):
        super().__init__(vmin, vmax, clip)
    
    def __call__(self, value, clip=None):
        if clip is None:
            clip = self.clip
        result = np.ma.masked_array(value, np.isnan(value))
        vmin, vmax = self.vmin, self.vmax
        if vmin is None or vmax is None:
            vmin, vmax = result.min(), result.max()
        if clip:
            result = np.clip(result, vmin, vmax)
        log_vmin = np.log2(vmin)
        log_vmax = np.log2(vmax)
        return (np.log2(result) - log_vmin) / (log_vmax - log_vmin)
    
    def inverse(self, value):
        vmin, vmax = self.vmin, self.vmax
        log_vmin = np.log2(vmin)
        log_vmax = np.log2(vmax)
        return 2**(value * (log_vmax - log_vmin) + log_vmin)

# Load the metrics data from the JSON file
with open('metrics_data.json', 'r') as f:
    metrics = json.load(f)

# Combine the data from all groups into one DataFrame
frames = []
for group, records in metrics.items():
    df_group = pd.DataFrame(records)
    df_group['Group'] = group
    frames.append(df_group)
df = pd.concat(frames, ignore_index=True)

# Pivot so that rows are groups and columns are the height values.
pivot = df.pivot(index='Group', columns='height', values='setup_runtime')

# Normalize so that the smallest value becomes 1.
min_val = pivot.min().min()
normalized = pivot / min_val

# Set fixed normalization range from 2^0 to 2^11.
fixed_vmin = 2**0    # 1
fixed_vmax = 2**11   # 2048

# Create a custom warm colormap.
warm_cmap = LinearSegmentedColormap.from_list("warm_cmap", 
                                              [(0.0, "orange"), 
                                               (0.33, "red"), 
                                               (0.67, "purple"), 
                                               (1.0, "black")])

# Create normalisation instance with fixed range.
norm_inst = LogNorm2(vmin=fixed_vmin, vmax=fixed_vmax)

plt.rcParams.update({
    'font.size': 9,          
    'axes.titlesize': 9,     
    'axes.labelsize': 9,     
    'xtick.labelsize': 9,    
    'ytick.labelsize': 9,    
    'legend.fontsize': 9,    
    'figure.titlesize': 9    
})

plt.figure(figsize=(3, 1.5))
ax = sns.heatmap(normalized, annot=False, cmap=warm_cmap,
                 norm=norm_inst,
                 cbar_kws={'aspect': 8})

# Set x-axis tick labels as powers of 2 (e.g. 2^1, 2^2, ...).
new_labels = [r'$2^{%d}$' % int(x) for x in pivot.columns]
ax.set_xticklabels(new_labels)

# Modify the colourbar to display fewer ticks.
cbar = ax.collections[0].colorbar
# Create ticks for every 2nd power, from 2^0 to 2^10.
ticks_values = [2**i for i in range(0, 12, 2)]
cbar.set_ticks(ticks_values)
def base2_formatter(x, pos):
    exponent = int(round(np.log2(x)))
    return f"$2^{{{exponent}}}$"
cbar.ax.yaxis.set_major_formatter(ticker.FuncFormatter(base2_formatter))

ax.xaxis.set_label_coords(-0.17, -0.08)

plt.tight_layout()
plt.savefig("figure/hm1.pdf", format='pdf', bbox_inches='tight', transparent=True)
plt.show()