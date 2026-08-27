# TradePulse — Final Jury Round: 4P Analysis & Business Case

> **Track:** Track 1 — Agentic AI | Cross-border Trade Finance / GIFT IFSC  
> **Team:** Abhishek (Platform/Intelligence), Ansh (Product/Workbench), Atharva (Integration/UI/Quality), Shivansh (QA/Release)  
> **Live Demo:** [Web UI](http://tradepulse-web-80820411.ap-south-1.elb.amazonaws.com) · [API](http://tradepulse-api-1608361585.ap-south-1.elb.amazonaws.com/docs)  
> **Status:** 341 tests passing · Zero failures · Deployed on AWS `ap-south-1`

---

## Table of Contents

- [1. Problem — The $4.5 Trillion Trust Gap](#1-problem--the-45-trillion-trust-gap)
- [2. Product — Agentic Trade-Trust Workbench](#2-product--agentic-trade-trust-workbench)
- [3. Picture — The Big Vision](#3-picture--the-big-vision)
- [4. Pitch — Why TradePulse, Why Now](#4-pitch--why-tradepulse-why-now)
- [5. Project Clarity](#5-project-clarity)
- [6. Scalability](#6-scalability)
- [7. Business Model](#7-business-model)

---

## 1. Problem — The $4.5 Trillion Trust Gap

### The Core Issue

Cross-border trade finance is a **$4.5 trillion global market** that still runs on fragmented PDFs, inconsistent entity evidence, and manual compliance reviews. Banks and GIFT City IBUs examine documentary packs under UCP-style pressure where a single undetected discrepancy can cascade into billion-dollar exposure.

### Real-World Failures That Prove the Need

| Case | What Happened | Root Cause |
|------|--------------|------------|
| **Hin Leong Trading** (Singapore, 2020) | $800M+ hidden losses; $3.5B bank exposure; oil pledged as collateral was sold to multiple lenders | Duplicate financing via forged trade documents; documentary inconsistencies undetected |
| **BlackRock/HPS × Brahmbhatt** (alleged, 2025) | ~$500M receivables fraud built on fabricated customer invoices and fake verification emails | One email-domain anomaly cracked years of "verified" paper — identity evidence was never stress-tested |

> **⚠️ Same failure mode in both cases:** financing that trusts documents the desk cannot stress-test fast enough.

### Why Current Tools Fail

Today, trade compliance officers face a **lose-lose tradeoff**:

```
Option A: Manual PDF grind
├── Slow turnaround (hours per case)
├── Inconsistent decisions across examiners
├── Missed cross-document discrepancies
└── Mounting audit burden as GIFT IFSC volume scales

Option B: "AI checkers" that overclaim
├── Treat fuzzy name match as identity proof
├── Silently skip missing documents
├── Average conflicting values instead of flagging them
└── Create FALSE CERTAINTY in audit — the most expensive failure
```

### The Pain by Persona

| Persona | Pain | Consequence |
|---------|------|-------------|
| **Head of Trade Finance Ops (GIFT City IBU)** | Manual document reading, fragmented entity evidence, missed discrepancies | Delayed turnaround, audit burden, regulatory exposure |
| **Compliance Officer** | Regulations scattered across IFSCA/DGFT/RBI/FEMA/CBIC; no unified view | Inconsistent decisions, missed policy changes |
| **Examiner on the Desk** | Exception queues managed by email/spreadsheets; no structured handoff | No defensible audit trail; maker-checker discipline breaks down |

### The Non-Obvious Insight

> The problem is **not** "OCR is slow."  
> The problem is **identity and evidence fragmentation across documentary trade.**

- A bank sees a name on an invoice
- A trade house sees a *slightly different* name on a Bill of Lading
- A domestic party is known by GSTIN/PAN/CIN
- A global counterparty may have an LEI
- An authorised signatory may later prove authority through vLEI
- Documents are checked separately, rules change separately, and duplicate documents can be reused across lenders

**Nobody builds the unified evidence graph.** TradePulse does.

---

## 2. Product — Agentic Trade-Trust Workbench

### What TradePulse Is

TradePulse AI is an **agentic, evidence-first trade-trust and compliance platform** for cross-border and domestic trade workflows. It converts a packet of trade documents into one reconciled, evidence-backed case file — helping bank and GIFT IFSC trade-house officers review faster, **without pretending the model is the compliance officer**.

### What TradePulse Is NOT

> **ℹ️ We are rigorous about what we don't do — because false claims in compliance tooling are as dangerous as the fraud they claim to detect.**

- ❌ Does not inspect physical goods inside a container
- ❌ Does not file or simulate Customs clearance / ICEGATE / Let Export Order
- ❌ Does not approve, reject, clear, or "AI-sanction" a transaction
- ❌ Does not treat fuzzy name match as identity proof
- ❌ Does not turn `DATA_UNAVAILABLE` into `PASS`
- ❌ Does not let agent consensus override human review

### Core Capabilities (Shipped & Live)

| Capability | What It Does | Why It Matters |
|-----------|-------------|----------------|
| **Case Workbench** | Create case → upload invoice (+ BoL/AWB) → process → review | Single surface for the complete compliance workflow |
| **Agentic Document Swarm** | Extractor → Validator → Challenger → Arbiter → Cross-doc Reconciler (max 3 rounds) | Multi-agent debate ensures evidence quality; bounded rounds prevent hallucination loops |
| **Identity Confidence Ladder** | 4-rung progression: `document_name → registry_candidate → verified_by_lei → supported_by_vlei` | Makes identity evidence *strength* visible — a GLEIF candidate is NOT the same as a verified LEI |
| **Examiner Case Pack** | Downloadable audit-ready JSON with findings, identity ladders, agent traces, document hashes, 5 mandatory safety disclaimers | Structured handoff for maker–checker discipline — defensible in audit |
| **Risk & Anomaly Signals** | Sanctions screening, price plausibility (USD/MT normalization), duplicate-submission detection | Signals for human review, never verdicts |
| **Document Policy Engine** | Profile-based rules: Required / Conditionally Required / Optional / Not Available | No silent skips — missing documents are surfaced, not hidden |
| **Cryptographic Audit Chain** | Append-only hash chain with actor, action, payload hash, source/model versions | Immutable provenance; replay cannot overwrite history |
| **RegWatch** | Regulation-change detection → LLM summary/proposal → human approval → selective case replay | Rules change; the system adapts with human oversight |

### The Agentic Intelligence Pipeline

```
  📄 Document Upload
       │
       ├──→ 🔍 Extractor ──→ ⚡ Challenger ──→ ⚖️ Arbiter
       │                         ↑
       └──→ ✅ Validator ────────┘
                                       │
                                       ↓
                              🔗 Cross-Doc Reconciler
                                       │
                                       ↓
                              📋 Deterministic Compliance Engine
                                       │
                                       ↓
                              👤 Human Workbench
```

**Key safety invariants of the swarm:**
- `MAX_AGENT_ROUNDS = 3` — no infinite debate
- `AGENT_MUST_CITE_EVIDENCE = true` — no unsupported claims
- `UNRESOLVED_OUTCOME = REVIEW_REQUIRED` — disagreement → human, always

### Identity Confidence Ladder — Our Core Innovation

```
  ┌─────────────────────────────────────────────────────────┐
  │              IDENTITY CONFIDENCE LADDER                  │
  ├──────────────────────┬──────────────────────────────────┤
  │  🔐 Rung 4 (Highest) │ Supported by vLEI               │
  │                      │ Cryptographic authority evidence  │
  ├──────────────────────┼──────────────────────────────────┤
  │  ✅ Rung 3           │ Verified by LEI                  │
  │                      │ Document LEI + GLEIF match        │
  ├──────────────────────┼──────────────────────────────────┤
  │  🏢 Rung 2           │ Registry Candidate               │
  │                      │ GLEIF name match (NOT verified)   │
  ├──────────────────────┼──────────────────────────────────┤
  │  📝 Rung 1 (Lowest)  │ Document Name Only               │
  │                      │ Raw extracted party name          │
  └──────────────────────┴──────────────────────────────────┘
```

> **Note:** Source outages are **explicit side-states** — they never advance the rung. A fuzzy match can **never** reach `verified_by_lei`. This is tested by 7 dedicated identity-ladder invariant tests.

### Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Next.js 15 + React 19 + TypeScript + Tailwind CSS | Examiner workbench with Investigation Canvas |
| **Backend** | FastAPI (Python 3.12) modular monolith | API, domain logic, adapters, rules engine |
| **Shared Contracts** | `packages/contracts` (Pydantic + enums + TypeScript mirror) | Type-safe boundary between frontend and backend |
| **LLM** | AWS Bedrock (Amazon Nova via Converse API) | Agent swarm: extraction, validation, challenge, arbitration |
| **OCR** | AWS Textract | PDF/TIFF document extraction with printable-text fallback |
| **Storage** | AWS S3 + SQLAlchemy/SQLite (dev) | Document objects + case data |
| **Entity Resolution** | GLEIF HTTP API (live + fixture) | LEI/legal-entity lookup with cache |
| **Screening** | OpenSanctions API (live + fixture) | Sanctions/restricted-party candidate screening |
| **Price Reference** | Yahoo Finance Futures API | Commodity benchmark for price plausibility |
| **Hosting** | AWS ECS Fargate + ALB + ECR (`ap-south-1`) | Containerized, load-balanced cloud deployment |

---

## 3. Picture — The Big Vision

### From Prototype to Platform to Ecosystem

```
  ┌──────────────────────────────────────────────────────────────┐
  │  🟢 HACKATHON KERNEL (Shipped & Live)                        │
  │                                                              │
  │  • Invoice + BoL Processing           • Risk Signals          │
  │  • Agentic Document Swarm             • Examiner Case Pack    │
  │  • Identity Ladder (LEI/GLEIF/vLEI)   • Maker-Checker + Audit│
  │  • 10 Synthetic Demo Scenarios        • Live AWS Deployment   │
  └──────────────────────────────┬───────────────────────────────┘
                                 │
                                 ▼
  ┌──────────────────────────────────────────────────────────────┐
  │  🟡 PLATFORM MODULES (Designed, Interfaces Preserved)        │
  │                                                              │
  │  • Packing List / Weight Plausibility  • RegWatch + Rule Packs│
  │  • Certificate of Origin              • Institution Rule Packs│
  │  • LC Terms-Lite + Insurance/Draft     • Multi-source Screening│
  │  • GSTIN / e-Invoice / e-Way Bill      • Full vLEI Verification│
  └──────────────────────────────┬───────────────────────────────┘
                                 │
                                 ▼
  ┌──────────────────────────────────────────────────────────────┐
  │  🔵 ECOSYSTEM AMBITION (Authorized Integration Only)         │
  │                                                              │
  │  • Merchant Readiness Console          • ULIP/ICEGATE (Auth) │
  │  • Logistics Milestones + Carriers     • Banking Core Integn. │
  │  • Cross-Lender Duplicate Registry     • Multi-Jurisdiction   │
  └──────────────────────────────────────────────────────────────┘
```

### The Shipment & Finance Passport Vision

TradePulse evolves into a **Shipment & Finance Passport** — a versioned digital case file that follows a transaction through its entire lifecycle:

```
┌──────────────────────────────────────────────────────────────┐
│                   SHIPMENT & FINANCE PASSPORT                │
├──────────────┬───────────────────────────────────────────────┤
│ Commercial   │ Buyer, seller, goods, quantity, price,       │
│   Layer      │ currency, Incoterm, corridor                 │
├──────────────┼───────────────────────────────────────────────┤
│ Identity     │ GSTIN/PAN/CIN/IEC + LEI/GLEIF + vLEI        │
│   Layer      │ authority evidence                            │
├──────────────┼───────────────────────────────────────────────┤
│ Document     │ Invoice, BoL/AWB, packing list, origin,      │
│   Layer      │ LC, insurance, draft, KYC                    │
├──────────────┼───────────────────────────────────────────────┤
│ Compliance   │ Sanctions screening, document consistency,    │
│   Layer      │ price indicators, duplicate signals           │
├──────────────┼───────────────────────────────────────────────┤
│ Logistics    │ Container, seal, weight, booking, departure,  │
│   Layer      │ carrier documents (future authorized feeds)   │
├──────────────┼───────────────────────────────────────────────┤
│ Finance      │ LC/collection/factoring checklist, document   │
│   Layer      │ presentation readiness                        │
├──────────────┼───────────────────────────────────────────────┤
│ Governance   │ Source snapshots, rule versions, model/prompt │
│   Layer      │ versions, agent trace, human actions          │
└──────────────┴───────────────────────────────────────────────┘
```

### Market Opportunity

| Dimension | Value |
|-----------|-------|
| **Global Trade Finance Gap** | $2.5 trillion (ADB estimate) |
| **Global Trade Finance Market** | $4.5+ trillion |
| **GIFT IFSC Growth** | 40+ operational IBUs, trade volume scaling rapidly under IFSCA |
| **Digital Trade Compliance TAM** | Growing as regulators mandate digital audit trails |
| **Pain Multiplier** | Every false-positive exception costs ~2–4 hours of examiner time; every missed discrepancy is potential regulatory action |

### Why GIFT City Is the Perfect Beachhead

1. **Greenfield regulatory environment** — IFSCA is actively shaping trade-finance rules
2. **Concentrated buyer base** — 40+ IBUs in one jurisdiction, accessible via IFIH network
3. **Cross-border by design** — every IBU transaction is international, making LEI/vLEI immediately relevant
4. **Scaling volume** — trade finance throughput increasing faster than compliance capacity
5. **Innovation-friendly** — GIFT IFSC is designed to compete with Singapore, Dubai, London IFSC standards

---

## 4. Pitch — Why TradePulse, Why Now

### The One-Liner

> **TradePulse converts scattered trade documents and identity evidence into one compliance-ready case file — helping Head of Trade Finance Ops / examiners review faster without pretending the model is the compliance officer.**

### Why Now — Three Converging Forces

```
  🤖 Agentic AI Maturity            🆔 Identity Rails Maturing        🏛️ GIFT IFSC Momentum
  ─────────────────────            ──────────────────────────        ─────────────────────
  • Multi-step debate               • LEI/vLEI adoption               • IBU volume scaling
    now affordable                    accelerating                    • IFSCA trade-finance
  • Bedrock/Nova cost               • GLEIF infrastructure              posture strengthening
    curve enables it                  production-ready                • Audit-grade speed needed
                    ╲                        │                       ╱
                     ╲                       │                      ╱
                      ╲                      ▼                     ╱
                       ╲        ┌──────────────────────┐          ╱
                        ╲──────→│   TradePulse Window  │←────────╱
                                │   of Opportunity     │
                                └──────────────────────┘
```

### Our Innovation: Epistemic Honesty as Product Architecture

Most AI compliance tools optimize for **confidence scores**. We optimize for **epistemic honesty** — the system's ability to distinguish what it knows, what it suspects, and what it cannot determine.

| Dimension | Typical "AI Checker" | TradePulse |
|-----------|---------------------|------------|
| **Identity** | Name match → "Verified ✅" | Name match → "Registry Candidate" (not verified) |
| **Missing Data** | Skip silently | `DATA_UNAVAILABLE` — cannot become `PASS` |
| **Agent Disagreement** | Average the values | `REVIEW_REQUIRED` — human decides |
| **Screening Hit** | "SANCTIONED ⛔" | "Potential match — review candidate" |
| **Price Anomaly** | "FRAUD DETECTED 🚨" | "Price variance signal — review indicator" |
| **Source Outage** | Cache stale data silently | Explicit degraded-source side-state |

> **💡 This is not conservatism — it is precision.** In trade compliance, false certainty (in either direction) is the systemic risk. Our product architecture makes uncertainty visible so humans can make defensible decisions.

### Competitive Differentiation

```
┌─────────────────────────────────────────────────────────────────┐
│                     COMPETITIVE LANDSCAPE                       │
├────────────────┬──────────────┬──────────────┬──────────────────┤
│                │ Manual Desk  │ AI "Checkers"│ TradePulse       │
├────────────────┼──────────────┼──────────────┼──────────────────┤
│ Speed          │ Hours/case   │ Minutes      │ < 30s live       │
│ Accuracy       │ High (human) │ Overclaims   │ Evidence-cited   │
│ Identity       │ Name-only    │ Fuzzy match  │ Confidence ladder│
│ Audit trail    │ Paper notes  │ Black-box    │ Hash-chain audit │
│ Missing data   │ Manual check │ Silent skip  │ Explicit surface │
│ Regulation     │ Manual track │ Static rules │ RegWatch + replay│
│ Agent safety   │ N/A          │ Unbounded    │ 3-round cap      │
│ Decision model │ Human        │ AI decides   │ Decision support │
└────────────────┴──────────────┴──────────────┴──────────────────┘
```

### What We Shipped in 22 Hours (Proof of Execution)

| Metric | Value |
|--------|-------|
| **Backend Tests** | 323 passing (FastAPI + Pytest) |
| **Shared Contract Tests** | 18 passing |
| **Frontend Tests** | 7 passing (Vitest) |
| **Total** | **341 tests, 0 failures** |
| **Complex Safety Tests** | 41 purpose-built across 6 classes |
| **Live Adapters** | Bedrock, GLEIF, OpenSanctions, Yahoo Finance, Textract, S3 |
| **Synthetic Demo Packs** | 10 scenario fixtures (clean match, qty mismatch, LEI exact, name-only review, duplicate, price anomaly, etc.) |
| **Deployment** | AWS ECS Fargate + ALB, live and accessible |
| **API Surface** | Full RESTful API with OpenAPI documentation |
| **Frontend** | Marketing + Workbench layouts, Investigation Canvas, Evidence Links, Document Preview |

---

## 5. Project Clarity

### Crystal-Clear Scope Boundaries

We maintain an explicit **authority order** for the project:

1. **Canonical Contracts** (`packages/contracts/`) — binding shared types
2. **PRD v7** — product scope & acceptance criteria
3. **System Design v4** — architecture & failure modes
4. **Master Prompt v2** — execution guidelines

> **If PRD and system design conflict: stop and resolve — do not guess.**

### Architecture at a Glance

```
  ┌──────────────────────┐
  │  🖥️ Next.js Workbench │
  │  (Examiner Interface) │
  └──────────┬───────────┘
             │ HTTPS / JSON
             ▼
  ┌──────────────────────┐
  │  ⚡ FastAPI API       │
  │  (Modular Monolith)  │
  └──┬───┬───┬───┬───┬───┘
     │   │   │   │   │
     ▼   ▼   ▼   ▼   ▼
  ┌────┐┌────┐┌────┐┌─────┐┌──────┐
  │Case││Orch││Plcy││Audit││RegWtch│
  └──┬─┘└──┬─┘└──┬─┘└──┬──┘└──┬───┘
     │     │     │     │      │
     │     │     │     │      └── Source Registry + Replay
     │     │     │     └── Hash Chain + Maker-Checker
     │     │     ├── GLEIF/LEI ──→ Identity Engine
     │     │     ├── OpenSanctions ──→ Screening Engine
     │     │     └── Yahoo Finance ──→ Price Plausibility
     │     │
     │     ├── Extractor → Validator → Challenger → Arbiter
     │     └── Cross-Doc Reconciler ──→ AWS Bedrock
     │
     └── SQLite/S3 ──→ AWS Textract (OCR)
```

### Ownership & Accountability

| Domain | Owner | Accountability |
|--------|-------|---------------|
| Backend, adapters, persistence, audit, deploy | **Abhishek** | Platform integrity, API contracts, fail-closed safety |
| Frontend, workbench product flow, API consumption | **Ansh** | User experience, case workflow, evidence visualization |
| UI/UX design system, visual QA, integration | **Atharva** | Accessibility, component quality, demo polish |
| Release verification, QA sign-off | **Shivansh** | Test coverage, regression, deployment validation |
| Shared contracts (`packages/contracts/`) | **All** | Dedicated review gate before merge |

### Failure Behavior — Designed for Safety

| Failure | TradePulse Response |
|---------|-------------------|
| LLM timeout / invalid response | Retry once → cache fallback → `REVIEW_REQUIRED` |
| Agent disagreement after 3 rounds | `REVIEW_REQUIRED` — never averaged |
| GLEIF / external source unavailable | `DATA_UNAVAILABLE` — no false verification |
| Screening data unavailable | `DATA_REVIEW_REQUIRED` — never `PASS` |
| Missing required document | `DOCUMENT_PACK_INCOMPLETE` — blocker surfaced |
| Potential sanctions/high-severity match | `HIGH_RISK_ESCALATION` — immediate human routing |

---

## 6. Scalability

### Technical Scalability Path

```
  CURRENT (Hackathon)          NEAR-TERM SCALE              PRODUCTION SCALE
  ───────────────────          ──────────────────            ─────────────────
  • SQLite + In-Memory    →    • PostgreSQL + Redis     →    • Multi-AZ RDS + Replicas
  • Single ECS Task       →    • Auto-scaling Tasks     →    • Target-Tracking Scaling
  • Synchronous Processing →   • Async Job Queue (SQS)  →    • Event-Driven Architecture
  • Direct API calls      →    • Connection pooling     →    • CDN + Edge Caching
```

| Scalability Dimension | Current | Path to Production |
|----------------------|---------|-------------------|
| **Compute** | ECS Fargate (single task) | Auto-scaling task groups; horizontal scaling behind ALB |
| **Storage** | SQLite (dev) / S3 (docs) | PostgreSQL (RDS) for cases; S3 remains for documents |
| **Processing** | Synchronous API calls | Async job queue (SQS → worker tasks) for document processing |
| **Caching** | In-memory | Redis/ElastiCache for GLEIF lookups, screening snapshots, price refs |
| **LLM** | Bedrock (on-demand) | Bedrock provisioned throughput; prompt caching; batch inference |
| **OCR** | Textract (sync) | Textract async with S3 output; parallel document processing |
| **Multi-tenancy** | Single instance | Tenant-isolated databases; role-based access; institution rule packs |
| **Observability** | Log-based | CloudWatch + X-Ray tracing; SLA dashboards per institution |

### Product Scalability — Profile-Driven Modularity

The architecture is **designed to scale without rewriting core logic**:

```
New document type?   → Add DocumentType enum + extraction prompt + policy rule
New trade profile?   → Add TradeProfile enum + document requirements config
New identity source? → Implement adapter Protocol + wire into Identity Engine
New screening list?  → Add source to Screening Engine + snapshot versioning
New regulation?      → RegWatch detects change → human approves → selective replay
New institution?     → Institution-specific rule pack + configuration
```

> **Note:** This is not aspirational. The interfaces (Protocol classes, adapter boundaries, policy data structures) are already in the codebase. Future modules "plug in" — they don't require architectural rework.

### Geographic Scalability

| Phase | Geography | Identity Focus |
|-------|-----------|---------------|
| **Phase 1** | GIFT IFSC / India cross-border | LEI/GLEIF + GSTIN/IEC/PAN |
| **Phase 2** | India domestic B2B | GSTIN/PAN/CIN + e-invoice IRN + e-way bill |
| **Phase 3** | GCC / ASEAN corridors | LEI/vLEI + local registry adapters |
| **Phase 4** | Global trade corridors | Full multi-jurisdiction identity fabric |

---

## 7. Business Model

### Revenue Model — SaaS for Trade Compliance

```
  Revenue Streams                          Unit Economics Target
  ────────────────                         ─────────────────────
  💰 Per-Case Processing Fee ($5–15)       Case processing: $5–15
  📊 Platform Subscription ($2K–8K/mo)     vs. Manual cost: $50–200/case
  🔧 Implementation & Configuration        (2–4 hours examiner time)
  📋 Premium Modules (RegWatch, etc.)      ROI: 5–15x cost reduction
```

### Pricing Tiers (Indicative)

| Tier | Target | Monthly Fee | Includes |
|------|--------|-------------|----------|
| **Pilot** | IBU onboarding | Free (supervised) | 50 cases/month, 1 corridor, basic identity |
| **Starter** | Small IBU / trade desk | $2,000–3,000 | 200 cases/month, 2 corridors, LEI + screening |
| **Professional** | Mid-size IBU | $5,000–8,000 | 1,000 cases/month, all corridors, RegWatch, examiner packs |
| **Enterprise** | Large bank / trade house | Custom | Unlimited cases, SSO, VPC deployment, institution rule packs |

### Go-to-Market Strategy

```
  🏛️ GIFT IFIH / Young Builders  →  🤝 First IBU Pilot  →  📈 Prove Value  →  🚀 Expand  →  🌍 Scale
     Residency + Mentor Network      4–6 week supervised     Fewer exceptions     More corridors    Private banks
                                     1 corridor (IN-AE)      Complete exam packs  More doc types    GCC/ASEAN
                                                             Audit-ready trail    More IBUs         Domestic India
```

### Key Business Metrics (Target Year 1)

| Metric | Target |
|--------|--------|
| **Pilot Institutions** | 3–5 GIFT City IBUs |
| **Cases Processed** | 500–2,000/month |
| **Examiner Time Saved** | 60–80% per case vs. manual |
| **Exception Reduction** | 30–50% fewer unexplained exceptions |
| **Audit Readiness** | 100% cases with structured examiner packs |

### Unit Economics

```
Manual Process:
  Examiner time per case:        2–4 hours
  Fully loaded examiner cost:    $25–50/hour
  Cost per case:                 $50–200

TradePulse:
  Processing cost per case:      $2–5 (compute + LLM + OCR)
  Subscription per case:         $5–15 (blended)
  Total per case:                $7–20

VALUE CREATED:  $30–180 per case
GROSS MARGIN:   65–80%
```

### First Paying Customer — Specifically

> **Head of Trade Finance Operations at a GIFT City IBU** (or a mid-size private-bank trade desk with IFSC corridor volume).

**Path to them:**
1. IFIH residency and mentor introductions (this hackathon)
2. One corridor supervised pilot (4–6 weeks, IN-AE or IN-GB)
3. Success metric: **fewer unexplained exceptions** and **complete examiner packs**
4. Champion is Ops; Compliance is the gate we design for by staying decision-support-only

### What We'd Build Monday (If We Won)

| Priority | Item | Why |
|----------|------|-----|
| 1 | **Trust core hardening** | Identity ladder, failure states that never false-PASS |
| 2 | **Async job queue** | Production latency SLA for document processing |
| 3 | **Enterprise SSO** | Required for any bank/IBU pilot |
| 4 | **Private VPC deployment** | Data residency and security compliance |
| 5 | **Model-risk review** | Prompt audit and bias testing for regulatory comfort |

> **⚠️ Important:** We know the difference between a **proof point** (tonight) and a **bank product** (months of supervised hardening). Prototype ≠ product — and saying that out loud is part of our credibility.

---

## Summary — Why TradePulse Wins

| Jury Criterion | TradePulse Answer |
|---------------|-------------------|
| **Problem** | Identity and evidence fragmentation in documentary trade — $4.5T market with billion-dollar failure cases |
| **Product** | Agentic trade-trust workbench with bounded agents, identity confidence ladder, and epistemic honesty |
| **Picture** | From examiner tool → Shipment & Finance Passport → trade-trust interoperability layer |
| **Pitch** | Right problem × right timing (agentic AI + LEI/vLEI maturity + GIFT IFSC scaling) × honest execution |
| **Project Clarity** | Named owners, authority order, explicit scope boundaries, 341 tests, fail-closed safety design |
| **Scalability** | Profile-driven modularity; plug-in adapters; clear path from SQLite → PostgreSQL → multi-tenant enterprise |
| **Business Model** | SaaS per-case + subscription; 5–15x ROI vs. manual; first customer is Head of Trade Finance Ops at GIFT IBU |

### The Ask

> **Young Builders / GIFT IFIH:** Pilot pathway, regulatory guidance, and IBU introductions — so Monday we harden the trust core for a supervised bank pilot, not a louder pitch deck.

---

*TradePulse: Examiner decision support. Live. Honest. Built for GIFT Trade Ops.*
