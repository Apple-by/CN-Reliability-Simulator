
"""Convert protocol results into CSV-ready metrics and summaries."""

from collections import defaultdict


def result_to_row(
    result,
    scenario,
    seed,
    bit_error_rate,
    packet_loss_rate,
    ack_loss_rate,
    window_size,
    input_packet_count,
):
    """Convert one protocol run into a dictionary."""
    return {
        "scenario": scenario,
        "seed": seed,
        "protocol": result.protocol,
        "success": int(result.success),
        "packets_in_input": input_packet_count,
        "transmissions": result.transmissions,
        "retransmissions": result.retransmissions,
        "acks_sent": result.acks_sent,
        "acks_lost": result.acks_lost,
        "packets_lost": result.packets_lost,
        "packets_corrupted": result.packets_corrupted,
        "total_delay_ms": result.total_delay_ms,
        "bit_error_rate": bit_error_rate,
        "packet_loss_rate": packet_loss_rate,
        "ack_loss_rate": ack_loss_rate,
        "window_size": window_size,
    }


def summarize_results(rows):
    """Calculate average performance for each scenario and protocol."""
    groups = defaultdict(list)

    for row in rows:
        groups[(row["scenario"], row["protocol"])].append(row)

    summaries = []

    for (scenario, protocol), group in sorted(groups.items()):
        count = len(group)

        summaries.append({
            "scenario": scenario,
            "protocol": protocol,
            "trials": count,
            "success_rate_percent": round(
                100 * sum(row["success"] for row in group) / count, 2
            ),
            "avg_transmissions": round(
                sum(row["transmissions"] for row in group) / count, 2
            ),
            "avg_retransmissions": round(
                sum(row["retransmissions"] for row in group) / count, 2
            ),
            "avg_delay_ms": round(
                sum(row["total_delay_ms"] for row in group) / count, 2
            ),
            "avg_packets_lost": round(
                sum(row["packets_lost"] for row in group) / count, 2
            ),
            "avg_packets_corrupted": round(
                sum(row["packets_corrupted"] for row in group) / count, 2
            ),
            "avg_acks_lost": round(
                sum(row["acks_lost"] for row in group) / count, 2
            ),
        })

    return summaries
