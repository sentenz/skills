---
name: go-benchmark-testing
description: Automates benchmark test creation for Go projects using the standard testing package with consistent software testing patterns. Use when creating performance benchmarks, profiling tests, or when the user mentions benchmarking, performance testing, or optimization.
metadata:
  version: "1.1.0"
  activation:
    implicit: true
    priority: 2
    triggers:
      - "benchmark"
      - "benchmarking"
      - "performance test"
      - "profiling"
      - "microbenchmark"
      - "optimization"
      - "performance"
    match:
      languages: ["go", "golang"]
      paths: ["pkg/**/*_test.go", "internal/**/*_test.go"]
      prompt_regex: "(?i)(benchmark|benchmarking|performance test|profiling|microbenchmark|optimization|performance)"
  usage:
    load_on_prompt: true
    autodispatch: true
---

# Benchmark Testing

Instructions for AI coding agents on automating benchmark test creation using consistent software testing patterns in this Go project.

- [1. Benefits](#1-benefits)
- [2. Principles](#2-principles)
  - [2.1. FIRST](#21-first)
- [3. Testing Patterns](#3-testing-patterns)
- [4. Test Design](#4-test-design)
  - [4.1. Microbenchmarking](#41-microbenchmarking)
  - [4.2. Comparative Benchmarking](#42-comparative-benchmarking)
  - [4.3. Memory Profiling](#43-memory-profiling)
  - [4.4. Statistical Benchmarking](#44-statistical-benchmarking)
- [5. Workflow](#5-workflow)
- [6. Commands](#6-commands)
- [7. Style Guide](#7-style-guide)
- [8. Template](#8-template)
  - [8.1. Multi-Scenario Benchmarks](#81-multi-scenario-benchmarks)
  - [8.2. Simple Benchmarks](#82-simple-benchmarks)
  - [8.3. Benchmarks with Validation](#83-benchmarks-with-validation)
- [9. References](#9-references)

## 1. Benefits

- Performance Measurement
  > Benchmark tests measure the execution time and memory allocation of functions, providing quantifiable metrics for performance analysis.

- Regression Detection
  > Continuous benchmarking helps identify performance regressions early in the development cycle before they reach production.

- Optimization Guidance
  > Benchmark results guide optimization efforts by identifying bottlenecks and quantifying the impact of performance improvements.

- Comparative Analysis
  > Benchmarks enable comparison of different implementations or algorithms to make informed decisions about performance trade-offs.

- Resource Profiling
  > Memory allocation tracking helps identify unnecessary allocations and optimize memory usage patterns.

## 2. Principles

### 2.1. FIRST

The `FIRST` principles for benchmark testing focus on creating reliable and meaningful measurements.

- Fast
  > Benchmark setup and teardown should be minimal and excluded from timing to ensure accurate measurement of the function under test.

- Independent
  > Each benchmark should be self-contained and not depend on shared state or results from other benchmarks to ensure isolated performance measurements.

- Repeatable
  > Benchmarks should produce consistent, comparable results across runs and environments by controlling inputs and avoiding non-deterministic operations.

- Self-Validating
  > Benchmarks should optionally validate results to prevent the compiler from optimizing away the code under measurement.

- Timely
  > Benchmarks should be established before optimization work begins to provide a performance baseline and measure the impact of changes.

## 3. Testing Patterns

Use patterns to organize repeated measurements; use Test Design to define the workload, measurement boundary, and comparison.

| Pattern                | Application                                                                             |
| ---------------------- | --------------------------------------------------------------------------------------- |
| Table-Driven Workloads | Reuse benchmark logic across named input sizes, shapes, and distributions.              |
| Benchmark Fixtures     | Own setup and cleanup explicitly; restore equivalent state for each measured operation. |
| Grouped Benchmarks     | Keep related workload variants discoverable without mixing their results.               |

FIRST describes isolation and repeatability. Microbenchmarks, comparative measurements, and profiling answer performance questions rather than define assertion structure.

## 4. Test Design

### 4.1. Microbenchmarking

Microbenchmarking is a software testing technique that measures the performance of small, isolated code units to identify performance characteristics and bottlenecks.

### 4.2. Comparative Benchmarking

Comparative Benchmarking is a testing approach that compares the performance of different implementations or algorithms side-by-side using consistent workloads.

### 4.3. Memory Profiling

Memory Profiling is the process of measuring memory allocations and usage patterns during benchmark execution using `-benchmem` flag.

### 4.4. Statistical Benchmarking

Statistical Benchmarking uses multiple iterations to calculate statistical measures (mean, variance) to ensure reliable and reproducible results.

## 5. Workflow

1. Identify

    Identify performance-critical functions in `pkg/` or `internal/` that benefit from performance tracking (e.g., `pkg/<package>/<file>.go`).

2. Add/Create

    Create benchmark tests in the same package (e.g., `pkg/<package>/<file>_test.go`).

3. Benchmark Test Coverage Requirements

    Focus on functions that:
    - Are called frequently in hot paths
    - Perform mathematical operations or calculations
    - Process data structures or collections
    - Have multiple implementation approaches to compare
    - Are candidates for optimization

4. Apply Templates

    Structure all benchmark tests using the [template](#8-template) pattern.

5. Baseline Measurements

    Establish performance baselines by running benchmarks on stable code before making changes.

## 6. Commands

Verify that the listed Make targets exist in the current project. Reuse its configured build and test tasks; do not assume these example targets are available.

1. Make Tasks

    | Tasks                | Description                                   |
    | -------------------- | --------------------------------------------- |
    | `make go-test-bench` | Execute all benchmarks with memory statistics |

2. Command Instructions

    | Instructions                                                    | Description                                        |
    | --------------------------------------------------------------- | -------------------------------------------------- |
    | `go test -bench=BenchmarkPercent -benchmem ./pkg/percent`       | Execute a specific benchmark function              |
    | `go test -bench=. -benchmem -cpuprofile=cpu.prof ./pkg/percent` | Generate CPU profile for performance analysis      |
    | `go test -bench=. -benchmem -memprofile=mem.prof ./pkg/percent` | Generate memory profile for allocation analysis    |
    | `go test -bench=. -benchtime=10s ./pkg/percent`                 | Run benchmarks for a specific duration             |
    | `benchstat old.txt new.txt`                                     | Compare benchmark results before and after changes |

## 7. Style Guide

- Test Framework
  > Use the standard Go `testing` package with `testing.B` for benchmark tests.

- Include Imports
  > Include `testing` and any packages needed for the function under test.

- Benchmark Function Naming
  > Name benchmark functions with the `Benchmark` prefix followed by the function name (e.g., `BenchmarkPercent` for testing `Percent()`).

- Benchmark Loop
  > Use `b.Loop()` to control the number of iterations. The testing framework automatically adjusts the loop iterations to get reliable timing measurements. `b.Loop()` is preferred over `b.N` as it provides better integration with the testing framework and more accurate measurements. Unlike `b.N`-style benchmarks, `b.Loop()` integrates timer management, it automatically handles `b.ResetTimer()` at the loop's start and `b.StopTimer()` at its end, eliminating the need to manually manage the benchmark timer for setup and cleanup code.

- Timer Control
  > When using `b.Loop()`, timer management is automatic and no manual `b.ResetTimer()`, `b.StopTimer()`, or `b.StartTimer()` calls are needed for typical benchmarks. For advanced scenarios not using `b.Loop()`, use `b.ResetTimer()` to exclude setup time from measurements and `b.StopTimer()`/`b.StartTimer()` to exclude specific operations.

- Sub-benchmarks
  > Use `b.Run()` to organize related benchmark cases with different input scenarios. Each sub-benchmark runs independently with its own `b.N` iterations.

- Memory Reporting
  > Use `b.ReportAllocs()` to report memory allocations per operation when not using `-benchmem` flag.

- Result Validation
  > Optionally validate results in benchmarks to prevent compiler optimizations from eliminating dead code.

## 8. Template

Use this template for new benchmark test functions. Replace placeholders with actual values and adjust as needed for the use case.

### 8.1. Multi-Scenario Benchmarks

For benchmarking multiple scenarios or input variations, use sub-benchmarks with table-driven approach.

```go
func Benchmark<FunctionName>(b *testing.B) {
	// Define benchmark cases with different scenarios
	benchmarks := []struct {
		name   string
		param1 <type>
		param2 <type>
		// Add more parameters as needed
	}{
		{
			name:   "scenario description 1",
			param1: <value1>,
			param2: <value2>,
		},
		{
			name:   "scenario description 2",
			param1: <value1>,
			param2: <value2>,
		},
		// Add more benchmark cases
	}

	for _, bm := range benchmarks {
		b.Run(bm.name, func(b *testing.B) {
			// Arrange
			// Setup code here (automatically excluded from timing by b.Loop)

			// Act
			for b.Loop() {
				_, _ = <Function>(bm.param1, bm.param2)
			}
		})
	}
}
```

### 8.2. Simple Benchmarks

For benchmarking a single scenario, use a simple loop without sub-benchmarks.

```go
func Benchmark<FunctionName>(b *testing.B) {
	// Arrange
	// Setup code here (automatically excluded from timing by b.Loop)
	param1 := <value1>
	param2 := <value2>

	// Act
	for b.Loop() {
		_, _ = <Function>(param1, param2)
	}
}
```

### 8.3. Benchmarks with Validation

For benchmarks that need to prevent compiler optimizations, store results in package-level variables.

```go
var (
	benchResult <type>
	benchError  error
)

func Benchmark<FunctionName>(b *testing.B) {
	// Arrange
	// Setup code here (automatically excluded from timing by b.Loop)
	param1 := <value1>
	param2 := <value2>

	// Act
	for b.Loop() {
		benchResult, benchError = <Function>(param1, param2)
	}
}
```

## 9. References

- Go [Benchmarks](https://pkg.go.dev/testing#hdr-Benchmarks) documentation.
- Go [testing.B](https://pkg.go.dev/testing#B) package documentation.
- Go [benchstat](https://pkg.go.dev/golang.org/x/perf/cmd/benchstat) tool documentation.
