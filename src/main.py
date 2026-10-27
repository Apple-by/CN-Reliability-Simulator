
"""Command-line interface for the Network Reliability Simulator."""

from src.crc import crc_encode, crc_check
from src.hamming import hamming_encode, hamming_decode
from src.channel import ChannelConfig, UnreliableChannel
from src.protocols import (
    stop_and_wait,
    go_back_n,
    selective_repeat,
)


def read_probability(prompt, default):
    """Read a probability between 0 and 1."""
    while True:
        raw = input(f"{prompt} [{default}]: ").strip()

        if not raw:
            return default

        try:
            value = float(raw)
            if 0 <= value <= 1:
                return value
        except ValueError:
            pass

        print("Enter a number between 0 and 1.")


def read_integer(prompt, default, minimum=0):
    """Read an integer with a minimum allowed value."""
    while True:
        raw = input(f"{prompt} [{default}]: ").strip()

        if not raw:
            return default

        try:
            value = int(raw)
            if value >= minimum:
                return value
        except ValueError:
            pass

        print(f"Enter an integer greater than or equal to {minimum}.")


def read_binary_data():
    """Read one or more binary packets separated by commas."""
    while True:
        raw = input(
            "Enter binary packets separated by commas (e.g. 1011,1100): "
        ).strip()

        packets = [part.strip() for part in raw.split(",")]

        if packets and all(
            packet and all(bit in "01" for bit in packet)
            for packet in packets
        ):
            return packets

        print("Each packet must contain only 0s and 1s.")


def configure_channel():
    """Ask the user for channel conditions."""
    print("\n--- Channel Configuration ---")

    bit_error = read_probability("Bit error probability", 0.0)
    packet_loss = read_probability("Packet loss probability", 0.0)
    ack_loss = read_probability("ACK loss probability", 0.0)
    min_delay = read_integer("Minimum delay in ms", 1)
    max_delay = read_integer("Maximum delay in ms", 10, min_delay)
    seed = read_integer("Random seed", 42)

    config = ChannelConfig(
        bit_error_rate=bit_error,
        packet_loss_rate=packet_loss,
        ack_loss_rate=ack_loss,
        min_delay_ms=min_delay,
        max_delay_ms=max_delay,
    )

    return UnreliableChannel(config, seed=seed)


def run_error_control():
    print("\n1. CRC Error Detection")
    print("2. Hamming Code Error Correction")

    choice = input("Choose error-control method: ").strip()
    packets = read_binary_data()

    for packet in packets:
        print(f"\nOriginal data: {packet}")

        if choice == "1":
            codeword = crc_encode(packet)
            print(f"CRC codeword: {codeword}")
            print(f"CRC check passed: {crc_check(codeword)}")

            received = input(
                "Optional received codeword (Enter to use original): "
            ).strip()

            if received:
                try:
                    print(f"Received CRC check: {crc_check(received)}")
                except ValueError as error:
                    print("Invalid input:", error)

        elif choice == "2":
            codeword = hamming_encode(packet)
            print(f"Hamming codeword: {codeword}")

            received = input(
                "Optional received codeword (Enter to use original): "
            ).strip() or codeword

            try:
                decoded, corrected, syndrome = hamming_decode(received)
                print(f"Decoded data: {decoded}")
                print(f"Error corrected: {corrected}")
                print(f"Syndrome: {syndrome}")
            except ValueError as error:
                print("Invalid input:", error)

        else:
            print("Invalid choice.")
            return


def display_result(result):
    """Display the result and channel metrics."""
    print(f"\n--- {result.protocol} Results ---")
    print(f"Success: {result.success}")
    print(f"Data delivered: {result.delivered_data}")
    print(f"Transmissions: {result.transmissions}")
    print(f"Retransmissions: {result.retransmissions}")
    print(f"ACKs lost: {result.acks_lost}")
    print(f"Packets lost: {result.packets_lost}")
    print(f"Packets corrupted: {result.packets_corrupted}")
    print(f"Total simulated delay: {result.total_delay_ms} ms")


def run_protocol(protocol, name):
    packets = read_binary_data()
    channel = configure_channel()
    retries = read_integer("Maximum retransmissions per frame", 5)

    if protocol == stop_and_wait:
        result = protocol(packets, channel=channel, max_retries=retries)
    else:
        window = read_integer("Sliding window size", 4, 1)
        result = protocol(
            packets,
            channel=channel,
            window_size=window,
            max_retries=retries,
        )

    display_result(result)


def compare_protocols():
    packets = read_binary_data()
    config_channel = configure_channel()
    config = config_channel.config
    seed = 42

    retries = read_integer("Maximum retransmissions per frame", 5)
    window = read_integer("Sliding window size", 4, 1)

    protocols = [
        (stop_and_wait, {}),
        (go_back_n, {"window_size": window}),
        (selective_repeat, {"window_size": window}),
    ]

    results = []

    for protocol, extra in protocols:
        channel = UnreliableChannel(config, seed=seed)
        result = protocol(
            packets,
            channel=channel,
            max_retries=retries,
            **extra,
        )
        results.append(result)
        display_result(result)

    print("\n--- Comparison Summary ---")
    print(f"{'Protocol':<20} {'Success':<10} {'Transmissions':<15} {'Retries':<10}")
    print("-" * 60)

    for result in results:
        print(
            f"{result.protocol:<20} "
            f"{str(result.success):<10} "
            f"{result.transmissions:<15} "
            f"{result.retransmissions:<10}"
        )


def main():
    while True:
        print("\n====================================")
        print(" NETWORK RELIABILITY SIMULATOR")
        print("====================================")
        print("1. CRC Error Detection")
        print("2. Hamming Code Error Correction")
        print("3. Stop-and-Wait ARQ")
        print("4. Go-Back-N ARQ")
        print("5. Selective Repeat ARQ")
        print("6. Compare All ARQ Protocols")
        print("0. Exit")

        choice = input("Choose an option: ").strip()

        try:
            if choice == "1" or choice == "2":
                run_error_control()
            elif choice == "3":
                run_protocol(stop_and_wait, "Stop-and-Wait")
            elif choice == "4":
                run_protocol(go_back_n, "Go-Back-N")
            elif choice == "5":
                run_protocol(selective_repeat, "Selective Repeat")
            elif choice == "6":
                compare_protocols()
            elif choice == "0":
                print("Exiting simulator. Goodbye!")
                break
            else:
                print("Invalid choice. Select 0-6.")

        except (ValueError, EOFError) as error:
            print("Could not complete the operation:", error)


if __name__ == "__main__":
    main()
