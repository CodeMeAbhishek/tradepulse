# TradePulse — 3-Minute One-Speaker Pitch Script

**Speaker:** 1 member (recommend Abhishek for platform/live demo, or Ansh for product narrative — pick one voice only)  
**Length:** ≤ 180 seconds (~420–450 words at calm pace)  
**Track:** Track 1 — Agentic AI | Cross-border trade finance / GIFT IFSC  
**Live proof:** Web `http://tradepulse-web-80820411.ap-south-1.elb.amazonaws.com`  
**Method:** YC-style clarity (what → problem → failure → mechanism → why now → proof → team → ask). Judged on rubric: technical live 25%, innovation 20%, problem/market/demo 15% each, team psychometrics R1 10%.

---

## Delivery rules (founder playbook)

1. **Clarity over flair** — one sentence = one idea. No “AI will revolutionize.”
2. **Lead with the non-obvious insight** — AI that *refuses* false certainty beats AI that rubber-stamps.
3. **Name the buyer** — “Head of Trade Finance Ops at a GIFT City IBU,” not “banks and fintechs.”
4. **Prototype ≠ product** — say it once, out loud. Judges hunt for this.
5. **Practice with a phone timer.** Cut anything that makes you rush. Pause after the one-liner and after “never PASS.”
6. **Demo:** Pre-open a completed case. Do *not* create a fresh case live unless pre-warmed.

---

## SCRIPT (speak this)

### [0:00–0:15] Hook + what we are

Hi — we’re **TradePulse**.

We build **documentary trade-compliance decision support** for the person who actually owns the exception queue: the **Head of Trade Finance Operations at a GIFT City IBU** — and the examiners on their desk.

We do **not** approve trades. We do **not** clear Customs. We make the documentary pack **defensible** — faster.

### [0:15–0:50] Problem + why current tools fail

Cross-border trade still runs on PDFs: commercial invoice, bill of lading, party names, amounts, routes.

Today that work is either **manual UCP-style grind**, or “AI checkers” that treat a **fuzzy name hit as identity** and quietly skip missing data as if it were a green pass.

That creates two failures banks cannot afford: **false certainty** in audit — or **endless exceptions** that kill turnaround.

GIFT IFSC is scaling trade finance through IBUs — IFSCA has been explicitly enabling trade credit, factoring, forfaiting; IBU trade-finance outstanding was on the order of **tens of billions of USD**. Volume is rising. Scrutiny is not going away.

### [0:50–1:35] Solution + why now + differentiation

**TradePulse** is an agentic examiner workbench.

Documents go through a **bounded swarm**: extract → validate → challenge → arbitrate — **maximum three rounds**. Every correction must cite evidence. If agents disagree, we return **REVIEW_REQUIRED**. We never average conflicting values.

On identity we use a **confidence ladder**: a GLEIF name candidate is **not** proof; an LEI on the document is stronger; **vLEI is separate** — and a fixture credential is labeled synthetic, never sold as live verification.

Missing source data stays **DATA_UNAVAILABLE**. It **cannot become PASS**.

**Why now:** agentic model costs finally make multi-step debate affordable; LEI/vLEI rails are maturing for cross-border counterparties; and **IFSCA’s GIFT trade-finance posture** means IBUs need audit-grade speed without autopilot risk.

That’s our innovation — not “more agents.” **Epistemic honesty baked into the product.**

### [1:35–2:20] Proof (technical execution — say “working live”)

This is not a slideware prototype.

**Working live on AWS** — Mumbai region: Next.js workbench and FastAPI on **ECS Fargate behind load balancers**, documents in **S3**, OCR via **Textract**, agents on **Bedrock**, typed contracts end-to-end.

In the product you’ll see: case create → upload invoice and transport docs → processing rail → workbench with identity ladder → **download examiner case pack** for maker–checker handoff.

What we shipped tonight is a **proof point**: the trust core + live path. It is **not** the finished bank product — and we know the difference.

### [2:20–2:45] First customer + how we get there

**First paying customer, specifically:** Head of Trade Finance Ops at a **GIFT City IBU** (or a mid-size private-bank trade desk with IFSC corridor volume).

**How we get to them:** residency and mentor intros here → one corridor pilot → success metric is **fewer unexplained exceptions** and **complete examiner packs** — not an “AI approval rate.” Champion is Ops; Compliance is the gate we design for by staying decision-support-only.

### [2:45–3:00] Team + ask

**Team:** platform and AWS contracts; workbench product; UI quality; QA release gate — named owners, not “everyone codes everything.” We stop when PRD and contracts conflict instead of inventing truth mid-demo.

**Ask:** Young Builders / GIFT IFIH for **pilot pathway, regulatory guidance, and IBU introductions** — so Monday we harden the trust core for a supervised bank pilot, not a louder pitch deck.

TradePulse: **examiner decision support. Live. Honest. Built for GIFT trade ops.** Thank you — happy to take questions.

---

## Word count check

Full spoken body above ≈ **430 words** → ~2:50–3:00 at 145 wpm. If you speak fast, add a 2-second pause after “never PASS” and after “proof point.”

---

## One-slide prompts (optional behind you)

| Time | On screen (max 6 words) |
|------|-------------------------|
| 0:00 | TradePulse · Decision support |
| 0:20 | False certainty kills audits |
| 0:50 | Bounded agents · Identity ladder |
| 1:35 | Live on AWS · Examiner pack |
| 2:20 | Buyer: GIFT IBU Trade Ops |
| 2:45 | Prototype ≠ product · Ask |

Do **not** read slides. Slides only reinforce.

---

## Pre-loaded answers to the 3 questions judges will ask

Speak these only in Q&A — do not cram into the 3 minutes unless a judge interrupts.

### 1) Who is your first paying customer, specifically, and how do you get to them?

> Head of Trade Finance Operations at a GIFT City IBU. Path: IFIH/mentor intro → 4–6 week supervised pilot on invoice + BoL for one corridor. We sell exception reduction and audit-ready examiner packs, not autopilot approval. Economic buyer is Ops; Compliance must sign the decision-support framing.

### 2) What would break first if you sold this to a real bank/NBFC next week?

> Enterprise SSO, private VPC networking, model-risk review of prompts, and live sanctions/list contracts — not the happy-path demo. Synchronous Textract + Bedrock latency would also fail SLA. We would sell a **supervised pilot** with labeled adapters and human-in-the-loop policy, not production autopilot.

### 3) If you started Monday, what would you build first — and is it what you built tonight?

> Monday #1: trust core — identity ladder, failure states that never false-PASS, examiner pack, async job queue, SSO. Tonight is the **agentic + live AWS proof point**. Same spine — different completeness. Prototype ≠ product.

---

## 30-second emergency cut (if timer is brutal)

> We’re TradePulse — decision support for Head of Trade Finance Ops at a GIFT City IBU. Banks drown in PDFs; AI checkers create false certainty. We run bounded agents, an identity ladder, and never turn missing data into PASS. Working live on AWS with an examiner pack for maker–checker. Tonight is a proof point, not the finished bank product. We want GIFT pilots and IBU intros. Thank you.

(~95 words ≈ 35–40s — only if forced)

---

## Rehearsal checklist

- [ ] Timer hits ≤ 2:55 with natural pauses  
- [ ] Said “Head of Trade Finance Ops at a GIFT City IBU” once  
- [ ] Said “decision support” / “not approve” once  
- [ ] Said “working live” / AWS once  
- [ ] Said “prototype is a proof point” once  
- [ ] Did **not** claim Customs clearance, physical container check, or “AI sanctioned”  
- [ ] Demo tab pre-loaded on a finished case  
- [ ] Teammates silent unless Q&A hands off  

---

*Sources used for framing: YC short-pitch clarity principles; 3-minute Demo Day structures (hook → problem → solution → proof → team → ask); IFSCA public materials on GIFT IFSC trade-finance enablers / IBU outstanding scale; Young Builders scoring + Judges’ Q&A guidebook.*
