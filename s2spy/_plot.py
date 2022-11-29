from typing import Dict
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import dates as mdates
from matplotlib.patches import Patch
from matplotlib.patches import Rectangle


def make_color_array(n_targets: int, n_intervals: int) -> np.ndarray:
    """Util that generates the colormap for the intervals.

    Args:
        n_targets: number of target intervals
        n_intervals: total number of intervals

    Returns:
        1-D array containing hex colors.
    """
    colors = np.array(["#ffffff"] * n_intervals)
    if n_targets > 0:
        colors[0:n_targets:2] = "#ff7700"  # Orange
        colors[1:n_targets:2] = "#ffa100"  # Orange (darker)
    if n_intervals - n_targets > 0:
        colors[n_targets::2] = "#1f9ce9"  # Blue
        colors[n_targets + 1 :: 2] = "#137fc1"  # Blue (darker)
    return colors[::-1]


def _get_xdata(
    relative_dates: bool,
    year_intervals: pd.Series,
    widths: np.ndarray,
    anchor_date: pd.Timestamp,
) -> np.ndarray:
    """Util that generates the x-coordinate of every interval rectangle for the plot.

    Args:
        relative_dates: If False, absolute dates will be used. If True, each anchor year
                        is aligned by the anchor date, so that all anchor years line up
                        vertically.
        year_intervals: The Series of intervals for a single anchor year.
        widths: Width of each interval, as generated by _get_widths.
        anchor_date: The anchor date.

    Returns:
        1-D array containing the x-coordinates for every interval rectangle.
    """
    if relative_dates:
        x_data = np.array([(i.left - anchor_date).days for i in year_intervals])
        return x_data + 0.5 * widths

    x_data = np.array([i.left for i in year_intervals])
    return x_data + 0.5 * widths


def _get_widths(
    relative_dates: bool,
    year_intervals: pd.Series,
) -> np.ndarray:
    """Util that generates the width of every interval rectangle for the plot.

    Args:
        relative_dates: If False, absolute dates will be used. If True, each anchor year
                        is aligned by the anchor date, so that all anchor years line up
                        vertically.
        year_intervals: The series of intervals for a single anchor year.

    Returns:
        1-D array containing the width of every interval rectangle.
    """
    if relative_dates:
        return np.array([(i.right - i.left).days for i in year_intervals])
    return np.array([(i.right - i.left) for i in year_intervals])


def generate_plot_data(
    calendar,
    relative_dates: bool,
    year_intervals: pd.Series,
) -> Dict:
    """Util to generate the plotting data, containing all variables to plot.

    Args:
        relative_dates: If False, absolute dates will be used. If True, each anchor year
                        is aligned by the anchor date, so that all anchor years line up
                        vertically.
        year_intervals: The pandas series of intervals for a single anchor year.

        n_targets: The number of target intervals in the calendar.

    Returns:
        Dict: Dictionary containing all the data to generate the Matplotlib or Bokeh
            plots.
    """
    n_targets = calendar.n_targets

    anchor_date = calendar._get_anchor(year=year_intervals.values[-1].left.year)  # type: ignore # pylint: disable=protected-access

    widths = _get_widths(relative_dates, year_intervals)
    interval_str = np.array(
        [f"{str(i.left)[:10]} -> {str(i.right)[:10]}" for i in year_intervals]
    )

    types = np.array(["Precursor"] * len(year_intervals))
    types[-n_targets:] = "Target"

    width_days = widths if relative_dates else np.array([x.days for x in widths])

    return {
        "x": _get_xdata(relative_dates, year_intervals, widths, anchor_date),
        "y": np.ones(len(year_intervals)) * anchor_date.year,
        "height": np.ones(len(year_intervals)) * 0.8,
        "width": widths,
        "width_days": width_days,
        "color": make_color_array(n_targets, len(year_intervals)),
        "desc": interval_str,
        "type": types,
    }


def plot_rectangles(ax: plt.Axes, data: Dict, show_length: bool):
    """Generates rectangles from the input data.

    Args:
        ax: Axis in which the rectangles should be shown.
        data: Data dictionary containing x, y, width, height, color and width_days.
        show_length: If the length of each interval should be displayed as text.
    """
    for _, row in pd.DataFrame(data).iterrows():  # type: ignore
        ax.add_patch(
            Rectangle(
                xy=(row["x"] - row["width"] / 2, row["y"] - row["height"] / 2),
                width=row["width"],
                height=row["height"],
                facecolor=row["color"],
                alpha=0.7,
                edgecolor="k",
                linewidth=1.5,
            )
        )

        if show_length:
            ax.text(
                x=row["x"],
                y=row["y"],
                s=f"{row['width_days']}",
                c="k",
                size=8,
                ha="center",
                va="center",
            )


# pylint: disable=too-many-arguments
def matplotlib_visualization(
    calendar,
    n_years: int,
    relative_dates: bool,
    show_length: bool = False,
    add_legend: bool = True,
    add_yticklabels: bool = True,
    ax = None,
):
    """Visualization routine for generating a calendar visualization with Bokeh.

    Args:
        calendar: Mapped calendar which should be visualized.
        n_years: Number of years which should be displayed (most recent years only).
        relative_dates: If False, absolute dates will be used. If True, each anchor year
                        is aligned by the anchor date, so that all anchor years line up
                        vertically.
        show_length: If the length of every periods should be displayed. Defaults False.
        add_yticklabels: If the years should be displayed on the y-axis ticks.
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(7,4))

    intervals = calendar.get_intervals()[:n_years]

    for _, year_intervals in intervals.iterrows():
        data = generate_plot_data(
            calendar=calendar,
            relative_dates=relative_dates,
            year_intervals=year_intervals,
        )
        plot_rectangles(ax, data, show_length)

    ax.set_xlabel("Days before anchor date" if relative_dates else "Date")
    ax.set_ylabel("Anchor year")

    if relative_dates:
        ax.set_xlim(
            (
                np.min(data["x"]) - data["width"][np.argmin(data["x"])] / 2 - 5,  # type: ignore
                np.max(data["x"]) + data["width"][np.argmax(data["x"])] / 2 + 5,  # type: ignore
            )
        )
    else:
        formatter = mdates.DateFormatter("%Y-%m-%d")
        ax.xaxis.set_major_formatter(formatter)
        ax.set_xlim(
            (
                intervals.stack().values.min().left - pd.Timedelta(days=5),
                intervals.stack().values.max().right + pd.Timedelta(days=5),
            )
        )

    ax.set_ylim([intervals.index.min() - 0.5, intervals.index.max() + 0.5])  # type: ignore
    ax.set_yticks([int(x) for x in intervals.index.to_list()])

    if not add_yticklabels:
        ax.set_yticklabels([])

    # Add a custom legend to explain to users what the colors mean
    if add_legend:
        legend_elements = [
        Patch(
            facecolor="#ff8c00",
            label="Target interval",
            linewidth=1.5,
        ),
        Patch(
            facecolor="#137fc1",
            label="Precursor interval",
            linewidth=1.5,
        ),
        ]
        ax.legend(handles=legend_elements, loc="center left", bbox_to_anchor=(1, 0.5))
