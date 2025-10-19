Experiment: medium_calculateRouteCost_Optimized
Date: Sat Oct 18 04:49:35 PM PDT 2025
Input: medium_4096.txt

Optimizations:
  - Inlined calculateRouteCost function
  - Simplified cost calculation: 2*n + 1
  - Eliminated 3.5M function calls per run

Contents:
  - speedup_summary.txt : Main results with speedup factors
  - tracy_profiles/     : .tracy files for performance analysis
  - logs/               : Full wireroute output for each run

Tracy Profiles:
total 19M
-rw-rw-r-- 1 raj raj 4.7M Oct 18 16:43 medium_t1.tracy
-rw-rw-r-- 1 raj raj 4.3M Oct 18 16:44 medium_t2.tracy
-rw-rw-r-- 1 raj raj 4.7M Oct 18 16:44 medium_t4.tracy
-rw-rw-r-- 1 raj raj 4.5M Oct 18 16:49 medium_t8.tracy

Logs:
total 16K
-rw-rw-r-- 1 raj raj 377 Oct 18 16:43 medium_t1.log
-rw-rw-r-- 1 raj raj 377 Oct 18 16:44 medium_t2.log
-rw-rw-r-- 1 raj raj 376 Oct 18 16:44 medium_t4.log
-rw-rw-r-- 1 raj raj 376 Oct 18 16:49 medium_t8.log
