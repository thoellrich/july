import calendar
import numpy as np
import matplotlib.pyplot as plt
from numpy.typing import ArrayLike
from typing import List, Tuple, Any, Optional
from datetime import date


def date_grid(
    dates: List[date], data: List[Any], flip: bool, dtype: str = "float64"
) -> ArrayLike:
    # Array with columns (iso year, iso week number, iso weekday).
    iso_dates = np.array([day.isocalendar() for day in dates])
    # Unique weeks, as defined by the tuple (iso year, iso week).
    unique_weeks = sorted(list(set([tuple(row) for row in iso_dates[:, :2]])))

    # Get dict that maps week tuple to week index in grid.
    weeknum2idx = {week: i for i, week in enumerate(unique_weeks)}
    week_coords = np.array([weeknum2idx[tuple(week)] for week in iso_dates[:, :2]])
    day_coords = iso_dates[:, 2] - 1

    # Define shape of grid.
    n_weeks = len(unique_weeks)
    n_days = 7

    # Create grid and fill with data.
    grid = np.empty((n_weeks, n_days), dtype=dtype)
    grid = np.nan * grid if dtype == "float64" else grid
    grid[week_coords, day_coords] = data

    if flip:
        return grid.T

    return grid


def cal_heatmap(
    cal: ArrayLike,
    dates,
    flip: bool,
    title=None,
    cmap: str = "Greens",
    colorbar: bool = False,
    date_label: bool = False,
    weekday_label: bool = True,
    month_label: bool = False,
    year_label: bool = False,
    month_grid: bool = False,
    cmin=None,
    cmax=None,
    ax=None,
):
    if not ax:
        figsize = (10, 5) if flip else (5, 10)
        fig, ax = plt.subplots(figsize=figsize, dpi=100)
    else:
        fig = ax.get_figure()

    ax.set_facecolor("white")

    pc = ax.pcolormesh(cal, edgecolors=ax.get_facecolor(), linewidth=0.25, cmap=cmap)
    pc.set_clim(cmin or np.nanmin(cal), cmax or np.nanmax(cal))
    ax.invert_yaxis()
    ax.set_aspect("equal")
    bbox = ax.get_position()

    if date_label:
        add_date_label(ax, dates, flip)
    if weekday_label:
        add_weekday_label(ax, flip)
    if month_label:
        add_month_label(ax, dates, flip)
    if year_label:
        add_year_label(ax, dates, flip)
    if month_grid:
        add_month_grid(ax, dates, cal, flip)
    if colorbar:
        adj_bbox = ax.get_position()
        height_diff = adj_bbox.height - bbox.height
        # Specify location and dimensions: [left, bottom, width, height].
        # This part is still not perfect when month_grid is True.
        cax = fig.add_axes(
            [
                bbox.x1 + 0.015,
                adj_bbox.y0 + height_diff / 2,
                0.015,
                bbox.height,
            ]
        )
        cbar = plt.colorbar(pc, cax=cax)
        cbar.ax.tick_params(size=0)
    if title:
        ax.set_title(title, fontname="monospace", fontsize=18, pad=25)

    ax.tick_params(axis="both", which="both", length=0)
    return ax


def add_date_label(ax, dates: List[date], flip: bool) -> None:
    days = [day.day for day in dates]
    day_grid = date_grid(dates, days, flip)

    for i, j in np.ndindex(day_grid.shape):
        try:
            ax.text(j + 0.5, i + 0.5, int(day_grid[i, j]), ha="center", va="center")
        except ValueError:
            # If date_grid[i, j] is nan.
            pass


def add_weekday_label(ax, flip: bool) -> None:
    if flip:
        ax.tick_params(axis="y", which="major", pad=8)
        ax.set_yticks([x + 0.5 for x in range(0, 7)])
        ax.set_yticklabels(
            calendar.weekheader(width=1).split(" "), fontname="monospace"
        )
    else:
        ax.tick_params(axis="x", which="major", pad=4)
        ax.set_xticks([x + 0.5 for x in range(0, 7)])
        ax.set_xticklabels(
            calendar.weekheader(width=1).split(" "), fontname="monospace"
        )
        ax.xaxis.tick_top()


def add_month_label(ax, dates: List[date], flip: bool) -> None:
    month_years = [(day.year, day.month) for day in dates]
    month_years_str = list(map(str, month_years))
    month_year_grid = date_grid(dates, month_years_str, flip, dtype="object")

    unique_month_years = sorted(set(month_years))

    month_locs = {}
    for month in unique_month_years:
        # Get 'avg' x, y coordinates of elements in grid equal to month_year.
        yy, xx = np.nonzero(month_year_grid == str(month))
        month_locs[month] = (
            xx.max() + 1 + xx.min() if flip else yy.max() + 1 + yy.min()
        ) / 2

    # Get month label for each unique month_year.
    month_labels = [calendar.month_abbr[x[1]] for x in month_locs.keys()]

    if flip:
        ax.set_xticks([*month_locs.values()])
        ax.set_xticklabels(month_labels, fontsize=14, fontname="monospace", ha="center")
    else:
        ax.set_yticks([*month_locs.values()])
        ax.set_yticklabels(
            month_labels, fontsize=14, fontname="monospace", rotation=90, va="center"
        )


def add_year_label(ax, dates, flip):
    years = [day.year for day in dates]
    year_grid = date_grid(dates, years, flip)
    unique_years = sorted(set(years))

    year_locs = {}
    for year in unique_years:
        yy, xx = np.nonzero(year_grid == year)
        year_locs[year] = (
            xx.max() + 1 + xx.min() if flip else yy.max() + 1 + yy.min()
        ) / 2

    if flip:
        for year, loc in year_locs.items():
            ax.annotate(
                year,
                (loc / year_grid.shape[1], 1),
                (0, 10),
                xycoords="axes fraction",
                textcoords="offset points",
                fontname="monospace",
                fontsize=16,
                va="center",
                ha="center",
            )
    else:
        for year, loc in year_locs.items():
            ax.annotate(
                year,
                (0, 1 - loc / len(year_grid)),
                (-40, 0),
                xycoords="axes fraction",
                textcoords="offset points",
                rotation=90,
                fontname="monospace",
                fontsize=16,
                va="center",
            )


def get_month_outline(dates, month_grid, flip, month):
    # This code is so ugly I'm amazed that it works.
    day_grid = date_grid(dates, dates, flip=False, dtype="object")
    if flip:
        month_grid = month_grid.T

    nrows, ncols = month_grid.shape
    coords_list = []
    for y in range(nrows):
        for x in range(ncols):
            if np.isfinite(month_grid[y, x]):
                if day_grid[y, x].month == month:
                    coords_list.append((x, y))

    sorted_coords = np.array(coords_list)
    min_y = sorted_coords[:, 1].min()
    max_y = sorted_coords[:, 1].max()
    upper_left = sorted_coords[0]
    upper_right = np.array([7, min_y])
    lower_right = np.array([7, max_y])
    lower_right2 = sorted_coords[-1] + np.array([1, 1])

    lower_right1 = (
        lower_right2
        if np.array_equal(lower_right, lower_right2)
        else lower_right2 - np.array([0, 1])
    )
    lower_left = np.array([0, sorted_coords[:, 1].max() + 1])
    corner_last = upper_left + np.array([0, 1])
    second_last = np.copy(corner_last)
    second_last[0] = 0

    coords = np.array(
        [
            upper_left,
            upper_right,
            lower_right,
            lower_right1,
            lower_right2,
            lower_left,
            second_last,
            corner_last,
            upper_left,
        ]
    )

    return coords[:, [1, 0]] if flip else coords


def add_month_grid(ax, dates, month_grid, flip):
    months = set([d.month for d in dates])
    for month in months:
        coords = get_month_outline(dates, month_grid, flip=flip, month=month)
        ax.plot(coords[:, 0], coords[:, 1], color="black", linewidth=2)

    # Pad axes so plotted line appears uniform also along edges.
    ax.set_xlim(ax.get_xlim()[0] - 0.03, ax.get_xlim()[1] + 0.05)
    ax.set_ylim(ax.get_ylim()[0] + 0.04, ax.get_ylim()[1] - 0.03)
    f = ax.get_figure()
    # Set frame in facecolor instead of turning off frame to keep cbar alignment.
    for pos in ["top", "bottom", "right", "left"]:
        ax.spines[pos].set_edgecolor(f.get_facecolor())
    return ax