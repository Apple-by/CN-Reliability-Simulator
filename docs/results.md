# Experimental Results and Analysis

## 1. Purpose

The experiments evaluate how Stop-and-Wait, Go-Back-N, and Selective Repeat ARQ behave under different simulated communication conditions.

The evaluation focuses on delivery success, transmission attempts, retransmissions, packet loss, packet corruption, acknowledgement loss, and simulated delay.

## 2. Experimental Setup

The experiment runner uses the following configuration:

- Number of protocols: 3
- Channel scenarios: 3
- Random seeds per scenario: 20
- Total protocol runs: 180
- Input data: 8 binary packets
- Sliding window size: 4 for Go-Back-N and Selective Repeat
- Maximum retransmissions per frame: 5
- Simulated delay range: 1–10 ms per transmission attempt

The scenarios use these channel probabilities:

| Scenario | Bit Error Probability | Packet Loss Probability | ACK Loss Probability |
|---|---:|---:|---:|
| Reliable | 0.00 | 0.00 | 0.00 |
| Moderate | 0.01 | 0.05 | 0.05 |
| Noisy | 0.05 | 0.10 | 0.10 |

The random seeds make individual runs reproducible for a fixed implementation and configuration.

## 3. Recorded Results

The following table records the results from the experiment run included in the project.

| Scenario | Protocol | Success Rate | Average Transmissions | Average Retransmissions | Average Delay |
|---|---|---:|---:|---:|---:|
| Reliable | Stop-and-Wait | 100% | 8.00 | 0.00 | 89.40 ms |
| Reliable | Go-Back-N | 100% | 8.00 | 0.00 | 55.15 ms |
| Reliable | Selective Repeat | 100% | 8.00 | 0.00 | 89.40 ms |
| Moderate | Stop-and-Wait | 100% | 9.40 | 1.40 | 98.20 ms |
| Moderate | Go-Back-N | 100% | 11.55 | 3.55 | 81.70 ms |
| Moderate | Selective Repeat | 100% | 9.40 | 1.40 | 98.20 ms |
| Noisy | Stop-and-Wait | 95% | 14.15 | 6.30 | 125.05 ms |
| Noisy | Go-Back-N | 85% | 21.55 | 13.65 | 156.95 ms |
| Noisy | Selective Repeat | 85% | 14.30 | 6.30 | 125.90 ms |

Each success rate is calculated across 20 runs for its scenario and protocol.

## 4. Analysis

### 4.1 Reliable Channel

All three protocols achieved 100% success and required an average of eight data-frame transmissions, matching the eight input packets.

Go-Back-N recorded a lower average simulated delay because it sends cumulative acknowledgements for a window of frames. Stop-and-Wait and Selective Repeat acknowledge individual successfully received frames in this implementation.

### 4.2 Moderate Channel

All three protocols achieved 100% success in the recorded runs.

Go-Back-N used more transmissions on average than the other protocols. However, it recorded a lower average simulated delay in this experiment. This illustrates that transmission count and accumulated delay do not necessarily rank protocols in the same order.

### 4.3 Noisy Channel

Stop-and-Wait achieved a 95% success rate, while Go-Back-N and Selective Repeat each achieved 85%.

Go-Back-N had the highest average number of transmissions and the highest average simulated delay. When a frame is lost or corrupted, later frames in the window may need to be sent again because the receiver accepts frames in sequence.

Selective Repeat can accept valid frames out of order, so it can avoid retransmitting frames that have already been received correctly. Its observed success rate in these runs was nevertheless the same as Go-Back-N's.

Stop-and-Wait performed best by success rate in this particular experiment. This result should not be interpreted as proof that it always outperforms the other protocols.

## 5. Metrics

- **Success rate:** Percentage of runs in which the protocol reports successful completion.
- **Average transmissions:** Mean number of data-frame transmission attempts.
- **Average retransmissions:** Mean number of transmission attempts beyond the first attempt for each individual packet, averaged across the evaluation trials.
- **Average simulated delay:** Mean accumulated delay recorded for packet and ACK transmission attempts.
- **Packet loss:** Number of packet transmission attempts dropped by the simulated channel.
- **Packet corruption:** Number of packet transmission attempts in which at least one bit was flipped.
- **ACK loss:** Number of acknowledgement attempts dropped by the simulated channel.

These metrics describe the current simulator implementation. They are not real-world network measurements.

## 6. Generated Files

The experiment runner creates:

- `results/protocol_comparison_raw.csv` — individual run results.
- `results/protocol_comparison_summary.csv` — aggregated metrics by scenario and protocol.

The plotting script creates:

- `results/success_rate.png`
- `results/average_transmissions.png`
- `results/average_delay.png`

To rerun the experiments and regenerate the graphs:

```bash
python3 -m src.evaluate
python3 -m src.plot_results
```

## 7. Limitations

1. The simulator models channel behavior locally rather than transmitting over a physical network.
2. The experiments use a fixed set of eight binary packets and three configured channel scenarios.
3. Only 20 seeds are evaluated per scenario, so observed percentages may change with other seeds or configurations.
4. The simulated delay is accumulated from generated transmission delays; it is not a measurement of actual end-to-end network latency.
5. The protocols are educational simulations and do not model every detail of a production networking stack.

## 8. Conclusion

The experiments demonstrate that channel conditions affect delivery success, transmission attempts, retransmissions, and accumulated simulated delay. The three ARQ protocols exhibit different behavior because they use different acknowledgement and retransmission strategies.

The CSV results and graphs provide a repeatable basis for comparing the implemented protocols under the selected simulated conditions.