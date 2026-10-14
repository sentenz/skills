---
name: cpp-benchmark-testing
description: Automates benchmark test creation for C++ projects using Google Benchmark with consistent software testing patterns. Use when creating performance benchmarks, profiling tests, or when the user mentions benchmarking, Google Benchmark, or performance testing.
metadata:
  version: "1.2.0"
  activation:
    implicit: true
    priority: 2
    triggers:
      - "benchmark"
      - "benchmarking"
      - "google benchmark"
      - "performance test"
      - "profiling"
      - "microbenchmark"
    match:
      languages: ["cpp", "c", "c++"]
      paths: ["src/**/*_bench.cpp", "tests/**/*_bench.cpp", "bench/**/*.cpp", "benchmark/**/*.cpp"]
      prompt_regex: "(?i)(benchmark|benchmarking|performance test|profiling|microbenchmark|google benchmark)"
  usage:
    load_on_prompt: true
    autodispatch: true
---

# Benchmark Testing

Create C++ performance benchmarks with Google Benchmark. Inspect existing build targets, dependency revisions, benchmark conventions, and baselines before adding a harness. Treat workload selection as test design and distinguish measured evidence from optimization hypotheses.

- [1. Benefits](#1-benefits)
- [2. Principles](#2-principles)
  - [2.1. FIRST](#21-first)
- [3. Testing Patterns](#3-testing-patterns)
- [4. Test Design](#4-test-design)
- [5. Workflow](#5-workflow)
- [6. Commands](#6-commands)
- [7. Style Guide](#7-style-guide)
- [8. Template](#8-template)
- [9. References](#9-references)

## 1. Benefits

- Performance Measurement
  > Measure representative operation costs.

- Comparative Analysis
  > Compare implementation changes.

- Regression Detection
  > Detect performance regressions.

- Correctness Baseline
  > Establish correctness with unit tests before interpreting timing results.

## 2. Principles

### 2.1. FIRST

The `FIRST` principles for benchmark testing focus on reliable and meaningful measurements.

- Fast
  > Keep setup bounded to support practical measurement runs.

- Independent
  > Keep workloads isolated from shared state and other measurements.

- Repeatable
  > Keep measurement conditions repeatable across runs.

- Self-Validating
  > Check results independently before interpreting measurements.

- Timely
  > Establish baselines before optimization.

Do not turn an unstable one-shot timing measurement into a correctness assertion.

## 3. Testing Patterns

| Pattern                | Application                                                                              |
| ---------------------- | ---------------------------------------------------------------------------------------- |
| Table-Driven Workloads | Register named sizes, shapes, distributions, and relevant cache states.                  |
| Benchmark Fixtures     | Manage shared setup and cleanup explicitly; restore equivalent state for each operation. |
| Grouped Benchmarks     | Keep comparable variants discoverable and retain separate results.                       |

> [!NOTE]
> Use Arrange-Act-Assert in companion correctness tests. In the benchmark, distinguish setup, measured work, and result consumption; do not automatically time all three.

## 4. Test Design

| Technique                       | Application                                                                            |
| ------------------------------- | -------------------------------------------------------------------------------------- |
| Microbenchmarking               | Measure one focused operation with an explicit unit of work.                           |
| Comparative Benchmarking        | Compare baseline and candidate with identical workloads and settings.                  |
| Boundary Workloads              | Include representative small, typical, and large inputs with explicit resource limits. |
| Repeated Measurements           | Inspect variation across repetitions before interpreting a change.                     |
| Performance Regression Analysis | Apply established project thresholds to comparable measurements.                       |

> [!NOTE]
> Measure CPU cost, elapsed latency, and memory behavior according to the question. Run profiling separately when instrumentation would distort timing. Decide whether allocation, copying, setup, and cleanup belong to the measured operation before writing the harness.

## 5. Workflow

1. Inspect Infrastructure

    Inspect the project toolchain, Google Benchmark revision, build tasks, and available benchmark runners.

2. Define Workload

    Define the operation, input distribution, size range, cache state, metric, and measured boundary.

3. Validate Correctness

    Verify correctness independently. Avoid benchmarking an implementation whose output is not checked elsewhere.

4. Register with CMake

    Add a target using the existing dependency setup. For a standalone CMake target, link `benchmark::benchmark_main`; if supplying a custom main, link `benchmark::benchmark` instead. Do not provide both mains.

5. Configure Build

    Build with representative optimization settings. Keep sanitizers, coverage collection, debugging, and profiling out of ordinary comparison runs unless their overhead is the explicit subject.

6. Collect Measurements

    Run a short harness check, then collect repeated baseline and candidate measurements under comparable conditions. Retain raw results and environment details.

7. Evaluate Results

    Examine dispersion, background load, and anomalies. Investigate unstable results before claiming a speedup or applying a performance gate.

8. Report Results

    Report commands, commit IDs, compiler flags, workload, machine details, measurement units, variation, and limitations.

## 6. Commands

Use existing project tasks when present. These examples assume an already configured CMake target named `sort_benchmark`; adapt its name and output location.

```bash
cmake -S . -B build/benchmark -DCMAKE_BUILD_TYPE=Release
cmake --build build/benchmark --target sort_benchmark
./build/benchmark/sort_benchmark --benchmark_filter=BM_Sort \
  --benchmark_repetitions=5 \
  --benchmark_out=benchmark-results.json --benchmark_out_format=json
```

Run the same workload on the baseline and candidate builds, with distinct output files. Verify flags against the pinned library version. Keep correctness tests and benchmarks as separate commands.

## 7. Style Guide

- Timing Boundaries
  > Exclude setup only when it is outside the stated operation; use `PauseTiming()` and `ResumeTiming()` around per-iteration resets where appropriate.

- Mutable Inputs
  > Recreate mutated inputs before every measured invocation; repeatedly sorting an already sorted vector changes the workload.

- Result Observability
  > Make results observable with `DoNotOptimize` and use `ClobberMemory` where applicable. These helpers do not guarantee that the intended operation cannot be optimized; inspect suspicious measurements.

- Harness Overhead
  > Account for harness overhead on very small operations. Keep input preparation deterministic.

- Target Platform
  > Do not infer embedded-target timing from host measurements; state the measured platform.

## 8. Template

This harness measures sorting a fresh descending vector at each size. Allocation, input copying, and destruction are outside timing. Replace the operation and distributions with production-representative workloads and validate correctness separately.

```cpp
#include <benchmark/benchmark.h>

#include <algorithm>
#include <numeric>
#include <vector>

static void BM_Sort(benchmark::State& state) {
  std::vector<int> seed(static_cast<std::size_t>(state.range(0)));
  std::iota(seed.rbegin(), seed.rend(), 0);

  for (auto _ : state) {
    state.PauseTiming();
    {
      auto values = seed;
      auto* data = values.data();
      benchmark::DoNotOptimize(data);
      state.ResumeTiming();
      std::sort(values.begin(), values.end());
      benchmark::ClobberMemory();
      state.PauseTiming();
    }
    state.ResumeTiming();
  }
}

BENCHMARK(BM_Sort)->Arg(16)->Arg(256)->Arg(4096);
```

Link this file with `benchmark::benchmark_main`. Add separately named random, duplicate-heavy, or already sorted workloads only when relevant to the performance question. Do not compare unlike distributions as if they measured the same workload.

## 9. References

- Google Benchmark [User Guide](https://google.github.io/benchmark/user_guide.html).
- Google Benchmark [Build and Usage](https://github.com/google/benchmark#usage).
