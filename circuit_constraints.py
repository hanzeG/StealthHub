import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# Define the variable u for logarithmic scaling of the X-axis, evenly spaced in [0,5]
u = np.linspace(0, 5, 200)
# Compute the actual X values using exponential scaling (X ranges from 1 to 1024)
x = 4**u

# Define the Y-axis range
y = np.linspace(20, 41, 200)

# Create meshgrid (U is used as the X-axis coordinate for even spacing)
U, Y_grid = np.meshgrid(u, y)
# Compute Z values
Z = 243 * (4**U) * Y_grid

# Apply base-2 logarithm transformation to Z
Z_log = np.log2(Z)

fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# Plot the surface with logarithmic Z values and apply a colour map
surf = ax.plot_surface(U, Y_grid, Z_log, cmap='YlGn', rstride=1, cstride=1,
                       antialiased=True, edgecolor='none')

ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('Visualization of Surface: Z = 243 * X * Y (log2-transformed)')

# Set X-axis ticks at u = 0,1,2,3,4,5 and convert to base-2 exponent format
x_ticks = [0, 1, 2, 3, 4, 5]
ax.set_xticks(x_ticks)

# Convert 4^u to 2-based exponent (since 4 = 2^2, we use 2^(2u))
def x_exponent_formatter(val, pos):
    exponent = int(2 * val)  # Since 4^u = 2^(2u)
    return r'$2^{%d}$' % exponent

ax.xaxis.set_major_formatter(FuncFormatter(x_exponent_formatter))

# Set Y-axis ticks at multiples of 10: 10, 20, 30, 40, 50
ax.set_yticks(np.arange(20, 41, 5))

# Invert X-axis if needed for symmetry
ax.invert_xaxis()

# Define fixed Z-axis ticks at 8, 12, 16, 20, 24
z_ticks = [12,15, 18,21,24]
ax.set_zticks(z_ticks)

# Custom tick labels for Z-axis, displayed as 2^n
def z_exponent_formatter(x, pos):
    return r'$2^{%d}$' % int(x)

ax.zaxis.set_major_formatter(FuncFormatter(z_exponent_formatter))

# Add a colour bar to represent the Z-axis gradient
cbar = fig.colorbar(surf, shrink=0.5, aspect=10, pad=0.1)
cbar.set_label("Log-scaled Z values (log₂ Z)")

plt.show()
