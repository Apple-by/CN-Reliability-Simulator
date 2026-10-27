
import unittest

from src.channel import ChannelConfig, UnreliableChannel
from src.protocols import (
    stop_and_wait,
    go_back_n,
    selective_repeat,
)


class TestReliableProtocols(unittest.TestCase):

    
    def test_all_protocols_deliver_clean_data(self):
        data = ["1011", "1100", "0101"]

        for protocol in (stop_and_wait, go_back_n, selective_repeat):
            with self.subTest(protocol=protocol.__name__):
                channel = UnreliableChannel(
                    ChannelConfig(
                        bit_error_rate=0,
                        packet_loss_rate=0,
                        ack_loss_rate=0,
                    ),
                    seed=42,
                )

                if protocol is stop_and_wait:
                    result = protocol(
                        data, channel=channel, max_retries=2
                    )
                else:
                    result = protocol(
                        data,
                        channel=channel,
                        window_size=2,
                        max_retries=2,
                    )

                self.assertTrue(result.success)
                self.assertEqual(result.delivered_data, data)
                self.assertEqual(result.retransmissions, 0)

    def test_stop_and_wait_fails_when_all_packets_are_lost(self):
        channel = UnreliableChannel(
            ChannelConfig(packet_loss_rate=1.0),
            seed=42,
        )

        result = stop_and_wait(
            ["1011"],
            channel=channel,
            max_retries=2,
        )

        self.assertFalse(result.success)
        self.assertEqual(result.transmissions, 3)
        self.assertEqual(result.retransmissions, 2)

    def test_go_back_n_fails_when_all_packets_are_lost(self):
        channel = UnreliableChannel(
            ChannelConfig(packet_loss_rate=1.0),
            seed=42,
        )

        result = go_back_n(
            ["1011", "1100"],
            channel=channel,
            window_size=2,
            max_retries=1,
        )

        self.assertFalse(result.success)
        self.assertGreater(result.retransmissions, 0)

    def test_selective_repeat_fails_when_all_packets_are_lost(self):
        channel = UnreliableChannel(
            ChannelConfig(packet_loss_rate=1.0),
            seed=42,
        )

        result = selective_repeat(
            ["1011", "1100"],
            channel=channel,
            window_size=2,
            max_retries=1,
        )

        self.assertFalse(result.success)
        self.assertGreater(result.retransmissions, 0)

    def test_stop_and_wait_fails_when_all_acks_are_lost(self):
        channel = UnreliableChannel(
            ChannelConfig(ack_loss_rate=1.0),
            seed=42,
        )

        result = stop_and_wait(
            ["1011"],
            channel=channel,
            max_retries=1,
        )

        self.assertFalse(result.success)
        self.assertEqual(result.transmissions, 2)
        self.assertEqual(result.acks_lost, 2)

    def test_invalid_data_is_rejected(self):
        for protocol in (
            stop_and_wait,
            go_back_n,
            selective_repeat,
        ):
            with self.subTest(protocol=protocol.__name__):
                with self.assertRaises(ValueError):
                    protocol(["10X1"])

    def test_invalid_window_size_is_rejected(self):
        with self.assertRaises(ValueError):
            go_back_n(["1011"], window_size=0)

        with self.assertRaises(ValueError):
            selective_repeat(["1011"], window_size=0)


if __name__ == "__main__":
    unittest.main()
