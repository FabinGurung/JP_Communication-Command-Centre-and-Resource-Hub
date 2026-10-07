# Operations Branch / Lane Control

This is a compulsory part of the Operations repository control system.

## Resolution rule

Before ChatGPT, an automation, or a human chooses a Git branch for work:

1. Read `ops/control/control-system.json`.
2. Read `ops/control/branch-lane-registry.json`.
3. Resolve the logical lane and confirm `allowed_for_work=true`.
4. Read the owning canonical authority for the fact being changed.
5. Validate before promotion to `main`.

An unregistered branch is **not authorized for work**.

## Library mapping

- **Main Library** → `main`
- **Local Library** → `feature/daily-ops-current-work`
- **Lane Library** → `ops/control/branch-lane-registry.json`
- **Archive lanes** → `archive/*`

## Archive rule

An archive branch is frozen. Its provider branch head must equal the registry's `frozen_sha`.

The old historical names that still exist outside `archive/*` are **legacy aliases only**. They are not working lanes. Resolve each one to the archive branch listed in `legacy_aliases`.

GitHub itself supports branch rename/delete, but the currently connected GitHub tool does not expose those branch-ref mutations. Therefore the archive refs are authoritative now, while the old aliases remain pending deletion through a rename/delete-capable GitHub interface.

## Topology changes

Creating, renaming, deleting, activating, superseding or archiving a branch requires updating the registry in the same governed operation. CI fails closed on unregistered provider refs or archive SHA drift.
