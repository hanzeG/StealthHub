import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import matplotlib.colors as mcolors

# Increase default font sizes for all text elements
plt.rcParams.update({
    'font.size': 14,
    'axes.titlesize': 14,
    'axes.labelsize': 14,
    'xtick.labelsize': 14,
    'ytick.labelsize': 14,
    'legend.fontsize': 14,
    'figure.titlesize': 14
})

# Define the variable u for logarithmic scaling of the X-axis, evenly spaced in [0, 5]
u = np.linspace(0, 5, 500)
# Compute the actual X values using exponential scaling (X ranges from 1 to 1024)
x = 4**u

# Define the Y-axis range
y = np.linspace(20, 41, 50)

# Create meshgrid (U is used as the X-axis coordinate for even spacing)
U, Y_grid = np.meshgrid(u, y)
# Compute Z values
Z = 678 * (4**U) * Y_grid

# Apply base‑2 logarithm transformation to Z so that the z coordinate represents the exponent
Z_log = np.log2(Z)

# Define the discrete boundaries for the colour mapping: one bin per integer exponent from 10 to 26.
boundaries = np.arange(10, 27, 1)
# Create a discrete version of the 'YlGn' colormap with one colour per bin.
discrete_cmap = plt.get_cmap('YlGn', len(boundaries) - 1)
# Define a norm that maps values into the discrete bins.
norm = mcolors.BoundaryNorm(boundaries, discrete_cmap.N, clip=False)

fig = plt.figure(figsize=(6, 4))
ax = fig.add_subplot(111, projection='3d')

# Plot the surface using the discrete colormap and norm.
surf = ax.plot_surface(
    U, Y_grid, Z_log,
    cmap=discrete_cmap, norm=norm,
    rstride=1, cstride=1, antialiased=True, edgecolor='none',
    rasterized=True  
)

ax.set_xlabel('batch size b')
ax.set_ylabel('tree height h')
ax.set_zlabel('log of constraint number')

# Set X-axis ticks at u = 0, 1, 2, 3, 4, 5 and convert them to base‑2 exponent format.
x_ticks = [0, 1, 2, 3, 4, 5]
ax.set_xticks(x_ticks)

def x_exponent_formatter(val, pos):
    # Since X = 4^u = 2^(2u)
    exponent = int(2 * val)
    return r'$2^{%d}$' % exponent

ax.xaxis.set_major_formatter(FuncFormatter(x_exponent_formatter))

# Set Y-axis ticks at an interval of 5 (from 20 to 40)
ax.set_yticks(np.arange(20, 41, 5))

# Invert X-axis if needed for symmetry
ax.invert_xaxis()

# Define fixed Z-axis ticks (using the discrete exponents for display)
z_ticks = [10, 13, 16, 19, 22, 25]
ax.set_zticks(z_ticks)

def z_exponent_formatter(x, pos):
    return r'$2^{%d}$' % int(x)

ax.zaxis.set_major_formatter(FuncFormatter(z_exponent_formatter))

# Define fewer ticks for the colourbar to avoid clutter (every 2nd tick)
cbar_ticks = np.arange(10, 27, 2)

# Add a colourbar using the discrete norm and colormap.
cbar = fig.colorbar(surf, ax=ax, shrink=1, aspect=10, pad=0.12,
                    boundaries=boundaries, ticks=cbar_ticks)
cbar.solids.set_alpha(0.7)
cbar.outline.set_visible(False)
cbar.ax.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: r'$%d$' % int(x)))

plt.savefig("gmimc_con.pdf", format="pdf", bbox_inches="tight", pad_inches=0.1, dpi=72)
plt.show()