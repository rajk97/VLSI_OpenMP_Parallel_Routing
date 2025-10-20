#!/usr/bin/env python3
"""
Generate speedup graphs for VLSI Wire Routing Assignment
Plots Total Speedup and Computation Speedup vs Number of Processors
"""

import matplotlib.pyplot as plt
import numpy as np

# Data from benchmarks (medium_4096.txt, across-wire mode)
# Based on results from medium_calculateRouteCost_Optimized with Tracy
threads = np.array([1, 2, 4, 8])

# Times with Tracy enabled (from speedup_summary.txt)
computation_time_tracy = np.array([24.5521825440, 15.9456518770, 6.7549419700, 3.7531591590])
# Assuming initialization time is approximately constant (~0.03s based on recent run)
init_time = 0.03
total_time_tracy = computation_time_tracy + init_time

# Calculate speedups
computation_speedup = computation_time_tracy[0] / computation_time_tracy
total_speedup = total_time_tracy[0] / total_time_tracy

# Calculate ideal (linear) speedup
ideal_speedup = threads

# Calculate efficiency
computation_efficiency = (computation_speedup / threads) * 100

# Create figure with two subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Plot 1: Speedup curves
ax1.plot(threads, total_speedup, 'o-', linewidth=2, markersize=8, label='Total Speedup', color='#2E86AB')
ax1.plot(threads, computation_speedup, 's-', linewidth=2, markersize=8, label='Computation Speedup', color='#A23B72')
ax1.plot(threads, ideal_speedup, '--', linewidth=2, label='Ideal (Linear) Speedup', color='#F18F01', alpha=0.7)

ax1.set_xlabel('Number of Processors', fontsize=12, fontweight='bold')
ax1.set_ylabel('Speedup', fontsize=12, fontweight='bold')
ax1.set_title('Speedup vs Number of Processors\n(medium_4096.txt, Across-Wire Mode)', fontsize=13, fontweight='bold')
ax1.grid(True, alpha=0.3, linestyle='--')
ax1.legend(fontsize=10, loc='upper left')
ax1.set_xticks(threads)
ax1.set_xlim(0.5, 8.5)
ax1.set_ylim(0, 9)

# Add speedup values as annotations
for i, (t, cs, ts) in enumerate(zip(threads, computation_speedup, total_speedup)):
    ax1.annotate(f'{cs:.2f}x', xy=(t, cs), xytext=(5, 5), textcoords='offset points', 
                fontsize=9, color='#A23B72', fontweight='bold')
    ax1.annotate(f'{ts:.2f}x', xy=(t, ts), xytext=(5, -15), textcoords='offset points', 
                fontsize=9, color='#2E86AB', fontweight='bold')

# Plot 2: Efficiency
ax2.plot(threads, computation_efficiency, 'o-', linewidth=2, markersize=8, color='#C73E1D')
ax2.axhline(y=100, linestyle='--', color='#F18F01', linewidth=2, alpha=0.7, label='Ideal (100%)')
ax2.axhline(y=75, linestyle=':', color='gray', linewidth=1, alpha=0.5)
ax2.axhline(y=50, linestyle=':', color='gray', linewidth=1, alpha=0.5)

ax2.set_xlabel('Number of Processors', fontsize=12, fontweight='bold')
ax2.set_ylabel('Parallel Efficiency (%)', fontsize=12, fontweight='bold')
ax2.set_title('Parallel Efficiency vs Number of Processors\n(medium_4096.txt, Across-Wire Mode)', fontsize=13, fontweight='bold')
ax2.grid(True, alpha=0.3, linestyle='--')
ax2.legend(fontsize=10)
ax2.set_xticks(threads)
ax2.set_xlim(0.5, 8.5)
ax2.set_ylim(0, 110)

# Add efficiency values as annotations
for i, (t, eff) in enumerate(zip(threads, computation_efficiency)):
    ax2.annotate(f'{eff:.1f}%', xy=(t, eff), xytext=(5, 5), textcoords='offset points', 
                fontsize=9, color='#C73E1D', fontweight='bold')

plt.tight_layout()
plt.savefig('speedup_analysis.png', dpi=300, bbox_inches='tight')
print("Graph saved as: speedup_analysis.png")

# Print summary statistics
print("\n" + "="*60)
print("SPEEDUP SUMMARY (medium_4096.txt, Across-Wire Mode)")
print("="*60)
print(f"{'Threads':<10} {'Comp Time (s)':<15} {'Comp Speedup':<15} {'Efficiency (%)':<15}")
print("-"*60)
for i, t in enumerate(threads):
    print(f"{t:<10} {computation_time_tracy[i]:<15.2f} {computation_speedup[i]:<15.2f} {computation_efficiency[i]:<15.1f}")

print("\n" + "="*60)
print("OBSERVATIONS:")
print("="*60)
print(f"• Best speedup achieved: {computation_speedup[-1]:.2f}x on {threads[-1]} threads")
print(f"• Parallel efficiency at 2 threads: {computation_efficiency[1]:.1f}%")
print(f"• Parallel efficiency at 4 threads: {computation_efficiency[2]:.1f}%")
print(f"• Parallel efficiency at 8 threads: {computation_efficiency[3]:.1f}%")
print(f"\n• Efficiency drop from 4 to 8 threads: {computation_efficiency[2] - computation_efficiency[3]:.1f}%")
print("  → Likely causes: Memory bandwidth saturation, cache coherence overhead")
print("  → L3 cache capacity (36 MB) exceeded by working set (~64 MB for 8 threads)")

# Don't show interactive plot in headless mode
# plt.show()
