"Exercise the browser batch state machine with simulated requests, never a load test."
import os, re, shutil, subprocess
import pytest
from screening.paths import ROOT


@pytest.mark.skipif(shutil.which("node") is None, reason="Node is only needed for frontend state-machine checks")
def test_browser_batch_sizes_cancellation_failures_and_identity():
    page = open(os.path.join(ROOT,"src/screening/ui/index.html")).read()
    engine = re.search(r"// BEGIN BATCH_ENGINE(.*?)// END BATCH_ENGINE",page,re.S).group(1)
    single = re.search(r"(async function evaluate\(body,k\).*?)(?=function render)",page,re.S).group(1)
    harness = r'''
const assert=require('node:assert/strict');
let busy=false,batching=false,rendered=false;const nodes={hospital:{innerHTML:''},service:{innerHTML:''}},document={body:{classList:{remove(){}}}};function $(id){return nodes[id]}function markProfile(){}function lockControls(){}function escapeHtml(s){return String(s)}async function api(){return {hospital:{integer_reference_match:false}}}function render(){rendered=true}
const config={api_sizes:[20,200,2000,16000],warmup:3,seed:2026,code_sha256:'a'.repeat(64),model_sha256:'b'.repeat(64)};
const state=()=>({machine:'SIMULATION',system:'SIMULATION',code_sha256:config.code_sha256,model_sha256:config.model_sha256,service:{state:'ok',key_private:false,code_sha256:config.code_sha256,model_sha256:config.model_sha256}});
function fixture(options={}){let calls=0,clock=0,states=0;const seeds=[];const run=new ApiBatchRun({config,now:()=>++clock,state:async()=>{states++;const s=state();if(options.drift&&states===2)s.machine='changed';return s},request:async body=>{calls++;seeds.push(body.synthetic_seed);if(options.failAt===calls)throw Error('simulated HTTP 502');return {id:options.duplicate?'duplicate':String(calls),synthetic:true,code_sha256:config.code_sha256,model_sha256:config.model_sha256,hospital:{integer_reference_match:options.inexactAt!==calls},timings_ms:{total_in_hospital:1}}},onResult:(r,i)=>{if(options.stopAt===i)run.stop()}});return {run,calls:()=>calls,seeds}}
(async()=>{
 await evaluate({},null);assert.equal(rendered,false);assert.equal(busy,false);assert.match(nodes.hospital.innerHTML,/result withheld/);
 for(const n of config.api_sizes){const f=fixture(),r=await f.run.run(n);assert.equal(r.status,'completed');assert.equal(r.completed,n);assert.equal(r.exact,n);assert.equal(r.client_ms.n,n);assert.equal(f.calls(),n+3);assert.deepEqual(f.seeds,Array.from({length:n+3},(_,i)=>2026+i))}
 let f=fixture({stopAt:5}),r=await f.run.run(16000);assert.equal(r.status,'cancelled');assert.equal(r.completed,5);assert.equal(f.calls(),8);
 f=fixture({failAt:5});r=await f.run.run(200);assert.equal(r.status,'failed');assert.equal(r.completed,1);assert.equal(f.calls(),5);
 f=fixture({inexactAt:4});r=await f.run.run(20);assert.equal(r.status,'failed');assert.equal(r.completed,0);
 f=fixture({duplicate:true});r=await f.run.run(20);assert.equal(r.status,'failed');assert.equal(r.completed,1);
 f=fixture({drift:true});r=await f.run.run(20);assert.equal(r.status,'failed');assert.match(r.error,/changed/);
 await assert.rejects(()=>fixture().run.run(1),/Unsupported/);
 const offline=fixture();offline.run.state=async()=>{throw Error('offline')};r=await offline.run.run(20);assert.equal(r.status,'failed');assert.equal(offline.calls(),0);
 assert.deepEqual(ApiBatchRun.stats([1,2,3,4]),{n:4,p50_ms:2.5,p95_ms:3.8499999999999996,mean_ms:2.5});
 console.log('Simulated sizes, stop-on-failure, cancellation, exactness, identity and linear percentiles passed');
})().catch(e=>{console.error(e);process.exit(1)});
'''
    result = subprocess.run(["node"],input=engine+single+harness,text=True,capture_output=True)
    assert result.returncode == 0, result.stderr
