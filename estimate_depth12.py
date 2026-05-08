#!/usr/bin/env python3
"""Estimate time for depth-12 opening book"""

# Current stats: 67,351 positions at depth 8 in 6.6 minutes
positions = 67351
depth8_time_minutes = 6.6

# Each depth level multiplies computation time by ~branching factor
# Connect 4 branching factor averages ~5-6
branching_factor = 5.5

# Depth 8 → Depth 12 = 4 additional levels
additional_levels = 4

# Time multiplier
multiplier = branching_factor ** additional_levels

# Estimated time for depth 12
depth12_time_minutes = depth8_time_minutes * multiplier
depth12_hours = depth12_time_minutes / 60
depth12_days = depth12_hours / 24

print(f"Opening book generation estimates:")
print(f"  Depth 8:  6.6 minutes (67,351 positions)")
print(f"  Depth 12: {depth12_time_minutes:,.0f} minutes = {depth12_hours:.1f} hours = {depth12_days:.1f} days")
print(f"\n  Time multiplier: {multiplier:.0f}x (from {additional_levels} extra depth levels)")
print(f"\nConclusion: Depth 12 opening book would take ~{depth12_days:.0f} DAYS! 😱")
