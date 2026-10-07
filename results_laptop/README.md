# Records computed on the laptop (07/10), NOT published to the queue

Jobs that fail on the fleet because the package's producer stops at 10^6 y2 candidates for one y1 (`"truncated": 1`): see
HANDOFF section 17. Computed with `q/tools/laptop_2026-10-06/local_big_job.py` = `q/producer_big.py` (cap 5 x 10^7; only the default
of `max_out` in `c1/code/y2_engine.py` is changed at run time) piped into `q/par_consumer.py` in quick deferral mode, package v10.
Each record has `merged.producer_max_out`; `<tag>_producer.err` is the producer's own end line (truncated 0, complete true).
To be imported only after the lab has validated the higher cap.

| Job | y2 candidates | pairs | under the package's cap |
|---|---|---|---|
| 003:162:182 | 1,765,122 | 19,635 | truncated at 1,006,595 candidates, 18,706 pairs |
