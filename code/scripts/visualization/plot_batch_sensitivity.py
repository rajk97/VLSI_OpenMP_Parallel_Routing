#!/usr/bin/env python3
"""
Batch Size Sensitivity Analysis for VLSI Wire Routing
Analyzes performance vs quality tradeoff for different batch sizes
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import re
import os

def parse_batch_results(results_dir):
    """Parse batch experiment results"""
    batch_sizes = []
    comp_times = []
    total_costs = []
    max_occupancies = []
    
    # Expected batch sizes
    test_batches = [1, 5, 10, 25, 50, 100]
    
    for batch in test_batches:
        log_file = os.path.join(results_dir, f'batch_{batch}.log')
        if not os.path.exists(log_file):
            print(f"Warning: {log_file} not found, skipping...")
            continue
            
        with open(log_file, 'r') as f:
            content = f.read()
        
        # Extract metrics
        comp_time_match = re.search(r'Computation time \(sec\): ([\d.]+)', content)
        total_cost_match = re.search(r'Total cost: (\d+)', content)
        max_occ_match = re.search(r'Max occupancy: (\d+)', content)
        
        if comp_time_match and total_cost_match and max_occ_match:
            batch_sizes.append(batch)
            comp_times.append(float(comp_time_match.group(1)))
            total_costs.append(int(total_cost_match.group(1)))
            max_occupancies.append(int(max_occ_match.group(1)))
    
    return (np.array(batch_sizes), 
            np.array(comp_times),
            np.array(total_costs),
            np.array(max_occupancies))

def plot_batch_analysis(batch_sizes, comp_times, total_costs, max_occupancies):
    """Generate comprehensive batch size analysis plots"""
    
    # Calculate speedups (relative to batch_size=1)
    baseline_time = comp_times[0]
    speedups = baseline_time / comp_times
    
    # Calculate relative cost increase
    baseline_cost = total_costs[0]
    cost_increase_pct = ((total_costs - baseline_cost) / baseline_cost) * 100
    
    # Create figure with 2x2 subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # ===== Plot 1: Computation Time vs Batch Size =====
    ax1.plot(batch_sizes, comp_times, 'o-', linewidth=2.5, markersize=10,
             color='#2E86AB', label='Computation Time')
    ax1.axhline(y=baseline_time, linestyle='--', color='#F18F01', 
                linewidth=2, alpha=0.7, label=f'Baseline (B=1): {baseline_time:.2f}s')
    
    ax1.set_xlabel('Batch Size', fontsize=13, fontweight='bold')
    ax1.set_ylabel('Computation Time (seconds)', fontsize=13, fontweight='bold')
    ax1.set_title('Computation Time vs Batch Size\n(medium_4096.txt, 8 threads)', 
                  fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.legend(fontsize=10)
    ax1.set_xscale('log')
    ax1.set_xticks(batch_sizes)
    ax1.set_xticklabels(batch_sizes)
    
    # Add value annotations
    for b, t in zip(batch_sizes, comp_times):
        ax1.annotate(f'{t:.2f}s', xy=(b, t), xytext=(0, 10),
                    textcoords='offset points', ha='center',
                    fontsize=9, color='#2E86AB', fontweight='bold')
    
    # ===== Plot 2: Speedup vs Batch Size =====
    ax2.plot(batch_sizes, speedups, 's-', linewidth=2.5, markersize=10,
             color='#A23B72', label='Speedup vs B=1')
    ax2.axhline(y=1.0, linestyle='--', color='#F18F01', 
                linewidth=2, alpha=0.7, label='No Improvement')
    
    ax2.set_xlabel('Batch Size', fontsize=13, fontweight='bold')
    ax2.set_ylabel('Speedup (relative to batch_size=1)', fontsize=13, fontweight='bold')
    ax2.set_title('Speedup from Batching\n(Higher = Faster)', 
                  fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.legend(fontsize=10)
    ax2.set_xscale('log')
    ax2.set_xticks(batch_sizes)
    ax2.set_xticklabels(batch_sizes)
    
    # Add speedup annotations
    for b, s in zip(batch_sizes, speedups):
        ax2.annotate(f'{s:.2f}x', xy=(b, s), xytext=(0, 10),
                    textcoords='offset points', ha='center',
                    fontsize=9, color='#A23B72', fontweight='bold')
    
    # ===== Plot 3: Total Cost vs Batch Size =====
    ax3.plot(batch_sizes, total_costs / 1000, '^-', linewidth=2.5, markersize=10,
             color='#D62828', label='Total Cost')
    ax3.axhline(y=baseline_cost / 1000, linestyle='--', color='#F18F01', 
                linewidth=2, alpha=0.7, label=f'Baseline (B=1): {baseline_cost:,}')
    
    ax3.set_xlabel('Batch Size', fontsize=13, fontweight='bold')
    ax3.set_ylabel('Total Cost (Thousands)', fontsize=13, fontweight='bold')
    ax3.set_title('Routing Quality vs Batch Size\n(Lower = Better Quality)', 
                  fontsize=14, fontweight='bold')
    ax3.grid(True, alpha=0.3, linestyle='--')
    ax3.legend(fontsize=10)
    ax3.set_xscale('log')
    ax3.set_xticks(batch_sizes)
    ax3.set_xticklabels(batch_sizes)
    
    # Add cost annotations
    for b, c in zip(batch_sizes, total_costs):
        ax3.annotate(f'{c:,}', xy=(b, c / 1000), xytext=(0, 10),
                    textcoords='offset points', ha='center',
                    fontsize=9, color='#D62828', fontweight='bold')
    
    # ===== Plot 4: Performance-Quality Tradeoff =====
    # Scatter plot: X = speedup, Y = cost increase %
    scatter = ax4.scatter(speedups, cost_increase_pct, c=batch_sizes, 
                         s=300, cmap='viridis', alpha=0.7, edgecolors='black', linewidth=2)
    
    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax4)
    cbar.set_label('Batch Size', fontsize=11, fontweight='bold')
    
    # Annotate each point with batch size
    for b, s, c in zip(batch_sizes, speedups, cost_increase_pct):
        ax4.annotate(f'B={b}', xy=(s, c), xytext=(5, 5),
                    textcoords='offset points', fontsize=10, fontweight='bold')
    
    # Mark the baseline
    ax4.plot(speedups[0], cost_increase_pct[0], 'r*', markersize=20, 
             label='Baseline (B=1)', zorder=5)
    
    ax4.set_xlabel('Speedup (relative to B=1)', fontsize=13, fontweight='bold')
    ax4.set_ylabel('Cost Increase (%)', fontsize=13, fontweight='bold')
    ax4.set_title('Performance-Quality Tradeoff\n(Bottom-Left = Best: Fast & High Quality)', 
                  fontsize=14, fontweight='bold')
    ax4.grid(True, alpha=0.3, linestyle='--')
    ax4.legend(fontsize=10)
    ax4.axhline(y=0, linestyle='--', color='gray', linewidth=1, alpha=0.5)
    
    # Add quadrant labels
    ax4.text(0.98, 0.98, 'Worse Performance\n& Quality',
             transform=ax4.transAxes, ha='right', va='top',
             fontsize=10, style='italic', alpha=0.5,
             bbox=dict(boxstyle='round', facecolor='red', alpha=0.1))
    ax4.text(0.98, 0.02, 'Better Performance\nWorse Quality',
             transform=ax4.transAxes, ha='right', va='bottom',
             fontsize=10, style='italic', alpha=0.5,
             bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.1))
    
    plt.tight_layout()
    plt.savefig('batch_sensitivity_analysis.png', dpi=300, bbox_inches='tight')
    print("✓ Graph saved as: batch_sensitivity_analysis.png")
    
    return speedups, cost_increase_pct

def print_analysis(batch_sizes, comp_times, speedups, total_costs, cost_increase_pct, max_occupancies):
    """Print detailed batch size analysis"""
    print("\n" + "="*80)
    print("BATCH SIZE SENSITIVITY ANALYSIS (medium_4096.txt, 8 threads)")
    print("="*80)
    print(f"{'Batch':<8} {'Time (s)':<12} {'Speedup':<12} {'Total Cost':<15} {'Cost +%':<12} {'Max Occ':<10}")
    print("-"*80)
    for i, b in enumerate(batch_sizes):
        print(f"{b:<8} {comp_times[i]:<12.2f} {speedups[i]:<12.2f} "
              f"{total_costs[i]:<15,} {cost_increase_pct[i]:<12.1f} {max_occupancies[i]:<10}")
    
    print("\n" + "="*80)
    print("KEY OBSERVATIONS:")
    print("="*80)
    
    # Performance improvement
    max_speedup_idx = np.argmax(speedups)
    max_speedup = speedups[max_speedup_idx]
    max_speedup_batch = batch_sizes[max_speedup_idx]
    perf_improvement = (max_speedup - 1) * 100
    
    print(f"\n1. PERFORMANCE IMPROVEMENT:")
    print(f"   • Best speedup: {max_speedup:.2f}x at batch_size={max_speedup_batch}")
    print(f"   • Performance gain: {perf_improvement:.1f}% faster than batch_size=1")
    print(f"   • Time reduction: {comp_times[0] - comp_times[max_speedup_idx]:.2f}s saved")
    
    # Quality degradation
    max_cost_increase = cost_increase_pct[-1]
    max_cost_batch = batch_sizes[-1]
    
    print(f"\n2. QUALITY DEGRADATION:")
    print(f"   • Worst quality: batch_size={max_cost_batch} (+{max_cost_increase:.1f}% cost increase)")
    print(f"   • Cost increase: {total_costs[-1] - total_costs[0]:,} additional cost")
    
    if max_occupancies[-1] > max_occupancies[0]:
        print(f"   ⚠ Max occupancy increased from {max_occupancies[0]} to {max_occupancies[-1]}")
        print(f"     → Requires additional metal layer in VLSI fabrication!")
    
    # Sweet spot analysis
    print(f"\n3. RECOMMENDED BATCH SIZE:")
    
    # Find batch size with good balance (< 2% cost increase, best speedup)
    good_batches = batch_sizes[cost_increase_pct < 2.0]
    if len(good_batches) > 1:
        good_speedups = speedups[cost_increase_pct < 2.0]
        best_idx = np.argmax(good_speedups)
        recommended_batch = good_batches[best_idx]
        recommended_speedup = good_speedups[best_idx]
        recommended_cost_increase = cost_increase_pct[cost_increase_pct < 2.0][best_idx]
        
        print(f"   • Recommended: batch_size={recommended_batch}")
        print(f"   • Speedup: {recommended_speedup:.2f}x ({(recommended_speedup-1)*100:.1f}% faster)")
        print(f"   • Cost increase: {recommended_cost_increase:.1f}% (acceptable)")
        print(f"   • Rationale: Best performance with minimal quality loss")
    else:
        print(f"   • Recommended: batch_size=1 (baseline)")
        print(f"   • Rationale: Higher batch sizes degrade quality too much")
    
    # Synchronization analysis
    print(f"\n4. SYNCHRONIZATION OVERHEAD:")
    sync_reduction = (1.0 - 1.0/batch_sizes[-1]) * 100
    print(f"   • Batch_size=1: Grab work {len(batch_sizes)} times per SA iteration")
    print(f"   • Batch_size={batch_sizes[-1]}: Grab work ~{int(595/batch_sizes[-1])} times per SA iteration")
    print(f"   • Synchronization reduction: ~{sync_reduction:.0f}%")
    print(f"   • Result: Less critical section contention")
    
    # Cache coherence
    print(f"\n5. CACHE COHERENCE IMPACT:")
    print(f"   • Larger batches → Fewer occupancy matrix updates")
    print(f"   • Fewer updates → Less MESI protocol traffic")
    print(f"   • But: Stale occupancy matrix → Worse routing decisions")
    print(f"   • Tradeoff visible in cost increase: {cost_increase_pct[-1]:.1f}%")
    
    print("\n" + "="*80)
    print("CONCLUSION:")
    print("="*80)
    print(f"Batch size introduces a performance-quality tradeoff:")
    print(f"  • Small batches (1-5): Best quality, good performance")
    print(f"  • Medium batches (10-25): Balanced tradeoff")
    print(f"  • Large batches (50-100): Best performance, degraded quality")
    print(f"\nFor production VLSI routing, batch_size=1 recommended to minimize")
    print(f"manufacturing cost, despite {perf_improvement:.0f}% performance penalty.")
    print("="*80)

def main():
    results_dir = 'batch_sensitivity_results'
    
    if not os.path.exists(results_dir):
        print(f"ERROR: {results_dir} directory not found!")
        print("Please run './test_batch_sizes.sh' first to collect data.")
        return
    
    try:
        print("Parsing batch sensitivity results...")
        batch_sizes, comp_times, total_costs, max_occupancies = parse_batch_results(results_dir)
        
        if len(batch_sizes) == 0:
            print("ERROR: No valid results found!")
            return
        
        print(f"Found data for {len(batch_sizes)} batch sizes: {list(batch_sizes)}")
        
        print("\nGenerating batch sensitivity analysis plots...")
        speedups, cost_increase_pct = plot_batch_analysis(batch_sizes, comp_times, total_costs, max_occupancies)
        
        print_analysis(batch_sizes, comp_times, speedups, total_costs, cost_increase_pct, max_occupancies)
        
        print("\n✓ Analysis complete!")
        print("  Generated: batch_sensitivity_analysis.png")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
