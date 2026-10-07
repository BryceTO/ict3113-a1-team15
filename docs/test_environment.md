# Test Environment

Owner: Performance Testing Lead, with the Service Lead

Fill every `TBD` before the first official run. Do not change either machine between runs.

## Machines

| | Service host (triage service + Ollama) | Load generator (JMeter) |
|---|---|---|
| Owner | TBD | Performance Testing Lead |
| CPU | TBD | Intel Core i5-1235U, 10 cores / 12 threads |
| Memory | TBD | 16 GB |
| Operating system | TBD | Windows 11 Home |
| Software | Docker Desktop TBD, Ollama image 0.35.0, CPU only | Apache JMeter 5.6.3, Java 8 |
| Docker CPU / memory limit | TBD | not applicable |
| Power | TBD (mains, power plan) | TBD (mains, power plan) |

## Network

| Item | Value |
|---|---|
| Link between the machines | TBD (same Wi-Fi network / wired LAN / phone hotspot) |
| Round-trip time, load generator to service host | TBD ms (`ping`, 20 packets, mean) |
| Service port | TCP 8000, opened on the service host firewall |

## Confirmations

- The load generator and the system under test ran on separate physical machines for every reported run: TBD (yes / no).
- No GPU was used. Ollama ran in the `ollama/ollama` container with no GPU settings: TBD (yes / no).

## Factors that could make the measurements unrepresentative

Keep the ones that apply and add any others seen during testing.

- The service host is a laptop, not a server: thermal throttling during long runs, and a mix of performance and efficiency cores if it has a hybrid CPU.
- Docker Desktop runs containers inside a virtual machine, which limits the CPU and memory available to Ollama.
- Wi-Fi adds variable delay. It is small next to model inference time but matters for `GET /search`.
- Background programs and operating system updates on either machine.
- One service instance and one Ollama instance. The client may run several.

## Scaling to the client's deployment

To be written with the Workload & Requirements Lead once results exist. State the assumptions: how the client's CPU compares with the service host, and that throughput is bounded by one inference at a time per Ollama instance.
