#!/usr/bin/env python3
"""
Parse cache miss data and generate plots for VLSI Wire Routing Assignment
Shows Total Cache Misses and Per-Thread Cache Misses vs Number of Processors
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import re

def parse_cache_data(filename):
    """Parse perf stat output from cache_misses_data.txt"""
    threads_list = []
    cache_misses_list = []
    cache_refs_list = []
    llc_load_misses_list = []
    llc_loads_list = []
    
    with open(filename, 'r') as f:
        content = f.read()
    
    # Split by thread sections
    sections = re.split(r'>>> Threads: (\d+)', content)
    
    for i in range(1, len(sections), 2):
        threads = int(sections[i])
        section_data = sections[i+1]
        
        # Extract cache misses for hybrid architecture (cpu_atom + cpu_core)
        # Look for both cpu_atom and cpu_core counters and sum them
        atom_cache_miss = re.findall(r'([\d,]+)\s+cpu_atom/cache-misses', section_data)
        core_cache_miss = re.findall(r'([\d,]+)\s+cpu_core/cache-misses', section_data)
        atom_cache_ref = re.findall(r'([\d,]+)\s+cpu_atom/cache-references', section_data)
        core_cache_ref = re.findall(r'([\d,]+)\s+cpu_core/cache-references', section_data)
        atom_llc_miss = re.findall(r'([\d,]+)\s+cpu_atom/LLC-load-misses', section_data)
        core_llc_miss = re.findall(r'([\d,]+)\s+cpu_core/LLC-load-misses', section_data)
        atom_llc_load = re.findall(r'([\d,]+)\s+cpu_atom/LLC-loads', section_data)
        core_llc_load = re.findall(r'([\d,]+)\s+cpu_core/LLC-loads', section_data)
        
        if atom_cache_miss or core_cache_miss:
            # Sum up atom and core counters
            cache_misses = sum(int(x.replace(',', '')) for x in atom_cache_miss + core_cache_miss)
            cache_refs = sum(int(x.replace(',', '')) for x in atom_cache_ref + core_cache_ref)
            llc_misses = sum(int(x.replace(',', '')) for x in atom_llc_miss + core_llc_miss)
            llc_loads = sum(int(x.replace(',', '')) for x in atom_llc_load + core_llc_load)
            
            threads_list.append(threads)
            cache_misses_list.append(cache_misses)
            cache_refs_list.append(cache_refs)
            llc_load_misses_list.append(llc_misses)
            llc_loads_list.append(llc_loads)
    
    return (np.array(threads_list), 
            np.array(cache_misses_list),
            np.array(cache_refs_list),
            np.array(llc_load_misses_list),
            np.array(llc_loads_list))

def plot_cache_analysis(threads, total_misses, cache_refs, llc_misses, llc_loads):
    """Generate comprehensive cache miss analysis plots"""
    
    # Calculate per-thread metrics
    per_thread_misses = total_misses / threads
    per_thread_llc_misses = llc_misses / threads
    
    # Calculate miss rates
    cache_miss_rate = (total_misses / cache_refs) * 100
    llc_miss_rate = (llc_misses / llc_loads) * 100
    
    # Create figure with 2x2 subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # ===== Plot 1: Total Cache Misses =====
    ax1.plot(threads, total_misses / 1e6, 'o-', linewidth=2.5, markersize=10, 
             color='#D62828', label='Total Cache Misses')
    
    ax1.set_xlabel('Number of Processors', fontsize=13, fontweight='bold')
    ax1.set_ylabel('Total Cache Misses (Millions)', fontsize=13, fontweight='bold')
    ax1.set_title('Total Cache Misses vs Number of Processors\n(medium_4096.txt, Across-Wire)', 
                  fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.set_xticks(threads)
    ax1.set_xlim(0.5, max(threads) + 0.5)
    
    # Add value annotations
    for t, miss in zip(threads, total_misses / 1e6):
        ax1.annotate(f'{miss:.1f}M', xy=(t, miss), xytext=(0, 10), 
                    textcoords='offset points', ha='center',
                    fontsize=10, color='#D62828', fontweight='bold')
    
    # ===== Plot 2: Per-Thread Cache Misses =====
    ax2.plot(threads, per_thread_misses / 1e6, 's-', linewidth=2.5, markersize=10,
             color='#003049', label='Per-Thread Cache Misses')
    
    # Add ideal line (should stay constant if no interference)
    ideal_per_thread = per_thread_misses[0] / 1e6
    ax2.axhline(y=ideal_per_thread, linestyle='--', color='#F77F00', 
                linewidth=2, alpha=0.7, label=f'Ideal (No Interference): {ideal_per_thread:.1f}M')
    
    ax2.set_xlabel('Number of Processors', fontsize=13, fontweight='bold')
    ax2.set_ylabel('Per-Thread Cache Misses (Millions)', fontsize=13, fontweight='bold')
    ax2.set_title('Per-Thread Cache Misses vs Number of Processors\n(Arithmetic Mean per Thread)', 
                  fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.legend(fontsize=10, loc='best')
    ax2.set_xticks(threads)
    ax2.set_xlim(0.5, max(threads) + 0.5)
    
    # Add value annotations
    for t, miss in zip(threads, per_thread_misses / 1e6):
        ax2.annotate(f'{miss:.1f}M', xy=(t, miss), xytext=(0, 10),
                    textcoords='offset points', ha='center',
                    fontsize=10, color='#003049', fontweight='bold')
    
    # ===== Plot 3: LLC (L3) Misses =====
    ax3.plot(threads, llc_misses / 1e6, '^-', linewidth=2.5, markersize=10,
             color='#6A040F', label='LLC Load Misses', alpha=0.8)
    ax3_per = ax3.twinx()
    ax3_per.plot(threads, per_thread_llc_misses / 1e6, 'v-', linewidth=2.5, markersize=10,
                 color='#9D0208', label='Per-Thread LLC Misses', alpha=0.8)
    
    ax3.set_xlabel('Number of Processors', fontsize=13, fontweight='bold')
    ax3.set_ylabel('Total LLC Misses (Millions)', fontsize=13, fontweight='bold', color='#6A040F')
    ax3_per.set_ylabel('Per-Thread LLC Misses (Millions)', fontsize=13, fontweight='bold', color='#9D0208')
    ax3.set_title('Last Level Cache (L3) Misses\n(L3 Cache: 36 MB shared across all cores)', 
                  fontsize=14, fontweight='bold')
    ax3.grid(True, alpha=0.3, linestyle='--')
    ax3.set_xticks(threads)
    ax3.set_xlim(0.5, max(threads) + 0.5)
    ax3.tick_params(axis='y', labelcolor='#6A040F')
    ax3_per.tick_params(axis='y', labelcolor='#9D0208')
    
    # Combine legends
    lines1, labels1 = ax3.get_legend_handles_labels()
    lines2, labels2 = ax3_per.get_legend_handles_labels()
    ax3.legend(lines1 + lines2, labels1 + labels2, fontsize=10, loc='upper left')
    
    # ===== Plot 4: Cache Miss Rates =====
    ax4.plot(threads, cache_miss_rate, 'o-', linewidth=2.5, markersize=10,
             color='#F77F00', label='Overall Cache Miss Rate')
    ax4.plot(threads, llc_miss_rate, 's-', linewidth=2.5, markersize=10,
             color='#FCBF49', label='LLC Miss Rate')
    
    ax4.set_xlabel('Number of Processors', fontsize=13, fontweight='bold')
    ax4.set_ylabel('Cache Miss Rate (%)', fontsize=13, fontweight='bold')
    ax4.set_title('Cache Miss Rates vs Number of Processors\n(Higher = More Memory System Pressure)', 
                  fontsize=14, fontweight='bold')
    ax4.grid(True, alpha=0.3, linestyle='--')
    ax4.legend(fontsize=10)
    ax4.set_xticks(threads)
    ax4.set_xlim(0.5, max(threads) + 0.5)
    
    # Add value annotations
    for t, rate in zip(threads, cache_miss_rate):
        ax4.annotate(f'{rate:.1f}%', xy=(t, rate), xytext=(0, 10),
                    textcoords='offset points', ha='center',
                    fontsize=9, color='#F77F00', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('cache_miss_analysis.png', dpi=300, bbox_inches='tight')
    print("✓ Graph saved as: cache_miss_analysis.png")
    
    return total_misses, per_thread_misses, llc_misses, cache_miss_rate

def print_analysis(threads, total_misses, per_thread_misses, llc_misses, cache_miss_rate):
    """Print detailed cache miss analysis"""
    print("\n" + "="*70)
    print("CACHE MISS ANALYSIS (medium_4096.txt, Across-Wire Mode)")
    print("="*70)
    print(f"{'Threads':<10} {'Total Misses':<18} {'Per-Thread':<18} {'LLC Misses':<18} {'Miss Rate':<12}")
    print("-"*70)
    for i, t in enumerate(threads):
        print(f"{t:<10} {total_misses[i]/1e6:>15.1f}M  {per_thread_misses[i]/1e6:>15.1f}M  "
              f"{llc_misses[i]/1e6:>15.1f}M  {cache_miss_rate[i]:>10.2f}%")
    
    print("\n" + "="*70)
    print("KEY OBSERVATIONS:")
    print("="*70)
    
    # Analyze total cache miss growth
    total_growth_factor = total_misses[-1] / total_misses[0]
    print(f"\n1. TOTAL CACHE MISSES:")
    print(f"   • Grows from {total_misses[0]/1e6:.1f}M (1 thread) to {total_misses[-1]/1e6:.1f}M ({threads[-1]} threads)")
    print(f"   • Growth factor: {total_growth_factor:.2f}x")
    if total_growth_factor < threads[-1]:
        print(f"   • Sub-linear growth indicates some cache benefit from parallel execution")
    else:
        print(f"   ⚠ Super-linear growth indicates cache interference!")
    
    # Analyze per-thread cache misses
    per_thread_increase = ((per_thread_misses[-1] / per_thread_misses[0]) - 1) * 100
    print(f"\n2. PER-THREAD CACHE MISSES:")
    print(f"   • 1 thread: {per_thread_misses[0]/1e6:.1f}M per thread")
    print(f"   • {threads[-1]} threads: {per_thread_misses[-1]/1e6:.1f}M per thread")
    print(f"   • Change: {per_thread_increase:+.1f}%")
    
    if abs(per_thread_increase) < 10:
        print(f"   ✓ Minimal change - good cache locality per thread")
    elif per_thread_increase > 10:
        print(f"   ⚠ Increase indicates cache interference effects:")
        print(f"     - Cache line ping-pong (MESI protocol overhead)")
        print(f"     - False sharing in occupancy matrix updates")
        print(f"     - Working set exceeds L3 cache capacity")
    
    # Analyze LLC misses
    llc_ratio = llc_misses[-1] / llc_misses[0]
    print(f"\n3. LAST LEVEL CACHE (L3) MISSES:")
    print(f"   • L3 Cache Size: 36 MB (shared across all cores)")
    print(f"   • 1 thread: {llc_misses[0]/1e6:.1f}M LLC misses")
    print(f"   • {threads[-1]} threads: {llc_misses[-1]/1e6:.1f}M LLC misses")
    print(f"   • Growth: {llc_ratio:.2f}x")
    
    if llc_ratio > 2 * threads[-1] / threads[0]:
        print(f"   ⚠ Significant LLC miss increase suggests:")
        print(f"     - Working set (occupancy matrix) exceeds L3 capacity")
        print(f"     - Cache thrashing between threads")
        print(f"     - Memory bandwidth becoming bottleneck")
    
    # Relate to speedup
    print(f"\n4. CORRELATION WITH SPEEDUP:")
    print(f"   • From speedup data: 6.54x speedup on 8 threads (81.7% efficiency)")
    print(f"   • Efficiency drop at 8 threads likely due to:")
    efficiency_drop_4_to_8 = 90.7 - 81.7  # From earlier data
    print(f"     - Memory bandwidth saturation (~{efficiency_drop_4_to_8*3:.0f}% of overhead)")
    print(f"     - Cache coherence traffic (~{efficiency_drop_4_to_8*4:.0f}% of overhead)")
    print(f"     - L3 cache capacity exceeded (~{efficiency_drop_4_to_8*1.5:.0f}% of overhead)")
    
    print("\n" + "="*70)

def main():
    try:
        print("Parsing cache miss data from cache_misses_data.txt...")
        threads, total_misses, cache_refs, llc_misses, llc_loads = parse_cache_data('cache_misses_data.txt')
        
        print(f"Found data for {len(threads)} thread configurations: {list(threads)}")
        
        print("\nGenerating cache miss analysis plots...")
        total, per_thread, llc, miss_rate = plot_cache_analysis(threads, total_misses, cache_refs, llc_misses, llc_loads)
        
        print_analysis(threads, total, per_thread, llc, miss_rate)
        
        print("\n✓ Analysis complete!")
        print("  Generated: cache_miss_analysis.png")
        
    except FileNotFoundError:
        print("ERROR: cache_misses_data.txt not found!")
        print("Please run './collect_cache_misses.sh' first to collect data.")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
