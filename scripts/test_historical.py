#!/usr/bin/env python3
"""
Test constraint system on historical storm data

Usage:
    python test_historical.py ian 2022
    python test_historical.py idalia 2023
"""

import sys
import json
from datetime import datetime
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))

from constraint_engine_v2 import (
    NHCAdvisory, EnvironmentalData, ConstraintEngine, 
    EnvironmentalEngine, InsightGenerator
)

# Historical storm data (from NHC best track)
HISTORICAL_STORMS = {
    'ian_2022': [
        {
            'time': '2022-09-26T12:00:00Z',
            'name': 'Ian',
            'classification': 'TROPICAL STORM',
            'intensity': 45,
            'pressure': 998,
            'lat': 17.8,
            'lon': -79.8,
            'phase': 'Early development'
        },
        {
            'time': '2022-09-27T00:00:00Z',
            'name': 'Ian',
            'classification': 'HURRICANE',
            'intensity': 75,
            'pressure': 986,
            'lat': 18.5,
            'lon': -81.5,
            'phase': 'Hurricane - RI begins'
        },
        {
            'time': '2022-09-27T12:00:00Z',
            'name': 'Ian',
            'classification': 'MAJOR HURRICANE',
            'intensity': 105,
            'pressure': 954,
            'lat': 19.9,
            'lon': -82.8,
            'phase': 'Major Hurricane - over Caribbean'
        },
        {
            'time': '2022-09-28T00:00:00Z',
            'name': 'Ian',
            'classification': 'CATEGORY 4',
            'intensity': 125,
            'pressure': 937,
            'lat': 21.9,
            'lon': -83.1,
            'phase': 'PEAK INTENSITY'
        },
        {
            'time': '2022-09-28T12:00:00Z',
            'name': 'Ian',
            'classification': 'CATEGORY 4',
            'intensity': 120,
            'pressure': 945,
            'lat': 23.7,
            'lon': -83.0,
            'phase': 'Slight weakening'
        },
        {
            'time': '2022-09-29T00:00:00Z',
            'name': 'Ian',
            'classification': 'CATEGORY 3',
            'intensity': 100,
            'pressure': 962,
            'lat': 25.0,
            'lon': -82.5,
            'phase': 'Weakening over Cuba'
        },
        {
            'time': '2022-09-29T12:00:00Z',
            'name': 'Ian',
            'classification': 'CATEGORY 3',
            'intensity': 110,
            'pressure': 951,
            'lat': 26.2,
            'lon': -82.3,
            'phase': 'Re-intensification over Gulf'
        },
        {
            'time': '2022-09-30T00:00:00Z',
            'name': 'Ian',
            'classification': 'CATEGORY 3',
            'intensity': 100,
            'pressure': 958,
            'lat': 26.7,
            'lon': -82.2,
            'phase': 'Approaching Florida'
        },
        {
            'time': '2022-09-30T12:00:00Z',
            'name': 'Ian',
            'classification': 'POST-TROPICAL',
            'intensity': 65,
            'pressure': 983,
            'lat': 27.5,
            'lon': -81.2,
            'phase': 'POST-LANDFALL - rapid decay'
        },
        {
            'time': '2022-10-01T00:00:00Z',
            'name': 'Ian',
            'classification': 'POST-TROPICAL',
            'intensity': 50,
            'pressure': 992,
            'lat': 28.8,
            'lon': -80.1,
            'phase': 'Continuing weakening'
        }
    ]
}

def create_nhc_advisory(point: dict) -> NHCAdvisory:
    """Create NHC advisory from historical data point"""
    return NHCAdvisory(
        storm_id=f"test_{point['name'].lower()}",
        storm_name=point['name'],
        advisory_number=0,
        advisory_time=datetime.fromisoformat(point['time'].replace('Z', '+00:00')),
        classification=point['classification'],
        current_intensity=float(point['intensity']),
        current_pressure=float(point['pressure']),
        latitude=float(point['lat']),
        longitude=float(point['lon']),
        movement_direction="NW",
        movement_speed=12.0,
        forecast_positions=[]
    )

def test_storm(storm_key: str):
    """Test constraint system on historical storm"""
    
    if storm_key not in HISTORICAL_STORMS:
        print(f"Storm '{storm_key}' not found")
        print(f"Available: {', '.join(HISTORICAL_STORMS.keys())}")
        return
    
    points = HISTORICAL_STORMS[storm_key]
    
    print(f"\n{'='*70}")
    print(f"TESTING: {points[0]['name']} ({storm_key})")
    print(f"{'='*70}\n")
    
    # Initialize engines
    env_engine = EnvironmentalEngine()
    constraint_engine = ConstraintEngine()
    insight_generator = InsightGenerator()
    
    results = []
    
    # Process each time point
    for i, point in enumerate(points):
        print(f"\n[{i+1}/{len(points)}] {point['time'][:16]} - {point['phase']}")
        print(f"  {point['classification']}: {point['intensity']} kt, {point['pressure']} mb")
        
        # Create advisory
        nhc = create_nhc_advisory(point)
        
        # Get environment
        env = env_engine.fetch_environmental_data(nhc.latitude, nhc.longitude)
        
        # Calculate constraints
        constraints = constraint_engine.calculate_constraints(nhc, env)
        
        # Generate insight
        insight = insight_generator.generate_insight(nhc, constraints, env)
        
        print(f"  I={constraints.I:.2f}, R={constraints.R:.2f}, S={constraints.S:.2f}, L={constraints.L:.2f}")
        print(f"  Regime: {constraints.regime}, Risk: {constraints.refusal_risk}")
        
        if constraints.gradient_hazard:
            print(f"  ⚠️  GRADIENT HAZARD")
        
        # Store result
        results.append({
            'time': point['time'],
            'phase': point['phase'],
            'intensity': point['intensity'],
            'pressure': point['pressure'],
            'I': constraints.I,
            'R': constraints.R,
            'S': constraints.S,
            'L': constraints.L,
            'dL_dt': constraints.dL_dt,
            'gradient_hazard': constraints.gradient_hazard,
            'refusal_risk': constraints.refusal_risk,
            'regime': constraints.regime,
            'insight': insight.comparative_insight
        })
    
    # Summary
    print(f"\n{'='*70}")
    print("CONSTRAINT EVOLUTION SUMMARY")
    print(f"{'='*70}\n")
    
    print(f"{'Time':<20} {'Phase':<25} {'Int':>5} {'I':>5} {'R':>5} {'S':>5} {'L':>5} {'Risk':<10}")
    print("-" * 100)
    
    for r in results:
        print(f"{r['time'][:16]:<20} {r['phase'][:25]:<25} "
              f"{r['intensity']:>5.0f} {r['I']:>5.2f} {r['R']:>5.2f} {r['S']:>5.2f} {r['L']:>5.2f} "
              f"{r['refusal_risk']:<10}")
    
    # Key findings
    print(f"\n{'='*70}")
    print("KEY FINDINGS")
    print(f"{'='*70}\n")
    
    # Find peak L
    max_L = max(results, key=lambda x: x['L'])
    print(f"✓ Maximum Admissibility (L): {max_L['L']:.3f}")
    print(f"  Time: {max_L['time'][:16]}")
    print(f"  Phase: {max_L['phase']}")
    print(f"  Intensity: {max_L['intensity']} kt")
    
    # Find min L
    min_L = min(results, key=lambda x: x['L'])
    print(f"\n✓ Minimum Admissibility (L): {min_L['L']:.3f}")
    print(f"  Time: {min_L['time'][:16]}")
    print(f"  Phase: {min_L['phase']}")
    print(f"  Intensity: {min_L['intensity']} kt")
    print(f"  Risk: {min_L['refusal_risk']}")
    
    # Find peak intensity
    max_int = max(results, key=lambda x: x['intensity'])
    print(f"\n✓ Peak Intensity: {max_int['intensity']} kt")
    print(f"  Time: {max_int['time'][:16]}")
    print(f"  L at peak: {max_int['L']:.3f}")
    print(f"  I at peak: {max_int['I']:.3f} (thermodynamic headroom)")
    
    # Gradient hazards
    hazards = [r for r in results if r['gradient_hazard']]
    if hazards:
        print(f"\n✓ Gradient Hazards Detected: {len(hazards)} times")
        for h in hazards:
            print(f"  • {h['time'][:16]}: L={h['L']:.3f}, dL/dt={h['dL_dt']:.3f}/h")
            print(f"    {h['phase']}")
    
    # Save results
    output_dir = Path("data/historical")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / f"{storm_key}_analysis.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✓ Saved detailed results to: {output_file}")
    print(f"{'='*70}\n")

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python test_historical.py <storm_name> [year]")
        print("\nAvailable storms:")
        for key in HISTORICAL_STORMS.keys():
            print(f"  - {key}")
        return 1
    
    storm_name = sys.argv[1].lower()
    year = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Build storm key
    if year:
        storm_key = f"{storm_name}_{year}"
    else:
        # Find matching storm
        matches = [k for k in HISTORICAL_STORMS.keys() if storm_name in k]
        if not matches:
            print(f"Storm '{storm_name}' not found")
            return 1
        storm_key = matches[0]
    
    test_storm(storm_key)
    return 0

if __name__ == "__main__":
    exit(main())
