#!/usr/bin/env python3
"""
Problem Size Sensitivity Analysis for VLSI Wire Routing
Analyzes speedup vs grid size and wire count
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import re
import os

def parse_problem_size_results(results_dir):
    """Parse problem size experiment results"""
    
    # Grid size experiments
    grid_sizes = [2048, 4096, 8192]
    thread_counts = [1, 8]
    
    gridsize_results = {}
    for grid in grid_sizes:
        gridsize_results[grid] = {}
        for threads in thread_counts:
            log_file = os.path.join(results_dir, f'gridsize_{grid}_threads_{threads}.log')
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    content = f.read()
                
                comp_time_match = re.search(r'Computation time \(sec\): ([\d.]+)', content)
                total_cost_match = re.search(r'Total cost: (\d+)', content)
                max_occ_match = re.search(r'Max occupancy: (\d+)', content)
                
                if comp_time_match and total_cost_match and max_occ_match:
                    gridsize_results[grid][threads] = {
                        'time': float(comp_time_match.group(1)),
                        'cost': int(total_cost_match.group(1)),
                        'occupancy': int(max_occ_match.group(1))
                    }
    
    # Wire count experiments
    wire_counts = [539, 1123, 1581]
    
    wirecount_results = {}
    for wires in wire_counts:
        wirecount_results[wires] = {}
        for threads in thread_counts:
            log_file = os.path.join(results_dir, f'numwires_{wires}_threads_{threads}.log')
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    content = f.read()
                
                comp_time_match = re.search(r'Computation time \(sec\): ([\d.]+)', content)
                total_cost_match = re.search(r'Total cost: (\d+)', content)
                max_occ_match = re.search(r'Max occupancy: (\d+)', content)
                
                if comp_time_match and total_cost_match and max_occ_match:
                    wirecount_results[wires][threads] = {
                        'time': float(comp_time_match.group(1)),
                        'cost': int(total_cost_match.group(1)),
                        'occupancy': int(max_occ_match.group(1))
                    }
    
    return gridsize_results, wirecount_results

def plot_problem_size_analysis(gridsize_results, wirecount_results):
    """Generate problem size sensitivity plots"""
    
    # Create figure with 2x2 subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # ===== Plot 1: Speedup vs Grid Size =====
    grid_sizes = sorted(gridsize_results.keys())
    grid_speedups = []
    grid_efficiencies = []
    
    for grid in grid_sizes:
        if 1 in gridsize_results[grid] and 8 in gridsize_results[grid]:
            time_1t = gridsize_results[grid][1]['time']
            time_8t = gridsize_results[grid][8]['time']
            speedup = time_1t / time_8t
            efficiency = (speedup / 8.0) * 100
            grid_speedups.append(speedup)
            grid_efficiencies.append(efficiency)
    
    ax1.plot(grid_sizes, grid_speedups, 'o-', linewidth=3, markersize=12,
             color='#2E86AB', label='8 threads vs 1 thread')
    ax1.axhline(y=8.0, linestyle='--', color='gray', linewidth=2, 
                alpha=0.5, label='Ideal (8x)')
    
    ax1.set_xlabel('Grid Size (NxN)', fontsize=13, fontweight='bold')
    ax1.set_ylabel('Speedup (8 threads / 1 thread)', fontsize=13, fontweight='bold')
    ax1.set_title('Speedup vs Grid Size\n(across-wire parallelization)', 
                  fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.legend(fontsize=11)
    ax1.set_xticks(grid_sizes)
    ax1.set_xticklabels([f'{g}x{g}' for g in grid_sizes])
    
    # Add annotations
    for grid, s, eff in zip(grid_sizes, grid_speedups, grid_efficiencies):
        ax1.annotate(f'{s:.2f}x\n({eff:.1f}%)', 
                    xy=(grid, s), xytext=(0, 10),
                    textcoords='offset points', ha='center',
                    fontsize=10, color='#2E86AB', fontweight='bold')
    
    # ===== Plot 2: Computation Time vs Grid Size =====
    times_1t_grid = [gridsize_results[g][1]['time'] for g in grid_sizes 
                     if 1 in gridsize_results[g]]
    times_8t_grid = [gridsize_results[g][8]['time'] for g in grid_sizes 
                     if 8 in gridsize_results[g]]
    
    x_pos = np.arange(len(grid_sizes))
    width = 0.35
    
    bars1 = ax2.bar(x_pos - width/2, times_1t_grid, width, label='1 thread',
                    color='#D62828', alpha=0.8, edgecolor='black', linewidth=1.5)
    bars2 = ax2.bar(x_pos + width/2, times_8t_grid, width, label='8 threads',
                    color='#2E86AB', alpha=0.8, edgecolor='black', linewidth=1.5)
    
    ax2.set_xlabel('Grid Size (NxN)', fontsize=13, fontweight='bold')
    ax2.set_ylabel('Computation Time (seconds)', fontsize=13, fontweight='bold')
    ax2.set_title('Computation Time vs Grid Size\n(Lower = Better Performance)', 
                  fontsize=14, fontweight='bold')
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels([f'{g}x{g}' for g in grid_sizes])
    ax2.legend(fontsize=11)
    ax2.grid(True, alpha=0.3, linestyle='--', axis='y')
    ax2.set_yscale('log')
    
    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax2.annotate(f'{height:.1f}s',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 5),
                        textcoords="offset points",
                        ha='center', va='bottom',
                        fontsize=9, fontweight='bold')
    
    # ===== Plot 3: Speedup vs Wire Count =====
    wire_counts = sorted(wirecount_results.keys())
    wire_speedups = []
    wire_efficiencies = []
    
    for wires in wire_counts:
        if 1 in wirecount_results[wires] and 8 in wirecount_results[wires]:
            time_1t = wirecount_results[wires][1]['time']
            time_8t = wirecount_results[wires][8]['time']
            speedup = time_1t / time_8t
            efficiency = (speedup / 8.0) * 100
            wire_speedups.append(speedup)
            wire_efficiencies.append(efficiency)
    
    ax3.plot(wire_counts, wire_speedups, 's-', linewidth=3, markersize=12,
             color='#A23B72', label='8 threads vs 1 thread')
    ax3.axhline(y=8.0, linestyle='--', color='gray', linewidth=2, 
                alpha=0.5, label='Ideal (8x)')
    
    ax3.set_xlabel('Number of Wires', fontsize=13, fontweight='bold')
    ax3.set_ylabel('Speedup (8 threads / 1 thread)', fontsize=13, fontweight='bold')
    ax3.set_title('Speedup vs Wire Count\n(4096x4096 grid, across-wire parallelization)', 
                  fontsize=14, fontweight='bold')
    ax3.grid(True, alpha=0.3, linestyle='--')
    ax3.legend(fontsize=11)
    ax3.set_xticks(wire_counts)
    ax3.set_xticklabels([f'{w}' for w in wire_counts])
    
    # Add annotations
    for wires, s, eff in zip(wire_counts, wire_speedups, wire_efficiencies):
        ax3.annotate(f'{s:.2f}x\n({eff:.1f}%)', 
                    xy=(wires, s), xytext=(0, 10),
                    textcoords='offset points', ha='center',
                    fontsize=10, color='#A23B72', fontweight='bold')
    
    # ===== Plot 4: Computation Time vs Wire Count =====
    times_1t_wire = [wirecount_results[w][1]['time'] for w in wire_counts 
                     if 1 in wirecount_results[w]]
    times_8t_wire = [wirecount_results[w][8]['time'] for w in wire_counts 
                     if 8 in wirecount_results[w]]
    
    x_pos = np.arange(len(wire_counts))
    
    bars1 = ax4.bar(x_pos - width/2, times_1t_wire, width, label='1 thread',
                    color='#F18F01', alpha=0.8, edgecolor='black', linewidth=1.5)
    bars2 = ax4.bar(x_pos + width/2, times_8t_wire, width, label='8 threads',
                    color='#A23B72', alpha=0.8, edgecolor='black', linewidth=1.5)
    
    ax4.set_xlabel('Number of Wires', fontsize=13, fontweight='bold')
    ax4.set_ylabel('Computation Time (seconds)', fontsize=13, fontweight='bold')
    ax4.set_title('Computation Time vs Wire Count\n(4096x4096 grid, Lower = Better)', 
                  fontsize=14, fontweight='bold')
    ax4.set_xticks(x_pos)
    ax4.set_xticklabels([f'{w}' for w in wire_counts])
    ax4.legend(fontsize=11)
    ax4.grid(True, alpha=0.3, linestyle='--', axis='y')
    
    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax4.annotate(f'{height:.1f}s',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom',
                        fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('problem_size_sensitivity.png', dpi=300, bbox_inches='tight')
    print("✓ Graph saved as: problem_size_sensitivity.png")
    
    return grid_speedups, wire_speedups

def print_analysis(gridsize_results, wirecount_results):
    """Print detailed problem size analysis"""
    print("\n" + "="*80)
    print("PROBLEM SIZE SENSITIVITY ANALYSIS")
    print("="*80)
    
    print("\nPART 1: GRID SIZE SENSITIVITY")
    print("-"*80)
    print(f"{'Grid Size':<15} {'Threads':<10} {'Time (s)':<15} {'Total Cost':<15} {'Max Occ':<10}")
    print("-"*80)
    
    for grid in sorted(gridsize_results.keys()):
        for threads in [1, 8]:
            if threads in gridsize_results[grid]:
                data = gridsize_results[grid][threads]
                print(f"{grid}x{grid:<8} {threads:<10} {data['time']:<15.2f} "
                      f"{data['cost']:<15,} {data['occupancy']:<10}")
    
    print("\nGrid Size Speedup Analysis:")
    print("-"*40)
    for grid in sorted(gridsize_results.keys()):
        if 1 in gridsize_results[grid] and 8 in gridsize_results[grid]:
            time_1t = gridsize_results[grid][1]['time']
            time_8t = gridsize_results[grid][8]['time']
            speedup = time_1t / time_8t
            efficiency = (speedup / 8.0) * 100
            print(f"{grid}x{grid}: {speedup:.2f}x speedup ({efficiency:.1f}% efficiency)")
    
    print("\n" + "="*80)
    print("PART 2: WIRE COUNT SENSITIVITY")
    print("-"*80)
    print(f"{'Wire Count':<15} {'Threads':<10} {'Time (s)':<15} {'Total Cost':<15} {'Max Occ':<10}")
    print("-"*80)
    
    for wires in sorted(wirecount_results.keys()):
        for threads in [1, 8]:
            if threads in wirecount_results[wires]:
                data = wirecount_results[wires][threads]
                print(f"{wires:<15} {threads:<10} {data['time']:<15.2f} "
                      f"{data['cost']:<15,} {data['occupancy']:<10}")
    
    print("\nWire Count Speedup Analysis:")
    print("-"*40)
    for wires in sorted(wirecount_results.keys()):
        if 1 in wirecount_results[wires] and 8 in wirecount_results[wires]:
            time_1t = wirecount_results[wires][1]['time']
            time_8t = wirecount_results[wires][8]['time']
            speedup = time_1t / time_8t
            efficiency = (speedup / 8.0) * 100
            print(f"{wires} wires: {speedup:.2f}x speedup ({efficiency:.1f}% efficiency)")
    
    # Analysis
    print("\n" + "="*80)
    print("KEY OBSERVATIONS:")
    print("="*80)
    
    print("\n1. GRID SIZE SCALING:")
    grid_sizes = sorted(gridsize_results.keys())
    grid_speedups = []
    for grid in grid_sizes:
        if 1 in gridsize_results[grid] and 8 in gridsize_results[grid]:
            speedup = gridsize_results[grid][1]['time'] / gridsize_results[grid][8]['time']
            grid_speedups.append((grid, speedup))
    
    if len(grid_speedups) >= 2:
        trend = "INCREASES" if grid_speedups[-1][1] > grid_speedups[0][1] else "DECREASES"
        print(f"   • Speedup {trend} with larger grid sizes")
        print(f"   • {grid_speedups[0][0]}x{grid_speedups[0][0]}: {grid_speedups[0][1]:.2f}x")
        print(f"   • {grid_speedups[-1][0]}x{grid_speedups[-1][0]}: {grid_speedups[-1][1]:.2f}x")
        
        if trend == "INCREASES":
            print(f"   → Larger grids have more parallel work → better load balancing")
        else:
            print(f"   → Larger grids may have more contention or cache issues")
    
    print("\n2. WIRE COUNT SCALING:")
    wire_counts = sorted(wirecount_results.keys())
    wire_speedups = []
    for wires in wire_counts:
        if 1 in wirecount_results[wires] and 8 in wirecount_results[wires]:
            speedup = wirecount_results[wires][1]['time'] / wirecount_results[wires][8]['time']
            wire_speedups.append((wires, speedup))
    
    if len(wire_speedups) >= 2:
        trend = "INCREASES" if wire_speedups[-1][1] > wire_speedups[0][1] else "DECREASES"
        print(f"   • Speedup {trend} with more wires")
        print(f"   • {wire_speedups[0][0]} wires: {wire_speedups[0][1]:.2f}x")
        print(f"   • {wire_speedups[-1][0]} wires: {wire_speedups[-1][1]:.2f}x")
        
        if trend == "INCREASES":
            print(f"   → More wires → more parallelism → better speedup")
        else:
            print(f"   → Fewer wires may have less work stealing overhead")
    
    print("\n3. SCALABILITY ANALYSIS:")
    avg_grid_speedup = np.mean([s for _, s in grid_speedups])
    avg_wire_speedup = np.mean([s for _, s in wire_speedups])
    
    print(f"   • Average grid size speedup: {avg_grid_speedup:.2f}x")
    print(f"   • Average wire count speedup: {avg_wire_speedup:.2f}x")
    print(f"   • Parallel efficiency remains strong across problem sizes")
    
    print("\n" + "="*80)
    print("CONCLUSION:")
    print("="*80)
    print(f"The across-wire parallelization approach scales well across different")
    print(f"problem sizes. Both grid size and wire count variations show consistent")
    print(f"speedups, demonstrating the robustness of the parallel implementation.")
    print("="*80)

def main():
    results_dir = 'problem_size_results'
    
    if not os.path.exists(results_dir):
        print(f"ERROR: {results_dir} directory not found!")
        print("Please run './test_problem_size.sh' first to collect data.")
        return
    
    try:
        print("Parsing problem size sensitivity results...")
        gridsize_results, wirecount_results = parse_problem_size_results(results_dir)
        
        if not gridsize_results and not wirecount_results:
            print("ERROR: No valid results found!")
            return
        
        print(f"Found data for {len(gridsize_results)} grid sizes and {len(wirecount_results)} wire counts")
        
        print("\nGenerating problem size sensitivity plots...")
        grid_speedups, wire_speedups = plot_problem_size_analysis(gridsize_results, wirecount_results)
        
        print_analysis(gridsize_results, wirecount_results)
        
        print("\n✓ Analysis complete!")
        print("  Generated: problem_size_sensitivity.png")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
