#!/usr/bin/env python3
"""Run the actual 21-feature project tests rather than a separate reference protocol.
Use the project environment Python from any working directory. Save pytest output and
execution provenance; s390x alone does not identify the cloud provider.
"""
import argparse
import datetime
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from screening import provenance


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, default=ROOT / "submission/evidence/instance")
    args = ap.parse_args()
    tests = ["tests/test_protocol.py", "tests/test_integration.py", "tests/test_measurement.py"]
    command = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", *tests]
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    run = subprocess.run(command, cwd=ROOT, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(run.stdout, end="")
    now = datetime.datetime.now(datetime.timezone.utc)
    args.output.mkdir(parents=True, exist_ok=True)
    base = args.output / ("claims_proyecto_" + now.strftime("%Y%m%dT%H%M%S%fZ"))
    log = base.with_suffix(".log")
    log.write_text(run.stdout, encoding="utf-8")
    record = {"date_utc": now.isoformat(), "kind": "tests_of_proyecto_cdc21",
                "architecture": platform.machine(), "python": platform.python_version(),
                "linuxone": "unverified: compare with the Community Cloud dashboard",
                "tests": tests, "pytest_exit_code": run.returncode,
                "provenance": provenance.capture(), "log": log.name,
                "log_sha256": provenance.sha256(log)}
    base.with_suffix(".json").write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Project evidence:", base.with_suffix(".json"))
    return run.returncode


if __name__ == "__main__":
    sys.exit(main())
