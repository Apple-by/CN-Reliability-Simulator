
"""Generate comparison graphs from the protocol evaluation CSV."""

import csv
from pathlib import Path

import matplotlib.pyplot as plt


RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
SUMMARY_FILE = RESULTS_DIR / "protocol_comparison_summary.csv"

SCENARIOS = ["Reliable", "Moderate", "Noisy"]
PROTOCOLS = ["Stop-and-Wait", "Go-Back-N", "Selective Repeat"]


def load_summary():
    with SUMMARY_FILE.open("r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def plot_metric(rows, column, ylabel, title, filename):
    """Create a grouped bar chart for one metric."""
    x_positions = list(range(len(SCENARIOS)))
    bar_width = 0.24

    fig, ax = plt.subplots(figsize=(9, 5))

    for index, protocol in enumerate(PROTOCOLS):
        values = []

        for scenario in SCENARIOS:
            match = next(
                row for row in rows
                if row["scenario"] == scenario
                and row["protocol"] == protocol
            )
            values.append(float(match[column]))

        offsets = [
            position + (index - 1) * bar_width
            for position in x_positions
        ]

        ax.bar(offsets, values, bar_width, label=protocol)

    ax.set_xlabel("Channel condition")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xticks(x_positions)
    ax.set_xticklabels(SCENARIOS)
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    fig.tight_layout()

    output_path = RESULTS_DIR / filename
    fig.savefig(output_path, dpi=200)
    plt.close(fig)

    print(f"Saved: {output_path}")


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    rows = load_summary()

    plot_metric(
        rows,
        "success_rate_percent",
        "Success rate (%)",
        "ARQ Protocol Success Rate",
        "success_rate.png",
    )

    plot_metric(
        rows,
        "avg_transmissions",
        "Average transmissions",
        "Average Transmissions by ARQ Protocol",
        "average_transmissions.png",
    )

    plot_metric(
        rows,
        "avg_delay_ms",
        "Average simulated delay (ms)",
        "Average Delay by ARQ Protocol",
        "average_delay.png",
    )


if __name__ == "__main__":
    main()
