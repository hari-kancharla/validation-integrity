# Frozen artifacts

Every file below is frozen: it is not edited after the moment recorded here. Verify with

    shasum -a 256 -c DIGESTS.sha256

| File | Frozen at | SHA-256 |
|---|---|---|
| `protocol.md` | K1 Phase 1 | 8918931244e66df65536c350312dd6df092146cb5b898d357a9e5be491805aee |
| `lint_cases.py` | K1 Phase 2 | 5f983f32a26c70ecb26e57d822184c2a1c5da9e0609d4d11fa87d010754d3ec3 |
| `lint_payloads.py` | K1 Phase 2 | 696dd6e876299c0a4b9eff31cdce9c3e973417ff2ddd1d9ac0af77c8166f997e |
| `protocol_k2.md` | K2 Step 5 | 0b59b1713f33b4a41a371375b09c7f9e34634e0009a8c16fc1605c1d051e77a3 |
| `protocol_k3.md` | K3 Step 1, before any K3 artifact | ae42be19bc346f18552977dad2827915f3e94fca6fe247c929d563fcac9baeb9 |
| `mechanism_subset.json` | K3 Step 4, before any mechanism-tier call | 33f24786ac7d1427164f074d48ace318d45bdbbcd88116d2e5e37d1d2d7a28c7 |

`mechanism_subset.json` was drawn from a pool of 98 cases whose
digest is `28e310d26dff0d6f2865bf52c4419996cc0782b1e381860472546f5b91d29025`. That digest covers exactly what the draw reads:
each case's id, tier and domain. Re-derive the list with

    .venv/bin/python mechanism_subset.py

which prints the same 30 ids for the same pool, or reports that the pool has moved.
