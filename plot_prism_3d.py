import rasterio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
from mpl_toolkits.mplot3d import Axes3D
import cartopy.io.shapereader as shpreader
import glob
import os

root_dir = "your_dir"
file_paths = sorted(glob.glob(os.path.join(root_dir, "**", "*.bil"), recursive=True))

precip_stack = []
for file in file_paths:
    with rasterio.open(file) as src:
        data = src.read(1).astype(float)
        data[data <= 0] = np.nan 
        precip_stack.append(data)
        if len(precip_stack) == 1:
            transform = src.transform
            bounds = src.bounds
            width = src.width
            height = src.height


precip_stack = np.array(precip_stack)
lon = np.linspace(bounds.left, bounds.right, width)
lat = np.linspace(bounds.top, bounds.bottom, height)
lon2d, lat2d = np.meshgrid(lon, lat)

shpfilename = shpreader.natural_earth(resolution='50m',
                                      category='cultural',
                                      name='admin_1_states_provinces_lakes')
reader = shpreader.Reader(shpfilename)
us_states = [rec.geometry for rec in reader.records() if rec.attributes['admin'] == 'United States of America']


fig = plt.figure(figsize=(38.4, 21.6), dpi=300) 
ax = fig.add_subplot(111, projection='3d')
def plot_us_states_on_surface(ax, z_offset=0):
    for state in us_states:
        try:
            x, y = state.exterior.xy
            ax.plot(x, y, z_offset, color='black', linewidth=0.3)
        except AttributeError:
            for part in state.geoms:
                x, y = part.exterior.xy
                ax.plot(x, y, z_offset, color='black', linewidth=0.3)

def update(frame):
    ax.clear()
    z = precip_stack[frame]
    ax.plot_surface(
        lon2d, lat2d, z,
        cmap='plasma',
        edgecolor='none',
        antialiased=False,
        rstride=1, cstride=1,
        alpha=0.95
    )
    plot_us_states_on_surface(ax, z_offset=0)
    ax.set_xlim(lon.min(), lon.max())
    ax.set_ylim(lat.min(), lat.max())
    ax.set_zlim(0, np.nanmax(precip_stack))

    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])
    ax.set_axis_off()
    ax.view_init(elev=35, azim=-120)

anim = FuncAnimation(fig, update, frames=len(precip_stack), interval=500)
writer = FFMpegWriter(fps=2, metadata=dict(artist='Naveen Sudharsan'), bitrate=10000)
anim.save("prism_precip_3d_4k_clean.mp4", writer=writer, dpi=300)
