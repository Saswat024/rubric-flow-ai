
import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from analyzers.utils import compare_complexity

def test_complexity_comparison():
    print("Testing complexity comparison...")
    
    # Test cases: (c1, c2, expected_result)
    # -1: c1 better, 0: equal, 1: c1 worse
    test_cases = [
        ("O(1)", "O(n)", -1),
        ("O(n)", "O(n^2)", -1),
        ("O(nlogn)", "O(n)", 1),
        ("O(n)", "O(n)", 0),
        ("O(log n)", "O(n)", -1),
        ("O(n!)", "O(2^n)", 1),
        ("O(n^2)", "O(n^2)", 0),
        ("O(n)", "O(1)", 1)
    ]
    
    passed = 0
    for c1, c2, expected in test_cases:
        result = compare_complexity(c1, c2)
        if result == expected:
            print(f"✅ {c1} vs {c2}: Expected {expected}, Got {result}")
            passed += 1
        else:
            print(f"❌ {c1} vs {c2}: Expected {expected}, Got {result}")
            
    print(f"\nPassed {passed}/{len(test_cases)} tests")

if __name__ == "__main__":
    test_complexity_comparison()
