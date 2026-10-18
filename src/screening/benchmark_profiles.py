"""Declared benchmark sizes: small diagnostics and release-sized comparisons.
Process counts refer to labeled CDC records; API counts refer to synthetic requests.
"""
SIZES = (20, 200, 2000, 16000)
DEFAULT = "2000"


def profile(name=DEFAULT, api_n=None):
    if str(name) not in tuple(map(str, SIZES)):
        raise ValueError("profile must be 20, 200, 2000 or 16000")
    n = int(name)
    api = min(n, 200) if api_n is None else api_n
    if type(api) is not int or api not in SIZES:
        raise ValueError("API sample must be 20, 200, 2000 or 16000")
    return {"name": str(n), "process_n": n, "api_n": api, "https_n": min(n, 200),
            "release_eligible": n >= 2000 and api >= 200}


def release_size(mode, n):
    return type(n) is int and n in SIZES and n >= (2000 if mode == "process" else 200)


def sample_size(available, maximum, budget_s, seconds_per_patient, requested=None):
    "Explicit sample counts never shrink to fit an adaptive time budget."
    if requested is not None:
        if type(requested) is not int or requested < 8 or requested > available:
            raise ValueError(f"requested sample must be between 8 and {available}")
        return requested
    return min(int(min(maximum, max(100, budget_s / seconds_per_patient))), available)
