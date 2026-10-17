# Optional two-host encrypted-flow test

The MVP uses two containers on one VM. This optional experiment places the risk service on VM A and the hospital on VM B. Synthetic inputs are the default; `DATA=cdc` explicitly selects a separate public-data benchmark. Captured evidence is an audit trail, not a formal proof of no leakage or of the provider's identity.

| Property | VM A: risk service | VM B: hospital |
|----------|--------------------|----------------|
| Holds | Service TLS certificate/key and CA certificate | Paillier private key in memory; hospital client credentials |
| Does not hold | Hospital Paillier/vault keys or hospital client credentials | No service private key required |
| Runs | `screening.service`, with `SERVICE_EVIDENCE` | `screening.two_hosts hospital` |
| Saves | Exact wire bytes and service audit log | Wire hashes, decrypted results and summary; no input vectors |

Use the same translated commit and Ubuntu images at both ends. Rebuild old containers before using the English v2 protocol. Restrict access to the intended hospital host or use an SSH tunnel.

## 0. Optional one-host rehearsal

```bash
make rehearse-two-hosts N=8
```

Expected result: **REHEARSAL PASSED**. It checks the flow but does not establish two real VMs or LinuxONE.

## 1. VM A: generate credentials

```bash
make secrets-two-hosts SERVICE_IP=VM_A_IP
```

This creates `~/.screening-two-hosts/service/certs` and moves the hospital credentials to `~/.screening-two-hosts/for_hospital`. Transfer them securely to VM B, then remove the transfer copy from VM A. The CA signing key is not retained; no vault key is created on the service host.

```bash
scp -r ~/.screening-two-hosts/for_hospital USER@VM_B:~/.screening-two-hosts/
```

If hosts cannot connect by SSH, use two transfers through the operator's laptop. Preserve restrictive file permissions. Never commit credentials or include them in screenshots.

## 2. VM A: run the service

```bash
make service-remote-docker
```

The service remains in the foreground; stop with Ctrl+C. Prefer an SSH tunnel from VM B:

```bash
ssh -N -L 8443:localhost:8443 USER@VM_A
```

Then use `SERVICE_URL=https://localhost:8443`; localhost is included in the certificate SAN. For direct networking, restrict firewall access to VM B's IP rather than broadly opening access. Do not expose the hospital UI or disable certificate verification.

## 3. VM B: evaluate encrypted synthetic inputs

```bash
make hospital-remote-docker SERVICE_URL=https://VM_A_IP:8443 N=200
```

Generate deterministic synthetic inputs (seed 2026), encrypt, send over mutual TLS 1.3, decrypt and compare exact integers. Verify remote code/model hashes before measuring. Synthetic inputs have no observed clinical labels, so AUC/sensitivity are not reported. The service records IDs, byte sizes, hashes, TLS identity and `private_key_in_memory=False`.

For a separate labeled public CDC benchmark:

```bash
make hospital-remote-docker SERVICE_URL=https://VM_A_IP:8443 N=200 DATA=cdc
```

Only this mode can compute AUC/sensitivity, and only if both classes are present. It is not clinical validation and does not replace the synthetic demonstration.

## 4. Audit on VM A

Copy VM B's `hospital_log` directory to the corresponding external directory on A, then run:

```bash
scp -r USER@VM_B:~/.screening-two-hosts/hospital_log ~/.screening-two-hosts/
make audit-two-hosts-docker
```

Reports `audit_TIMESTAMP.md/.json` and sample wire pairs go to `submission/evidence/two_hosts/`. The audit checks:

1. Matching request/response SHA-256 across both endpoints and intact saved files.
2. Exact protocol fields, 21 ciphertexts, correct group/size properties and no plaintext inputs.
3. Randomized ciphertexts despite repeated underlying input values.
4. No decrypted integer/logit/probability or small 21-value input vector in service evidence.
5. No live Python Paillier private-key object at service startup or request handling.
6. TLS 1.3 and hospital client identity.
7. Present, distinct host IDs; different container hostnames do not establish host separation.
8. Exact reference integers and applicable labeled-data metrics.
9. Hospital log hash/counts matching its summary.
10. Matching code/model hashes at hospital, service health and service startup.

Strict mode returns PASSED or FAILED, with exit code 1 on failure. The same-host override always remains REHEARSAL. Commit the report, not credential directories or private patient logs. Complete raw service evidence, approximately 27 KB/request, remains outside Git.

## Scope and limits

- Captured bytes, versions and results can be compared; Python object inspection is not proof that a key never existed or that the administrator/hypervisor cannot access it.
- Declared machine IDs require corroborating evidence of both VMs. They can be spoofed by an administrator and do not identify the cloud provider.
- This experiment does not measure CPACF or replace the LinuxONE dashboard/architecture evidence.
- The direct hospital client includes inter-host networking but excludes the UI API, browser and vault. Use `make measure-api-docker` for the complete deployed hospital API/vault path; these are different timing operations.
- The hospital log contains decrypted results. Copying it for operator audit is a later operation, outside the inference service process; do not claim those audit copies are ciphertext-only.
- Public CDC `record_id` can reconstruct the public source row. Renaming an ID does not increase anonymity.
