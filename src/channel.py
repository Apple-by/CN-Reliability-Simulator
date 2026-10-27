
"""Simulate packet errors, packet loss, ACK loss, and transmission delay."""

from dataclasses import dataclass
import random


@dataclass
class ChannelConfig:
    bit_error_rate: float = 0.0
    packet_loss_rate: float = 0.0
    ack_loss_rate: float = 0.0
    min_delay_ms: int = 1
    max_delay_ms: int = 10

    def __post_init__(self):
        for name in (
            "bit_error_rate",
            "packet_loss_rate",
            "ack_loss_rate",
        ):
            value = getattr(self, name)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1.")

        if self.min_delay_ms < 0:
            raise ValueError("Minimum delay cannot be negative.")

        if self.max_delay_ms < self.min_delay_ms:
            raise ValueError(
                "Maximum delay must be at least the minimum delay."
            )


@dataclass
class TransmissionResult:
    delivered: bool
    payload: str | None
    corrupted: bool
    delay_ms: int


class UnreliableChannel:
    """A reproducible, local simulation of an unreliable channel."""

    def __init__(self, config=None, seed=None):
        self.config = config or ChannelConfig()
        self.rng = random.Random(seed)
        self.reset_stats()

    def reset_stats(self):
        self.stats = {
            "packets_sent": 0,
            "packets_lost": 0,
            "packets_corrupted": 0,
            "acks_sent": 0,
            "acks_lost": 0,
            "total_delay_ms": 0,
        }

    def _delay(self):
        delay = self.rng.randint(
            self.config.min_delay_ms,
            self.config.max_delay_ms,
        )
        self.stats["total_delay_ms"] += delay
        return delay

    def transmit_packet(self, packet):
        """Transmit a binary packet; return its delivery result."""
        if not packet or any(bit not in "01" for bit in packet):
            raise ValueError("Packet must be a non-empty binary string.")

        self.stats["packets_sent"] += 1
        delay = self._delay()

        if self.rng.random() < self.config.packet_loss_rate:
            self.stats["packets_lost"] += 1
            return TransmissionResult(False, None, False, delay)

        received = list(packet)
        corrupted = False

        for i in range(len(received)):
            if self.rng.random() < self.config.bit_error_rate:
                received[i] = "1" if received[i] == "0" else "0"
                corrupted = True

        if corrupted:
            self.stats["packets_corrupted"] += 1

        return TransmissionResult(
            True,
            "".join(received),
            corrupted,
            delay,
        )

    def transmit_ack(self):
        """Simulate sending an acknowledgement (ACK)."""
        self.stats["acks_sent"] += 1
        delay = self._delay()

        if self.rng.random() < self.config.ack_loss_rate:
            self.stats["acks_lost"] += 1
            return TransmissionResult(False, None, False, delay)

        return TransmissionResult(True, "ACK", False, delay)

    def get_stats(self):
        """Return a copy of the channel statistics."""
        return self.stats.copy()
