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


def _parse_complexity_factors(c: str) -> dict:
    """
    Parse a complexity string into its component factors.
    Returns a dict with factor weights for comparison.

    Factor weights (for combining multiplicative factors):
    - 1: O(1) constant
    - log: O(log n) logarithmic
    - sqrt: O(sqrt n)
    - linear: O(n) or O(k) etc
    - nlogn: O(n log n) linearithmic
    - quadratic: O(n^2)
    - cubic: O(n^3)
    - exponential: O(2^n)
    - factorial: O(n!)
    """
    c = c.replace(" ", "").lower()

    # Remove O() wrapper
    if c.startswith("o(") and c.endswith(")"):
        c = c[2:-1]

    factors = {
        "constant": 0,
        "log_count": 0,  # Number of log factors
        "sqrt_count": 0,
        "linear_count": 0,  # Number of n/k/m/l variables
        "quadratic": False,
        "cubic": False,
        "exponential": False,
        "factorial": False,
    }

    # Check for exponential/factorial first (they dominate)
    if "!" in c:
        factors["factorial"] = True
        return factors
    if re.search(r"2\^[nkml]", c) or re.search(r"[nkml]\^[nkml]", c):
        factors["exponential"] = True
        return factors

    # Check for polynomial powers
    power_match = re.search(r"\^(\d+)", c)
    if power_match:
        power = int(power_match.group(1))
        if power >= 3:
            factors["cubic"] = True
        elif power >= 2:
            factors["quadratic"] = True

    # Count log factors (log n, log k, log l, log m)
    log_matches = re.findall(r"log\s*[nkml]?", c)
    factors["log_count"] = len(log_matches)

    # Remove log expressions for counting linear variables
    c_no_log = re.sub(r"log\s*[nkml]?", "", c)

    # Count sqrt factors
    sqrt_matches = re.findall(r"sqrt\s*\(?[nkml]?\)?", c_no_log)
    factors["sqrt_count"] = len(sqrt_matches)

    # Remove sqrt expressions
    c_no_sqrt = re.sub(r"sqrt\s*\(?[nkml]?\)?", "", c_no_log)

    # Count linear variables (n, k, m, l) - each occurrence is a factor
    linear_matches = re.findall(r"[nkml]", c_no_sqrt)
    factors["linear_count"] = len(linear_matches)

    # If nothing found and string is "1", it's constant
    if (
        factors["linear_count"] == 0
        and factors["log_count"] == 0
        and factors["sqrt_count"] == 0
        and not factors["quadratic"]
        and not factors["cubic"]
    ):
        factors["constant"] = 1

    return factors


def _complexity_weight(factors: dict) -> float:
    """
    Calculate a numerical weight for complexity comparison.
    Higher weight = worse complexity.
    """
    if factors["factorial"]:
        return 1000
    if factors["exponential"]:
        return 500
    if factors["cubic"]:
        return 100
    if factors["quadratic"]:
        return 50

    # For polynomial and below, calculate based on factors
    # Base weight for linear factors (each n/k/l/m adds multiplier)
    weight = 0

    if factors["constant"] == 1 and factors["linear_count"] == 0:
        return 0.1  # O(1)

    # Each linear variable multiplies complexity
    # O(n) = 10, O(n*k) = 20, O(n*k*m) = 30
    weight += factors["linear_count"] * 10

    # Each log adds a smaller factor
    # O(n log n) is between O(n) and O(n^2)
    # O(n * k log k) is between O(n*k) and O(n*k^2)
    weight += factors["log_count"] * 3

    # sqrt is between O(1) and O(n)
    weight += factors["sqrt_count"] * 5

    # If only logs (no linear), it's very efficient
    if factors["linear_count"] == 0 and factors["log_count"] > 0:
        weight = factors["log_count"] * 2

    return weight if weight > 0 else 0.1


def compare_complexity(c1: str, c2: str) -> int:
    """
    Compare two Big-O complexity strings.
    Returns:
        -1 if c1 < c2 (c1 is better/faster)
        0 if c1 == c2
        1 if c1 > c2 (c1 is worse/slower)

    Handles multi-variable expressions like:
    - O(N * K) vs O(N * K log K) -> N*K is better
    - O(N log N) vs O(N^2) -> N log N is better
    - O(N * L log L) vs O(N * K) -> N*K is better (assuming L≈K)
    """
    # Normalize strings
    c1 = c1.replace(" ", "").lower()
    c2 = c2.replace(" ", "").lower()

    # Quick equality check
    if c1 == c2:
        return 0

    # Normalize variable names for comparison (all become 'n')
    def normalize_vars(c):
        return re.sub(r"[klm]", "n", c)

    c1_norm = normalize_vars(c1)
    c2_norm = normalize_vars(c2)

    if c1_norm == c2_norm:
        return 0

    # Parse and compare factors
    f1 = _parse_complexity_factors(c1)
    f2 = _parse_complexity_factors(c2)

    w1 = _complexity_weight(f1)
    w2 = _complexity_weight(f2)

    print(f"Complexity comparison: {c1} (weight={w1}) vs {c2} (weight={w2})")

    if w1 < w2:
        return -1
    if w1 > w2:
        return 1
    return 0


def compare_overall_complexity(time1: str, space1: str, time2: str, space2: str) -> int:
    """
    Compare overall complexity considering both time and space.
    Time complexity takes priority, space is used as tiebreaker.

    Returns:
        -1 if solution1 is better (lower time, or equal time with lower space)
        0 if equal (both time and space are the same)
        1 if solution2 is better
    """
    time_comparison = compare_complexity(time1, time2)

    if time_comparison != 0:
        return time_comparison

    # Time is equal, use space as tiebreaker
    return compare_complexity(space1, space2)
