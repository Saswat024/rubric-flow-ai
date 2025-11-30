import json
import re

def parse_json_response(response_text: str) -> dict:
    """
    Clean and parse JSON response from Gemini.
    Removes markdown code blocks and handles common formatting issues.
    """
    try:
        cleaned_text = response_text.strip()
        # Remove markdown code blocks if present
        if "```" in cleaned_text:
            cleaned_text = re.sub(r"```json\s*", "", cleaned_text)
            cleaned_text = re.sub(r"```\s*", "", cleaned_text)
        
        cleaned_text = cleaned_text.strip()
        return json.loads(cleaned_text)
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Original text: {response_text}")
        raise e


def compare_complexity(c1: str, c2: str) -> int:
    """
    Compare two Big-O complexity strings.
    Returns:
        -1 if c1 < c2 (c1 is better/faster)
        0 if c1 == c2
        1 if c1 > c2 (c1 is worse/slower)
    """
    # Normalize strings
    c1 = c1.replace(" ", "").lower()
    c2 = c2.replace(" ", "").lower()
    
    # Define complexity rank (lower index = better)
    ranks = {
        "o(1)": 0,
        "o(loglogn)": 1,
        "o(logn)": 2,
        "o(sqrt(n))": 3,
        "o(n)": 4,
        "o(nlogn)": 5,
        "o(nsqrt(n))": 6,
        "o(n^2)": 7,
        "o(n^2logn)": 8,
        "o(n^3)": 9,
        "o(2^n)": 10,
        "o(n!)": 11
    }
    
    # Helper to get rank with fallback
    def get_rank(c):
        if c in ranks:
            return ranks[c]
        
        # Handle K/M as N for approximation
        c_norm = c.replace('k', 'n').replace('m', 'n')
        if c_norm in ranks:
            return ranks[c_norm]
            
        # Heuristics
        
        # Check for N * sqrt(N)
        if "n" in c and "sqrt" in c:
            return 6
            
        if "log" in c:
            # Check if it's N * log... or just log...
            parts = c.split('log')
            if len(parts) > 0 and 'n' in parts[0]:
                return 5 # O(nlogn)
            return 2 # O(logn)
            
        if "^2" in c: return 7
        if "^3" in c: return 9
        if "2^" in c: return 10
        if "!" in c: return 11
        if "n" in c: return 4
        if "sqrt" in c: return 3
        
        return 12 # Unknown/High complexity
        
    r1 = get_rank(c1)
    r2 = get_rank(c2)
    
    if r1 < r2: return -1
    if r1 > r2: return 1
    return 0
