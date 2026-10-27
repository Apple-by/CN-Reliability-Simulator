
import unittest

from src.channel import ChannelConfig, UnreliableChannel


class TestChannel(unittest.TestCase):

    def test_clean_packet_delivery(self):
        channel = UnreliableChannel(
            ChannelConfig(
                bit_error_rate=0,
                packet_loss_rate=0,
                min_delay_ms=5,
                max_delay_ms=5,
            ),
            seed=42,
        )

        result = channel.transmit_packet("10110")

        self.assertTrue(result.delivered)
        self.assertEqual(result.payload, "10110")
        self.assertFalse(result.corrupted)
        self.assertEqual(result.delay_ms, 5)

    def test_all_bits_flip(self):
        channel = UnreliableChannel(
            ChannelConfig(bit_error_rate=1.0),
            seed=42,
        )

        result = channel.transmit_packet("10110")

        self.assertTrue(result.delivered)
        self.assertEqual(result.payload, "01001")
        self.assertTrue(result.corrupted)

    def test_packet_loss(self):
        channel = UnreliableChannel(
            ChannelConfig(packet_loss_rate=1.0),
            seed=42,
        )

        result = channel.transmit_packet("10110")

        self.assertFalse(result.delivered)
        self.assertIsNone(result.payload)
        self.assertEqual(channel.get_stats()["packets_lost"], 1)

    def test_ack_loss(self):
        channel = UnreliableChannel(
            ChannelConfig(ack_loss_rate=1.0),
            seed=42,
        )

        result = channel.transmit_ack()

        self.assertFalse(result.delivered)
        self.assertIsNone(result.payload)
        self.assertEqual(channel.get_stats()["acks_lost"], 1)

    def test_reproducible_results(self):
        config = ChannelConfig(
            bit_error_rate=0.2,
            packet_loss_rate=0.1,
        )

        channel_a = UnreliableChannel(config, seed=123)
        channel_b = UnreliableChannel(config, seed=123)

        result_a = channel_a.transmit_packet("101101101")
        result_b = channel_b.transmit_packet("101101101")

        self.assertEqual(result_a, result_b)

    def test_invalid_packet(self):
        channel = UnreliableChannel()

        with self.assertRaises(ValueError):
            channel.transmit_packet("10A1")

    def test_invalid_configuration(self):
        with self.assertRaises(ValueError):
            ChannelConfig(bit_error_rate=1.5)


if __name__ == "__main__":
    unittest.main()
