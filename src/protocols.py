
"""Reliable data transmission using Stop-and-Wait, Go-Back-N,
and Selective Repeat ARQ."""

from dataclasses import dataclass
from src.channel import UnreliableChannel
from src.crc import crc_encode, crc_check


@dataclass
class ProtocolResult:
    protocol: str
    success: bool
    delivered_data: list[str]
    transmissions: int
    retransmissions: int
    acks_sent: int
    acks_lost: int
    packets_lost: int
    packets_corrupted: int
    total_delay_ms: int


def _validate(data, max_retries, window_size=1):
    if any(
        not isinstance(packet, str)
        or not packet
        or any(bit not in "01" for bit in packet)
        for packet in data
    ):
        raise ValueError("Every data packet must be a non-empty binary string.")

    if not isinstance(max_retries, int) or max_retries < 0:
        raise ValueError("max_retries must be a non-negative integer.")

    if not isinstance(window_size, int) or window_size < 1:
        raise ValueError("window_size must be a positive integer.")


def _finish(name, data, channel, success, transmissions, received):
    stats = channel.get_stats()

    # Deliver only the continuous sequence starting at frame zero.
    delivered = []
    for index, packet in enumerate(data):
        if index not in received:
            break
        delivered.append(packet)

    return ProtocolResult(
        protocol=name,
        success=success,
        delivered_data=delivered,
        transmissions=transmissions,
        retransmissions=max(0, transmissions - len(data)),
        acks_sent=stats["acks_sent"],
        acks_lost=stats["acks_lost"],
        packets_lost=stats["packets_lost"],
        packets_corrupted=stats["packets_corrupted"],
        total_delay_ms=stats["total_delay_ms"],
    )


def stop_and_wait(data, channel=None, max_retries=5):
    """Send one frame and wait for its ACK before proceeding."""
    _validate(data, max_retries)
    channel = channel or UnreliableChannel()
    channel.reset_stats()

    transmissions = 0
    received = set()

    for seq, packet in enumerate(data):
        frame = crc_encode(packet)
        acknowledged = False

        for attempt in range(max_retries + 1):
            transmissions += 1
            result = channel.transmit_packet(frame)

            if not result.delivered:
                continue

            if not crc_check(result.payload):
                continue

            received.add(seq)
            ack = channel.transmit_ack()

            if ack.delivered:
                acknowledged = True
                break

        if not acknowledged:
            return _finish(
                "Stop-and-Wait", data, channel, False,
                transmissions, received
            )

    return _finish(
        "Stop-and-Wait", data, channel, True,
        transmissions, received
    )


def go_back_n(data, channel=None, window_size=4, max_retries=5):
    """Use a sliding window and retransmit from the earliest
    unacknowledged frame onward."""
    _validate(data, max_retries, window_size)
    channel = channel or UnreliableChannel()
    channel.reset_stats()

    n = len(data)
    base = 0
    expected = 0
    attempts = [0] * n
    transmissions = 0
    received = set()

    while base < n:
        end = min(base + window_size, n)

        # Send the current window.
        for seq in range(base, end):
            if attempts[seq] > max_retries:
                return _finish(
                    "Go-Back-N", data, channel, False,
                    transmissions, received
                )

            attempts[seq] += 1
            transmissions += 1

            result = channel.transmit_packet(crc_encode(data[seq]))

            if not result.delivered or not crc_check(result.payload):
                continue

            # Go-Back-N receiver accepts only the next expected frame.
            if seq == expected:
                received.add(seq)
                expected += 1

        # Send a cumulative ACK representing the next expected sequence.
        ack = channel.transmit_ack()

        if ack.delivered:
            base = expected

        # If the ACK is lost, base does not advance and the window retries.
        # A missing/corrupted frame also keeps expected from advancing.

    return _finish(
        "Go-Back-N", data, channel, True, transmissions, received
    )


def selective_repeat(data, channel=None, window_size=4, max_retries=5):
    """Buffer valid frames and retransmit only unacknowledged frames."""
    _validate(data, max_retries, window_size)
    channel = channel or UnreliableChannel()
    channel.reset_stats()

    n = len(data)
    attempts = [0] * n
    received = set()
    acknowledged = set()
    transmissions = 0

    while len(acknowledged) < n:
        pending = [
            seq for seq in range(n)
            if seq not in acknowledged
        ]

        # Transmit pending frames in groups no larger than the window.
        current_window = pending[:window_size]

        for seq in current_window:
            if attempts[seq] > max_retries:
                return _finish(
                    "Selective Repeat", data, channel, False,
                    transmissions, received
                )

            attempts[seq] += 1
            transmissions += 1

            result = channel.transmit_packet(crc_encode(data[seq]))

            if not result.delivered or not crc_check(result.payload):
                continue

            # Selective Repeat can accept a valid frame out of order.
            received.add(seq)
            ack = channel.transmit_ack()

            if ack.delivered:
                acknowledged.add(seq)

    return _finish(
        "Selective Repeat", data, channel, True, transmissions, received
    )
