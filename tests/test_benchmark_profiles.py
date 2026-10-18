"Benchmark profile declarations and sequential execution without running Docker."
import json, os, pathlib, subprocess, sys
import pytest
from screening import benchmark_profiles as bp
from screening.paths import ROOT


@pytest.mark.parametrize("name,api,eligible", [("20",20,False),("200",200,False),("2000",200,True),("16000",200,True)])
def test_default_profile_scopes(name, api, eligible):
    p = bp.profile(name)
    assert p["process_n"] == int(name) and p["api_n"] == api
    assert p["release_eligible"] is eligible


@pytest.mark.parametrize("name,api", [("1",None),("8000",None),("16000",1),("2000",True),("2000","200")])
def test_unsupported_profile_sizes_fail(name, api):
    with pytest.raises(ValueError): bp.profile(name, api)


@pytest.mark.skipif(not os.path.isfile(os.path.join(ROOT, "Makefile")), reason="Makefile is not copied into the dev image")
@pytest.mark.parametrize("fail_at,expected", [(None,[20,200,2000,16000]),(200,[20,200])])
def test_suite_runs_in_order_and_stops_on_failure(tmp_path, fail_at, expected):
    trace = tmp_path / "calls.jsonl"
    fake = tmp_path / "fake_make.py"
    fake.write_text('''import json,sys
from pathlib import Path
n=int(next(a.split('=')[1] for a in sys.argv if a.startswith('PROFILE=')))
p=Path(sys.argv[1])
with p.open('a') as f: f.write(json.dumps(n)+'\\n')
sys.exit(3 if str(n)==sys.argv[2] else 0)
''')
    result = subprocess.run(["make", "--no-print-directory", "evidence-suite", f"MAKE={sys.executable} {fake} {trace} {fail_at}"], cwd=ROOT, capture_output=True, text=True)
    assert [json.loads(line) for line in trace.read_text().splitlines()] == expected
    assert (result.returncode == 0) == (fail_at is None)
