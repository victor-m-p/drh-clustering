import pandas as pd
import matplotlib.pyplot as plt
import ast
import geopandas as gpd
from shapely.geometry import (
    Polygon,
    MultiPolygon,
)
import matplotlib.patches as mpatches
from PIL import Image
import os


def plot_spatiotemporal(
    gdf,
    time,
    centroid=True,
    active_geometry="geometry",
    alpha=0.2,
    color_column=None,
    zoom=False,
    outpath=False,
):
    fig, ax = plt.subplots(figsize=(15, 10))
    ax.set_axis_off()

    # Set up the world map as a background
    world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
    world.plot(ax=ax, color="lightgray")

    # threshold
    gdf_threshold = gdf[gdf["time_slice_start"] == time]

    # Plot polygons with consistent colors
    for color in gdf_threshold[color_column].unique():
        poll_data = gdf_threshold[gdf_threshold[color_column] == color]
        poll_data.plot(ax=ax, color=color, alpha=alpha)

    # plot centroids
    if centroid:
        centroid_data = gdf_threshold.copy()
        centroid_data[active_geometry] = centroid_data[active_geometry].centroid
        for _, row in centroid_data.iterrows():
            color = row[color_column]
            plt.plot(
                row[active_geometry].x,
                row[active_geometry].y,
                marker="o",
                color=color,
                markersize=5,
            )

    # if zoom set
    if zoom:
        ax.set_xlim([zoom.get("xmin"), zoom.get("xmax")])
        ax.set_ylim([zoom.get("ymin"), zoom.get("ymax")])

    # Create legend patches using consistent color mapping
    # legend_patches = [
    #    mpatches.Patch(color=color_mapping[poll_type], label=poll_type)
    #    for poll_type in gdf[
    #        color_column
    #    ].unique()  # Use all regions from the full dataset
    # ]

    # Add legend to the plot with a consistent position
    # legend = ax.legend(
    #    handles=legend_patches,
    #    title=color_column,
    #    fontsize=16,
    #    bbox_to_anchor=(1, 0.03),
    #    loc="lower right",
    # )
    # plt.setp(legend.get_title(), fontsize=16)

    # Add title
    title = plt.suptitle(f"{time}", fontsize=25)
    title.set_position([0.5, 0.85])

    if outpath:
        plt.savefig(
            outpath,
            dpi=300,
            bbox_inches="tight",
            facecolor="white",
        )
        plt.close()

    else:
        plt.show()


def format_year(year):
    """Format the year for the filename."""
    if year < 0:
        return f"BC_{-year:05d}"
    else:
        return f"AD_{year:05d}"


def create_animation(
    inpath="spatiotemporal_png",
    outpath="spatiotemporal_animation",
    outname="animation",
    format="gif",  # Add format parameter with default as 'gif'
):
    # Ensure output directory exists
    if not os.path.exists(outpath):
        os.makedirs(outpath)

    # Loop through time slices and append each PNG file to frames
    filenames = os.listdir(inpath)
    filenames_ad = sorted([f for f in filenames if "AD" in f])
    filenames_bc = sorted([f for f in filenames if "BC" in f], reverse=True)
    filenames = filenames_bc + filenames_ad

    # Create frames from sorted file names
    frames = []
    for filename in filenames:
        img = Image.open(os.path.join(inpath, filename))
        frames.append(img)

    # Save the frames as an animation
    if format.lower() == "gif":
        # Save as GIF
        gif_filename = os.path.join(outpath, outname + ".gif")
        frames[0].save(
            gif_filename, save_all=True, append_images=frames[1:], duration=500, loop=0
        )
    elif format.lower() == "mp4":
        # Save as MP4
        import matplotlib.pyplot as plt
        import matplotlib.animation as animation

        # Set up the figure
        fig = plt.figure(dpi=300)
        ax = fig.add_subplot(111)
        ax.axis("off")  # Hide axes

        ims = []
        for frame in frames:
            im = ax.imshow(frame, animated=True)
            ims.append([im])

        # Create an animation
        ani = animation.ArtistAnimation(
            fig, ims, interval=500, repeat_delay=1000, blit=True
        )

        # Use ffmpeg as the writer
        Writer = animation.writers["ffmpeg"]
        writer = Writer(
            fps=2,
            metadata=dict(artist="Me"),
            bitrate=5000,
            extra_args=["-vcodec", "libx264", "-pix_fmt", "yuv420p", "-crf", "17"],
        )

        # Save the file
        mp4_filename = os.path.join(outpath, outname + ".mp4")
        ani.save(mp4_filename, writer=writer)
    else:
        raise ValueError("Unsupported format. Choose 'gif' or 'mp4'.")
