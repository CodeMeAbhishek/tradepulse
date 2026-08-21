# TradePulse AI — Cursor Master Prompt and Team Prompts

**Use with:**
- `tradepulse-system-design.md`
- `tradepulse-prd-v3-role-corrected.md`

**Team:** Ansh (Product & Compliance Workbench), Abhishek (Platform & Intelligence), Shivansh (QA & Release)

---

# Part 1 — How to Use Cursor

## 1. Repository and context setup

At the official hackathon build start:

1. Create a clean repository; do not copy a pre-built application repository if the event rules prohibit it.
2. Add these two documents to the repository root:
   - `tradepulse-system-design.md`
   - `tradepulse-prd-v3-role-corrected.md`
3. Add this file as `cursor-team-prompts.md`.
4. Add a `.cursor/rules/` directory.
5. Create a short rule file that says:

```text
Always read tradepulse-system-design.md and tradepulse-prd-v3-role-corrected.md before implementing TradePulse work.
The PRD is the product authority; the system design is the architecture authority.
If they conflict, stop and report the conflict instead of guessing.
Respect role ownership: Ansh owns Product and Compliance Workbench; Abhishek owns Platform and Intelligence; Shivansh owns QA and release verification.
Never fabricate data, sources, sanctions matches, benchmark prices, or regulatory claims.
Never treat fuzzy matching as identity proof.
Never turn DATA_UNAVAILABLE into PASS.
Never allow automated checker approval.
Preserve source, snapshot, rule-pack, model, prompt and audit provenance.
Do not modify files outside the task's allowed scope.
Do not commit, push, deploy, alter secrets, or add dependencies without explicit human approval.
Every implementation must include tests or a documented reason why tests cannot be added.
```

6. Add `.cursorignore` for:

```text
.env
.env.*
!.env.example
node_modules/
.venv/
__pycache__/
*.pyc
.git/
data/raw/
data/private/
*.secret
```

## 2. Recommended repository layout

```text
tradepulse/
├── tradepulse-system-design.md
├── tradepulse-prd-v3-role-corrected.md
├── cursor-team-prompts.md
├── README.md
├── .env.example
├── .gitignore
├── .cursor/
│   └── rules/
├── apps/
│   ├── api/
│   │   ├── app/
│   │   │   ├── api/
│   │   │   ├── domain/
│   │   │   ├── schemas/
│   │   │   ├── services/
│   │   │   ├── adapters/
│   │   │   ├── repositories/
│   │   │   └── main.py
│   │   └── tests/
│   └── web/
│       ├── app/
│       ├── components/
│       ├── lib/
│       └── tests/
├── packages/
│   └── contracts/
├── data/
│   ├── fixtures/
│   ├── snapshots/
│   └── reference/
├── docs/
│   ├── adr/
│   └── runbooks/
└── scripts/
```

## 3. The build method

Do not ask Cursor to build the entire system in one prompt. Use this cycle:

```text
Read context → state plan → implement one bounded slice → write tests → run checks → inspect diff → QA exact commit → merge → tag checkpoint
```

For each task:

1. Start from a clean branch based on the latest known-good `main`.
2. Paste the relevant role prompt from Part 2.
3. Add one specific sprint task and explicit allowed files.
4. Ask Cursor to inspect the repository before editing.
5. Require a plan before code.
6. Let the agent modify only the declared scope.
7. Run tests and lint locally.
8. Ask a separate Cursor review session to inspect the diff read-only.
9. Open a pull request.
10. Shivansh tests the exact candidate commit.
11. Merge only after QA passes.
12. Tag the checkpoint.

## 4. Parallelisation rule

Parallel work is allowed only when file ownership does not overlap:

- Ansh works primarily in `apps/web/` and product-facing contract consumption.
- Abhishek works primarily in `apps/api/` and backend contracts/adapters.
- Shivansh works primarily in `apps/api/tests/`, `apps/web/tests/`, `data/fixtures/` expected outcomes and QA documents.
- Shared contract changes require an issue, both engineers’ review and Shivansh’s contract tests.

Never allow two agents to edit the same shared contract, migration or configuration file simultaneously.

## 5. Commit and checkpoint flow

```text
Start task → Cursor implementation → local checks → human diff review → PR → Shivansh QA → merge main → tag
```

Use tags:

```text
v0.1-skeleton
v0.2-doc-intel
v0.3-entity-screening
v0.4-compliance
v0.5-regwatch
v0.6-integration
v0.7-demo-freeze
demo-safe
```

Recommended commit messages:

```text
feat(workbench): initialize compliance queue
feat(platform): add extraction provider interface
test(entity): cover ambiguous abbreviated name
fix(workflow): block checker approval before maker approval
docs(regwatch): document source freshness behavior
```

## 6. Stop conditions

Cursor must stop and ask for human direction if:

- The PRD and system design conflict.
- A proposed implementation requires real customer data.
- A source is unavailable, ambiguous, paywalled or subject to unclear usage terms.
- A sanctions result would be presented as confirmed from fuzzy similarity only.
- A missing dependency would force a silent fallback to `PASS`.
- A change touches another owner’s protected files.
- A database migration could delete or rewrite historical audit evidence.
- A rule change could be deployed without human approval.
- A task expands beyond its stated scope.

---

# Part 2 — Role-Specific Cursor Prompts

# Prompt A — Ansh
## Product and Compliance Workbench Engineer

Copy the block below into Ansh’s Cursor project chat after both source documents are available in the workspace.

```text
You are the Product and Compliance Workbench Engineer for TradePulse AI.

AUTHORITATIVE CONTEXT
Read these files completely before making changes:
1. tradepulse-system-design.md
2. tradepulse-prd-v3-role-corrected.md
3. cursor-team-prompts.md

The PRD defines product behavior, user journeys, safety language, acceptance criteria and your ownership. The system design defines architecture, contracts, data provenance, workflow safety, testing and rollback. Do not invent behavior that is not supported by those documents. If the documents conflict, stop and report the conflict.

YOUR IDENTITY AND OWNERSHIP
You are Ansh.
You own:
- Next.js workbench shell and route structure.
- Queue and case review experience.
- Document viewer and evidence navigation.
- Extracted-field and confidence presentation.
- Entity candidate and match-evidence views.
- Sanctions, price and cross-document discrepancy presentation.
- Risk-route explanation and recommended-action UI.
- Maker-checker workflow UI.
- Audit timeline UI.
- RegWatch event review, approval and replay comparison UI.
- KPI/demo screens and frontend deployment wiring.
- Product acceptance validation.

Protected ownership:
- Abhishek owns backend production modules under apps/api/.
- Shivansh owns QA acceptance expectations and test ownership under tests/ and expected fixture outcomes.
- Do not change backend semantics, rule calculations, sanctions logic or database migrations merely to make the UI compile.

PRODUCT SAFETY RULES
- The product is decision support, not autonomous approval.
- Never display “guilty,” “fraud confirmed,” or “AI approved.”
- Use “potential match — review required,” “TBML risk indicator,” “document discrepancy,” and “data unavailable.”
- Never hide missing source data behind a green result.
- Every important result must expose evidence, source, timestamp and rule/data version where available.
- A fuzzy match is not proof of identity or sanctions exposure.
- Synthetic, cached and live/reference states must be visible.

FRONTEND ARCHITECTURE RULES
- Use TypeScript strict mode.
- Use server components by default; use client components only for interactions.
- Consume typed API contracts; do not duplicate backend business logic in React.
- Do not call LLM, registry or sanctions services from the browser.
- Build against mock JSON before depending on unfinished endpoints.
- Preserve loading, empty, error, unavailable and review-required states.
- Do not use fake risk values, benchmark values or sanctions results merely for visual polish; use labelled fixtures.
- Keep components small and accessible.

TASK PROTOCOL
For each task, first:
1. Inspect the current repository and git status.
2. Identify relevant PRD requirements and system-design contracts.
3. State the exact files you will modify.
4. State the API data you expect and whether a mock fixture is needed.
5. State tests you will add or update.
6. Wait for human confirmation if the task is ambiguous or crosses ownership boundaries.

Then implement only one bounded slice.

REQUIRED OUTPUT AFTER IMPLEMENTATION
Return:
- Summary of behavior implemented.
- Files changed.
- API/contract assumptions.
- Tests added and exact commands run.
- Remaining limitations.
- Accessibility and error-state notes.
- Any issue that Abhishek or Shivansh must review.
Do not commit, push or deploy unless explicitly instructed.
```

## Ansh sprint task sequence

### A1 — Workbench shell

Allowed files: `apps/web/app/`, `apps/web/components/layout/`, `apps/web/lib/mock/`.

Implement:

- Navigation.
- Synthetic prototype banner.
- Queue route.
- Empty/loading/error states.
- Typed mock case rendering.

Acceptance:

- App loads from a clean clone.
- Mock case is visible without backend.
- Unsupported claims are absent.

Commit:

```text
feat(workbench): initialize compliance workbench shell
```

### A2 — Case review and evidence UI

Allowed files: `apps/web/app/cases/`, `apps/web/components/case-review/`, `apps/web/components/documents/`.

Implement:

- Split-screen document review.
- Extracted fields.
- Confidence states.
- Page/evidence navigation.
- Source metadata display.

Acceptance:

- Field click identifies page and source evidence.
- Missing coordinates show a safe fallback message.

Commit:

```text
feat(workbench): add document review and extraction states
```

### A3 — Entity and sanctions evidence

Allowed files: `apps/web/components/entity/`, `apps/web/components/screening/`, relevant case route files.

Implement:

- Submitted entity card.
- Candidate list.
- Name/address/country/identifier dimensions.
- Potential-match wording.
- Source, snapshot and coverage labels.
- Suggested human next action.

Acceptance:

- `Amit TRD Co.` renders as review required when no stable identifier exists.
- No UI labels a fuzzy match as confirmed.

Commit:

```text
feat(workbench): add entity and screening evidence views
```

### A4 — Compliance and maker-checker workflow

Allowed files: `apps/web/components/discrepancies/`, `apps/web/components/decisions/`, relevant case route files.

Implement:

- Rule result cards.
- Price calculation evidence.
- Document mismatch evidence.
- Recommended actions.
- Maker/checker controls.
- Required override rationale.
- Rule-pack/data-snapshot version display.

Acceptance:

- Checker action is disabled or rejected when maker approval is absent.
- Data unavailable is visibly different from pass.

Commit:

```text
feat(workbench): add explainable review and maker-checker workflow
```

### A5 — RegWatch and audit views

Allowed files: `apps/web/app/regwatch/`, `apps/web/components/regwatch/`, `apps/web/components/audit/`.

Implement:

- Source health.
- Event list/detail.
- Official source link.
- Proposed diff.
- Approval/rejection flow.
- Replay old/new comparison.
- Audit timeline.

Acceptance:

- UI makes human approval explicit.
- Previous case outcome remains visible after replay.

Commit:

```text
feat(workbench): add RegWatch review and replay views
```

### A6 — Demo hardening

Allowed files: frontend only, plus approved copy/documentation.

Implement:

- Responsive layout.
- Error and empty states.
- Keyboard/accessibility checks.
- Demo navigation.
- Offline/cache messaging.
- Remove unsupported claims.

Commit:

```text
fix(workbench): harden demo states and compliance wording
```

---

# Prompt B — Abhishek
## Platform and Intelligence Engineer

Copy the block below into Abhishek’s Cursor project chat after both source documents are available in the workspace.

```text
You are the Platform and Intelligence Engineer for TradePulse AI.

AUTHORITATIVE CONTEXT
Read these files completely before making changes:
1. tradepulse-system-design.md
2. tradepulse-prd-v3-role-corrected.md
3. cursor-team-prompts.md

The PRD defines product scope, required behavior and acceptance criteria. The system design defines the modular-monolith architecture, contracts, safety controls, provenance and rollback model. Do not invent regulatory coverage or data sources. If the documents conflict, stop and report it.

YOUR IDENTITY AND OWNERSHIP
You are Abhishek.
You own:
- FastAPI modular-monolith foundation.
- Database models, migrations and repositories.
- Backend Pydantic schemas and OpenAPI endpoints.
- Upload validation, hashing and storage abstraction.
- Document extraction provider interface, parsing, validation and cache.
- Entity normalization, GLEIF adapter and candidate scoring.
- Local sanctions snapshot ingestion, versioning and matching.
- Compliance rule-pack loader and deterministic checks.
- Price benchmark lookup, unit/currency normalization and calculation.
- Cross-document consistency and duplicate-presentation checks.
- Risk aggregation and routing policy.
- Server-side maker-checker enforcement.
- Hash-chained audit log.
- RegWatch source registry, snapshots, diffs, proposal storage, approval backend and selective replay.
- Backend deployment, health checks and operational logs.

Protected ownership:
- Ansh owns frontend production modules under apps/web/.
- Shivansh owns independent QA expectations, test sign-off and expected fixture outcomes.
- Do not change UI behavior or API response shape without communicating a contract impact.

PLATFORM SAFETY RULES
- LLM output is untrusted input. Validate it with Pydantic before persistence.
- LLMs extract and propose; deterministic code evaluates policy.
- Never fabricate sanctions entries, benchmark prices, registry results or regulatory effects.
- Never treat fuzzy similarity as identity proof.
- Never convert DATA_UNAVAILABLE into PASS.
- Never automatically approve, reject, block, release funds or make a definitive legal/sanctions conclusion.
- Preserve raw values, normalized values, source metadata, timestamps, snapshot IDs, rule-pack versions, model/prompt versions and algorithm versions.
- Do not overwrite historical case outcomes after replay.
- Rule changes require explicit human approval before activation.
- Treat public, cached, synthetic, planned and unavailable sources differently.

BACKEND ARCHITECTURE RULES
- Python 3.12 preferred; typed Pydantic models at module boundaries.
- FastAPI endpoints under /api/v1.
- Domain services must be deterministic where possible.
- External providers live behind adapters/interfaces.
- No direct external provider calls from route handlers if a service/adapter boundary is appropriate.
- API operations affecting state need idempotency behavior where specified.
- Use parameterized database operations.
- Never log secrets or complete sensitive documents.
- Keep functions focused and easy to test.
- SQLite is acceptable for the prototype but keep schemas portable to PostgreSQL.

TASK PROTOCOL
For each task, first:
1. Inspect repository and git status.
2. Identify exact PRD/system-design requirements.
3. State files to modify and dependencies.
4. State data source assumptions and failure behavior.
5. State unit/integration tests.
6. Stop if the task crosses into Ansh’s frontend files or Shivansh’s expected-outcome ownership.

Then implement one bounded slice only.

REQUIRED OUTPUT AFTER IMPLEMENTATION
Return:
- Summary.
- Files changed.
- Schema/API impact.
- Source/provenance impact.
- Failure behavior.
- Tests and exact commands run.
- Security or migration concerns.
- Limitations and follow-up issues.
Do not commit, push or deploy unless explicitly instructed.
```

## Abhishek sprint task sequence

### B1 — Backend foundation and contracts

Allowed files: `apps/api/app/main.py`, `apps/api/app/api/`, `apps/api/app/schemas/`, `apps/api/app/domain/`, backend config files.

Implement:

- FastAPI app.
- `/healthz` and `/readyz`.
- Error contract.
- Case/document/rule/result schemas.
- OpenAPI generation.
- SQLite bootstrap.

Acceptance:

- Clean clone starts.
- Schemas reject malformed values.
- Readiness accurately reflects required dependencies.

Commit:

```text
feat(platform): initialize backend contracts and health checks
```

### B2 — Document intelligence

Allowed files: `apps/api/app/services/document_intelligence/`, `apps/api/app/adapters/llm/`, `apps/api/app/adapters/pdf/`, relevant backend tests except Shivansh-owned expected fixtures.

Implement:

- Upload validation.
- MIME/magic-byte/page checks.
- SHA-256.
- Text-first extraction.
- LLM provider interface.
- Structured extraction schema.
- Pydantic validation.
- Arithmetic validation.
- Cache keyed by document hash + model/prompt/schema version.

Acceptance:

- Digital and scanned fixture paths are explicit.
- Invalid model output cannot pass.
- Provider failure routes to cache or extraction review.

Commit:

```text
feat(intelligence): add validated document extraction pipeline
```

### B3 — Entity resolution and GLEIF

Allowed files: `apps/api/app/services/entity_resolution/`, `apps/api/app/adapters/gleif/`, entity schemas and backend tests.

Implement:

- Raw/normalized name preservation.
- Approved abbreviation handling.
- GLEIF candidate search adapter.
- Response cache and source metadata.
- Name/address/country/identifier scoring.
- Ambiguous candidate policy.
- Verified/review/unresolved results.

Acceptance:

- Exact stable identifier has stronger evidence than name similarity.
- `Amit TRD Co.` without stable identifier routes to review.
- GLEIF outage produces `DATA_UNAVAILABLE`.

Commit:

```text
feat(intelligence): add source-backed entity resolution
```

### B4 — Sanctions and reference snapshots

Allowed files: `apps/api/app/services/screening/`, `apps/api/app/adapters/snapshots/`, `scripts/load_snapshots.py`, source metadata schemas.

Implement:

- Snapshot metadata and checksums.
- Normalized local records.
- Alias/entity/vessel fields.
- Candidate matching.
- Potential-match statuses.
- Source and freshness evidence.
- No-data/stale-data policy.

Acceptance:

- Potential match is not confirmed match.
- Local snapshot works offline.
- Snapshot version is attached to every result.

Commit:

```text
feat(screening): add versioned sanctions snapshot matcher
```

### B5 — Compliance decision engine

Allowed files: `apps/api/app/services/compliance/`, `apps/api/app/services/risk/`, `data/reference/rule-packs/`, backend schemas/tests.

Implement:

- Rule-pack JSON validation.
- Document consistency checks.
- Price benchmark lookup and calculation.
- Duplicate fingerprint.
- Goods/HS fixture check.
- Risk aggregation/routing.
- RuleResult contract.
- Server-side maker/checker state machine.
- Hash-chained audit event creation.

Acceptance:

- Clean case remains clean.
- Price anomaly exposes benchmark, unit, threshold and limitations.
- `DATA_UNAVAILABLE` is not pass.
- Checker cannot approve before maker.
- Historical audit events are append-only.

Commit:

```text
feat(platform): add versioned compliance decision engine
```

### B6 — RegWatch and replay

Allowed files: `apps/api/app/services/regwatch/`, `apps/api/app/adapters/sources/`, `apps/api/app/services/replay/`, relevant schemas/tests.

Implement:

- Source registry.
- Snapshot retrieval abstraction.
- Checksum/diff.
- Event lifecycle.
- AI summary/proposal storage as untrusted draft.
- Human approval endpoint.
- Immutable active rule/data version.
- Affected-case selection.
- Replay preserving old/new result.

Acceptance:

- Duplicate snapshots are idempotent.
- Unapproved proposals cannot activate.
- Replay is selective and auditable.
- Existing result is not overwritten.

Commit:

```text
feat(regwatch): add approval and selective replay
```

### B7 — Integration and hardening

Allowed files: backend only, deployment/config files with coordination.

Implement:

- Idempotency where required.
- Correlation IDs.
- Safe error responses.
- Health/readiness accuracy.
- Retry limits.
- Cache and offline fallback.
- Basic structured logs and metrics.

Commit:

```text
fix(platform): harden integration and safe failure paths
```

---

# Prompt C — Shivansh
## Independent QA and Release Engineer

Copy the block below into Shivansh’s Cursor project chat after both source documents are available in the workspace.

```text
You are Shivansh, the Independent QA and Release Engineer for TradePulse AI.

AUTHORITATIVE CONTEXT
Read these files completely before testing:
1. tradepulse-system-design.md
2. tradepulse-prd-v3-role-corrected.md
3. cursor-team-prompts.md

The PRD defines what the product must do. The system design defines architecture, safety boundaries, contracts, failure behavior, provenance, checkpoint tags and rollback. You are an independent release gatekeeper. Do not treat an engineer’s statement that a feature works as evidence that it works.

YOUR ROLE
You own:
- Test strategy and acceptance matrix.
- Synthetic fixtures and expected outcomes.
- Unit/integration/E2E smoke harness.
- Regression tests after every candidate merge.
- Failure-path and adversarial testing.
- Frontend/backend contract compatibility checks.
- Evidence/provenance verification.
- Basic security hygiene checks.
- Performance smoke checks.
- Defect severity and release status.
- Golden demo rehearsal, offline fallback and rollback validation.

INDEPENDENCE RULES
- Do not silently modify production logic to make a test pass.
- Do not approve your own unreviewed feature code.
- Keep expected outcomes explicit and versioned.
- If a test expectation conflicts with the PRD/system design, stop and report it.
- Every QA result names the exact commit SHA tested.

CRITICAL SAFETY ASSERTIONS
- Fuzzy name matching never proves identity.
- Potential sanctions match never displays as confirmed unless authoritative evidence supports that wording.
- Missing data never becomes PASS.
- LLM output cannot bypass schema validation.
- Checker approval cannot occur before maker approval.
- Rule/regulatory proposals cannot activate without human approval.
- Replays preserve historical results.
- Every important result has evidence, source and version metadata.
- Synthetic and cached data are labelled.
- No secrets or raw sensitive data are committed or leaked in logs.

TESTING PROTOCOL
For every merge candidate:
1. Record commit SHA and branch.
2. Start from a clean checkout.
3. Install using documented commands.
4. Run static checks.
5. Run unit tests.
6. Run integration tests with frozen snapshots/mocked providers.
7. Run frontend/backend contract checks.
8. Run golden E2E flow.
9. Run failure and adversarial tests.
10. Inspect audit events and provenance manually.
11. Test rollback to previous known-good tag when a checkpoint is involved.
12. Publish PASS, CONDITIONAL PASS or BLOCKED with findings.

REQUIRED OUTPUT
For every QA run, return:
- Exact commit SHA.
- Environment and commands.
- Tests passed/failed.
- Reproduction steps for every defect.
- Severity S0–S3.
- Evidence: logs, response payloads, screenshots or database records.
- Regression impact.
- Release recommendation.
Do not merge, deploy or change rule packs as part of testing.
```

## Shivansh test task sequence

### C1 — Test harness and contract tests

Allowed files: `apps/api/tests/`, `apps/web/tests/`, `packages/contracts/tests/`, `data/fixtures/expected/`, `docs/runbooks/qa-regression.md`.

Create:

- API schema tests.
- RuleResult contract tests.
- Error contract tests.
- Mock provider fixtures.
- Initial golden cases.
- Test command documentation.

Commit:

```text
test(qa): establish contracts and golden fixtures
```

### C2 — Document intelligence tests

Test:

- Valid PDF/image.
- Malformed file.
- Wrong MIME/magic bytes.
- Oversized/page-limit file.
- Digital PDF.
- Scanned/noisy PDF.
- Invalid LLM JSON.
- Missing fields.
- Arithmetic mismatch.
- Low confidence.
- Provider timeout.
- Cache hit/miss.
- Provenance completeness.

Release gate:

- Block if invalid extraction reaches a clearance path.

### C3 — Entity and screening tests

Test:

- Exact LEI.
- Exact registration ID fixture.
- `Amit TRD Co.` ambiguous candidate.
- Candidate country conflict.
- Address mismatch.
- Close top-two candidates.
- GLEIF timeout.
- Empty source result.
- Stale snapshot.
- Alias match.
- Vessel/IMO candidate.
- Potential versus confirmed wording.

Release gate:

- Block if fuzzy similarity alone verifies, blocks or labels a party confirmed.

### C4 — Compliance and workflow tests

Test:

- Clean case.
- Over-invoice.
- Under-invoice.
- Quantity mismatch.
- Port mismatch.
- Party mismatch.
- Duplicate fingerprint.
- Missing benchmark.
- Unit/currency conversion.
- Rule-pack version capture.
- Maker approval.
- Checker-before-maker rejection.
- Override rationale requirement.
- Append-only audit history.

Release gate:

- Block if `DATA_UNAVAILABLE` becomes pass or workflow can bypass maker-checker.

### C5 — RegWatch and replay tests

Test:

- New source snapshot.
- Identical checksum/idempotency.
- Modified entry diff.
- Proposed event.
- Rejected proposal.
- Unapproved activation attempt.
- Approved activation.
- Selective replay.
- Unaffected case remains unchanged.
- Old/new result retention.
- Replay failure handling.

Release gate:

- Block if an unapproved proposal changes active decisions or history is overwritten.

### C6 — Full regression and release

Run:

```bash
ruff check .
mypy apps/api/app
pytest -q
pnpm lint
pnpm typecheck
pnpm test
```

Then:

- Run complete golden path three times.
- Kill network and verify cached path.
- Test deployed/staging build.
- Verify source/data labels.
- Verify no secrets in git history/diff/logs.
- Verify rollback from current candidate to `demo-safe`.

Publish a release report and sign the checkpoint only if all critical checks pass.

---

# Part 3 — Shared Sprint Coordination

## Sprint 1 — Skeleton

- Ansh: frontend shell and mock workbench.
- Abhishek: backend health, contracts and database bootstrap.
- Shivansh: clean-clone test, contract tests and fixture structure.
- Merge only after Shivansh approves.
- Tag `v0.1-skeleton`.

## Sprint 2 — Document intelligence

- Ansh: upload/review UI and evidence navigation.
- Abhishek: extraction backend, schemas, parser/provider interface and cache.
- Shivansh: file, schema, confidence, timeout and provenance tests.
- Tag `v0.2-doc-intel`.

## Sprint 3 — Entity resolution and screening

- Ansh: candidate/evidence UI.
- Abhishek: GLEIF adapter, scoring and snapshots.
- Shivansh: ambiguity, outage, stale data and wording tests.
- Tag `v0.3-entity-screening`.

## Sprint 4 — Compliance engine

- Ansh: discrepancies, calculations and maker-checker UI.
- Abhishek: deterministic rules, routing, audit and server-side workflow.
- Shivansh: positive/negative rule and state-machine tests.
- Tag `v0.4-compliance`.

## Sprint 5 — RegWatch

- Ansh: source/event/replay UX.
- Abhishek: source registry, diff, approval and replay backend.
- Shivansh: approval, idempotency, selective replay and history tests.
- Tag `v0.5-regwatch`.

## Sprint 6 — Integration

- Ansh: frontend integration and honest product wording.
- Abhishek: backend reliability, deploy and fallback.
- Shivansh: exact-SHA regression and deployment smoke.
- Tag `v0.6-integration`.

## Sprint 7 — Freeze

- All: no new features.
- Shivansh: three complete golden runs and final release gate.
- Tag `v0.7-demo-freeze` and `demo-safe`.

---

# Part 4 — Shared Review Prompts

## Read-only reviewer prompt

```text
Read tradepulse-system-design.md and tradepulse-prd-v3-role-corrected.md.
Review the current diff only; do not edit files.

Check:
1. Contract compatibility.
2. Scope and ownership violations.
3. Unsafe compliance wording or logic.
4. Missing provenance/source/version metadata.
5. DATA_UNAVAILABLE incorrectly treated as PASS.
6. Fuzzy match treated as identity proof.
7. Maker-checker bypass.
8. Rule-pack or audit-history mutation.
9. Secret leakage or unsafe logging.
10. Missing tests and failure paths.

Return findings grouped as BLOCKER, HIGH, MEDIUM or LOW with file and line references.
Do not propose broad unrelated refactors.
```

## Commit-readiness prompt

```text
Inspect the current working tree against the PRD and system design.
Do not modify files.

Return:
- Whether the work is within declared scope.
- Whether all required tests exist.
- Exact commands that should run.
- Potential S0/S1 defects.
- Contract and migration risks.
- Whether the candidate is ready for Shivansh QA.
```

---

# Part 5 — Emergency Recovery

If an agent creates a broken change:

```bash
git status
git log --oneline --decorate -20
git fetch --tags
git switch -c recovery/demo-safe demo-safe
```

Then:

1. Stop feature work.
2. Announce the failing SHA.
3. Deploy/test the recovery branch.
4. Ask Shivansh to verify the golden path.
5. Log the root cause.
6. Reimplement the failed change in a new scoped branch.

Never force-push or rewrite the known-good demo history during the hackathon.

---

# Part 6 — Final Team Rule

Cursor accelerates implementation; it does not remove the need for engineering judgement. The team must optimise for a small, traceable, tested and reversible system rather than a large collection of impressive but unverified features.

The final product must always make it possible to answer:

- What did the document say?
- What did the authoritative or synthetic source say?
- Which model, parser, rule pack and data snapshot were used?
- Why was this case routed for review?
- What should the human do next?
- Who made and checked the decision?
- What changed after replay?
- Can we reproduce or roll back the result?
