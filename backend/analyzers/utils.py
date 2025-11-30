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
        "o(n^2)": 6,
        "o(n^2logn)": 7,
        "o(n^3)": 8,
        "o(2^n)": 9,
        "o(n!)": 10
    }
    
    # Helper to get rank with fallback
    def get_rank(c):
        if c in ranks:
            return ranks[c]
        # Try to handle variations like O(N) vs O(n) or O(M+N)
        # Simple heuristic: length of string often correlates with complexity for simple cases
        # but let's try to map common ones
        if "log" in c and "n" in c and "^" not in c:
            return 2 if c.count("n") == 1 else 5 # O(logn) vs O(nlogn) approx
        if "^2" in c: return 6
        if "^3" in c: return 8
        if "2^" in c: return 9
        if "!" in c: return 10
        if "n" in c: return 4
        return 11 # Unknown/High complexity
        
    r1 = get_rank(c1)
    r2 = get_rank(c2)
    
    if r1 < r2: return -1
    if r1 > r2: return 1
    return 0
