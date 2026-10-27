
"""Run repeatable experiments comparing the three ARQ protocols."""

import csv
from pathlib import Path

from src.channel import ChannelConfig, UnreliableChannel
from src.metrics import result_to_row, summarize_results
from src.protocols import stop_and_wait, go_back_n, selective_repeat


OUTPUT_DIR = Path(__file__).resolve().parent.parent / "results"

PACKETS = [
    "1011", "1100", "0101", "1110",
    "0001", "1010", "0110", "1001",
]

WINDOW_SIZE = 4
MAX_RETRIES = 5
SEEDS = range(42, 62)

SCENARIOS = {
    "Reliable": {
        "bit_error_rate": 0.0,
        "packet_loss_rate": 0.0,
        "ack_loss_rate": 0.0,
    },
    "Moderate": {
        "bit_error_rate": 0.01,
        "packet_loss_rate": 0.05,
        "ack_loss_rate": 0.05,
    },
    "Noisy": {
        "bit_error_rate": 0.05,
        "packet_loss_rate": 0.10,
        "ack_loss_rate": 0.10,
    },
}

PROTOCOLS = [
    (stop_and_wait, {}),
    (go_back_n, {"window_size": WINDOW_SIZE}),
    (selective_repeat, {"window_size": WINDOW_SIZE}),
]


def write_csv(path, rows):
    """Write dictionaries to a CSV file."""
    if not rows:
        return

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    all_rows = []

    total_runs = len(SCENARIOS) * len(SEEDS) * len(PROTOCOLS)
    print(f"Running {total_runs} protocol experiments...")

    for scenario_name, probabilities in SCENARIOS.items():
        for seed in SEEDS:
            for protocol, extra_options in PROTOCOLS:
                config = ChannelConfig(
                    **probabilities,
                    min_delay_ms=1,
                    max_delay_ms=10,
                )
                channel = UnreliableChannel(config, seed=seed)

                result = protocol(
                    PACKETS,
                    channel=channel,
                    max_retries=MAX_RETRIES,
                    **extra_options,
                )

                all_rows.append(
                    result_to_row(
                        result=result,
                        input_packet_count=len(PACKETS),
                        scenario=scenario_name,
                        seed=seed,
                        bit_error_rate=probabilities["bit_error_rate"],
                        packet_loss_rate=probabilities["packet_loss_rate"],
                        ack_loss_rate=probabilities["ack_loss_rate"],
                        window_size=WINDOW_SIZE,
                    )
                )

    summary_rows = summarize_results(all_rows)

    raw_path = OUTPUT_DIR / "protocol_comparison_raw.csv"
    summary_path = OUTPUT_DIR / "protocol_comparison_summary.csv"

    write_csv(raw_path, all_rows)
    write_csv(summary_path, summary_rows)

    print("\n--- Summary Results ---")
    print(
        f"{'Scenario':<12} {'Protocol':<20} {'Success %':>10} "
        f"{'Avg sends':>11} {'Avg retries':>12} {'Avg delay':>11}"
    )
    print("-" * 80)

    for row in summary_rows:
        print(
            f"{row['scenario']:<12} "
            f"{row['protocol']:<20} "
            f"{row['success_rate_percent']:>9.2f}% "
            f"{row['avg_transmissions']:>11.2f} "
            f"{row['avg_retransmissions']:>12.2f} "
            f"{row['avg_delay_ms']:>10.2f} ms"
        )

    print(f"\nDetailed results saved to: {raw_path}")
    print(f"Summary results saved to:  {summary_path}")


if __name__ == "__main__":
    main()
