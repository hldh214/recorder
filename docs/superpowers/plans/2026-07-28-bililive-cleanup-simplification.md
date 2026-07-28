# Bililive Cleanup Simplification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the unfinished quarantine transaction cleanup with a small age-gated direct cleanup and update the pending service plan so it can run only while the room is settled offline.

**Architecture:** `StateAwareCleanup` owns disk pressure, terminal publication eligibility, the six-hour age gate, and identity-checked unlink. `BililiveDirectoryService` owns the room/session gate and invokes cleanup only after an available offline observation has completed directory settling. The JSONL journal retains only the durable `source_deleted` result; no delete intent, quarantine, lease, or recovery state remains because this mode has not been deployed.

**Tech Stack:** Python 3, pytest, append-only JSONL journal, directory-fd filesystem operations.

---

## Scope and File Responsibilities

- `recorder/bililive/cleanup.py`: calculate protected/eligible paths, enforce the six-hour age gate, delete oldest-first under disk pressure, and append `source_deleted`.
- `recorder/bililive/cleanup_fs.py`: perform one final directory-fd identity check and direct unlink without following symlinks.
- `recorder/bililive/journal.py`: retain ordinary `source_deleted` replay and remove undeployed quarantine transaction events.
- `recorder/bililive/models.py`: remove undeployed pending-deletion transaction models and replay fields.
- `tests/test_bililive_cleanup.py`: focused cleanup policy and filesystem-race coverage.
- `tests/test_bililive_journal.py`: simple `source_deleted` replay coverage without transaction protocol tests.
- `docs/superpowers/plans/2026-07-27-bililive-directory-publisher.md`: remove the obsolete requirement to clean on every wake while live.

### Task 1: Lock the Simplified Cleanup Contract With Failing Tests

**Files:**
- Modify: `tests/test_bililive_cleanup.py`

- [ ] **Step 1: Remove quarantine-protocol-only tests and helpers**

Delete tests whose only subject is `source_delete_intent`, quarantine naming,
delete leases, rollback/recovery paths, crash-window phases, or
`source_quarantine_removal_started`. Preserve tests for root containment,
symlinks, hard links, terminal upload states, independent FLV/XML eligibility,
dry run, disk thresholds, oldest-first order, and final identity changes.

- [ ] **Step 2: Add failing six-hour and terminal-state tests**

Use a deterministic nanosecond clock and add these cases:

```python
MIN_AGE_NS = 6 * 60 * 60 * 1_000_000_000
NOW_NS = 1_800_000_000_000_000_000


def test_cleanup_protects_processed_file_younger_than_six_hours(tmp_path):
    video, state = processed_video(tmp_path, mtime_ns=NOW_NS - MIN_AGE_NS + 1)
    _, cleanup = cleanup_for(
        tmp_path, [state], Usage(99), clock_ns=lambda: NOW_NS,
    )

    result = cleanup.run([state], dry_run=False)

    assert video.exists()
    assert result.deleted == ()
    assert video in result.protected


def test_cleanup_deletes_processed_file_at_six_hour_boundary(tmp_path):
    video, state = processed_video(tmp_path, mtime_ns=NOW_NS - MIN_AGE_NS)
    _, cleanup = cleanup_for(
        tmp_path, [state], Usage(99, 84), clock_ns=lambda: NOW_NS,
    )

    result = cleanup.run([state], dry_run=False)

    assert not video.exists()
    assert result.deleted == (video,)


def test_cleanup_never_deletes_baseline_file(tmp_path):
    video, state = baseline_video(tmp_path, mtime_ns=NOW_NS - 10 * MIN_AGE_NS)
    _, cleanup = cleanup_for(
        tmp_path, [state], Usage(99), clock_ns=lambda: NOW_NS,
    )

    result = cleanup.run([state], dry_run=False)

    assert video.exists()
    assert video in result.protected


@pytest.mark.parametrize(
    'event', ('ignored_tiny', 'ignored_invalid', 'ignored_invalid_tail')
)
def test_cleanup_deletes_old_terminal_ignored_pair(tmp_path, event):
    video, xml, state = ignored_pair(
        tmp_path, event=event, mtime_ns=NOW_NS - MIN_AGE_NS,
    )
    _, cleanup = cleanup_for(
        tmp_path, [state], Usage(99, 99, 84), clock_ns=lambda: NOW_NS,
    )

    result = cleanup.run([state], dry_run=False)

    assert result.deleted == (video, xml)
```

- [ ] **Step 3: Add a failing direct-unlink event test**

```python
def test_cleanup_direct_unlink_only_records_source_deleted(tmp_path):
    video, state = processed_video(tmp_path, mtime_ns=NOW_NS - MIN_AGE_NS)
    journal, cleanup = cleanup_for(
        tmp_path, [state], Usage(99, 84), clock_ns=lambda: NOW_NS,
    )

    cleanup.run([state], dry_run=False)

    assert [event for event, _ in journal.events] == ['source_deleted']
    assert not (tmp_path / '.bililive-cleanup-quarantine').exists()
```

- [ ] **Step 4: Run the new tests and verify RED**

Run:

```shell
.venv/bin/python -m pytest \
  tests/test_bililive_cleanup.py::test_cleanup_protects_processed_file_younger_than_six_hours \
  tests/test_bililive_cleanup.py::test_cleanup_deletes_processed_file_at_six_hour_boundary \
  tests/test_bililive_cleanup.py::test_cleanup_never_deletes_baseline_file \
  tests/test_bililive_cleanup.py::test_cleanup_direct_unlink_only_records_source_deleted -q
```

Expected: failures because cleanup has no age clock, baseline is currently eligible, and deletion emits quarantine transaction events.

### Task 2: Replace Transactional Cleanup With Direct Identity-Checked Cleanup

**Files:**
- Modify: `recorder/bililive/cleanup.py`
- Modify: `recorder/bililive/cleanup_fs.py`
- Test: `tests/test_bililive_cleanup.py`

- [ ] **Step 1: Add the age constant and injected clock**

Define the file-level constants and constructor dependency:

```python
DISK_CLEANUP_THRESHOLD_PERCENT = 85
MIN_CLEANUP_AGE_SECONDS = 6 * 60 * 60


class StateAwareCleanup:
    def __init__(
        self,
        journal,
        root,
        disk_usage=filesystem_usage_percent,
        clock_ns=time.time_ns,
    ):
        self.journal = journal
        self.root = Path(root).resolve()
        self.disk_usage = disk_usage
        self.clock_ns = clock_ns
```

A path is old enough exactly when:

```python
self.clock_ns() - file_stat.st_mtime_ns >= MIN_CLEANUP_AGE_SECONDS * 1_000_000_000
```

Future mtimes and malformed identities are protected.

- [ ] **Step 2: Narrow eligibility**

Implement these exact predicates:

```python
ignored = state.event in {
    'ignored_tiny', 'ignored_invalid', 'ignored_invalid_tail',
}
video_eligible = ignored or (
    state.youtube_processed is True
    and bool(state.video_id)
    and not state.ambiguous
)
xml_eligible = ignored or (
    state.caption_uploaded is True
    and state.caption_refresh_required is False
    and bool(state.video_id)
)
```

`baseline`, `file_ready`, `upload_started`, video retry/fatal states,
unprocessed uploaded video, ambiguous state, unknown/corrupt state, active
session paths, and invalidated/resettling manifests remain protected.

- [ ] **Step 3: Add a directory-fd direct-unlink helper**

Add this public behavior to `RootDirectory`:

```python
def unlink_source(self, path, expected_identity):
    # Resolve the relative parent beneath the already-open recorder root.
    # Open each directory with O_DIRECTORY | O_NOFOLLOW.
    # lstat the final name through dir_fd without following symlinks.
    # Require a regular file, st_nlink == 1, and exact
    # (st_dev, st_ino, st_size, st_mtime_ns) equality.
    # os.unlink(name, dir_fd=parent_fd), then fsync(parent_fd).
    # Return False on an identity/safety mismatch and True after unlink.
```

Do not call `Path.unlink`, do not create a quarantine directory, and do not
rename the source.

- [ ] **Step 4: Reduce `StateAwareCleanup.run` to one-pass decisions**

Replay the journal once, calculate control-protected paths, return below 85%,
sort eligible and old-enough candidates by `(mtime_ns, str(path))`, and for each
candidate:

```python
deleted = root_directory.unlink_source(candidate.path, candidate.identity)
if not deleted:
    protected.add(candidate.path)
    continue
journal.append(
    'source_deleted',
    fingerprint=candidate.fingerprint,
    path=str(candidate.path),
    reason='disk usage at or above 85 percent',
)
```

Recompute disk usage after every successful unlink and stop below 85%. In dry
run, return the same ordered candidates without filesystem or journal writes.
An absent candidate is protected/ignored safely; replay already prevents a
completed deleted path from becoming a candidate again.

- [ ] **Step 5: Run focused cleanup tests and verify GREEN**

Run:

```shell
.venv/bin/python -m pytest tests/test_bililive_cleanup.py -q
```

Expected: all retained cleanup policy and filesystem-safety tests pass.

- [ ] **Step 6: Commit the cleanup rewrite**

```shell
git add recorder/bililive/cleanup.py recorder/bililive/cleanup_fs.py tests/test_bililive_cleanup.py
git commit -m "refactor: simplify Bililive source cleanup"
```

### Task 3: Remove the Undeployed Quarantine Journal Protocol

**Files:**
- Modify: `recorder/bililive/journal.py`
- Modify: `recorder/bililive/models.py`
- Modify: `tests/test_bililive_journal.py`

- [ ] **Step 1: Replace transaction tests with simple deletion replay tests**

Keep or add:

```python
def test_source_deleted_marks_only_the_exact_owned_path(tmp_path):
    journal = journal_with_ready_pair(tmp_path)
    video_state = next(iter(journal.replay().files.values()))

    journal.append(
        'source_deleted',
        fingerprint=video_state.fingerprint,
        path=video_state.file,
        reason='disk usage at or above 85 percent',
    )

    replayed = journal.replay().files[video_state.fingerprint]
    assert replayed.deleted_paths == (video_state.file,)
    assert replayed.event != 'source_deleted'
```

Also assert a path not owned by the fingerprint, a relative path, a duplicate
deletion, or a deletion with an empty reason is rejected.

- [ ] **Step 2: Run deletion replay tests before removing the protocol**

Run:

```shell
.venv/bin/python -m pytest tests/test_bililive_journal.py -k source_deleted -q
```

Expected: the simple deletion cases pass; this preserves the required journal
contract before transaction code is removed.

- [ ] **Step 3: Remove transaction-only schema and reducers**

Remove `JournalDeleteIntent`, `JournalDeleteAbort`, `pending_deletions`,
`deletion_aborts`, and support for these undeployed events:

```text
source_delete_intent
source_quarantine_removal_started
quarantine_removed
source_delete_aborted
```

Retain `source_deleted` as an ordinary validated file lifecycle event that adds
the exact canonical source path to `deleted_paths` without replacing the file's
publication event.

- [ ] **Step 4: Run journal, cleanup, monitor, and runner tests**

Run:

```shell
.venv/bin/python -m pytest \
  tests/test_bililive_journal.py \
  tests/test_bililive_cleanup.py \
  tests/test_bililive_monitor.py \
  tests/test_bililive_runner.py -q
```

Expected: all tests pass.

- [ ] **Step 5: Commit journal simplification**

```shell
git add recorder/bililive/journal.py recorder/bililive/models.py tests/test_bililive_journal.py
git commit -m "refactor: remove Bililive cleanup transactions"
```

### Task 4: Correct the Pending Service Plan

**Files:**
- Modify: `docs/superpowers/plans/2026-07-27-bililive-directory-publisher.md`

- [ ] **Step 1: Replace the obsolete live-cleanup requirement**

In Task 10 of the master plan, replace “performs state-aware cleanup on every
wake even while live” with this exact predicate:

```python
cleanup_allowed = (
    room is not None
    and not room.active
    and decision.state in {SessionState.READY, SessionState.WAITING}
)
```

State that the observation/main thread records the latest room and monitor
decision under the service lock. The single worker reads the same gate before
cleanup and before each upload. It may finish an already-running upload, but it
must not start cleanup or the next upload unless the latest gate is open.

- [ ] **Step 2: Add exact cleanup-gate tests to Task 10**

Require injected fake runner and cleanup objects. Assert `cleanup.run` is not
called when room state is unavailable, `recording=True`, `streaming=True`, or
the monitor decision is `RECORDING`/`SETTLING`. Assert it is called after an
available `RoomState(False, False)` observation returns `READY`, and on later
available offline `WAITING` observations. Assert a transition back to live
closes the gate before another cleanup begins.

- [ ] **Step 3: Check the plan diff**

Run:

```shell
git diff --check -- docs/superpowers/plans/2026-07-27-bililive-directory-publisher.md
rg -n "cleanup_allowed|cleanup.*while live" docs/superpowers/plans/2026-07-27-bililive-directory-publisher.md
```

Expected: the settled-offline predicate is present and no requirement to clean
while live remains.

- [ ] **Step 4: Commit the corrected Task 10 contract**

```shell
git add docs/superpowers/plans/2026-07-27-bililive-directory-publisher.md
git commit -m "docs: gate Bililive cleanup on settled offline state"
```

### Task 5: Focused and Full Verification

**Files:**
- Modify only if verification exposes an in-scope defect.

- [ ] **Step 1: Verify all Bililive functionality**

Run:

```shell
.venv/bin/python -m pytest tests/test_bililive_*.py -q
```

Expected: all Bililive tests pass.

- [ ] **Step 2: Verify the full repository**

Run:

```shell
.venv/bin/python -m pytest -q
```

Expected: no new failures. The accepted pre-existing environment failures may
remain: three Huya DNS/network tests in `tests/test_ffmpeg.py` and one Panda
test caused by missing configuration.

- [ ] **Step 3: Inspect the final diff and source tree**

Run:

```shell
git diff --check
rg -n "source_delete_intent|source_quarantine_removal_started|quarantine_removed|source_delete_aborted|pending_deletions|cleanup.*while live" recorder tests docs/superpowers
git status --short
```

Expected: no whitespace errors; no cleanup transaction protocol remains; only
intentional feature-branch changes are present.

- [ ] **Step 4: Request code review**

Use `superpowers:requesting-code-review` against the completed diff. Resolve
only verified in-scope findings, rerun the affected focused tests, then rerun
the Bililive suite.
