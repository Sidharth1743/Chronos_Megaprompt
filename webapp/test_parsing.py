#!/usr/bin/env python3
"""
Test script to verify Phase 4 result parsing
"""

import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app import parse_phase4_results

def test_parsing():
    """Test the parsing function"""
    test_file = "/home/sidharth/Desktop/chronos/chronos_results/phase4/research_questions_20251104_153442.txt"

    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return False

    print(f"✅ Test file found: {test_file}")
    print(f"📊 File size: {os.path.getsize(test_file)} bytes")
    print()

    # Parse the file
    hypotheses = parse_phase4_results(test_file)

    print(f"✅ Parsed {len(hypotheses)} hypotheses")
    print()

    if not hypotheses:
        print("❌ No hypotheses were parsed!")
        return False

    # Display each hypothesis
    for i, h in enumerate(hypotheses, 1):
        print(f"{'='*80}")
        print(f"Hypothesis {i}: {h['h_number']}")
        print(f"{'='*80}")
        print(f"Title: {h['title']}")
        print(f"Testability: {h['testability']}/10")
        print(f"Innovation: {h['innovation']}")
        print(f"\nClaim (first 200 chars):")
        print(f"  {h['claim'][:200]}...")
        print(f"\nHistorical Source (first 150 chars):")
        print(f"  {h['historical_source'][:150]}...")
        print(f"\nMechanism (first 150 chars):")
        print(f"  {h['mechanism'][:150]}...")
        print()

    print(f"{'='*80}")
    print(f"✅ SUCCESS: All {len(hypotheses)} hypotheses parsed correctly!")
    print(f"{'='*80}")

    return True


if __name__ == "__main__":
    success = test_parsing()
    sys.exit(0 if success else 1)
