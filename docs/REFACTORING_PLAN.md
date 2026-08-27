# TradePulse Refactoring Plan

**Analysis Date:** 2026-08-27  
**Branch:** `code-refactor`  
**Status:** In Progress

---

## Executive Summary

This document outlines refactoring opportunities identified in the TradePulse codebase through comprehensive static analysis. The goal is to improve maintainability, testability, and code quality without changing external behavior.

**Scope:**
- Backend: `apps/api/app/` (Python 3.11+, FastAPI)
- Frontend: `apps/web/` (Next.js 15, React 19, TypeScript)
- Shared: `packages/contracts/` (Python + TypeScript mirror)

**Key Metrics:**
- Python Backend: 93 files, ~10K lines
- TypeScript Frontend: ~31K lines
- Critical long functions: 5 (>150 lines)
- Major duplication patterns: 3
- Type safety issues: 8 instances

---

## Priority Issues

### 🔴 P0: Critical Refactorings (High Impact)

#### 1. Break Up `process_case` Function

**File:** `apps/api/app/services/case_service.py:205-402`  
**Size:** 197 lines  
**Complexity:** Very High  
**Status:** 🔲 Not Started

**Issue:**
Single function orchestrates:
- Document processing
- Extraction pipeline
- Cross-document reconciliation
- Identity resolution
- Compliance screening
- Duplicate detection
- Risk routing
- Version management

**Impact:**
- Difficult to test individual logic branches
- Hard to debug failures
- Mixed abstraction levels
- High cognitive load

**Refactoring Plan:**
Break into 8 focused functions:
```python
def process_case(case_id: str, *, state: PlatformState | None = None) -> dict[str, Any]:
    platform = state or get_platform_state()
    case = platform.cases.require(case_id)
    
    _transition_to_processing(case)
    policy = _evaluate_policy(case)
    
    # Document processing
    extraction_result = _process_invoice(case, platform)
    bol_result = _process_bol(case, platform)
    
    if extraction_result:
        # Intelligence pipeline
        reconciliation = _reconcile_documents(case, extraction_result, bol_result)
        identity = _resolve_identity(case, extraction_result, platform)
        findings = _run_compliance_checks(case, extraction_result, bol_result, identity, platform)
        risk = _route_risk(findings, policy)
    else:
        findings = []
        risk = _default_risk_route()
    
    # Finalization
    _record_result_version(case, findings, risk, reconciliation, policy)
    _transition_to_maker(case)
    
    return _build_workbench_response(case, policy, findings, reconciliation, identity, risk)
```

**Benefits:**
- Each function testable in isolation
- Clear responsibility boundaries
- Easier to add new processing steps
- Better error handling per stage

---

#### 2. Replace Global State with Dependency Injection

**File:** `apps/api/app/services/case_service.py:46-73`  
**Status:** 🔲 Not Started

**Issue:**
```python
_STATE: PlatformState | None = None

def get_platform_state() -> PlatformState:
    global _STATE
    if _STATE is None:
        _STATE = PlatformState()
    return _STATE
```

**Problems:**
- Not thread-safe
- Makes testing difficult (requires manual `reset_platform_state()`)
- Tight coupling across service layer
- Cannot run isolated tests

**Refactoring Plan:**
Use FastAPI dependency injection:

```python
# app/deps.py
from typing import Annotated

async def get_platform_state() -> PlatformState:
    """FastAPI dependency for platform state. Override in tests."""
    if not hasattr(get_platform_state, "_state"):
        get_platform_state._state = PlatformState()
    return get_platform_state._state

PlatformStateDep = Annotated[PlatformState, Depends(get_platform_state)]

# app/api/v1/cases.py
@router.post("/cases/{case_id}/process")
def process_case_endpoint(
    case_id: str,
    state: PlatformStateDep
) -> dict:
    return process_case(case_id, state=state)

# tests/conftest.py
@pytest.fixture
def mock_state():
    return MockPlatformState()

@pytest.fixture
def client(mock_state):
    app.dependency_overrides[get_platform_state] = lambda: mock_state
    yield TestClient(app)
    app.dependency_overrides.clear()
```

**Benefits:**
- Thread-safe
- Testable (dependency overrides)
- Explicit dependencies
- No global mutation

---

#### 3. Refactor `CaseWorkbench` Component

**File:** `apps/web/components/case/CaseWorkbench.tsx:155-693`  
**Size:** 538 lines  
**Complexity:** Very High  
**Status:** 🔲 Not Started

**Issue:**
Single component handles:
- Tab navigation (7 tabs)
- API calls and state management
- Modal logic
- Evidence toggling
- Examiner pack download
- Audit timeline
- Maker/checker actions
- Multiple `useEffect` hooks with complex dependencies

**Impact:**
- Unmaintainable
- Untestable (no way to unit test individual tab logic)
- Difficult to add new tabs or features
- Props drilling

**Refactoring Plan:**

**Phase 1: Extract Custom Hooks**
```typescript
// hooks/useCaseData.ts
export function useCaseData(caseId: string) {
  const [data, setData] = useState<TradeCase | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    fetchCase(caseId).then(setData).catch(setError);
  }, [caseId]);
  
  return { data, loading, error, refetch: () => fetchCase(caseId) };
}

// hooks/useCaseActions.ts
export function useCaseActions(caseId: string, onSuccess: () => void) {
  const applyAction = useCallback((action: string, comment?: string) => {
    return applyCaseAction(caseId, action, comment).then(onSuccess);
  }, [caseId, onSuccess]);
  
  const downloadPack = useCallback(() => {
    return downloadExaminerPack(caseId);
  }, [caseId]);
  
  return { applyAction, downloadPack };
}
```

**Phase 2: Extract Tab Components**
```typescript
// components/case/tabs/InvestigateTab.tsx
export function InvestigateTab({ case: tradeCase }: { case: TradeCase }) {
  const [expandedEvidence, setExpandedEvidence] = useState<Set<string>>(new Set());
  // Tab-specific logic
  return <div>...</div>;
}

// Similar for:
// - ChecksTab.tsx
// - ReconciliationTab.tsx
// - IdentityTab.tsx
// - RiskTab.tsx
// - DecideTab.tsx
// - AuditTab.tsx
```

**Phase 3: Refactor Main Component**
```typescript
// components/case/CaseWorkbench.tsx (orchestrator only)
export function CaseWorkbench({ caseId }: { caseId: string }) {
  const [tab, setTab] = useState<TabId>("investigate");
  const { data: tradeCase, loading, error, refetch } = useCaseData(caseId);
  const actions = useCaseActions(caseId, refetch);
  
  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorDisplay error={error} />;
  if (!tradeCase) return <NotFound />;
  
  return (
    <div>
      <CaseHeader case={tradeCase} onDownloadPack={actions.downloadPack} />
      <TabNavigation current={tab} onChange={setTab} />
      <TabContent tab={tab} case={tradeCase} actions={actions} />
    </div>
  );
}
```

**Benefits:**
- Each tab testable in isolation
- Clear separation of concerns
- Easier to add new tabs
- Reduced props drilling
- Better performance (each tab can memoize independently)

---

#### 4. Split `case_service.py` into Focused Modules

**File:** `apps/api/app/services/case_service.py` (443 lines)  
**Status:** 🔲 Not Started

**Issue:**
Single file contains:
- State management (`PlatformState`)
- Case CRUD operations
- Document processing orchestration
- Policy evaluation
- Identity resolution orchestration
- Compliance checks orchestration
- Workflow transitions
- Version management
- DTO mapping

**Refactoring Plan:**
```
services/case/
    __init__.py           # Public API exports
    state.py              # PlatformState class
    crud.py               # create_case, add_document, get_case
    processing.py         # process_case orchestration (after split)
    actions.py            # apply_case_action, workflow transitions
    mappers.py            # to_case_record, to_case_summary DTOs
    policy.py             # Policy evaluation helpers
```

**Migration Strategy:**
1. Create new module structure
2. Move functions one by one with tests
3. Update imports in `__init__.py`
4. Update all consumers to import from submodules
5. Delete old `case_service.py`

**Benefits:**
- Clear module boundaries
- Easier to navigate codebase
- Better test organization
- Reduced cognitive load

---

### 🟡 P1: Code Duplication (Medium Priority)

#### 5. Consolidate Datetime Utilities

**Status:** 🔲 Not Started

**Locations:**
- `apps/api/app/services/case_service.py:76` (`_now()`)
- `apps/api/app/adapters/gleif/base.py:37` (`utc_now()`)
- `apps/api/app/repositories/case_store.py:51-52` (inline `datetime.now(timezone.utc)`)
- 14+ call sites across codebase

**Issue:**
Three different implementations of the same functionality with inconsistent naming.

**Refactoring Plan:**
Create shared utility:

```python
# apps/api/app/utils/datetime.py
"""Shared datetime utilities for TradePulse."""
from datetime import datetime, timezone

def utc_now() -> datetime:
    """
    Return current UTC datetime with timezone info.
    
    Use this instead of datetime.now() to ensure all timestamps
    are timezone-aware and in UTC.
    
    Returns:
        datetime: Current time in UTC with tzinfo=timezone.utc
    """
    return datetime.now(timezone.utc)
```

**Replacement:**
```bash
# Search and replace:
datetime.now(timezone.utc) → utc_now()
_now() → utc_now()
```

**Benefits:**
- Single source of truth
- Consistent naming
- Self-documenting (clear that we always use UTC)
- Easy to mock in tests

---

#### 6. Consolidate Status Label Mapping

**Status:** 🔲 Not Started

**Locations:**
- `apps/web/lib/api/map.ts:66-145` (multiple dictionaries)
- `apps/web/components/case/CaseWorkbench.tsx:30-46` (inline helpers)

**Issue:**
Label mapping logic scattered across files:
```typescript
// map.ts
const STATUS_LABELS: Record<string, string> = { PASS: "Clear", FAIL: "Issue", ... };
const AUDIT_ACTIONS: Record<string, string> = { ... };
const AGENT_LABELS: Record<string, string> = { ... };

// CaseWorkbench.tsx
function agentStepTitle(agent: string): string { ... }
function agentStatusLabel(status: string): string { ... }
```

**Refactoring Plan:**
Create centralized label module:

```typescript
// apps/web/lib/labels/index.ts
import { CheckStatus, AgentRole, AuditAction } from '@tradepulse/contracts/types';

export const checkStatusLabel = (status: CheckStatus): string => {
  const labels: Record<CheckStatus, string> = {
    [CheckStatus.PASS]: "Clear",
    [CheckStatus.FAIL]: "Issue",
    [CheckStatus.REVIEW_REQUIRED]: "Review Required",
    [CheckStatus.NOT_AVAILABLE]: "N/A",
    [CheckStatus.MISMATCH]: "Mismatch",
  };
  return labels[status] || status;
};

export const agentRoleLabel = (role: AgentRole): string => { ... };
export const auditActionLabel = (action: AuditAction): string => { ... };
```

**Benefits:**
- Single source of truth for UI labels
- Type-safe (uses contract enums)
- Easier to maintain consistent labeling
- Can add i18n support later

---

#### 7. Extract Text Normalization Helper

**Status:** 🔲 Not Started

**Location:** `apps/api/app/services/document_intelligence/reconciler.py:20-26`

**Issue:**
`_norm_text` pattern repeated in multiple places for text normalization.

**Refactoring Plan:**
```python
# apps/api/app/utils/normalization.py
"""Text normalization utilities for document intelligence."""
import re
from typing import Any

_NON_ALNUM = re.compile(r"[^a-z0-9]+")

def normalize_text(value: str | int | float | None) -> str | None:
    """
    Normalize text for fuzzy comparison.
    
    - Converts to lowercase
    - Removes non-alphanumeric characters
    - Collapses whitespace
    - Returns None for empty strings
    
    Args:
        value: Text-like value to normalize
        
    Returns:
        Normalized string or None
        
    Raises:
        TypeError: If value is not text-like
    """
    if value is None:
        return None
    if not isinstance(value, (str, int, float)):
        raise TypeError(f"Cannot normalize {type(value).__name__}")
    
    text = str(value).strip().lower()
    if not text:
        return None
    
    return _NON_ALNUM.sub(" ", text).strip()
```

**Benefits:**
- Reusable across entity resolution, reconciliation, screening
- Testable in isolation
- Clear semantics and error handling

---

### 🟢 P2: Type Safety Improvements (Medium Priority)

#### 8. Add Type Hints to Middleware

**Status:** 🔲 Not Started

**File:** `apps/api/app/main.py:102-108`

**Issue:**
```python
@application.middleware("http")
async def correlation_id_middleware(request: Request, call_next):  # type: ignore[no-untyped-def]
    # ...
```

**Refactoring Plan:**
```python
from collections.abc import Awaitable, Callable
from fastapi import Request, Response

@application.middleware("http")
async def correlation_id_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
    request.state.correlation_id = correlation_id
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    return response
```

---

#### 9. Replace `Any` with Typed Models in Orchestrator

**Status:** 🔲 Not Started

**File:** `apps/api/app/services/document_intelligence/orchestrator.py:110-164`

**Issue:**
`_serialize_result` and `_deserialize_result` use `dict[str, Any]` heavily.

**Refactoring Plan:**
```python
from typing import TypedDict

class SerializedIngestedDoc(TypedDict):
    document_id: str
    filename: str
    content_type: str
    storage_url: str
    uploaded_at: str

class SerializedPipelineResult(TypedDict):
    ingested: SerializedIngestedDoc
    cache_key: str
    cache_hit: bool
    extraction: dict | None
    validation: dict | None
    text_length: int
    extracted_at: str | None

def _serialize_result(result: PipelineResult) -> SerializedPipelineResult:
    return {
        "ingested": {
            "document_id": result.ingested.document_id,
            # ... explicit field mapping
        },
        # ...
    }
```

**Benefits:**
- Type checking catches field access errors
- Clear contract for serialization
- Better IDE autocomplete

---

#### 10. Replace Magic Strings with Enums

**Status:** 🔲 Not Started

**Locations:** `apps/web/lib/api/map.ts`, `components/case/CaseWorkbench.tsx`

**Issue:**
Hardcoded strings like `"PASS"`, `"REVIEW_REQUIRED"`, `"MISMATCH"` instead of enum imports.

**Refactoring Plan:**
```typescript
// Before
if (r.status === "PASS") { ... }

// After
import { CheckStatus } from '@tradepulse/contracts/types';
if (r.status === CheckStatus.PASS) { ... }
```

**Benefits:**
- Type-safe (compiler catches typos)
- Refactoring support (rename propagates)
- Consistent with backend

---

### 🔵 P3: Structural Improvements (Low Priority)

#### 11. Introduce React Context for Case Data

**Status:** 🔲 Not Started

**File:** `apps/web/components/case/CaseWorkbench.tsx`

**Issue:**
Props drilling of `live` case object and action handlers through multiple levels.

**Refactoring Plan:**
```typescript
// context/CaseContext.tsx
const CaseContext = createContext<{
  case: TradeCase;
  actions: CaseActions;
  refetch: () => Promise<void>;
} | null>(null);

export function CaseProvider({ caseId, children }: PropsWithChildren<{ caseId: string }>) {
  const caseData = useCaseData(caseId);
  const actions = useCaseActions(caseId, caseData.refetch);
  
  return (
    <CaseContext.Provider value={{ case: caseData.data!, actions, refetch: caseData.refetch }}>
      {children}
    </CaseContext.Provider>
  );
}

export function useCase() {
  const ctx = useContext(CaseContext);
  if (!ctx) throw new Error("useCase must be within CaseProvider");
  return ctx;
}
```

---

#### 12. Introduce Agent Config Protocol

**Status:** 🔲 Not Started

**File:** `apps/api/app/services/document_intelligence/agents.py`

**Issue:**
All agent functions construct `AgentResponse` directly with hardcoded `_CRITICAL_PATHS`.

**Refactoring Plan:**
```python
from dataclasses import dataclass
from typing import Protocol

@dataclass
class AgentConfig:
    critical_paths: tuple[str, ...]
    confidence_threshold: float
    max_retries: int = 3

class AgentRunner(Protocol):
    def run(self, document_text: str, run_id: str, config: AgentConfig) -> AgentResponse:
        ...

class ExtractorAgent:
    def __init__(self, llm: LLMAdapter):
        self.llm = llm
    
    def run(self, document_text: str, run_id: str, config: AgentConfig) -> AgentResponse:
        # Implementation with config.critical_paths
        ...
```

---

#### 13. Custom Exception Classes

**Status:** 🔲 Not Started

**File:** `apps/api/app/services/entity_resolution/service.py:168-169`

**Issue:**
Using generic `RuntimeError` for business logic violations.

**Refactoring Plan:**
```python
# apps/api/app/exceptions.py
class TradePulseException(Exception):
    """Base exception for TradePulse business logic errors."""

class InvalidVLEIStateError(TradePulseException):
    """Raised when VLEI verifier emits invalid status."""

class DocumentProcessingError(TradePulseException):
    """Raised when document processing fails."""

# Usage
if vlei_evidence.status is VLEIVerificationStatus.VERIFIED_LIVE:
    raise InvalidVLEIStateError(
        "Fixture VLEI verifier must not emit VERIFIED_LIVE. "
        "Check adapter configuration."
    )
```

---

## Implementation Strategy

### Phase 1: Foundation (Week 1)
- ✅ Create refactoring plan document
- 🔲 Consolidate datetime utilities (#5)
- 🔲 Extract text normalization helper (#7)
- 🔲 Add type hints to middleware (#8)

### Phase 2: Core Refactorings (Week 2-3)
- 🔲 Break up `process_case` function (#1)
- 🔲 Replace global state with dependency injection (#2)
- 🔲 Split `case_service.py` into modules (#4)

### Phase 3: Frontend Refactoring (Week 4)
- 🔲 Extract custom hooks from `CaseWorkbench` (#3)
- 🔲 Extract tab components (#3)
- 🔲 Consolidate status label mapping (#6)
- 🔲 Replace magic strings with enums (#10)

### Phase 4: Polish (Week 5)
- 🔲 Introduce React Context (#11)
- 🔲 Replace `Any` with typed models (#9)
- 🔲 Custom exception classes (#13)
- 🔲 Agent config protocol (#12)

---

## Testing Strategy

For each refactoring:
1. **Before:** Run existing tests to establish baseline
2. **During:** Write new tests for extracted functions/components
3. **After:** Verify all tests pass, no behavior changes

**Test Coverage Goals:**
- Backend: 80%+ for refactored modules
- Frontend: Unit tests for extracted components/hooks

---

## Success Metrics

**Code Quality:**
- Reduce average function length from 45 → 25 lines
- Reduce maximum function length from 197 → 80 lines
- Increase type coverage from 85% → 95%

**Maintainability:**
- Reduce cyclomatic complexity in `process_case` from 25 → 5
- Reduce `CaseWorkbench` component size from 538 → 100 lines
- Split monolithic files into focused modules (< 200 lines each)

**Testability:**
- Enable unit testing of individual processing stages
- Enable unit testing of tab components
- Remove global state dependencies from tests

---

## Risks & Mitigations

**Risk:** Breaking existing behavior  
**Mitigation:** Comprehensive test coverage before refactoring, feature flags for gradual rollout

**Risk:** Merge conflicts during long-running refactor  
**Mitigation:** Work in small, focused PRs; coordinate with team

**Risk:** Performance regression  
**Mitigation:** Benchmark critical paths before/after; profile in staging

---

## References

- **Authority Documents:**
  - `docs/adr/001-canonical-contracts-addendum.md`
  - `tradepulse-prd-v7-unified-trade-trust.md`
  - `tradepulse-system-design-v4-unified-trade-trust.md`

- **Coding Standards:**
  - `.cursor/rules/00-project-core.mdc`
  - `.cursor/rules/01-agentic-safety.mdc`
  - `.cursor/rules/01-document-policy.mdc`

---

**Last Updated:** 2026-08-27  
**Next Review:** After Phase 1 completion
