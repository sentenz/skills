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

Benchmark testing measures the execution cost of a defined workload under recorded conditions. Python benchmarks use [pytest-benchmark](https://pytest-benchmark.readthedocs.io/en/latest/usage.html) for callable measurements within pytest suites and [pyperf](https://pyperf.readthedocs.io/en/latest/cli.html) for calibrated measurements across worker processes.

This skill guides workload design, correctness validation, and baseline comparison. Latency measures elapsed time per operation; throughput measures completed work per unit time. Traced Python allocations and total process memory are distinct measurements.

- [1. Benefits](#1-benefits)
- [2. Principles](#2-principles)
  - [2.1. FIRST](#21-first)
- [3. Patterns](#3-patterns)
  - [3.1. Workload Design](#31-workload-design)
  - [3.2. Measurement Techniques](#32-measurement-techniques)
- [4. Workflow](#4-workflow)
- [5. Commands](#5-commands)
- [6. Style Guide](#6-style-guide)
- [7. Templates](#7-templates)
  - [7.1. Table-Driven Benchmark](#71-table-driven-benchmark)
  - [7.2. Mutating Operation](#72-mutating-operation)
  - [7.3. Separate Allocation Measurement](#73-separate-allocation-measurement)
- [8. References](#8-references)

## 1. Benefits

Benchmarks provide comparative evidence when the workload, environment, and measured boundary remain consistent.

- Optimization Evidence
  > Recorded execution costs inform optimization decisions for the measured workload.

- Regression Detection
  > Comparable workloads and retained baselines expose changes in execution cost.

- Cost Attribution
  > Explicit measurement boundaries distinguish algorithmic work from setup, cache effects, and instrumentation overhead.

## 2. Principles

Benchmark design combines repeatable work with sufficient sampling and independent correctness checks.

### 2.1. FIRST

FIRST groups five test-design properties: Fast, Independent, Repeatable, Self-Validating, and Timely. Benchmark design applies these properties to the workload and the measurement process.

- Fast
  > A bounded suite collects enough repeated samples to assess variation within the available execution budget.

- Independent
  > Mutable inputs reset between invocations, and benchmark workers avoid competing workloads.

- Repeatable
  > Recorded interpreter, dependencies, hardware, runtime settings, and input data support comparable measurements.

- Self-Validating
  > Correctness assertions outside the measured operation verify the workload's result.

- Timely
  > Baseline measurements precede implementation changes intended to improve performance.

## 3. Patterns

Workload-design patterns specify the operation and its inputs. Measurement techniques determine how execution cost is sampled or attributed.

### 3.1. Workload Design

The following patterns vary workload scope, comparison, input distribution, or state ownership.

| Pattern | Application |
| --- | --- |
| Microbenchmark | Measure a small, isolated operation with a defined boundary. |
| Comparative Benchmark | Measure the same workload and environment before and after a change. |
| Table-Driven Workload | Parametrize representative sizes, shapes, and distributions with stable case identifiers. |
| Stateful Operation | Recreate state outside timing for each measured invocation, or explicitly measure setup as part of the workload. |

### 3.2. Measurement Techniques

Timing samples quantify elapsed cost; CPU and allocation profiles attribute costs in separate instrumented runs. CPU denotes the central processing unit.

| Technique | Application |
| --- | --- |
| Callable Timing | Use pytest-benchmark for an isolated callable within an existing pytest suite. |
| Process-Isolated Timing | Use pyperf for calibrated runs across worker processes. |
| CPU Profiling | Use [cProfile](https://docs.python.org/3/library/profile.html) to locate execution costs separately from latency measurements. |
| Allocation Tracing | Use [tracemalloc](https://docs.python.org/3/library/tracemalloc.html) to inspect traced Python allocations separately from latency measurements. |

## 4. Workflow

The workflow establishes a correct workload and baseline before measuring a candidate change under comparable conditions.

1. Inspect the project's supported interpreters, dependency manager, benchmark suite, continuous integration (CI) runners, and existing baselines. Select the existing tool where possible; add optional development dependencies only as needed.
2. Define the operation, unit of work, input distribution, size range, cache state, and metric. Decide whether startup, imports, serialization, input/output (I/O), and cleanup belong inside the measured boundary.
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

These conventions preserve equivalent work across repeated invocations and make measurement limits explicit.

- Naming
  > Use `test_<operation>` under the existing benchmark directory so pytest discovers the benchmark fixture.

- Callable Invocation
  > Pass a callable and its arguments to `benchmark`; do not call the operation before passing it. Assert the returned result outside the measured callable.

- Measurement Boundary
  > Keep input generation, unrelated validation, printing, and logging outside timing unless they are part of the defined workload.

- Mutable State
  > Use `benchmark.pedantic` with a setup callback and `iterations=1` so each measured invocation receives fresh state.

- Garbage Collection
  > Explicitly choose and record garbage collection (GC) behavior; defaults differ between tools. Do not disable GC merely to improve reported numbers when collection is part of the production workload.

- Environment Metadata
  > Record the Python implementation and version, build mode, operating system, CPU, and relevant native-library thread counts. Do not attribute differences across interpreter versions or machines solely to a code change.

- Asynchronous Completion
  > Do not pass a coroutine directly to a synchronous benchmark fixture: that measures coroutine creation. Use an async-aware harness or a documented wrapper that awaits completion, declaring whether event-loop startup is included.

- Memory Scope
  > Profile memory separately from latency. `tracemalloc` measures traced allocations, not all native memory or total resident set size. Use an appropriate process-memory tool for those questions.

- Result Interpretation
  > Treat differences within measurement noise as inconclusive. Report distributions and practical effect sizes instead of selecting only the fastest run.

## 7. Templates

These runnable examples use sorting to demonstrate immutable and mutable workloads. Replace sorting with the actual hot path and preserve meaningful validation.

### 7.1. Table-Driven Benchmark

The benchmark holds immutable inputs constant across invocations and validates each returned result outside timing. Save the example as `benchmarks/test_sort.py`.

Example:

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

Example:

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

Example:

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

- pytest-benchmark [Usage](https://pytest-benchmark.readthedocs.io/en/latest/usage.html) documentation.
- pytest-benchmark [Pedantic Mode](https://pytest-benchmark.readthedocs.io/en/latest/pedantic.html) documentation.
- pyperf [Commands](https://pyperf.readthedocs.io/en/latest/cli.html) documentation.
- pyperf [Running Benchmarks](https://pyperf.readthedocs.io/en/latest/run_benchmark.html) documentation.
- Python Software Foundation [Profiling](https://docs.python.org/3/library/profile.html) documentation.
- Python Software Foundation [tracemalloc](https://docs.python.org/3/library/tracemalloc.html) documentation.
- Python Software Foundation [timeit](https://docs.python.org/3/library/timeit.html) documentation.
