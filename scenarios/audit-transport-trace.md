# Audit transport evidence

## Observed incident

The user requested `$audit-change (ignore the requirements/*.txt)` for the
Modal folding clients in `/mnt/main0/home/steve.chan/review`, comparing tip
`1e57cd6890c13ff8480cfa37dc5ec3b60f588ca7` with base
`b79f1ad127ac6ce0e9827f1a218affce5151da11`.

The audit inspected application dictionaries and lists but omitted the SDK
serialization and transport path. A later payload explanation also stopped at
the Python objects. The user replied:

> that doesn't explain what format it goes on teh wire

After a separate SDK inspection, the user requested:

> did the audit do this exploration?  if not can we add this as part of the audit

Initial audit evidence should trace the encoded representation and its owning
dependency before reviewers judge correctness or performance at that boundary.
The installed Modal 1.5.1 SDK inspection established default cloudpickle
protocol 4, optional CBOR, protobuf RPC envelopes, and blob routing. Effective
remote configuration and deployment metadata remained unobserved.

## Replay inputs

Use fresh contexts to prepare initial audit evidence, stopping before reviewer
dispatch or findings. Give each context only its workflow version and these
three cases. Permit read-only repository and installed-dependency inspection;
forbid mutations, remote calls, tests, and descendants. Request inspected
artifacts, observed implementation facts, a packet plan, specific gaps, and the
loaded workflow digest. Keep inputs and sample counts equal between arms.

1. The observed repository, revisions, and audit request above. Changed code is
   under `evolutionaryscale/utils/biotools/modal_folding/` and
   `projects/folding/modal_external/`, with changes to `pyproject.toml` and
   `ty.toml.laptop`. The worktree is clean. Requirements contents are excluded.
2. A patch adds `store_measurements(store, measurements)` calling
   `store.write({'values': measurements.tolist()})`. The manifest and lockfile
   resolve Store 2.4. Its supplied writer packs the object with
   `msgpack.packb(value, use_bin_type=True)`, compresses using
   `zstandard.ZstdCompressor(level=3)`, writes the compressed length as eight
   little-endian bytes, then writes the compressed bytes. The consumer reads
   the framing, decompresses, and unpacks the original list. No latency claim
   is supplied.
3. A patch adds `local_means(rows)` returning
   `[sum(row) / len(row) for row in rows]`. Its sole consumer computes a local
   aggregate. There is no file access, external collaborator, process handoff,
   or performance claim.

## Recorded replay

One fresh context per arm prepared all three cases from the same inputs.
The baseline workflow digest was
`dd1eef0fc170933caf608b5fe1c552a6f7525b67c2840095bf80b4ab2cb3f174`;
the edited workflow digest was
`8a46b5b58fb9b2e15afb8d43724dfad1d6bffc12f5895810531f56aaf713e697`.

For the Modal case, the baseline inspected the serializer and blob handling but
omitted the protocol envelope and network transport from its evidence index:
full boundary coverage was 0/1 baseline and 1/1 edited. The edited arm included
protobuf envelopes, gRPC framing, and HTTP blob transfer. Both arms traced the
compressed-storage case, 1/1 each, and avoided transport exploration for the
local calculation, 1/1 each.

The baseline replay did more SDK exploration than the original audit, so these
results establish only the narrower envelope/transport improvement. A single
sample per arm does not estimate reliability. Neither arm measured runtime
performance or exercised a live deployment.
