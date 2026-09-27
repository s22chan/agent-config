# Choose Compute Execution

Choose local execution or Slurm from the current process's effective cgroup,
not host-wide `nproc` or `free`.

On cgroup v2, resolve the controller path through `/proc/self/cgroup`. Derive
CPU capacity from `cpu.max` as quota divided by period. Sample `cpu.stat`'s
`usage_usec` twice at least one second apart and divide its delta by elapsed
microseconds to estimate used cores.

Read `memory.current`, `memory.max`, `memory.stat`, `memory.pressure`, and
`memory.swap.max`. Compare observed use plus requested workers and projected
peak RSS with those limits.

Keep at least 20% of the CPU quota, and no less than one core, free. Keep 10% of
the memory limit free. If raw `memory.current` would consume that reserve, count
only demonstrably reclaimable file or slab cache as headroom and only while
memory pressure is low. Cap local workers to the remaining quota.

Use Slurm when the run would consume either reserve, usage is too volatile to
assess safely, the work is sustained, or its resource demand is unknown. A
`max` or missing controller limit does not make a shared login node unlimited;
follow cluster policy and use Slurm for substantial work.

Before running a selected marked test, inspect the repository's pytest
selection defaults and include the marker explicitly when required. A clean
exit with every target deselected is not a test result.

Before allocating GPUs for a test, inspect the repository's GPU-test decorator
and visible-device policy. Request the allocation it actually requires, which
may exceed its logical rank count when the decorator reserves a fixed device
group. Mark a test that genuinely requires CUDA as `gpu`.
