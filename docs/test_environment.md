# Test Environment

Owner: Performance Testing Lead, with the Service Lead

The same two machines were used for every reported run.

## Machines

| | Service host (triage service + Ollama) | Load generator (JMeter) |
|---|---|---|
| Owner | Model & Accuracy Lead | Performance Testing Lead |
| CPU | Intel Core Ultra 7 155H, 16 cores / 22 threads | Intel Core i5-1235U, 10 cores / 12 threads |
| Memory | 16 GB (15.6 GB usable) | 16 GB (15.6 GB usable) |
| Operating system | Windows 11 Home, version 25H2, 64-bit | Windows 11 Home |
| Software | Docker Desktop 4.48.0, Docker Engine 28.5.1, Docker Compose 2.40.0, Ollama image 0.35.0, CPU only | Apache JMeter 5.6.3, Java 8 |
| Docker CPU / memory limit | 22 logical CPUs / 9.713 GiB available to Docker (WSL 2 backend) | not applicable |
| Power | Mixed: on battery for some runs and plugged in for others. Power mode: Best Power Efficiency | Mixed: on battery for some runs and plugged in for others. Power mode: Best Power Efficiency |

## Network

| Item | Value |
|---|---|
| Link between the machines | Over the Internet, through Tailscale (a WireGuard VPN). The two machines were on different networks |
| Path | Direct peer-to-peer, not through a Tailscale relay (`tailscale status` showed `direct`) |
| Protocol seen by the load generator | Plain HTTP to the service host's Tailscale address on port 8000, the service's own port |
| Round-trip time, load generator to service host | 25 ms mean, 10 ms minimum, 94 ms maximum, 0% loss (`ping`, 10 packets, before the first run) |
| Network overhead per request | `POST /tickets`: 124 ms typical (28 to 502 ms across runs). `GET /search`: 39 ms typical (30 to 112 ms across runs). This is `median_outside_service_ms` in `results/summary/load_runs.csv`: JMeter's elapsed time minus the service's own logged latency, taken as the median within each run. Figures cover all 18 reported load runs |

## Confirmations

- The load generator and the system under test ran on separate physical machines for every reported run: yes.
- No GPU was used. Ollama ran in the `ollama/ollama` container with no GPU settings (see `docker-compose.yml`): yes.

## Factors that could make the measurements unrepresentative

- The service host is a laptop, not a server. Its CPU mixes performance and efficiency cores, and it can slow down under sustained load.
- The service host's speed was not constant. With the same model and the same tickets, mean Ollama time per ticket rose from about 1.8 s to 3.3 s in `llama3.2-1b_high_run3`, and was 8.1 s in `gemma3-4b_stretch_run1` against about 4.3 s in runs 2 and 3. The cause was not identified. These runs are reported, and they widen the spread across runs.
- Docker Desktop runs containers inside a virtual machine, which limits the CPU and memory available to Ollama.
- The requests cross the public Internet between two different networks, so network delay varies (10 to 94 ms round trip when measured). It is small next to model inference time but large next to `GET /search`, which takes milliseconds inside the service. A LAN connection would give lower and steadier latencies.
- Tailscale encrypts traffic on both machines, which uses a small amount of the service host's CPU.
- The first attempt used a VS Code forwarded port (Microsoft dev tunnel) instead. That run, `llama3.2-1b_stretch_run1`, is kept but not reported: the tunnel returned `504 Gateway Timeout` after 100 seconds for 3 of 20 tickets that never reached the service, so it did not reconcile with the service log.
- Background programs and operating system updates on either machine.
- One service instance and one Ollama instance. The client may run several.

## Scaling to the client's deployment

Draft, to be agreed with the Workload & Requirements Lead.

- **Throughput is set by one Ollama instance handling one ticket at a time.** The limit of one instance is about 60 divided by the model's seconds per ticket. The stress test confirmed this for `gemma3:4b`: about 6 s per ticket and a limit of about 10 tickets per minute.
- **A faster or slower CPU moves the limit in proportion.** The client's servers are commodity CPU servers of unknown specification, so absolute latencies from a laptop do not transfer directly. The ranking of the models and the ratio between them should.
- **More capacity comes from more instances, not from one busier instance.** Running several Ollama instances, each with its own copy of the model in memory, should raise throughput roughly in proportion. This was not tested.
- **Network overhead in these tests is higher than the client would see.** The client's intake system and service would sit on the same network, without the Internet path used here.
