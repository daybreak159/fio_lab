#!/usr/bin/env python3
"""Generate charts from FIO summary.csv."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


SCRIPT_DIR = Path(__file__).resolve().parent
RESULTS_DIR = SCRIPT_DIR.parent / "results"
SUMMARY_CSV = RESULTS_DIR / "summary.csv"
OUTPUT_DIR = SCRIPT_DIR.parent / "images"

BASELINE_ORDER = ["seq_read", "seq_write", "rand_read", "rand_write"]
ENGINE_ORDER = ["pvsync", "libaio", "io_uring", "mmap"]
RW_LABELS = {
    "read": "Seq Read",
    "write": "Seq Write",
    "randread": "Rand Read",
    "randwrite": "Rand Write",
}
ENGINE_DEPTH_COMPARE = {
    "randread": {
        1: {
            "pvsync": {"iops": 7630.18, "bw_mib_s": 29.80, "lat_mean_us": 130.66},
            "libaio": {"iops": 7794.37, "bw_mib_s": 30.45, "lat_mean_us": 123.54},
            "io_uring": {"iops": 7882.60, "bw_mib_s": 30.79, "lat_mean_us": 122.19},
            "mmap": {"iops": 7511.03, "bw_mib_s": 29.34, "lat_mean_us": 132.58},
        },
        32: {
            "pvsync": {"iops": 7789.89, "bw_mib_s": 30.43, "lat_mean_us": 128.35},
            "libaio": {"iops": 139734.18, "bw_mib_s": 545.84, "lat_mean_us": 227.01},
            "io_uring": {"iops": 139722.86, "bw_mib_s": 545.79, "lat_mean_us": 227.12},
            "mmap": {"iops": 7482.98, "bw_mib_s": 29.23, "lat_mean_us": 133.55},
        },
    },
    "randwrite": {
        1: {
            "pvsync": {"iops": 12624.71, "bw_mib_s": 49.31, "lat_mean_us": 82.42},
            "libaio": {"iops": 15803.62, "bw_mib_s": 61.73, "lat_mean_us": 58.88},
            "io_uring": {"iops": 14861.20, "bw_mib_s": 58.05, "lat_mean_us": 62.75},
            "mmap": {"iops": 1495.10, "bw_mib_s": 5.84, "lat_mean_us": 667.83},
        },
        32: {
            "pvsync": {"iops": 8580.28, "bw_mib_s": 33.52, "lat_mean_us": 121.43},
            "libaio": {"iops": 20834.87, "bw_mib_s": 81.39, "lat_mean_us": 1600.39},
            "io_uring": {"iops": 29640.09, "bw_mib_s": 115.78, "lat_mean_us": 1511.51},
            "mmap": {"iops": 1392.39, "bw_mib_s": 5.44, "lat_mean_us": 720.56},
        },
    },
}


plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial Unicode MS", "Noto Sans CJK SC", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False
plt.style.use("seaborn-v0_8-whitegrid")


def save_figure(fig: plt.Figure, outdir: Path, filename: str) -> None:
    fig.tight_layout()
    fig.savefig(outdir / filename, dpi=180, bbox_inches="tight")
    plt.close(fig)


def size_to_bytes(raw: str) -> int:
    raw = str(raw).strip().lower()
    if not raw:
        return 0
    unit_map = {"k": 1024, "m": 1024 ** 2, "g": 1024 ** 3, "t": 1024 ** 4}
    if raw[-1] in unit_map:
        return int(float(raw[:-1]) * unit_map[raw[-1]])
    return int(float(raw))


def load_rows(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(
                {
                    "category": row["category"],
                    "experiment": row["experiment"],
                    "rw": row["rw"],
                    "bs": row["bs"],
                    "ioengine": row["ioengine"],
                    "numjobs": int(row["numjobs"]),
                    "iodepth": int(row["iodepth"]),
                    "iops": float(row["iops"]),
                    "bw_mib_s": float(row["bw_mib_s"]),
                    "lat_mean_us": float(row["lat_mean_us"]),
                    "lat_p95_us": float(row["lat_p95_us"]) if row["lat_p95_us"] else None,
                    "lat_p99_us": float(row["lat_p99_us"]) if row["lat_p99_us"] else None,
                }
            )
    return rows


def annotate_bars(ax: plt.Axes, fmt: str) -> None:
    ymax = ax.get_ylim()[1]
    for patch in ax.patches:
        height = patch.get_height()
        if height <= 0:
            continue
        ax.text(
            patch.get_x() + patch.get_width() / 2,
            height + ymax * 0.015,
            format(height, fmt),
            ha="center",
            va="bottom",
            fontsize=8,
        )


def plot_baseline(rows: list[dict[str, object]], outdir: Path) -> None:
    subset = [row for row in rows if row["category"] == "baseline"]
    subset.sort(key=lambda row: BASELINE_ORDER.index(str(row["experiment"])))

    labels = [RW_LABELS[str(row["rw"])] for row in subset]
    iops = [float(row["iops"]) for row in subset]
    bw = [float(row["bw_mib_s"]) for row in subset]
    lat = [float(row["lat_mean_us"]) for row in subset]
    colors = ["#2D6A4F", "#40916C", "#1D3557", "#E76F51"]

    chart_specs = [
        ("chart_baseline_iops.png", iops, "Baseline IOPS", "IOPS", ".0f"),
        ("chart_baseline_bandwidth.png", bw, "Baseline Bandwidth", "MiB/s", ".1f"),
        ("chart_baseline_latency.png", lat, "Baseline Mean Latency", "us", ".1f"),
    ]

    for filename, values, title, ylabel, fmt in chart_specs:
        fig, ax = plt.subplots(figsize=(6.4, 4.8))
        ax.bar(labels, values, color=colors)
        ax.set_title(title)
        ax.set_ylabel(ylabel)
        annotate_bars(ax, fmt)
        save_figure(fig, outdir, filename)


def plot_blocksize(rows: list[dict[str, object]], outdir: Path) -> None:
    subset = [row for row in rows if row["category"] == "blocksize"]
    subset.sort(key=lambda row: (str(row["rw"]), size_to_bytes(str(row["bs"]))))

    by_rw: dict[str, list[dict[str, object]]] = {"randread": [], "randwrite": []}
    for row in subset:
        by_rw[str(row["rw"])].append(row)

    series = [
        ("chart_blocksize_iops.png", "iops", "IOPS vs Block Size", "IOPS"),
        ("chart_blocksize_bandwidth.png", "bw_mib_s", "Bandwidth vs Block Size", "MiB/s"),
        ("chart_blocksize_latency.png", "lat_mean_us", "Mean Latency vs Block Size", "us"),
    ]
    colors = {"randread": "#1D4ED8", "randwrite": "#DC2626"}
    labels = {"randread": "Random Read", "randwrite": "Random Write"}

    for filename, field, title, ylabel in series:
        fig, ax = plt.subplots(figsize=(6.8, 4.8))
        for rw in ("randread", "randwrite"):
            points = by_rw[rw]
            x = [str(row["bs"]) for row in points]
            y = [float(row[field]) for row in points]
            ax.plot(x, y, marker="o", linewidth=2, color=colors[rw], label=labels[rw])
        ax.set_title(title)
        ax.set_xlabel("Block Size")
        ax.set_ylabel(ylabel)
        ax.legend()
        save_figure(fig, outdir, filename)


def build_matrix(rows: list[dict[str, object]], value_key: str) -> tuple[list[int], list[int], list[list[float]]]:
    numjobs = sorted({int(row["numjobs"]) for row in rows})
    iodepths = sorted({int(row["iodepth"]) for row in rows})
    matrix: list[list[float]] = []

    for nj in numjobs:
        current = []
        for iod in iodepths:
            match = next(row for row in rows if int(row["numjobs"]) == nj and int(row["iodepth"]) == iod)
            current.append(float(match[value_key]))
        matrix.append(current)

    return numjobs, iodepths, matrix


def annotate_heatmap(
    ax: plt.Axes,
    image: matplotlib.image.AxesImage,
    matrix: list[list[float]],
    use_kilo: bool = False,
) -> None:
    for row_idx, row in enumerate(matrix):
        for col_idx, value in enumerate(row):
            label = f"{value/1000:.1f}K" if use_kilo else f"{value:.0f}"
            normalized = image.norm(value)
            color = "black" if normalized > 0.68 else "white"
            ax.text(col_idx, row_idx, label, ha="center", va="center", color=color, fontsize=8)


def save_heatmap(
    outdir: Path,
    filename: str,
    rows: list[dict[str, object]],
    value_key: str,
    title: str,
    use_kilo: bool = False,
) -> None:
    numjobs, iodepths, matrix = build_matrix(rows, value_key)
    fig, ax = plt.subplots(figsize=(6.4, 4.8))
    image = ax.imshow(matrix, cmap="viridis", aspect="auto")
    ax.set_title(title)
    ax.set_xlabel("iodepth")
    ax.set_ylabel("numjobs")
    ax.set_xticks(range(len(iodepths)))
    ax.set_xticklabels(iodepths)
    ax.set_yticks(range(len(numjobs)))
    ax.set_yticklabels(numjobs)
    annotate_heatmap(ax, image, matrix, use_kilo=use_kilo)
    fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    save_figure(fig, outdir, filename)


def plot_queue_heatmaps(rows: list[dict[str, object]], outdir: Path) -> None:
    subset = [row for row in rows if row["category"] == "queue"]
    read_rows = [row for row in subset if row["rw"] == "randread"]
    write_rows = [row for row in subset if row["rw"] == "randwrite"]

    plots = [
        ("chart_queue_read_iops.png", read_rows, "iops", "Random Read IOPS", True),
        ("chart_queue_write_iops.png", write_rows, "iops", "Random Write IOPS", True),
        ("chart_queue_read_latency.png", read_rows, "lat_mean_us", "Random Read Mean Latency (us)", False),
        ("chart_queue_write_latency.png", write_rows, "lat_mean_us", "Random Write Mean Latency (us)", False),
    ]

    for filename, current_rows, field, title, use_kilo in plots:
        save_heatmap(outdir, filename, current_rows, field, title, use_kilo=use_kilo)


def plot_engine(rows: list[dict[str, object]], outdir: Path) -> None:
    subset = [row for row in rows if row["category"] == "engine"]
    read_rows = sorted(
        [row for row in subset if row["rw"] == "randread"],
        key=lambda row: ENGINE_ORDER.index(str(row["ioengine"])),
    )
    write_rows = sorted(
        [row for row in subset if row["rw"] == "randwrite"],
        key=lambda row: ENGINE_ORDER.index(str(row["ioengine"])),
    )

    labels = [str(row["ioengine"]) for row in read_rows]
    x = list(range(len(labels)))
    width = 0.38

    metrics = [
        ("chart_engine_iops.png", "iops", "IOPS by I/O Engine", "IOPS"),
        ("chart_engine_bandwidth.png", "bw_mib_s", "Bandwidth by I/O Engine", "MiB/s"),
        ("chart_engine_latency.png", "lat_mean_us", "Mean Latency by I/O Engine", "us"),
    ]

    for filename, field, title, ylabel in metrics:
        fig, ax = plt.subplots(figsize=(6.8, 4.8))
        read_values = [float(row[field]) for row in read_rows]
        write_values = [float(row[field]) for row in write_rows]
        ax.bar([idx - width / 2 for idx in x], read_values, width=width, label="Random Read", color="#2563EB")
        ax.bar([idx + width / 2 for idx in x], write_values, width=width, label="Random Write", color="#EF4444")
        ax.set_title(title)
        ax.set_ylabel(ylabel)
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend()
        save_figure(fig, outdir, filename)


def plot_engine_depth_compare(outdir: Path) -> None:
    metric_specs = [
        ("iops", "IOPS", "chart_engine_read_iops_depth.png", "chart_engine_write_iops_depth.png"),
        ("bw_mib_s", "MiB/s", "chart_engine_read_bw_depth.png", "chart_engine_write_bw_depth.png"),
        ("lat_mean_us", "us", "chart_engine_read_lat_depth.png", "chart_engine_write_lat_depth.png"),
    ]
    title_map = {"randread": "Random Read", "randwrite": "Random Write"}
    depth_labels = {1: "iodepth=1", 32: "iodepth=32"}
    colors = {1: "#2563EB", 32: "#DC2626"}

    for metric, ylabel, read_file, write_file in metric_specs:
        for rw, filename in (("randread", read_file), ("randwrite", write_file)):
            fig, ax = plt.subplots(figsize=(6.8, 4.8))
            x = list(range(len(ENGINE_ORDER)))
            width = 0.38
            for depth, offset in ((1, -width / 2), (32, width / 2)):
                values = [ENGINE_DEPTH_COMPARE[rw][depth][engine][metric] for engine in ENGINE_ORDER]
                ax.bar(
                    [idx + offset for idx in x],
                    values,
                    width=width,
                    label=depth_labels[depth],
                    color=colors[depth],
                )
            ax.set_title(f"{title_map[rw]} {ylabel} by Engine and iodepth")
            ax.set_ylabel(ylabel)
            ax.set_xticks(x)
            ax.set_xticklabels(ENGINE_ORDER)
            ax.legend()
            save_figure(fig, outdir, filename)


def main() -> int:
    if not SUMMARY_CSV.exists():
        print(f"Missing summary file: {SUMMARY_CSV}")
        print("Run scripts/extract_results.py first.")
        return 1

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = load_rows(SUMMARY_CSV)

    plot_baseline(rows, OUTPUT_DIR)
    plot_blocksize(rows, OUTPUT_DIR)
    plot_queue_heatmaps(rows, OUTPUT_DIR)
    plot_engine(rows, OUTPUT_DIR)
    plot_engine_depth_compare(OUTPUT_DIR)

    print(f"Charts written to {OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
