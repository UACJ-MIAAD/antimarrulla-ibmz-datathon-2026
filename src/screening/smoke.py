"""Smoke-test the deployed hospital/service flow using synthetic profiles.
Require exact equality with the fixed-point integer reference for every profile.
Run: python -m screening.smoke [http://127.0.0.1:8080]
"""
import json, sys, time, urllib.request
from . import contract, synthetic
from .paths import MODEL_JSON


def request(url, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"} if data else {})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def main(base="http://127.0.0.1:8080"):
    model = json.load(open(MODEL_JSON))
    for _ in range(30):
        try:
            state = request(base + "/api/state")
            if state["service"].get("state") == "ok":
                break
        except OSError:
            pass
        time.sleep(1)
    else:
        sys.exit("the demo did not respond within 30 seconds")
    assert state["service"]["key_private"] is False
    import hashlib
    local = hashlib.sha256(open(MODEL_JSON, "rb").read()).hexdigest()
    assert state.get("model_sha256") == local, f"hospital model differs ({state.get('model_sha256')}) from the local model ({local})"
    print(f"service OK · architecture {state['machine']} · key {state['key_bits']} bits · model {local[:12]}")
    for profile, p in synthetic.PROFILES.items():
        r = request(base + "/api/evaluate", {"profile": profile})
        x = [p[n] for n in model["variables"]]
        ref = contract.logit_integer(model["weights_integers"], model["intercept_integer"], x)
        assert int(r["hospital"]["z_integer"]) == ref, "decrypted integer differs from the reference"
        print(f"{profile}: p={r['hospital']['probability']:.3f} · exact z · {r['timings_ms']['total_in_hospital']} ms inside the hospital")
    print("smoke OK")


if __name__ == "__main__":
    main(*sys.argv[1:])
