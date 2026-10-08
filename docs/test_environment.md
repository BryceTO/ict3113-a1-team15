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
| Link between the machines | Over the Internet, through a VS Code forwarded port (Microsoft dev tunnel, public visibility). The two machines were on different networks |
| Protocol seen by the load generator | HTTPS on port 443 at a `devtunnels.ms` address. The tunnel forwards to the service's HTTP port 8000 on the service host |
| Network overhead per request | TBD ms: `median_outside_service_ms` in `results/summary/load_runs.csv`, which is JMeter's elapsed time minus the service's own logged latency |
| Connections | Each request opens a new HTTPS connection, so every request pays a TLS handshake through the tunnel |

## Confirmations

- The load generator and the system under test ran on separate physical machines for every reported run: TBD (yes / no).
- No GPU was used. Ollama ran in the `ollama/ollama` container with no GPU settings: TBD (yes / no).

## Factors that could make the measurements unrepresentative

Keep the ones that apply and add any others seen during testing.

- The service host is a laptop, not a server: thermal throttling during long runs, and a mix of performance and efficiency cores if it has a hybrid CPU.
- Docker Desktop runs containers inside a virtual machine, which limits the CPU and memory available to Ollama.
- The tunnel adds Internet and relay delay to every request, and it varies. It is small next to model inference time but large next to `GET /search`, which takes milliseconds inside the service. A direct LAN connection would give lower and steadier latencies.
- The tunnel is a third-party relay with its own limits. If it drops or times out a long-waiting request, JMeter records an error that the service log does not show. Any such run is flagged `reconciled = no` and must be explained as a tunnel effect, not a service failure.
- The tunnel client runs inside VS Code on the service host and uses a small amount of its CPU.
- Background programs and operating system updates on either machine.
- One service instance and one Ollama instance. The client may run several.

## Scaling to the client's deployment

To be written with the Workload & Requirements Lead once results exist. State the assumptions: how the client's CPU compares with the service host, and that throughput is bounded by one inference at a time per Ollama instance.
