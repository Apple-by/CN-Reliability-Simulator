# Implementation Details

## 1. System Overview

The Network Transmission Reliability and Error Recovery Simulator is implemented in Python. It models data transmission through an unreliable communication channel and demonstrates error detection, error correction, and automatic repeat request (ARQ) protocols.

The implementation is divided into modules so that error-control algorithms, channel behavior, protocol logic, evaluation metrics, and the user interface can be tested independently.

## 2. Module Description

### 2.1 CRC — `src/crc.py`

Cyclic Redundancy Check (CRC) is used to detect errors in transmitted data.

The sender appends CRC bits to the original binary data using modulo-2 division with a generator polynomial. The receiver checks the received codeword by dividing it by the same generator. A zero remainder indicates that the check passes.

CRC detects many common transmission errors, but a passing check does not guarantee that every possible error has been detected.

### 2.2 Hamming Code — `src/hamming.py`

Hamming Code adds parity bits to data so that certain errors can be detected and corrected.

The implementation calculates parity bits during encoding. During decoding, the receiver calculates a syndrome to identify a possible erroneous bit position. The implementation supports single-bit error correction.

### 2.3 Unreliable Channel — `src/channel.py`

The channel simulates communication conditions that may prevent correct delivery. Its configurable parameters include:

- Bit error probability.
- Packet loss probability.
- ACK loss probability.
- Minimum and maximum transmission delay.
- Random seed for repeatable experiments.

When a packet is transmitted, the channel may drop it, flip one or more bits, or deliver it with simulated delay. ACK transmission is simulated separately.

The channel also maintains counters for transmitted and lost packets, corrupted packets, ACKs, and accumulated simulated delay.

### 2.4 ARQ Protocols — `src/protocols.py`

Automatic Repeat reQuest (ARQ) protocols retransmit frames when delivery or acknowledgement fails.

**Stop-and-Wait ARQ**

The sender transmits one frame and waits for its acknowledgement before moving to the next frame. If delivery or acknowledgement fails, the sender retries the frame until it succeeds or reaches the retry limit.

**Go-Back-N ARQ**

The sender transmits multiple frames within a sliding window. The receiver accepts frames in sequence and uses cumulative acknowledgements. When progress is not acknowledged, the sender retransmits from the earliest unacknowledged frame.

**Selective Repeat ARQ**

The sender maintains a sliding window and retransmits unacknowledged frames. Valid frames can be accepted out of order, reducing the need to resend frames that have already been received correctly.

The protocols use CRC checks to reject corrupted frames and a configured retry limit to bound retransmission attempts.

### 2.5 Metrics — `src/metrics.py`

The metrics module converts individual protocol results into structured records and calculates summary statistics grouped by channel scenario and protocol.

The summaries include success rate, average transmissions, average retransmissions, average simulated delay, packet losses, packet corruption, and ACK losses.

### 2.6 Command-Line Interface — `src/main.py`

The command-line interface allows the user to select an error-control method or ARQ protocol, enter binary packets, configure channel conditions, and view transmission results.

It also provides an option to run all three ARQ protocols with the same configured channel conditions for comparison.

### 2.7 Experiment Runner — `src/evaluate.py`

The experiment runner evaluates Stop-and-Wait, Go-Back-N, and Selective Repeat under Reliable, Moderate, and Noisy channel conditions.

It uses 20 random seeds per scenario and saves individual and aggregated results as CSV files in the `results/` directory.

### 2.8 Graph Generator — `src/plot_results.py`

The graph generator reads the summary CSV and creates bar charts for:

- Protocol success rate.
- Average number of transmissions.
- Average simulated delay.

The charts are saved as PNG files for inclusion in the project report.

## 3. Data Flow

1. The user enters binary data packets through the command-line interface or experiment runner.
2. The selected protocol encodes each packet using CRC.
3. The channel simulates packet transmission, potential bit corruption, packet loss, and delay.
4. The receiver checks the received frame and processes acknowledgements according to the protocol.
5. The sender retransmits frames when required, subject to the retry limit.
6. The protocol returns its results and transmission statistics.
7. The evaluation module writes experiment results to CSV.
8. The plotting module generates graphs from the summary CSV.

## 4. Testing

The project includes automated tests for CRC, Hamming Code, channel behavior, input validation, and ARQ protocol outcomes.

Run the tests using:

```bash
python3 -m unittest discover -s tests -v
```

The tests help verify expected behavior for clean transmissions, errors, losses, and invalid inputs.
