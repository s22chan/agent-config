# Evorun Environment

- Treat `evorun` as snapshotting the current checkout at submission. For A/B
  arms that use different revisions, create a separate detached worktree at
  each exact revision under a collision-free temporary parent and submit from
  that worktree. Never switch the shared primary checkout or move a shared ref.
  Record each submitted revision, then remove only the exact clean worktree
  created for that arm without `--force`; leave and report any worktree whose
  state is not known clean.
- Source `/mnt/main0/home/steve.chan/wandb/.env.wandb` inside the generated
  Slurm task before starting an online W&B run. Sourcing it only in the
  submitting shell does not propagate the API key through `evorun`.
- When a run depends on uncommitted configuration-schema or trainer-plumbing
  changes, create it with `evorun --dry-run`. Inspect both the archived source
  and generated script, then submit that exact script with `sbatch`; do not
  create a second unverified snapshot.
- Store transient or paired-replay checkpoints under local `/bio/projects`.
  Do not upload them to remote storage unless the user explicitly requests
  durable retention.
