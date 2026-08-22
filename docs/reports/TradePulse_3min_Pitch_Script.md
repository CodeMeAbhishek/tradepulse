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
7. **Hook cases:** Name Hin Leong + BlackRock/HPS. Do **not** claim TradePulse would have “caught” or “prevented” either fraud. Frame as *why paper without challengeable evidence is lethal*.

---

## SCRIPT (speak this)

### [0:00–0:35] Hook — two real cases + what we are

Hi — we’re **TradePulse**.

This is not a hypothetical.

In **2020**, Singapore oil trader **Hin Leong** collapsed after disclosing **over $800 million** in hidden losses — with oil that had already been **pledged as collateral and sold to multiple lenders** through **duplicate financing** and **forged trade documents**. Bank exposure ran into the **billions**.

And it is not only commodities history. Lenders led by **BlackRock’s HPS**, with **BNP Paribas** as a major co-financier, have alleged a roughly **$500 million** receivables fraud built on **fabricated customer invoices** and **fake verification emails**. One **email-domain anomaly** cracked years of paper that looked “verified.”

**Same failure mode:** financing that trusts documents the desk cannot stress-test fast enough.

We build **documentary trade-compliance decision support** for the person who owns that desk: the **Head of Trade Finance Operations at a GIFT City IBU** — and their examiners.

We do **not** approve trades. We do **not** clear Customs. We make the documentary pack **defensible** — faster.

### [0:35–1:00] Problem + why current tools fail

Cross-border trade still runs on PDFs: commercial invoice, bill of lading, party names, amounts, routes.

Today that work is either **manual PDF grind**, or “AI checkers” that treat a **similar-looking name as the same company** and quietly skip missing papers as if everything were fine.

That creates two failures banks cannot afford: **false certainty** in audit — or **endless exceptions** that kill turnaround.

GIFT IFSC is scaling trade finance through IBUs. Volume is rising. Scrutiny is not going away.

### [1:00–1:40] Solution + why now + differentiation

**TradePulse** is an agentic examiner workbench.

Documents go through a **bounded swarm**: extract → validate → challenge → arbitrate — **maximum three rounds**. Every correction must cite evidence. If agents disagree, we return **REVIEW_REQUIRED**. We never average conflicting values.

On identity we use a **confidence ladder**: a GLEIF name candidate is **not** proof; an LEI on the document is stronger; **vLEI is separate** — and a fixture credential is labeled synthetic, never sold as live verification.

Missing source data stays **DATA_UNAVAILABLE**. It **cannot become PASS**.

**Why now:** agentic model costs finally make multi-step debate affordable; LEI/vLEI rails are maturing; and **IFSCA’s GIFT trade-finance posture** means IBUs need audit-grade speed without autopilot risk.

That’s our innovation — not “more agents.” **Epistemic honesty baked into the product.**

### [1:40–2:20] Proof (technical execution — say “working live”)

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

Full spoken body above ≈ **440–460 words** → rehearse to ≤ 2:55. If over time, cut the GIFT sentence in the problem block first, then one proof sentence. Pause after “not a hypothetical” and after “never PASS.”

---

## One-slide prompts (optional behind you)

| Time | On screen (max 6 words) |
|------|-------------------------|
| 0:00 | Hin Leong · BlackRock paper |
| 0:35 | False certainty kills audits |
| 1:00 | Bounded agents · Identity ladder |
| 1:40 | Live on AWS · Examiner pack |
| 2:20 | Buyer: GIFT IBU Trade Ops |
| 2:45 | Prototype ≠ product · Ask |

Do **not** read slides. Slides only reinforce.

---

## Speaker brief — the two hook cases (do not recite; use if judges ask)

### 1) Hin Leong Trading (Singapore, 2020)

- Founder disclosed **>$800m** undisclosed futures / trading losses; oil pledged as bank collateral had also been sold.
- PwC (interim judicial managers): forged documents “on a massive scale,” **non-existent inventory**, **same cargo sold to multiple parties**, fabricated invoices for receivables / factoring facilities.
- Bank / creditor liabilities reported around **~$3.5bn**.
- **TradePulse angle (honest):** documentary inconsistency and duplicate-financing *signals* for human review — **not** physical oil verification, **not** a claim we would have stopped the collapse.

Public framing sources: [GTR analysis](https://www.gtreview.com/news/asia/analysis-hin-leongs-vicious-cycle-of-trade-finance-fraud/), Business Times / PwC reporting on inventory shortfalls and fabricated docs.

### 2) BlackRock / HPS × Bankim Brahmbhatt (alleged, 2025 filings)

- Lenders led by **HPS Investment Partners** (BlackRock’s private-credit unit) alleged **~$500m+** fraud via **fabricated invoices / accounts receivable** at telecom firms (Broadband Telecom, Bridgevoice) and financing vehicles.
- **BNP Paribas** reportedly co-financed a large share; later took material loan-loss provisions (press ~€190m / ~$220m).
- Scheme allegedly relied on **fake customer emails / lookalike domains**; an HPS analyst’s domain anomaly triggered forensic review (Quinn Emanuel / auditors). Belgian carrier **BICS** reportedly confirmed emails as a fraud attempt.
- Chapter 11 filings and civil suit reported **August 2025**; federal / FBI probes reported in coverage. Treat as **allegations** unless you have a later final judgment in hand.
- **TradePulse angle (honest):** invoice authenticity, counterparty evidence, and “verification that is not verification” — **not** “we catch $500m frauds.”

Public framing sources: [WSJ](https://www.wsj.com/finance/how-fake-invoices-duped-blackrock-unit-into-a-400-million-loan-888b7e06), [Yahoo / HPS flag](https://finance.yahoo.com/news/blackrock-unit-flags-suspected-400-150656293.html), Times of India explainers summarizing the WSJ account.

---

## Pre-loaded answers to the 3 questions judges will ask

Speak these only in Q&A — do not cram into the 3 minutes unless a judge interrupts.

### 1) Who is your first paying customer, specifically, and how do you get to them?

> Head of Trade Finance Operations at a GIFT City IBU. Path: IFIH/mentor intro → 4–6 week supervised pilot on invoice + BoL for one corridor. We sell exception reduction and audit-ready examiner packs, not autopilot approval. Economic buyer is Ops; Compliance must sign the decision-support framing.

### 2) What would break first if you sold this to a real bank/NBFC next week?

> Enterprise SSO, private VPC networking, model-risk review of prompts, and live sanctions/list contracts — not the happy-path demo. Synchronous Textract + Bedrock latency would also fail SLA. We would sell a **supervised pilot** with labeled adapters and human-in-the-loop policy, not production autopilot.

### 3) If you started Monday, what would you build first — and is it what you built tonight?

> Monday #1: trust core — identity ladder, failure states that never false-PASS, examiner pack, async job queue, SSO. Tonight is the **agentic + live AWS proof point**. Same spine — different completeness. Prototype ≠ product.

### Bonus if they ask: “Would TradePulse have stopped Hin Leong / BlackRock?”

> No honest founder claims that. Those cases mix forged paper, collusion, and sometimes physical inventory. We surface **documentary contradictions, weak identity evidence, and unavailable data that must not PASS** — so a human maker–checker can escalate before false certainty hardens. Decision support, not a fraud oracle.

---

## 30-second emergency cut (if timer is brutal)

> We’re TradePulse. Hin Leong hid $800m+ losses with duplicate-pledged cargo and forged docs; BlackRock’s HPS and BNP allege ~$500m fake-invoice financing. Same lesson: paper without challengeable evidence. We give Head of Trade Finance Ops at a GIFT City IBU bounded agents, an identity ladder, and never turn missing data into PASS. Working live on AWS. Proof point, not finished bank product. We want GIFT pilots and IBU intros. Thank you.

(~95 words ≈ 35–40s — only if forced)

---

## Rehearsal checklist

- [ ] Timer hits ≤ 2:55 with natural pauses  
- [ ] Named **Hin Leong** and **BlackRock / HPS** once each in the hook  
- [ ] Did **not** claim we would have prevented either case  
- [ ] Said “Head of Trade Finance Ops at a GIFT City IBU” once  
- [ ] Said “decision support” / “not approve” once  
- [ ] Said “working live” / AWS once  
- [ ] Said “prototype is a proof point” once  
- [ ] Did **not** claim Customs clearance, physical container check, or “AI sanctioned”  
- [ ] Demo tab pre-loaded on a finished case  
- [ ] Teammates silent unless Q&A hands off  

---

*Sources used for framing: YC short-pitch clarity; Demo Day 3-min structure; GTR / PwC reporting on Hin Leong (2020); WSJ and follow-on coverage of HPS–Brahmbhatt alleged receivables fraud (2025); IFSCA/GIFT trade-finance context; Young Builders scoring + Judges’ Q&A guidebook.*
