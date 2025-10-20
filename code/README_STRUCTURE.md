# Code Directory Structure

## Overview
This directory contains the VLSI wire routing parallel implementation with organized experiments, results, and documentation.

---

## 📁 Directory Structure

```
code/
├── README_STRUCTURE.md          # This file
│
├── 📂 Core Implementation
│   ├── wireroute.cpp            # Main parallel wire router implementation
│   ├── wireroute.h              # Header file
│   ├── wireroute                # Compiled binary
│   ├── wireroute.o              # Object file
│   ├── Makefile                 # Build configuration
│   ├── validate.cpp             # Solution validator
│   ├── validate.o               # Validator object
│   ├── validate.py              # Python validator
│   └── WireGrapher.java         # Visualization tool
│
├── 📂 inputs/                   # Test input files
│   ├── testinput/               # Basic test cases
│   ├── timeinput/               # Performance benchmarks
│   └── problemsize/             # Sensitivity studies
│       ├── gridsize/            # Grid size variations
│       └── numwires/            # Wire count variations
│
├── 📂 scripts/
│   ├── experiments/             # Experiment automation scripts
│   │   ├── test_sa_probability.sh      # SA parameter sensitivity
│   │   ├── test_problem_size.sh        # Problem size sensitivity
│   │   ├── test_batch_sizes.sh         # Batch size experiments
│   │   └── collect_cache_misses.sh     # Cache analysis collection
│   │
│   └── visualization/           # Plotting scripts
│       ├── plot_speedup.py              # Speedup graphs
│       ├── plot_sa_probability.py      # SA sensitivity plots
│       ├── plot_problem_size.py        # Problem size plots
│       ├── plot_batch_sensitivity.py   # Batch size plots
│       └── plot_cache_misses.py        # Cache analysis plots
│
├── 📂 results/                  # Experimental results
│   ├── speedup_analysis.png     # Main speedup graph
│   │
│   ├── cache_analysis/          # Cache miss analysis
│   │   ├── cache_miss_analysis.png
│   │   └── cache_misses_data.txt
│   │
│   ├── batch_sensitivity/       # Batch size experiments
│   │   ├── batch_sensitivity_analysis.png
│   │   ├── batch_*.log          # Individual experiment logs
│   │   └── summary.txt
│   │
│   ├── sa_probability/          # SA probability sensitivity
│   │   ├── sa_probability_sensitivity.png
│   │   ├── p_*_threads_*.log    # Individual experiment logs
│   │   └── summary.txt
│   │
│   └── problem_size/            # Problem size sensitivity
│       ├── problem_size_sensitivity.png
│       ├── gridsize_*.log       # Grid size experiments
│       ├── numwires_*.log       # Wire count experiments
│       └── summary.txt
│
├── 📂 outputs/                  # Generated routing solutions
│   ├── routes/                  # Route files (routes_*.txt)
│   └── occupancy/               # Occupancy files (occupancy_*.txt)
│
├── 📂 docs/
│   ├── analysis/                # Comprehensive analysis documents
│   │   ├── SENSITIVITY_STUDIES_RESULTS.md    # Detailed analysis
│   │   └── SENSITIVITY_QUICK_REFERENCE.md    # Quick summary
│   │
│   └── guides/                  # Technical guides
│       ├── BATCHING_EXPLAINED.md
│       ├── BATCH_SENSITIVITY_RESULTS.md
│       ├── BATCH_SENSITIVITY_SUMMARY.md
│       ├── CACHE_MISS_GUIDE.md
│       ├── FALSE_SHARING_EXPLAINED.md
│       ├── IMPLEMENTATION_COMPLETE.md
│       ├── QUICK_REFERENCE.md
│       └── RESULTS_SUMMARY.md
│
└── 📂 old_files/                # Archived/deprecated files
    ├── Makefile.optimized
    ├── Makefile.original
    ├── wireroute.baseline
    ├── TracyClient.cpp
    ├── tracy_example.cpp
    ├── *.sh (old scripts)
    └── *.md (old documentation)
```

---

## 🚀 Quick Start

### Build the Project
```bash
make
```

### Run Wire Router
```bash
# Basic run
./wireroute -f inputs/timeinput/medium_4096.txt -n 8 -i 5 -m A

# With custom parameters
./wireroute -f <input> -n <threads> -i <iterations> -m <mode> -b <batch_size> -p <sa_prob>
```

### Run Experiments
```bash
# SA probability sensitivity
cd scripts/experiments && ./test_sa_probability.sh

# Problem size sensitivity
cd scripts/experiments && ./test_problem_size.sh

# Batch size sensitivity
cd scripts/experiments && ./test_batch_sizes.sh

# Cache miss analysis
cd scripts/experiments && ./collect_cache_misses.sh
```

### Generate Visualizations
```bash
cd scripts/visualization

# Generate speedup plots
python3 plot_speedup.py

# Generate SA probability plots
python3 plot_sa_probability.py

# Generate problem size plots
python3 plot_problem_size.py

# Generate batch sensitivity plots
python3 plot_batch_sensitivity.py

# Generate cache analysis plots
python3 plot_cache_misses.py
```

---

## 📊 Key Results Summary

### Speedup Analysis
- **Baseline**: 6.54x speedup on 8 threads (81.8% efficiency)
- **File**: `results/speedup_analysis.png`

### Cache Behavior
- **Exceptional**: 28% DECREASE in cache misses with parallelization
- **File**: `results/cache_analysis/cache_miss_analysis.png`

### SA Probability Sensitivity
- **Range**: 7.69x - 8.12x speedup (P = 0.01, 0.1, 0.5)
- **Best**: P=0.5 achieves 101.5% super-linear efficiency
- **File**: `results/sa_probability/sa_probability_sensitivity.png`

### Problem Size Sensitivity
- **Grid Size**: 7.13x → 7.97x (larger grids scale better)
- **Wire Count**: 6.18x → 7.53x (more wires scale better)
- **File**: `results/problem_size/problem_size_sensitivity.png`

### Batch Size Sensitivity
- **Finding**: batch_size=1 (dynamic scheduling) is optimal
- **Reason**: Load imbalance dominates synchronization overhead
- **File**: `results/batch_sensitivity/batch_sensitivity_analysis.png`

---

## 📖 Documentation

### For Assignment Writeup
- **Quick Reference**: `docs/analysis/SENSITIVITY_QUICK_REFERENCE.md`
- **Detailed Analysis**: `docs/analysis/SENSITIVITY_STUDIES_RESULTS.md`

### Technical Guides
- **Batching Strategy**: `docs/guides/BATCHING_EXPLAINED.md`
- **Cache Analysis**: `docs/guides/CACHE_MISS_GUIDE.md`
- **False Sharing**: `docs/guides/FALSE_SHARING_EXPLAINED.md`
- **Implementation**: `docs/guides/IMPLEMENTATION_COMPLETE.md`

---

## 🗂️ File Naming Conventions

### Input Files
- `circuit_<grid>x<grid>_<wires>.txt` - Basic test cases
- `easy/medium/hard_<size>.txt` - Difficulty-based tests
- `hard_<grid>_<wires>.txt` - Problem size variations

### Output Files
- `routes_<test>_<threads>.txt` - Routing solutions
- `occupancy_<test>_<threads>.txt` - Grid occupancy maps

### Log Files
- `batch_<size>.log` - Batch size experiment results
- `p_<prob>_threads_<n>.log` - SA probability results
- `gridsize_<size>_threads_<n>.log` - Grid size results
- `numwires_<count>_threads_<n>.log` - Wire count results

---

## 🧹 Maintenance

### Clean Build
```bash
make clean
```

### Regenerate All Results
```bash
# Run all experiments
cd scripts/experiments
./test_sa_probability.sh
./test_problem_size.sh
./test_batch_sizes.sh
./collect_cache_misses.sh

# Generate all plots
cd ../visualization
python3 plot_speedup.py
python3 plot_sa_probability.py
python3 plot_problem_size.py
python3 plot_batch_sensitivity.py
python3 plot_cache_misses.py
```

### Archive Old Files
Old/deprecated files are automatically moved to `old_files/` directory.
These can be deleted if no longer needed.

---

## 📝 Notes

- All experiments use **across-wire parallelization** (mode A)
- Default batch size is 1 (dynamic scheduling)
- Default SA probability is 0.1
- All graphs are generated in PNG format at 300 DPI
- Result summaries are automatically generated in each result directory

---

## ✅ Status

- ✅ Core implementation complete
- ✅ All sensitivity studies complete
- ✅ Comprehensive analysis documented
- ✅ All graphs generated
- ✅ Directory structure organized
- ✅ Ready for writeup and submission

---

**Last Updated**: October 20, 2025
**Branch**: across-wire
**Commit**: Latest sensitivity studies
