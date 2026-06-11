"""Matplotlib chart generators for Day 9 slide deck.

Each function writes a PNG to images/<name>.png and returns the file path.
All charts use the dark theme from theme.py.
"""
from __future__ import annotations
import os
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, Patch, FancyArrowPatch, Rectangle, Circle

import theme as T

T.apply_mpl_style(plt)

OUT_DIR = Path(__file__).parent / "images"
OUT_DIR.mkdir(exist_ok=True)


def _save(fig, name: str) -> str:
    path = OUT_DIR / f"{name}.png"
    fig.savefig(path, bbox_inches="tight", facecolor=T.MPL_BG)
    plt.close(fig)
    return str(path)


# --------------------------------------------------------------------------- #
# 1. Four Golden Signals quadrant (SRE book)
# --------------------------------------------------------------------------- #
def chart_four_golden_signals():
    fig, ax = plt.subplots(figsize=(10, 6.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6.8)
    ax.axis("off")

    quadrants = [
        (0.3, 3.1, "Latency",
         "Time to serve a request\n(success vs failure separated)",
         T.MPL_ACCENT),
        (5.1, 3.1, "Traffic",
         "Demand on the system\n(req/s, MB/s, sessions)",
         T.MPL_YELLOW),
        (0.3, 0.2, "Errors",
         "Rate of failed requests\n(explicit + implicit)",
         T.MPL_RED),
        (5.1, 0.2, "Saturation",
         '"Fullness" of the service\n(CPU, memory, queue depth)',
         T.MPL_PURPLE),
    ]
    for x, y, label, body, color in quadrants:
        box = FancyBboxPatch((x, y), 4.6, 2.7,
                             boxstyle="round,pad=0.08",
                             linewidth=2, edgecolor=color,
                             facecolor=T.MPL_PANEL)
        ax.add_patch(box)
        ax.text(x + 0.3, y + 2.25, label, fontsize=20,
                fontweight="bold", color=color)
        ax.text(x + 0.3, y + 1.3, body, fontsize=12,
                color=T.MPL_TEXT)

    ax.text(5, 6.55, "The Four Golden Signals",
            fontsize=16, fontweight="bold",
            color=T.MPL_TEXT, ha="center")
    ax.text(5, 6.15,
            "Google SRE Book — monitoring distributed user-facing systems",
            fontsize=10, color="#A0A8B4", ha="center", style="italic")
    return _save(fig, "four_golden_signals")


# --------------------------------------------------------------------------- #
# 2. RED vs USE methods
# --------------------------------------------------------------------------- #
def chart_red_vs_use():
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis("off")

    # RED panel
    red = FancyBboxPatch((0.1, 0.4), 4.7, 4,
                         boxstyle="round,pad=0.05",
                         linewidth=2, edgecolor=T.MPL_RED,
                         facecolor=T.MPL_PANEL)
    ax.add_patch(red)
    ax.text(2.45, 4, "RED", fontsize=24, fontweight="bold",
            color=T.MPL_RED, ha="center")
    ax.text(2.45, 3.6, "for request-driven services",
            fontsize=11, color="#A0A8B4", ha="center", style="italic")
    for i, (k, v) in enumerate([
        ("Rate", "requests per second"),
        ("Errors", "failed request count"),
        ("Duration", "latency distribution"),
    ]):
        ax.text(0.4, 2.9 - i * 0.85, k, fontsize=18,
                fontweight="bold", color=T.MPL_RED)
        ax.text(2.0, 2.95 - i * 0.85, v, fontsize=13,
                color=T.MPL_TEXT)

    # USE panel
    use = FancyBboxPatch((5.2, 0.4), 4.7, 4,
                         boxstyle="round,pad=0.05",
                         linewidth=2, edgecolor=T.MPL_ACCENT,
                         facecolor=T.MPL_PANEL)
    ax.add_patch(use)
    ax.text(7.55, 4, "USE", fontsize=24, fontweight="bold",
            color=T.MPL_ACCENT, ha="center")
    ax.text(7.55, 3.6, "for resources (CPU, disk, net)",
            fontsize=11, color="#A0A8B4", ha="center", style="italic")
    for i, (k, v) in enumerate([
        ("Utilization", "% time resource was busy"),
        ("Saturation", "queued work that can't be served"),
        ("Errors", "error events"),
    ]):
        ax.text(5.5, 2.9 - i * 0.85, k, fontsize=16,
                fontweight="bold", color=T.MPL_ACCENT)
        ax.text(7.5, 2.95 - i * 0.85, v, fontsize=13,
                color=T.MPL_TEXT)
    return _save(fig, "red_vs_use")


# --------------------------------------------------------------------------- #
# 3. Prometheus architecture
# --------------------------------------------------------------------------- #
def chart_prometheus_architecture():
    fig, ax = plt.subplots(figsize=(11, 5.2))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 5.2)
    ax.axis("off")

    def box(x, y, w, h, label, sub, color):
        b = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05",
                           linewidth=2, edgecolor=color,
                           facecolor=T.MPL_PANEL)
        ax.add_patch(b)
        ax.text(x + w / 2, y + h - 0.35, label, fontsize=12,
                fontweight="bold", color=color, ha="center")
        ax.text(x + w / 2, y + 0.25, sub, fontsize=9,
                color="#A0A8B4", ha="center")

    # Targets (left column)
    targets = [
        ("Kafka Broker", "JMX exporter :9404"),
        ("Postgres", "postgres_exporter"),
        ("App", "/metrics endpoint"),
        ("Kafka Lag", "kafka-lag-exporter"),
    ]
    for i, (a, b) in enumerate(targets):
        box(0.2, 3.6 - i * 1.05, 2.4, 0.85, a, b, T.MPL_YELLOW)

    # Prometheus
    box(3.5, 1.9, 2.6, 1.4, "Prometheus", "TSDB · scrape · rules",
        T.MPL_ACCENT)
    # arrows from targets to Prometheus
    for i in range(4):
        ay = 4.0 - i * 1.05
        arr = FancyArrowPatch((2.6, ay), (3.5, 2.6),
                              arrowstyle="-|>", mutation_scale=12,
                              color=T.MPL_ACCENT, alpha=0.7)
        ax.add_patch(arr)

    # Alertmanager
    box(7.0, 3.4, 2.4, 1.0, "Alertmanager",
        "routes · groups · dedups", T.MPL_RED)
    arr = FancyArrowPatch((6.1, 2.9), (7.0, 3.9),
                          arrowstyle="-|>", mutation_scale=15,
                          color=T.MPL_RED, linewidth=2)
    ax.add_patch(arr)
    ax.text(6.4, 3.4, "alerts", fontsize=10, color=T.MPL_RED,
            fontweight="bold")

    # Grafana
    box(7.0, 1.4, 2.4, 1.0, "Grafana",
        "dashboards · ad-hoc PromQL", T.MPL_BLUE)
    arr = FancyArrowPatch((6.1, 2.4), (7.0, 1.9),
                          arrowstyle="-|>", mutation_scale=15,
                          color=T.MPL_BLUE, linewidth=2)
    ax.add_patch(arr)
    ax.text(6.4, 1.9, "PromQL", fontsize=10, color=T.MPL_BLUE,
            fontweight="bold")

    # Slack / email
    box(7.0, 0.05, 2.4, 0.8, "Slack · Email · PagerDuty",
        "notification receivers", T.MPL_PURPLE)
    arr = FancyArrowPatch((8.2, 3.4), (8.2, 0.85),
                          arrowstyle="-|>", mutation_scale=12,
                          color=T.MPL_PURPLE, alpha=0.8)
    ax.add_patch(arr)

    ax.text(5.5, 5.0, "Prometheus pull-based monitoring stack",
            fontsize=14, fontweight="bold",
            color=T.MPL_TEXT, ha="center")
    return _save(fig, "prometheus_architecture")


# --------------------------------------------------------------------------- #
# 4. Prometheus metric types (Counter, Gauge, Histogram, Summary) sketch
# --------------------------------------------------------------------------- #
def chart_metric_types():
    fig, axes = plt.subplots(1, 4, figsize=(13, 3.3))
    titles = ["Counter", "Gauge", "Histogram", "Summary"]
    colors = [T.MPL_ACCENT, T.MPL_YELLOW, T.MPL_BLUE, T.MPL_PURPLE]

    # Counter — monotonically increasing
    x = np.linspace(0, 60, 60)
    y = np.cumsum(np.random.RandomState(1).poisson(3, size=60))
    axes[0].plot(x, y, color=colors[0], linewidth=2.5)
    axes[0].set_title(titles[0], color=colors[0])
    axes[0].set_ylabel("value")
    axes[0].set_xlabel("time (s)")

    # Gauge — up and down
    rng = np.random.RandomState(7)
    g = 50 + np.cumsum(rng.normal(0, 4, 60)).clip(-30, 60)
    axes[1].plot(x, g, color=colors[1], linewidth=2.5)
    axes[1].axhline(80, color=T.MPL_RED, linewidth=1,
                    linestyle="--", alpha=0.6, label="threshold")
    axes[1].set_title(titles[1], color=colors[1])
    axes[1].set_xlabel("time (s)")
    axes[1].legend(loc="upper left", fontsize=8)

    # Histogram — bucket distribution
    rng2 = np.random.RandomState(13)
    samples = np.concatenate([
        rng2.lognormal(2.0, 0.4, 800),
        rng2.lognormal(3.5, 0.3, 100),
    ])
    axes[2].hist(samples, bins=25, color=colors[2],
                 edgecolor=T.MPL_GRID)
    axes[2].axvline(np.percentile(samples, 50), color=T.MPL_YELLOW,
                    linewidth=1.5, label="p50")
    axes[2].axvline(np.percentile(samples, 95), color=T.MPL_RED,
                    linewidth=1.5, label="p95")
    axes[2].axvline(np.percentile(samples, 99), color=T.MPL_PURPLE,
                    linewidth=1.5, label="p99")
    axes[2].set_title(titles[2], color=colors[2])
    axes[2].set_xlabel("latency (ms)")
    axes[2].legend(loc="upper right", fontsize=8)

    # Summary — quantile lines over time
    t = np.arange(60)
    p50 = 50 + 5 * np.sin(t / 6)
    p95 = 120 + 15 * np.sin(t / 5 + 1)
    p99 = 220 + 40 * np.sin(t / 4 + 2)
    axes[3].plot(t, p50, color=T.MPL_GREEN, label="p50")
    axes[3].plot(t, p95, color=T.MPL_YELLOW, label="p95")
    axes[3].plot(t, p99, color=T.MPL_RED, label="p99")
    axes[3].set_title(titles[3], color=colors[3])
    axes[3].set_xlabel("time (s)")
    axes[3].set_ylabel("latency (ms)")
    axes[3].legend(loc="upper left", fontsize=8)

    fig.tight_layout()
    return _save(fig, "metric_types")


# --------------------------------------------------------------------------- #
# 5. Latency histogram with percentiles
# --------------------------------------------------------------------------- #
def chart_latency_histogram():
    rng = np.random.RandomState(42)
    samples = np.concatenate([
        rng.lognormal(2.5, 0.45, 5000),
        rng.lognormal(4.0, 0.35, 600),
    ])
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(samples, bins=60, color=T.MPL_ACCENT,
            edgecolor=T.MPL_GRID, alpha=0.9)
    for q, color, label in [
        (50, T.MPL_GREEN, "p50"),
        (95, T.MPL_YELLOW, "p95"),
        (99, T.MPL_RED, "p99"),
        (99.9, T.MPL_PURPLE, "p99.9"),
    ]:
        v = np.percentile(samples, q)
        ax.axvline(v, color=color, linewidth=2,
                   label=f"{label} = {v:.0f} ms")
    ax.set_xlabel("Request latency (ms)")
    ax.set_ylabel("Number of requests")
    ax.set_title("Why averages lie: a long-tail latency distribution")
    ax.legend(loc="upper right")
    return _save(fig, "latency_histogram")


# --------------------------------------------------------------------------- #
# 6. Consumer lag over time (rising → alert → recovery)
# --------------------------------------------------------------------------- #
def chart_consumer_lag():
    t = np.arange(0, 120)
    lag = np.zeros_like(t, dtype=float)
    for i in range(120):
        if i < 30:
            lag[i] = 50 + 20 * np.sin(i / 3)
        elif i < 65:
            lag[i] = 50 + (i - 30) * 180 + 50 * np.sin(i / 2)
        elif i < 80:
            lag[i] = lag[i - 1] - (i - 65) * 60
        else:
            lag[i] = max(80, 80 + 20 * np.sin(i / 3))
    lag = lag.clip(0, None)
    fig, ax = plt.subplots(figsize=(11, 4.8))
    ax.fill_between(t, 0, lag, color=T.MPL_ACCENT, alpha=0.25)
    ax.plot(t, lag, color=T.MPL_ACCENT, linewidth=2.5)
    ax.axhline(2000, color=T.MPL_RED, linestyle="--",
               linewidth=1.4, label="alert threshold (2 000 msgs)")
    ax.axvspan(45, 65, color=T.MPL_RED, alpha=0.18,
               label="alert firing")
    ax.axvspan(65, 80, color=T.MPL_GREEN, alpha=0.18,
               label="auto-scale recovery")
    ax.annotate("scale up consumers", xy=(65, 5500),
                xytext=(78, 6500), color=T.MPL_GREEN,
                fontsize=11, fontweight="bold",
                arrowprops=dict(arrowstyle="-|>", color=T.MPL_GREEN))
    ax.set_xlabel("time (minutes)")
    ax.set_ylabel("kafka_consumer_lag (messages)")
    ax.set_title("Consumer lag: detection · alert · recovery")
    ax.legend(loc="upper left")
    return _save(fig, "consumer_lag")


# --------------------------------------------------------------------------- #
# 7. Black-box vs White-box monitoring
# --------------------------------------------------------------------------- #
def chart_black_vs_white_box():
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis("off")

    bb = FancyBboxPatch((0.2, 0.4), 4.6, 4.2,
                        boxstyle="round,pad=0.05",
                        linewidth=2, edgecolor=T.MPL_RED,
                        facecolor=T.MPL_PANEL)
    ax.add_patch(bb)
    ax.text(2.5, 4.0, "Black-box", fontsize=22, fontweight="bold",
            color=T.MPL_RED, ha="center")
    ax.text(2.5, 3.55, "outside-in · symptom-oriented",
            fontsize=11, color="#A0A8B4", ha="center", style="italic")
    for i, line in enumerate([
        "• HTTP probe / synthetic check",
        "• 'Is the dashboard reachable?'",
        "• Detects user-visible problems",
        "• Cannot explain WHY",
    ]):
        ax.text(0.45, 2.85 - i * 0.55, line, fontsize=12,
                color=T.MPL_TEXT)

    wb = FancyBboxPatch((5.2, 0.4), 4.6, 4.2,
                        boxstyle="round,pad=0.05",
                        linewidth=2, edgecolor=T.MPL_ACCENT,
                        facecolor=T.MPL_PANEL)
    ax.add_patch(wb)
    ax.text(7.5, 4.0, "White-box", fontsize=22, fontweight="bold",
            color=T.MPL_ACCENT, ha="center")
    ax.text(7.5, 3.55, "inside-out · cause-oriented",
            fontsize=11, color="#A0A8B4", ha="center", style="italic")
    for i, line in enumerate([
        "• Logs · metrics · traces · JMX",
        "• Under-replicated partitions",
        "• Consumer lag · GC pauses",
        "• Explains imminent failures",
    ]):
        ax.text(5.45, 2.85 - i * 0.55, line, fontsize=12,
                color=T.MPL_TEXT)
    return _save(fig, "blackbox_vs_whitebox")


# --------------------------------------------------------------------------- #
# 8. Partitions: producer → 3 partitions → 3 consumers
# --------------------------------------------------------------------------- #
def chart_partitions_distribution():
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 5)
    ax.axis("off")

    # Producer
    box = FancyBboxPatch((0.2, 1.9), 1.8, 1.2,
                         boxstyle="round,pad=0.05",
                         linewidth=2, edgecolor=T.MPL_YELLOW,
                         facecolor=T.MPL_PANEL)
    ax.add_patch(box)
    ax.text(1.1, 2.7, "Producer", fontsize=14,
            fontweight="bold", color=T.MPL_YELLOW, ha="center")
    ax.text(1.1, 2.3, "key → hash → partition", fontsize=9,
            color="#A0A8B4", ha="center")

    # Topic partitions (3)
    for i, (label, color) in enumerate([
        ("Partition 0", T.MPL_ACCENT),
        ("Partition 1", T.MPL_BLUE),
        ("Partition 2", T.MPL_PURPLE),
    ]):
        py = 3.6 - i * 1.4
        box = FancyBboxPatch((3.6, py - 0.4), 3.2, 0.9,
                             boxstyle="round,pad=0.05",
                             linewidth=2, edgecolor=color,
                             facecolor=T.MPL_PANEL)
        ax.add_patch(box)
        ax.text(5.2, py, label, fontsize=13, fontweight="bold",
                color=color, ha="center")
        # arrow from producer
        arr = FancyArrowPatch((2.0, 2.5), (3.6, py),
                              arrowstyle="-|>", mutation_scale=12,
                              color=color, alpha=0.8)
        ax.add_patch(arr)

    # Consumer group (3 consumers)
    for i, (label, color) in enumerate([
        ("Consumer A", T.MPL_ACCENT),
        ("Consumer B", T.MPL_BLUE),
        ("Consumer C", T.MPL_PURPLE),
    ]):
        cy = 3.6 - i * 1.4
        box = FancyBboxPatch((7.8, cy - 0.4), 2.8, 0.9,
                             boxstyle="round,pad=0.05",
                             linewidth=2, edgecolor=color,
                             facecolor=T.MPL_PANEL)
        ax.add_patch(box)
        ax.text(9.2, cy, label, fontsize=13, fontweight="bold",
                color=color, ha="center")
        arr = FancyArrowPatch((6.8, cy), (7.8, cy),
                              arrowstyle="-|>", mutation_scale=12,
                              color=color)
        ax.add_patch(arr)

    ax.text(5.5, 4.6,
            "One partition → at most one consumer in a group",
            fontsize=14, fontweight="bold",
            color=T.MPL_TEXT, ha="center")
    ax.text(5.5, 0.3,
            "More consumers than partitions = idle consumers",
            fontsize=11, color=T.MPL_YELLOW,
            ha="center", style="italic")
    return _save(fig, "partitions_distribution")


# --------------------------------------------------------------------------- #
# 9. ISR shrink/expand timeline
# --------------------------------------------------------------------------- #
def chart_isr_timeline():
    fig, ax = plt.subplots(figsize=(11, 4.5))
    t = np.arange(0, 100)
    rng = np.random.RandomState(3)
    # simulate broker 3 falling behind around t=40, recovering at t=70
    leader_offset = np.cumsum(rng.poisson(8, size=100))
    b1 = leader_offset - rng.randint(0, 3, size=100)
    b2 = leader_offset - rng.randint(0, 3, size=100)
    b3 = leader_offset.copy()
    b3[40:70] = b3[40] + np.linspace(0, 10, 30)  # frozen / lagging

    ax.plot(t, leader_offset, color=T.MPL_YELLOW, linewidth=2.5,
            label="Leader (broker 1)")
    ax.plot(t, b1, color=T.MPL_ACCENT, linewidth=2,
            label="Follower (broker 2)")
    ax.plot(t, b3, color=T.MPL_RED, linewidth=2,
            label="Follower (broker 3)")
    ax.axvspan(40, 70, color=T.MPL_RED, alpha=0.12)
    ax.annotate("ISR shrinks\n(b3 removed)", xy=(45, 380),
                xytext=(20, 600), color=T.MPL_RED,
                fontweight="bold",
                arrowprops=dict(arrowstyle="-|>", color=T.MPL_RED))
    ax.annotate("ISR expands\n(b3 back)", xy=(72, b3[72]),
                xytext=(80, b3[72] - 200), color=T.MPL_GREEN,
                fontweight="bold",
                arrowprops=dict(arrowstyle="-|>", color=T.MPL_GREEN))
    ax.set_xlabel("time (s)")
    ax.set_ylabel("log-end offset")
    ax.set_title("In-Sync Replicas (ISR): shrink → recover")
    ax.legend(loc="upper left")
    return _save(fig, "isr_timeline")


# --------------------------------------------------------------------------- #
# 10. DQ dimensions bar chart
# --------------------------------------------------------------------------- #
def chart_dq_dimensions():
    dims = ["Accuracy", "Completeness", "Consistency",
            "Timeliness", "Uniqueness", "Validity"]
    scores = [98.4, 99.7, 97.1, 96.5, 99.9, 98.8]
    fig, ax = plt.subplots(figsize=(11, 4.8))
    bars = ax.bar(dims, scores,
                  color=[T.MPL_ACCENT, T.MPL_GREEN, T.MPL_YELLOW,
                         T.MPL_BLUE, T.MPL_PURPLE, T.MPL_RED])
    for bar, score in zip(bars, scores):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.05,
                f"{score:.1f}%", ha="center", color=T.MPL_TEXT,
                fontweight="bold")
    ax.set_ylim(90, 102)
    ax.set_ylabel("Quality score (%)")
    ax.set_title("Six Data-Quality Dimensions — sample run")
    return _save(fig, "dq_dimensions")


# --------------------------------------------------------------------------- #
# 11. DLQ flow (producer → topic → consumer → DLQ branch)
# --------------------------------------------------------------------------- #
def chart_dlq_flow():
    fig, ax = plt.subplots(figsize=(11, 4.6))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 4.5)
    ax.axis("off")

    def box(x, y, w, h, label, sub, color):
        b = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05",
                           linewidth=2, edgecolor=color,
                           facecolor=T.MPL_PANEL)
        ax.add_patch(b)
        ax.text(x + w / 2, y + h - 0.3, label, fontsize=13,
                fontweight="bold", color=color, ha="center")
        if sub:
            ax.text(x + w / 2, y + 0.25, sub, fontsize=9,
                    color="#A0A8B4", ha="center")

    box(0.2, 1.6, 1.9, 1.3, "Producer", "send()", T.MPL_YELLOW)
    box(2.6, 1.6, 2.0, 1.3, "trips", "topic", T.MPL_ACCENT)
    box(5.1, 1.6, 2.4, 1.3, "Consumer", "process()", T.MPL_BLUE)
    box(8.0, 2.5, 2.6, 1.0, "trips-warehouse", "happy path",
        T.MPL_GREEN)
    box(8.0, 0.6, 2.6, 1.0, "trips-dlq",
        "poison · schema · DQ failures", T.MPL_RED)

    for (a, b) in [((2.1, 2.25), (2.6, 2.25)),
                   ((4.6, 2.25), (5.1, 2.25))]:
        arr = FancyArrowPatch(a, b, arrowstyle="-|>",
                              mutation_scale=15,
                              color=T.MPL_TEXT)
        ax.add_patch(arr)
    arr = FancyArrowPatch((7.5, 2.5), (8.0, 3.0),
                          arrowstyle="-|>", mutation_scale=15,
                          color=T.MPL_GREEN, linewidth=2)
    ax.add_patch(arr)
    arr = FancyArrowPatch((7.5, 1.9), (8.0, 1.1),
                          arrowstyle="-|>", mutation_scale=15,
                          color=T.MPL_RED, linewidth=2)
    ax.add_patch(arr)
    ax.text(7.6, 1.15, "on error", fontsize=10,
            color=T.MPL_RED, fontweight="bold")
    ax.text(7.6, 2.95, "on success", fontsize=10,
            color=T.MPL_GREEN, fontweight="bold")
    return _save(fig, "dlq_flow")


# --------------------------------------------------------------------------- #
# 12. Throttling delay curve
# --------------------------------------------------------------------------- #
def chart_throttling_curve():
    throttle_mb = np.linspace(5, 100, 50)  # MB/s
    response_max_bytes_mb = 10               # default 10 MB
    n_brokers = 3
    delay_s = response_max_bytes_mb * n_brokers / throttle_mb
    fig, ax = plt.subplots(figsize=(10, 4.7))
    ax.plot(throttle_mb, delay_s, color=T.MPL_ACCENT, linewidth=2.5)
    ax.axhline(1, color=T.MPL_RED, linestyle="--", linewidth=1.2,
               label="1 s ceiling (Confluent recommendation)")
    ax.fill_between(throttle_mb, delay_s, 1,
                    where=(delay_s > 1), color=T.MPL_RED, alpha=0.15)
    ax.set_xlabel("Replication throttle (MB/s)")
    ax.set_ylabel("Worst-case response delay (s)")
    ax.set_title("Throttle vs delay: 3 brokers · "
                 "replica.fetch.response.max.bytes = 10 MB")
    ax.legend(loc="upper right")
    return _save(fig, "throttling_curve")


# --------------------------------------------------------------------------- #
# 13. Compression ratio comparison
# --------------------------------------------------------------------------- #
def chart_compression_compare():
    codecs = ["none", "gzip", "snappy", "lz4", "zstd"]
    ratio = [1.0, 4.5, 2.6, 2.4, 4.1]
    cpu = [0, 70, 18, 15, 35]
    fig, ax = plt.subplots(figsize=(11, 4.7))
    x = np.arange(len(codecs))
    w = 0.38
    b1 = ax.bar(x - w/2, ratio, w, color=T.MPL_ACCENT,
                label="compression ratio (×)")
    ax2 = ax.twinx()
    b2 = ax2.bar(x + w/2, cpu, w, color=T.MPL_YELLOW,
                 label="CPU overhead (%)")
    ax.set_xticks(x)
    ax.set_xticklabels(codecs)
    ax.set_ylabel("Compression ratio", color=T.MPL_ACCENT)
    ax2.set_ylabel("CPU overhead (%)", color=T.MPL_YELLOW)
    ax2.grid(False)
    ax.set_title("Codec tradeoffs: ratio vs CPU "
                 "(illustrative — workload dependent)")
    handles = [b1[0], b2[0]]
    ax.legend(handles, [h.get_label() for h in handles],
              loc="upper left")
    return _save(fig, "compression_compare")


# --------------------------------------------------------------------------- #
# 14. Scaling axes diagram
# --------------------------------------------------------------------------- #
def chart_scaling_axes():
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis("off")
    axes_data = [
        ("Vertical", "bigger brokers — RAM, CPU, NVMe",
         T.MPL_ACCENT),
        ("Horizontal", "more brokers · more partitions · "
                       "more consumers in the group",
         T.MPL_YELLOW),
        ("Time", "batching · linger.ms · compression · "
                 "back-pressure trade time for throughput",
         T.MPL_PURPLE),
    ]
    for i, (k, v, c) in enumerate(axes_data):
        y = 3.6 - i * 1.4
        box = FancyBboxPatch((0.4, y), 9.2, 1.1,
                             boxstyle="round,pad=0.05",
                             linewidth=2, edgecolor=c,
                             facecolor=T.MPL_PANEL)
        ax.add_patch(box)
        ax.text(0.7, y + 0.7, k, fontsize=20, fontweight="bold",
                color=c)
        ax.text(2.8, y + 0.7, v, fontsize=14, color=T.MPL_TEXT)
    ax.text(5, 4.7, "Three axes of scaling a Kafka pipeline",
            fontsize=14, fontweight="bold",
            color=T.MPL_TEXT, ha="center")
    return _save(fig, "scaling_axes")


# --------------------------------------------------------------------------- #
# 15. Retry with backoff illustration
# --------------------------------------------------------------------------- #
def chart_retry_backoff():
    attempts = np.arange(1, 8)
    constant = np.full_like(attempts, 1.0, dtype=float)
    linear = attempts * 0.5
    exp = 0.5 * 2 ** (attempts - 1)
    expj = exp + np.random.RandomState(5).uniform(-0.2, 0.2, size=7)

    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.plot(attempts, constant, "-o", color=T.MPL_BLUE,
            label="constant (1 s)")
    ax.plot(attempts, linear, "-o", color=T.MPL_GREEN,
            label="linear (0.5 × n)")
    ax.plot(attempts, exp, "-o", color=T.MPL_YELLOW,
            label="exponential (0.5 × 2ⁿ⁻¹)")
    ax.plot(attempts, expj, "-o", color=T.MPL_RED,
            label="exponential + jitter")
    ax.set_xlabel("Retry attempt")
    ax.set_ylabel("Wait time (s)")
    ax.set_yscale("log")
    ax.set_title("Retry backoff strategies")
    ax.legend(loc="upper left")
    return _save(fig, "retry_backoff")


# --------------------------------------------------------------------------- #
# 16. Schema evolution compatibility modes
# --------------------------------------------------------------------------- #
def chart_schema_compat():
    fig, ax = plt.subplots(figsize=(11, 4.8))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 5)
    ax.axis("off")
    modes = [
        ("BACKWARD",
         "new consumer can read old data",
         "delete optional fields · add optional",
         T.MPL_ACCENT),
        ("FORWARD",
         "old consumer can read new data",
         "add optional · delete optional",
         T.MPL_YELLOW),
        ("FULL",
         "both directions",
         "add/delete optional only",
         T.MPL_GREEN),
        ("NONE",
         "anything goes (dangerous)",
         "use only for greenfield topics",
         T.MPL_RED),
    ]
    for i, (k, v, ex, c) in enumerate(modes):
        x = 0.3 + (i % 2) * 5.4
        y = 2.7 - (i // 2) * 2.3
        box = FancyBboxPatch((x, y), 5.1, 2.0,
                             boxstyle="round,pad=0.05",
                             linewidth=2, edgecolor=c,
                             facecolor=T.MPL_PANEL)
        ax.add_patch(box)
        ax.text(x + 0.3, y + 1.55, k, fontsize=18, fontweight="bold",
                color=c)
        ax.text(x + 0.3, y + 1.1, v, fontsize=12,
                color=T.MPL_TEXT)
        ax.text(x + 0.3, y + 0.5, ex, fontsize=10,
                color="#A0A8B4", style="italic")
    ax.text(5.5, 4.8, "Schema Registry compatibility modes",
            fontsize=14, fontweight="bold",
            color=T.MPL_TEXT, ha="center")
    return _save(fig, "schema_compat")


# --------------------------------------------------------------------------- #
# 17. Symptoms vs causes
# --------------------------------------------------------------------------- #
def chart_symptoms_vs_causes():
    fig, ax = plt.subplots(figsize=(11, 4.8))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 5)
    ax.axis("off")
    # Symptom
    box = FancyBboxPatch((0.3, 0.6), 4.6, 3.8,
                         boxstyle="round,pad=0.05",
                         linewidth=2, edgecolor=T.MPL_RED,
                         facecolor=T.MPL_PANEL)
    ax.add_patch(box)
    ax.text(2.6, 4.0, "Symptom", fontsize=20, fontweight="bold",
            color=T.MPL_RED, ha="center")
    ax.text(2.6, 3.55, "what's broken (user impact)",
            fontsize=11, color="#A0A8B4", ha="center", style="italic")
    for i, line in enumerate([
        "• 500s on /api/trips",
        "• Dashboard 30 s slower",
        "• Bad data in warehouse",
        "• Pages → alerts → PagerDuty",
    ]):
        ax.text(0.55, 3.0 - i * 0.5, line, fontsize=12,
                color=T.MPL_TEXT)

    # Cause
    box = FancyBboxPatch((5.6, 0.6), 4.8, 3.8,
                         boxstyle="round,pad=0.05",
                         linewidth=2, edgecolor=T.MPL_ACCENT,
                         facecolor=T.MPL_PANEL)
    ax.add_patch(box)
    ax.text(8.0, 4.0, "Cause", fontsize=20, fontweight="bold",
            color=T.MPL_ACCENT, ha="center")
    ax.text(8.0, 3.55, "why it broke (diagnostic)",
            fontsize=11, color="#A0A8B4", ha="center", style="italic")
    for i, line in enumerate([
        "• DB replica lag (jrm-3 down)",
        "• ISR shrunk on partition 11",
        "• Schema mismatch in producer",
        "• Disk 96% on broker-2",
    ]):
        ax.text(5.85, 3.0 - i * 0.5, line, fontsize=12,
                color=T.MPL_TEXT)

    # arrow
    arr = FancyArrowPatch((4.9, 2.5), (5.6, 2.5),
                          arrowstyle="-|>", mutation_scale=20,
                          color=T.MPL_YELLOW, linewidth=2)
    ax.add_patch(arr)
    ax.text(5.25, 2.7, "drill\ndown",
            fontsize=10, color=T.MPL_YELLOW,
            ha="center", fontweight="bold")
    return _save(fig, "symptoms_vs_causes")


# --------------------------------------------------------------------------- #
# 18. Pipeline architecture (Lab reference)
# --------------------------------------------------------------------------- #
def chart_pipeline_arch():
    fig, ax = plt.subplots(figsize=(12, 5.4))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 5.4)
    ax.axis("off")

    def box(x, y, w, h, label, sub, color):
        b = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05",
                           linewidth=2, edgecolor=color,
                           facecolor=T.MPL_PANEL)
        ax.add_patch(b)
        ax.text(x + w / 2, y + h - 0.3, label, fontsize=11,
                fontweight="bold", color=color, ha="center")
        ax.text(x + w / 2, y + 0.2, sub, fontsize=8,
                color="#A0A8B4", ha="center")

    # Sources
    box(0.2, 4.0, 1.9, 1.1, "Taxi simulator", "100 trips/s",
        T.MPL_YELLOW)
    box(0.2, 2.6, 1.9, 1.1, "Postgres CDC", "Debezium connector",
        T.MPL_YELLOW)
    box(0.2, 1.2, 1.9, 1.1, "Driver enricher", "lookup join",
        T.MPL_YELLOW)

    # Kafka cluster
    box(2.6, 1.3, 3.0, 3.8, "Kafka (3 brokers, KRaft)",
        "trips · drivers · surge · DLQ", T.MPL_ACCENT)

    # Processors
    box(6.1, 4.0, 2.0, 1.1, "Surge detector",
        "windowed avg", T.MPL_BLUE)
    box(6.1, 2.6, 2.0, 1.1, "Quality validator",
        "8 expectations", T.MPL_PURPLE)
    box(6.1, 1.2, 2.0, 1.1, "Consumer",
        "Postgres warehouse", T.MPL_BLUE)

    # Sinks / obs
    box(8.6, 4.0, 1.9, 1.1, "Grafana", "dashboards",
        T.MPL_GREEN)
    box(8.6, 2.6, 1.9, 1.1, "Prometheus", "TSDB · alerts",
        T.MPL_GREEN)
    box(8.6, 1.2, 1.9, 1.1, "Loki", "logs",
        T.MPL_GREEN)
    box(10.8, 2.6, 1.0, 1.1, "Alert\nmgr", "slack",
        T.MPL_RED)

    ax.text(6.0, 5.2, "Day 9 reference pipeline",
            fontsize=14, fontweight="bold",
            color=T.MPL_TEXT, ha="center")
    return _save(fig, "pipeline_arch")


# --------------------------------------------------------------------------- #
# 19. Idempotent producer guarantee
# --------------------------------------------------------------------------- #
def chart_idempotent_producer():
    fig, ax = plt.subplots(figsize=(11, 4.8))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 5)
    ax.axis("off")
    # left
    box = FancyBboxPatch((0.3, 0.4), 4.7, 4.2,
                         boxstyle="round,pad=0.05",
                         linewidth=2, edgecolor=T.MPL_RED,
                         facecolor=T.MPL_PANEL)
    ax.add_patch(box)
    ax.text(2.65, 4.1, "Without idempotence",
            fontsize=16, fontweight="bold",
            color=T.MPL_RED, ha="center")
    for i, line in enumerate([
        "1. Producer sends batch B1",
        "2. Broker writes B1, ACK lost",
        "3. Producer retries B1",
        "4. Broker writes B1 AGAIN",
        "→ duplicates in topic",
    ]):
        ax.text(0.5, 3.5 - i * 0.55, line, fontsize=12,
                color=T.MPL_TEXT)

    # right
    box = FancyBboxPatch((5.7, 0.4), 4.9, 4.2,
                         boxstyle="round,pad=0.05",
                         linewidth=2, edgecolor=T.MPL_GREEN,
                         facecolor=T.MPL_PANEL)
    ax.add_patch(box)
    ax.text(8.15, 4.1, "With idempotence",
            fontsize=16, fontweight="bold",
            color=T.MPL_GREEN, ha="center")
    for i, line in enumerate([
        "1. Producer sends B1 (PID + seq=5)",
        "2. Broker writes B1, ACK lost",
        "3. Producer retries (PID + seq=5)",
        "4. Broker sees seq=5 already done",
        "→ exactly once on the partition",
    ]):
        ax.text(5.9, 3.5 - i * 0.55, line, fontsize=12,
                color=T.MPL_TEXT)
    return _save(fig, "idempotent_producer")


# --------------------------------------------------------------------------- #
# 20. JMX exporter mechanism
# --------------------------------------------------------------------------- #
def chart_jmx_exporter():
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 4.5)
    ax.axis("off")

    def box(x, y, w, h, label, sub, color):
        b = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05",
                           linewidth=2, edgecolor=color,
                           facecolor=T.MPL_PANEL)
        ax.add_patch(b)
        ax.text(x + w / 2, y + h - 0.3, label, fontsize=12,
                fontweight="bold", color=color, ha="center")
        ax.text(x + w / 2, y + 0.2, sub, fontsize=9,
                color="#A0A8B4", ha="center")

    # broker
    big = FancyBboxPatch((0.2, 0.4), 5.0, 3.7,
                         boxstyle="round,pad=0.05",
                         linewidth=2, edgecolor=T.MPL_ACCENT,
                         facecolor="#161B26")
    ax.add_patch(big)
    ax.text(2.7, 3.85, "Kafka broker JVM",
            fontsize=13, fontweight="bold",
            color=T.MPL_ACCENT, ha="center")
    box(0.45, 2.4, 4.4, 1.0, "MBeans",
        "kafka.server:type=BrokerTopicMetrics …",
        T.MPL_YELLOW)
    box(0.45, 0.8, 4.4, 1.3, "jmx_prometheus_javaagent",
        "in-process · YAML rules · :9404/metrics",
        T.MPL_PURPLE)
    arr = FancyArrowPatch((2.65, 2.4), (2.65, 2.1),
                          arrowstyle="-|>", mutation_scale=15,
                          color=T.MPL_TEXT)
    ax.add_patch(arr)

    box(7.0, 1.8, 2.8, 1.2, "Prometheus",
        "scrape :9404 / 15 s", T.MPL_ACCENT)
    arr = FancyArrowPatch((5.2, 1.5), (7.0, 2.4),
                          arrowstyle="-|>", mutation_scale=15,
                          color=T.MPL_ACCENT, linewidth=2)
    ax.add_patch(arr)
    ax.text(6.0, 2.05, "HTTP pull", fontsize=10,
            color=T.MPL_ACCENT, fontweight="bold",
            rotation=20)

    return _save(fig, "jmx_exporter")


# --------------------------------------------------------------------------- #
# 21. PromQL anatomy — visual breakdown of one query
# --------------------------------------------------------------------------- #
def chart_promql_anatomy():
    """Big annotated diagram explaining what PromQL is in one picture."""
    fig, ax = plt.subplots(figsize=(12, 5.8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 5.8)
    ax.axis("off")

    # title + subtitle
    ax.text(6, 5.45,
            "PromQL = Prometheus Query Language "
            "(SQL-for-time-series-metrics)",
            fontsize=15, fontweight="bold",
            color=T.MPL_TEXT, ha="center")
    ax.text(6, 5.05,
            "Read every query in three pieces: WHAT · FILTERED HOW · DONE WITH IT",
            fontsize=11, color="#6E7681", ha="center", style="italic")

    # Four colour-coded boxes laid out left-to-right with FIXED widths
    # so nothing can overlap. Each box has the syntax piece on top and
    # the plain-English label on the bottom.
    pieces = [
        ("rate(  )",                  "function",
         "rate of change",            T.MPL_PURPLE),
        ("http_requests_total",       "metric name",
         "the COUNTER",               T.MPL_ACCENT),
        ("{status=\"500\"}",          "label filter",
         "only 500s",                 T.MPL_YELLOW),
        ("[5m]",                      "time window",
         "over last 5 min",           T.MPL_BLUE),
    ]

    n = len(pieces)
    box_w = 2.7
    gap = 0.15
    total_w = n * box_w + (n - 1) * gap
    x0 = (12 - total_w) / 2.0
    y_box = 3.05
    box_h = 1.4

    for i, (syntax, role, plain, color) in enumerate(pieces):
        x = x0 + i * (box_w + gap)
        # box
        box = FancyBboxPatch((x, y_box), box_w, box_h,
                             boxstyle="round,pad=0.05",
                             linewidth=2, edgecolor=color,
                             facecolor=T.MPL_PANEL)
        ax.add_patch(box)
        # syntax (monospace, big) — auto-scale font to fit width
        size = 18 if len(syntax) <= 12 else 14 if len(syntax) <= 18 else 12
        ax.text(x + box_w / 2, y_box + box_h - 0.55,
                syntax, fontsize=size, fontweight="bold",
                color=color, ha="center", family="monospace")
        # role label
        ax.text(x + box_w / 2, y_box + 0.55,
                role, fontsize=10, fontweight="bold",
                color=color, ha="center")
        # plain English
        ax.text(x + box_w / 2, y_box + 0.22,
                plain, fontsize=10, color=T.MPL_TEXT, ha="center")

        # connector arrow down to the "READS AS" banner
        arrow = FancyArrowPatch(
            (x + box_w / 2, y_box - 0.05),
            (x + box_w / 2, 2.05),
            arrowstyle="-|>", mutation_scale=10,
            color=color, alpha=0.6, linewidth=1.4)
        ax.add_patch(arrow)

    # "reads as" plain English banner
    banner = FancyBboxPatch((0.4, 0.4), 11.2, 1.45,
                            boxstyle="round,pad=0.08",
                            linewidth=2, edgecolor=T.MPL_GREEN,
                            facecolor=T.MPL_PANEL)
    ax.add_patch(banner)
    ax.text(0.75, 1.55,
            "READS AS:",
            fontsize=12, fontweight="bold",
            color=T.MPL_GREEN)
    ax.text(0.75, 0.85,
            "\"For HTTP requests that returned status 500, "
            "what's the rate-per-second over the last 5 minutes?\"",
            fontsize=13, color=T.MPL_TEXT, style="italic")

    return _save(fig, "promql_anatomy")


# --------------------------------------------------------------------------- #
# 22. Prometheus architecture — clean redraw of the official diagram
# --------------------------------------------------------------------------- #
def chart_prometheus_official():
    """Custom drawing of the Prometheus architecture (matches prometheus.io)."""
    fig, ax = plt.subplots(figsize=(12, 6.2))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6.4)
    ax.axis("off")

    def lbl(x, y, w, h, title, sub, edge, fill=None):
        f = fill if fill else T.MPL_PANEL
        b = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05",
                           linewidth=1.8, edgecolor=edge, facecolor=f)
        ax.add_patch(b)
        ax.text(x + w / 2, y + h / 2 + 0.12, title,
                fontsize=11, fontweight="bold",
                color=T.MPL_TEXT, ha="center")
        if sub:
            ax.text(x + w / 2, y + h / 2 - 0.22, sub,
                    fontsize=8.5, color="#6E7681", ha="center",
                    style="italic")

    def arrow(p1, p2, color=T.MPL_TEXT, lw=1.4, style="-|>"):
        a = FancyArrowPatch(p1, p2, arrowstyle=style,
                            mutation_scale=11, color=color, linewidth=lw)
        ax.add_patch(a)

    # ── LEFT: targets (jobs Prometheus scrapes) ──
    lbl(0.3, 4.7, 2.4, 0.8,
        "Short-lived jobs", "push to gateway", T.MPL_PURPLE)
    lbl(0.3, 3.5, 2.4, 0.8,
        "Pushgateway", "metrics buffer", T.MPL_YELLOW)
    lbl(0.3, 2.1, 2.4, 0.8,
        "Service discovery", "Kubernetes · DNS · file_sd", T.MPL_BLUE)
    lbl(0.3, 0.7, 2.4, 0.8,
        "Exporters", "node · JMX · postgres · …",
        T.MPL_ACCENT)

    # ── CENTER: Prometheus server cluster (orange box) ──
    server_x, server_y = 3.6, 1.7
    server_w, server_h = 5.6, 3.4
    big = FancyBboxPatch(
        (server_x, server_y), server_w, server_h,
        boxstyle="round,pad=0.08",
        linewidth=2.2, edgecolor=T.MPL_YELLOW,
        facecolor="#FFF8EC")
    ax.add_patch(big)
    ax.text(server_x + server_w / 2, server_y + server_h - 0.25,
            "Prometheus Server",
            fontsize=13, fontweight="bold",
            color=T.MPL_YELLOW, ha="center")

    # inner components
    lbl(server_x + 0.3, server_y + 1.7, 1.55, 0.9,
        "Retrieval", "scrape loop", T.MPL_YELLOW)
    lbl(server_x + 2.05, server_y + 1.7, 1.55, 0.9,
        "TSDB", "local time-series DB", T.MPL_YELLOW)
    lbl(server_x + 3.8, server_y + 1.7, 1.55, 0.9,
        "HTTP API", "/api/v1/query", T.MPL_YELLOW)
    lbl(server_x + 1.2, server_y + 0.4, 3.2, 0.9,
        "Rule engine", "recording rules · alerting rules",
        T.MPL_RED)

    # scrape arrows: targets → Retrieval
    retrieval_anchor = (server_x + 0.3 + 0.775, server_y + 1.7 + 0.45)
    for (sy) in [5.1, 3.9, 2.5, 1.1]:
        arrow((2.7, sy), retrieval_anchor, color=T.MPL_YELLOW, lw=1.3)

    # ── RIGHT-TOP: Alertmanager ──
    lbl(9.6, 4.6, 2.2, 0.95,
        "Alertmanager", "dedupe · route · notify",
        T.MPL_RED)
    lbl(9.6, 5.7, 0.95, 0.55, "Email", "", T.MPL_RED)
    lbl(10.7, 5.7, 1.05, 0.55, "PagerDuty", "", T.MPL_RED)
    arrow((10.1, 5.55), (10.1, 5.65), color=T.MPL_RED)
    arrow((11.2, 5.55), (11.2, 5.65), color=T.MPL_RED)
    # rules → alertmanager
    arrow((server_x + 4.4, server_y + 0.85), (9.6, 5.07),
          color=T.MPL_RED, lw=1.6)
    ax.text(9.0, 4.35, "fired alerts",
            fontsize=8.5, color=T.MPL_RED, style="italic")

    # ── RIGHT-BOTTOM: query consumers ──
    lbl(9.6, 2.8, 2.2, 0.95,
        "Grafana", "dashboards", T.MPL_ACCENT)
    lbl(9.6, 1.5, 2.2, 0.95,
        "PromQL Web UI", "ad-hoc queries", T.MPL_ACCENT)
    arrow((server_x + server_w, server_y + 1.95), (9.6, 3.25),
          color=T.MPL_ACCENT, lw=1.6)
    arrow((server_x + server_w, server_y + 1.95), (9.6, 1.95),
          color=T.MPL_ACCENT, lw=1.6)

    # ── caption / title ──
    ax.text(6, 6.15, "Prometheus — official architecture",
            fontsize=14, fontweight="bold",
            color=T.MPL_TEXT, ha="center")
    ax.text(6, 5.85,
            "Prometheus PULLS — it reaches out to /metrics endpoints on a schedule.",
            fontsize=10.5, color="#6E7681", ha="center", style="italic")

    return _save(fig, "prometheus_official")


# --------------------------------------------------------------------------- #
# Generate all
# --------------------------------------------------------------------------- #
def generate_all() -> dict:
    return {
        "four_golden_signals": chart_four_golden_signals(),
        "red_vs_use": chart_red_vs_use(),
        "prometheus_architecture": chart_prometheus_architecture(),
        "metric_types": chart_metric_types(),
        "latency_histogram": chart_latency_histogram(),
        "consumer_lag": chart_consumer_lag(),
        "blackbox_vs_whitebox": chart_black_vs_white_box(),
        "partitions_distribution": chart_partitions_distribution(),
        "isr_timeline": chart_isr_timeline(),
        "dq_dimensions": chart_dq_dimensions(),
        "dlq_flow": chart_dlq_flow(),
        "throttling_curve": chart_throttling_curve(),
        "compression_compare": chart_compression_compare(),
        "scaling_axes": chart_scaling_axes(),
        "retry_backoff": chart_retry_backoff(),
        "schema_compat": chart_schema_compat(),
        "symptoms_vs_causes": chart_symptoms_vs_causes(),
        "pipeline_arch": chart_pipeline_arch(),
        "idempotent_producer": chart_idempotent_producer(),
        "jmx_exporter": chart_jmx_exporter(),
        "promql_anatomy": chart_promql_anatomy(),
        "prometheus_official": chart_prometheus_official(),
    }


if __name__ == "__main__":
    paths = generate_all()
    for k, v in paths.items():
        print(f"{k}: {v}")
