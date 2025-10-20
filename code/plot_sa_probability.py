#!/usr/bin/env python3
"""
SA Probability Sensitivity Analysis for VLSI Wire Routing
Analyzes speedup vs SA probability parameter (P = 0.01, 0.1, 0.5)
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import re
import os

def parse_sa_results(results_dir):
    """Parse SA probability experiment results"""
    p_values = [0.01, 0.1, 0.5]
    thread_counts = [1, 8]
    
    results = {}
    
    for p in p_values:
        results[p] = {}
        for threads in thread_counts:
            log_file = os.path.join(results_dir, f'p_{p}_threads_{threads}.log')
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
                results[p][threads] = {
                    'time': float(comp_time_match.group(1)),
                    'cost': int(total_cost_match.group(1)),
                    'occupancy': int(max_occ_match.group(1))
                }
    
    return results

def plot_sa_analysis(results):
    """Generate SA probability sensitivity plots"""
    
    p_values = sorted(results.keys())
    speedups = []
    times_1t = []
    times_8t = []
    costs_1t = []
    costs_8t = []
    
    for p in p_values:
        if 1 in results[p] and 8 in results[p]:
            time_1t = results[p][1]['time']
            time_8t = results[p][8]['time']
            speedup = time_1t / time_8t
            
            speedups.append(speedup)
            times_1t.append(time_1t)
            times_8t.append(time_8t)
            costs_1t.append(results[p][1]['cost'])
            costs_8t.append(results[p][8]['cost'])
    
    # Create figure with 2x2 subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # ===== Plot 1: Speedup vs P Value =====
    ax1.plot(p_values, speedups, 'o-', linewidth=3, markersize=12,
             color='#2E86AB', label='8 threads vs 1 thread')
    
    # Add ideal speedup line
    ax1.axhline(y=8.0, linestyle='--', color='gray', linewidth=2, 
                alpha=0.5, label='Ideal (8x)')
    
    ax1.set_xlabel('SA Probability (P)', fontsize=13, fontweight='bold')
    ax1.set_ylabel('Speedup (8 threads / 1 thread)', fontsize=13, fontweight='bold')
    ax1.set_title('Speedup vs SA Probability\n(medium_4096.txt, across-wire parallelization)', 
                  fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.legend(fontsize=11)
    ax1.set_xscale('log')
    ax1.set_xticks(p_values)
    ax1.set_xticklabels([str(p) for p in p_values])
    
    # Add speedup annotations
    for p, s in zip(p_values, speedups):
        efficiency = (s / 8.0) * 100
        ax1.annotate(f'{s:.2f}x\n({efficiency:.1f}%)', 
                    xy=(p, s), xytext=(0, 10),
                    textcoords='offset points', ha='center',
                    fontsize=10, color='#2E86AB', fontweight='bold')
    
    # ===== Plot 2: Computation Time vs P Value =====
    x_pos = np.arange(len(p_values))
    width = 0.35
    
    bars1 = ax2.bar(x_pos - width/2, times_1t, width, label='1 thread',
                    color='#D62828', alpha=0.8, edgecolor='black', linewidth=1.5)
    bars2 = ax2.bar(x_pos + width/2, times_8t, width, label='8 threads',
                    color='#2E86AB', alpha=0.8, edgecolor='black', linewidth=1.5)
    
    ax2.set_xlabel('SA Probability (P)', fontsize=13, fontweight='bold')
    ax2.set_ylabel('Computation Time (seconds)', fontsize=13, fontweight='bold')
    ax2.set_title('Computation Time vs SA Probability\n(Lower = Better Performance)', 
                  fontsize=14, fontweight='bold')
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels([str(p) for p in p_values])
    ax2.legend(fontsize=11)
    ax2.grid(True, alpha=0.3, linestyle='--', axis='y')
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax2.annotate(f'{height:.1f}s',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom',
                        fontsize=9, fontweight='bold')
    
    # ===== Plot 3: Total Cost vs P Value =====
    x_pos = np.arange(len(p_values))
    
    bars1 = ax3.bar(x_pos - width/2, np.array(costs_1t)/1000, width, label='1 thread',
                    color='#F18F01', alpha=0.8, edgecolor='black', linewidth=1.5)
    bars2 = ax3.bar(x_pos + width/2, np.array(costs_8t)/1000, width, label='8 threads',
                    color='#A23B72', alpha=0.8, edgecolor='black', linewidth=1.5)
    
    ax3.set_xlabel('SA Probability (P)', fontsize=13, fontweight='bold')
    ax3.set_ylabel('Total Cost (Thousands)', fontsize=13, fontweight='bold')
    ax3.set_title('Routing Quality vs SA Probability\n(Lower = Better Quality)', 
                  fontsize=14, fontweight='bold')
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels([str(p) for p in p_values])
    ax3.legend(fontsize=11)
    ax3.grid(True, alpha=0.3, linestyle='--', axis='y')
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax3.annotate(f'{int(height*1000):,}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom',
                        fontsize=8, fontweight='bold', rotation=0)
    
    # ===== Plot 4: Efficiency vs P Value =====
    efficiencies = [(s / 8.0) * 100 for s in speedups]
    
    ax4.plot(p_values, efficiencies, 's-', linewidth=3, markersize=12,
             color='#A23B72', label='Parallel Efficiency')
    ax4.axhline(y=100, linestyle='--', color='gray', linewidth=2, 
                alpha=0.5, label='Ideal (100%)')
    
    ax4.set_xlabel('SA Probability (P)', fontsize=13, fontweight='bold')
    ax4.set_ylabel('Parallel Efficiency (%)', fontsize=13, fontweight='bold')
    ax4.set_title('Parallel Efficiency vs SA Probability\n(Higher = Better Scalability)', 
                  fontsize=14, fontweight='bold')
    ax4.grid(True, alpha=0.3, linestyle='--')
    ax4.legend(fontsize=11)
    ax4.set_xscale('log')
    ax4.set_xticks(p_values)
    ax4.set_xticklabels([str(p) for p in p_values])
    ax4.set_ylim([0, 110])
    
    # Add efficiency annotations
    for p, eff in zip(p_values, efficiencies):
        ax4.annotate(f'{eff:.1f}%', 
                    xy=(p, eff), xytext=(0, 10),
                    textcoords='offset points', ha='center',
                    fontsize=10, color='#A23B72', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('sa_probability_sensitivity.png', dpi=300, bbox_inches='tight')
    print("✓ Graph saved as: sa_probability_sensitivity.png")
    
    return speedups, efficiencies

def print_analysis(results):
    """Print detailed SA probability analysis"""
    print("\n" + "="*80)
    print("SA PROBABILITY SENSITIVITY ANALYSIS")
    print("="*80)
    print(f"{'P Value':<10} {'Threads':<10} {'Time (s)':<15} {'Total Cost':<15} {'Max Occ':<10}")
    print("-"*80)
    
    for p in sorted(results.keys()):
        for threads in [1, 8]:
            if threads in results[p]:
                data = results[p][threads]
                print(f"{p:<10} {threads:<10} {data['time']:<15.2f} "
                      f"{data['cost']:<15,} {data['occupancy']:<10}")
    
    print("\n" + "="*80)
    print("SPEEDUP ANALYSIS:")
    print("="*80)
    
    for p in sorted(results.keys()):
        if 1 in results[p] and 8 in results[p]:
            time_1t = results[p][1]['time']
            time_8t = results[p][8]['time']
            speedup = time_1t / time_8t
            efficiency = (speedup / 8.0) * 100
            
            print(f"\nP = {p}:")
            print(f"  • 1 thread:  {time_1t:.2f}s")
            print(f"  • 8 threads: {time_8t:.2f}s")
            print(f"  • Speedup:   {speedup:.2f}x")
            print(f"  • Efficiency: {efficiency:.1f}%")
            
            # Compare costs
            cost_1t = results[p][1]['cost']
            cost_8t = results[p][8]['cost']
            cost_diff_pct = ((cost_8t - cost_1t) / cost_1t) * 100
            
            print(f"  • Cost (1t): {cost_1t:,}")
            print(f"  • Cost (8t): {cost_8t:,}")
            print(f"  • Quality degradation: {cost_diff_pct:+.1f}%")
    
    # Overall analysis
    print("\n" + "="*80)
    print("KEY OBSERVATIONS:")
    print("="*80)
    
    p_values = sorted(results.keys())
    speedups = []
    
    for p in p_values:
        if 1 in results[p] and 8 in results[p]:
            speedup = results[p][1]['time'] / results[p][8]['time']
            speedups.append((p, speedup))
    
    # Find best speedup
    best_p, best_speedup = max(speedups, key=lambda x: x[1])
    worst_p, worst_speedup = min(speedups, key=lambda x: x[1])
    
    print(f"\n1. PERFORMANCE IMPACT:")
    print(f"   • Best speedup: {best_speedup:.2f}x at P={best_p}")
    print(f"   • Worst speedup: {worst_speedup:.2f}x at P={worst_p}")
    print(f"   • Speedup variance: {best_speedup - worst_speedup:.2f}x difference")
    
    print(f"\n2. SA PROBABILITY EFFECT:")
    print(f"   • Lower P (0.01): More greedy optimization")
    print(f"     - Faster convergence within each iteration")
    print(f"     - Risk of local minima")
    print(f"   • Higher P (0.5): More randomization")
    print(f"     - Better exploration of solution space")
    print(f"     - Slower convergence per iteration")
    
    print(f"\n3. PARALLELIZATION IMPACT:")
    if speedups[0][1] < speedups[-1][1]:
        print(f"   • Speedup INCREASES with P")
        print(f"   • Higher randomization → more independent work")
        print(f"   • Less contention on shared occupancy matrix")
    elif speedups[0][1] > speedups[-1][1]:
        print(f"   • Speedup DECREASES with P")
        print(f"   • Higher randomization → worse quality per iteration")
        print(f"   • More SA iterations needed → slower overall")
    else:
        print(f"   • Speedup relatively STABLE across P values")
        print(f"   • SA probability doesn't significantly affect parallelism")
    
    print("\n" + "="*80)
    print("CONCLUSION:")
    print("="*80)
    print(f"The SA probability parameter affects both solution quality and parallel")
    print(f"performance. P={best_p} provides the best speedup ({best_speedup:.2f}x) in")
    print(f"this experiment, though the optimal value depends on the quality-performance")
    print(f"tradeoff desired for the specific application.")
    print("="*80)

def main():
    results_dir = 'sa_probability_results'
    
    if not os.path.exists(results_dir):
        print(f"ERROR: {results_dir} directory not found!")
        print("Please run './test_sa_probability.sh' first to collect data.")
        return
    
    try:
        print("Parsing SA probability sensitivity results...")
        results = parse_sa_results(results_dir)
        
        if not results:
            print("ERROR: No valid results found!")
            return
        
        print(f"Found data for {len(results)} P values")
        
        print("\nGenerating SA probability sensitivity plots...")
        speedups, efficiencies = plot_sa_analysis(results)
        
        print_analysis(results)
        
        print("\n✓ Analysis complete!")
        print("  Generated: sa_probability_sensitivity.png")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
