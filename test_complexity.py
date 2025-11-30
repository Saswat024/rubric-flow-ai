
import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from analyzers.utils import compare_complexity

def test_comprehensive_complexities():
    print("Testing comprehensive complexities...")
    
    # (c1, c2, expected) -> -1 if c1 < c2, 0 if c1 == c2, 1 if c1 > c2
    test_cases = [
        # Standard
        ("O(1)", "O(log n)", -1),
        ("O(log n)", "O(n)", -1),
        ("O(n)", "O(n log n)", -1),
        ("O(n log n)", "O(n^2)", -1),
        ("O(n^2)", "O(n^3)", -1),
        ("O(n^3)", "O(2^n)", -1),
        ("O(2^n)", "O(n!)", -1),
        
        # Variations
        ("O(log k)", "O(n)", -1), # Assuming k <= n usually, or at least log k < n
        ("O(n log k)", "O(n)", 1), # n log k > n
        ("O(n log k)", "O(n log n)", 0), # Roughly same class if k ~ n
        ("O(n + k)", "O(n)", 0), # Linear sum vs linear
        ("O(n + m)", "O(n^2)", -1), # Linear sum vs quadratic
        
        # Sqrt cases
        ("O(sqrt(n))", "O(n)", -1),
        ("O(n sqrt(n))", "O(n log n)", 1), # n^1.5 > n log n
        ("O(n sqrt(n))", "O(n^2)", -1), # n^1.5 < n^2
        
        # Formatting
        ("O( N )", "O(n)", 0),
        ("O(n^2 + n)", "O(n^2)", 0), # Dominant term
    ]
    
    passed = 0
    failed = 0
    
    for c1, c2, expected in test_cases:
        try:
            result = compare_complexity(c1, c2)
            
            # For 0 (equal), we might accept loose equality if we can't distinguish
            # But for strict inequalities, we want to be correct.
            
            is_pass = False
            if expected == 0:
                is_pass = (result == 0)
            else:
                is_pass = (result == expected)
                
            if is_pass:
                print(f"✅ {c1} vs {c2}: Got {result}")
                passed += 1
            else:
                print(f"❌ {c1} vs {c2}: Expected {expected}, Got {result}")
                failed += 1
        except Exception as e:
            print(f"❌ {c1} vs {c2}: ERROR {e}")
            failed += 1
            
    print(f"\nPassed {passed}/{len(test_cases)} tests")

if __name__ == "__main__":
    test_comprehensive_complexities()
