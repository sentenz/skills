---
name: python-benchmark-testing
description: Create and review Python performance benchmarks using pytest-benchmark, pyperf, and standard-library profiling tools. Use for microbenchmarks, performance regressions, baseline comparisons, timing, allocation analysis, profiling, or validating optimizations.
metadata:
  version: "1.0.0"
  activation:
    implicit: true
    priority: 1
    triggers:
      - "benchmark test"
      - "pytest-benchmark"
      - "python benchmark"
      - "benchmarking"
      - "performance test"
      - "profile code"
    match:
      languages: ["python"]
      paths: ["**/test*.py", "**/*_test.py", "tests/**/*.py"]
      prompt_regex: '(?i)(benchmark test|pytest-benchmark|python benchmark|benchmarking|performance test|profile code|profiling)'
    usage:
      load_on_prompt: true
      autodispatch: true
---

# Benchmark Testing

Measure a defined Python workload, validate its result, and compare repeated measurements under controlled conditions. Preserve existing benchmark infrastructure and distinguish latency, throughput, Python allocations, and total process memory.

- [1. Benefits](#1-benefits)
- [2. Principles](#2-principles)
- [3. Patterns](#3-patterns)
- [4. Workflow](#4-workflow)
- [5. Commands](#5-commands)
- [6. Style Guide](#6-style-guide)
- [7. Templates](#7-templates)
- [8. References](#8-references)

## 1. Benefits

- Establish evidence before making optimization decisions.
- Detect regressions using comparable workloads and recorded baselines.
- Separate algorithmic cost from setup, cache effects, and instrumentation overhead.

## 2. Principles

Apply FIRST to benchmark design:

- **Fast:** Bound the suite while collecting enough repeated samples to assess variation.
- **Independent:** Reset mutable inputs and avoid concurrent benchmark workers.
- **Repeatable:** Record interpreter, dependencies, hardware, runtime settings, and workload.
- **Self-Validating:** Verify correctness outside the measured operation.
- **Timely:** Measure the baseline before changing the implementation.

## 3. Patterns

| Pattern | Application |
| --- | --- |
| Microbenchmark | Use pytest-benchmark for an isolated callable within an existing pytest suite. |
| Process-isolated measurement | Use pyperf for calibrated runs across worker processes. |
| Comparative benchmark | Measure the same workload and environment before and after a change. |
| Table-driven workload | Parametrize representative sizes, shapes, and distributions with stable IDs. |
| Stateful operation | Recreate state outside timing for each measured invocation, or explicitly measure setup as part of the workload. |
| Profiling | Use cProfile to locate CPU costs and tracemalloc for traced Python allocations in separate runs. |

## 4. Workflow

1. Inspect the project's supported interpreters, dependency manager, benchmark suite, CI runners, and existing baselines. Select the existing tool where possible; add optional development dependencies only as needed.
2. Define the operation, unit of work, input distribution, size range, cache state, and metric. Decide whether startup, imports, serialization, I/O, and cleanup belong inside the measured boundary.
3. Establish correctness with unit tests before timing. Construct representative deterministic inputs and independently known expected results.
4. Record the baseline commit and environment. Run benchmarks without coverage, a debugger, profiling, or pytest-xdist. Check background load and warmup behavior.
5. Use the [templates](#7-templates), ensuring repeated calls perform equivalent work. Rebuild exhausted iterators and mutated collections between calls. Make warm-cache and cold-cache measurements separate workloads.
6. Compare repeated before/after runs with the same tool, inputs, interpreter build, machine, and settings. Inspect dispersion and tool warnings; rerun unstable measurements before claiming an improvement.
7. Apply only established project regression thresholds. Avoid a one-shot elapsed-time assertion in a correctness test. Use dedicated stable runners for performance gates.
8. Report workload, commands, versions, baseline/candidate commits, sample statistics, relative change, and uncertainty. Retain result files as benchmark artifacts; distinguish unmeasured hypotheses from findings.

## 5. Commands

Run in the project environment with pytest-benchmark or pyperf installed. Replace illustrative paths and output names; do not compare unrelated runners or overwrite the baseline with the candidate run.

| Command | Purpose |
| --- | --- |
| `python -m pytest benchmarks/test_sort.py --benchmark-only` | Execute pytest benchmarks. |
| `python -m pytest benchmarks/test_sort.py --benchmark-only --benchmark-save=baseline` | Save the baseline in pytest-benchmark storage. |
| `python -m pytest benchmarks/test_sort.py --benchmark-only --benchmark-compare=0001` | Compare against the actual saved run ID, replacing `0001`. |
| `python -m pyperf timeit -s 'values = tuple(range(1000, 0, -1))' 'sorted(values)' -o before.json` | Measure a workload with calibrated workers. |
| `python -m pyperf compare_to before.json after.json --table` | Compare result files collected with the same workload. |
| `python -m cProfile -o profile.pstats path/to/workload.py` | Profile a representative script separately from timing runs. |
| `python -m pstats profile.pstats` | Inspect CPU profiling output. |

For a changed application callable, use the same import/setup and statement on the baseline and candidate revisions, writing `before.json` and `after.json` respectively. `timeit` alone is useful for local exploration, but does not replace a controlled regression experiment.

## 6. Style Guide

- Use `test_<operation>` under the existing benchmark directory so pytest discovers the benchmark fixture.
- Pass a callable and its arguments to `benchmark`; do not call the operation before passing it. Assert the returned result outside the measured callable.
- Keep input generation, unrelated validation, printing, and logging outside timing unless they are part of the defined workload.
- For mutable operations, use `benchmark.pedantic` with a setup callback and `iterations=1` so each measured invocation receives fresh state.
- Explicitly choose and record garbage-collection behavior; defaults differ between tools. Do not disable GC merely to improve reported numbers when collection is part of the production workload.
- Record Python implementation/version, build mode, OS, CPU, and relevant native-library thread counts. Do not attribute differences across interpreter versions or machines solely to a code change.
- Do not pass a coroutine directly to a synchronous benchmark fixture: that measures coroutine creation. Use an async-aware harness or a documented wrapper that awaits completion, declaring whether event-loop startup is included.
- Profile memory separately from latency. `tracemalloc` measures traced allocations, not all native memory or total resident set size. Use an appropriate process-memory tool for those questions.
- Treat tiny differences within measurement noise as inconclusive. Report distributions and practical effect sizes instead of selecting only the fastest run.

## 7. Templates

These runnable examples use sorting to demonstrate immutable and mutable workloads. Replace sorting with the actual hot path and preserve meaningful validation.

### 7.1. Table-Driven Benchmark

Save as `benchmarks/test_sort.py`.

```python
import pytest


@pytest.mark.parametrize("size", [10, 1000, 10000], ids=["small", "medium", "large"])
def test_sorted_descending(benchmark, size):
    # Arrange: exclude workload construction from timing.
    values = tuple(range(size, 0, -1))
    want = list(range(1, size + 1))

    # Act: each invocation receives the same immutable input.
    got = benchmark(sorted, values)

    # Assert: exclude result validation from timing.
    assert got == want
```

### 7.2. Mutating Operation

Do not repeatedly sort the same list; later invocations would measure already-sorted data. Use setup to create fresh input for every round and return it for validation without timing validation itself.

```python
def test_sort_in_place(benchmark):
    source = tuple(range(1000, 0, -1))
    want = list(range(1, 1001))

    def setup():
        return (list(source),), {}

    def sort_values(values):
        values.sort()
        return values

    got = benchmark.pedantic(sort_values, setup=setup, rounds=20, iterations=1)
    assert got == want
```

The wrapper's return is part of this measured workload. For very small operations, account for wrapper overhead when interpreting results.

### 7.3. Separate Allocation Measurement

Run as a standalone script so tracing ownership is unambiguous. Replace the demonstrated operation with the target workload; do not run this instrumentation inside a latency benchmark.

```python
import tracemalloc


values = tuple(range(1000, 0, -1))
tracemalloc.start()
try:
    tracemalloc.reset_peak()
    got = sorted(values)
    current, peak = tracemalloc.get_traced_memory()
finally:
    tracemalloc.stop()

assert got == list(range(1, 1001))
print(f"traced_current_bytes={current}, traced_peak_bytes={peak}")
```

## 8. References

- pytest-benchmark [Usage](https://pytest-benchmark.readthedocs.io/en/latest/usage.html) and [Pedantic mode](https://pytest-benchmark.readthedocs.io/en/latest/pedantic.html).
- pyperf [Commands](https://pyperf.readthedocs.io/en/latest/cli.html) and [Running benchmarks](https://pyperf.readthedocs.io/en/latest/run_benchmark.html).
- Python [Profiling](https://docs.python.org/3/library/profile.html), [tracemalloc](https://docs.python.org/3/library/tracemalloc.html), and [timeit](https://docs.python.org/3/library/timeit.html).
