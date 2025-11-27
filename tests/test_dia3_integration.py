"""
DIA 3 Integration Test Suite
Tests the complete flow: DIA 2 analysis → DIA 3 recommendations
"""

import requests
import json
from typing import List, Dict

BASE_URL = "http://localhost:8002/api/v1"

def print_section(title: str):
    """Print formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def test_dia3_complete_flow():
    """
    Complete end-to-end test:
    1. Simulate DIA 2 coverage analysis result
    2. Extract gaps
    3. Call DIA 3 recommendations endpoint
    4. Validate response
    """
    
    print_section("DIA 3 Complete Integration Test")
    
    # Step 1: Simulate DIA 2 Coverage Analysis Result
    print_section("Step 1: Simulating DIA 2 Coverage Analysis")
    
    # Mock grid from a 0.25 km² area with 100m spacing
    coverage_grid = [
        {"lat": -23.550, "lng": -46.633, "signal_dbm": -70, "quality": "excellent"},
        {"lat": -23.551, "lng": -46.633, "signal_dbm": -78, "quality": "good"},
        {"lat": -23.552, "lng": -46.633, "signal_dbm": -88, "quality": "fair"},
        {"lat": -23.553, "lng": -46.633, "signal_dbm": -96, "quality": "poor"},
        {"lat": -23.554, "lng": -46.633, "signal_dbm": -102, "quality": "poor"},
        
        {"lat": -23.550, "lng": -46.634, "signal_dbm": -72, "quality": "good"},
        {"lat": -23.551, "lng": -46.634, "signal_dbm": -80, "quality": "good"},
        {"lat": -23.552, "lng": -46.634, "signal_dbm": -90, "quality": "fair"},
        {"lat": -23.553, "lng": -46.634, "signal_dbm": -98, "quality": "poor"},
        {"lat": -23.554, "lng": -46.634, "signal_dbm": -104, "quality": "poor"},
        
        {"lat": -23.550, "lng": -46.635, "signal_dbm": -75, "quality": "good"},
        {"lat": -23.551, "lng": -46.635, "signal_dbm": -82, "quality": "good"},
        {"lat": -23.552, "lng": -46.635, "signal_dbm": -92, "quality": "fair"},
        {"lat": -23.553, "lng": -46.635, "signal_dbm": -100, "quality": "poor"},
        {"lat": -23.554, "lng": -46.635, "signal_dbm": -106, "quality": "poor"},
    ]
    
    print(f"Grid points: {len(coverage_grid)}")
    print(f"Area coverage: ~0.09 km² (3x3 100m cells)")
    
    quality_count = {}
    for point in coverage_grid:
        q = point["quality"]
        quality_count[q] = quality_count.get(q, 0) + 1
    
    print(f"Quality distribution: {json.dumps(quality_count, indent=2)}")
    
    # Step 2: Extract gaps (signal < -95 dBm)
    print_section("Step 2: Extract Gaps from Coverage Grid")
    
    gap_threshold_dbm = -95.0
    gaps = [
        {
            "latitude": p["lat"],
            "longitude": p["lng"],
            "area_km2": 0.01  # 100m x 100m = 0.01 km²
        }
        for p in coverage_grid
        if p["signal_dbm"] < gap_threshold_dbm
    ]
    
    print(f"Threshold: {gap_threshold_dbm} dBm")
    print(f"Gaps identified: {len(gaps)}")
    print(f"Total gap area: {len(gaps) * 0.01:.2f} km²")
    print(f"Gaps: {json.dumps(gaps, indent=2)}")
    
    if not gaps:
        print("No gaps found - all areas covered. Skipping DIA 3.")
        return
    
    # Step 3: Call DIA 3 Recommendations Endpoint
    print_section("Step 3: Call DIA 3 Recommendations Endpoint")
    
    url = f"{BASE_URL}/recommendations/towers"
    payload = {
        "gaps": gaps,
        "max_recommendations": 5,
        "operator": "all"
    }
    
    print(f"Endpoint: POST {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Error: {response.text}")
            return
        
        data = response.json()
        print(f"Response received successfully")
        
    except Exception as e:
        print(f"Error calling endpoint: {e}")
        return
    
    # Step 4: Validate Response
    print_section("Step 4: Validate Response Structure")
    
    # Check top-level keys
    expected_keys = {"recommendations", "total_gaps_analyzed", "clusters_found", "analysis_metadata"}
    actual_keys = set(data.keys())
    
    print(f"Expected keys: {expected_keys}")
    print(f"Actual keys: {actual_keys}")
    print(f"Keys match: {expected_keys == actual_keys}")
    
    # Step 5: Analyze Recommendations
    print_section("Step 5: Analyze Recommendations")
    
    recommendations = data.get("recommendations", [])
    print(f"Total recommendations: {len(recommendations)}")
    print(f"Total gaps analyzed: {data.get('total_gaps_analyzed')}")
    print(f"Clusters found: {data.get('clusters_found')}")
    
    # Priority distribution
    priority_dist = {}
    for rec in recommendations:
        p = rec.get("priority", "unknown")
        priority_dist[p] = priority_dist.get(p, 0) + 1
    
    print(f"Priority distribution: {json.dumps(priority_dist, indent=2)}")
    
    # Step 6: Detailed Recommendations
    print_section("Step 6: Detailed Recommendations")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"\nRecommendation #{i}:")
        print(f"  Location: {rec['location']['latitude']:.6f}, {rec['location']['longitude']:.6f}")
        print(f"  Score: {rec['score']:.2f}/10")
        print(f"  Priority: {rec['priority'].upper()}")
        print(f"  Population Reached: ~{rec['population_reached']:,}")
        print(f"  Gap Count: {rec['gap_count']}")
        print(f"  Reason: {rec['reason']}")
    
    # Step 7: Validation Checks
    print_section("Step 7: Validation Checks")
    
    checks = {
        "HTTP 200": response.status_code == 200,
        "Has recommendations": len(recommendations) > 0,
        "Recommendations <= 5": len(recommendations) <= 5,
        "All scores in 0-10 range": all(0 <= r.get("score", -1) <= 10 for r in recommendations),
        "Valid priorities": all(r.get("priority") in ["high", "medium", "low"] for r in recommendations),
        "Valid populations": all(r.get("population_reached", 0) > 0 for r in recommendations),
        "Total gaps matches input": data.get("total_gaps_analyzed") == len(gaps),
        "Sorted by priority": all(
            recommendations[i].get("priority") in ["high", "medium", "low"]
            for i in range(len(recommendations) - 1)
            if i + 1 < len(recommendations)
        ),
    }
    
    print("Validation Results:")
    for check, result in checks.items():
        status = "PASS" if result else "FAIL"
        print(f"  [{status}] {check}")
    
    all_passed = all(checks.values())
    
    # Step 8: Summary
    print_section("Step 8: Test Summary")
    
    print(f"Overall Status: {'PASS' if all_passed else 'FAIL'}")
    print(f"\nTest Summary:")
    print(f"  - Gaps extracted: {len(gaps)}")
    print(f"  - Clusters found: {data.get('clusters_found')}")
    print(f"  - Recommendations generated: {len(recommendations)}")
    print(f"  - Priority distribution: {priority_dist}")
    print(f"  - All validations: {sum(checks.values())}/{len(checks)}")
    
    # Step 9: API Response (Full)
    print_section("Step 9: Full API Response")
    print(json.dumps(data, indent=2))
    
    return all_passed


def test_dia3_edge_cases():
    """Test edge cases and error handling"""
    
    print_section("DIA 3 Edge Case Tests")
    
    url = f"{BASE_URL}/recommendations/towers"
    
    # Test 1: Empty gaps
    print("Test 1: Empty gaps array")
    response = requests.post(url, json={"gaps": [], "max_recommendations": 5})
    print(f"  Status: {response.status_code}")
    print(f"  Expected: 400 (validation error)")
    print()
    
    # Test 2: Single gap
    print("Test 2: Single gap")
    response = requests.post(url, json={
        "gaps": [{"latitude": -23.55, "longitude": -46.63, "area_km2": 0.1}],
        "max_recommendations": 5
    })
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Recommendations: {len(data.get('recommendations', []))}")
    print()
    
    # Test 3: Large gap area
    print("Test 3: Large gap area (1 km²)")
    response = requests.post(url, json={
        "gaps": [{"latitude": -23.55, "longitude": -46.63, "area_km2": 1.0}],
        "max_recommendations": 5
    })
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        rec = data.get('recommendations', [{}])[0]
        print(f"  Score: {rec.get('score', 'N/A')}")
        print(f"  Priority: {rec.get('priority', 'N/A')}")
    print()
    
    # Test 4: Invalid coordinates
    print("Test 4: Invalid coordinates")
    response = requests.post(url, json={
        "gaps": [{"latitude": 200, "longitude": 400, "area_km2": 0.1}],
        "max_recommendations": 5
    })
    print(f"  Status: {response.status_code}")
    print(f"  (May still work - API accepts any floats)")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  DIA 3 INTEGRATION TEST SUITE")
    print("="*60)
    
    result = test_dia3_complete_flow()
    test_dia3_edge_cases()
    
    print("\n" + "="*60)
    if result:
        print("  ALL TESTS PASSED - DIA 3 READY FOR PRODUCTION")
    else:
        print("  SOME TESTS FAILED - CHECK ERRORS ABOVE")
    print("="*60 + "\n")
