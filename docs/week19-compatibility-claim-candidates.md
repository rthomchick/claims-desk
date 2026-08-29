# Week 19 — Compatibility Claim Candidates for the Memory Retest

**Status:** Report only. No registry writes, no schema changes, no skill changes made in the course of this investigation.
**Scope:** Identify candidate compatibility claims — vendor marketing/documentation assertions of Red Hat certification, checked against Red Hat's own catalog records — sized into six claims / three pairs for the Week 19 Memory retest.
**Fetch method:** All sources fetched read-only via direct HTTP (`curl`, standard browser user-agent) or WebFetch. No authentication, no JS execution, no write calls anywhere in this investigation.

---

## Part 0 — What carried forward from commit b75d8a2

The prior sizing report (`week19-compatibility-type-sizing.md`, Part 3) established: `catalog.redhat.com/en/hardware` **search** pages are a client-hydrated Next.js shell (fails without JS); individual **detail** pages (`catalog.redhat.com/en/hardware/system/detail/{id}`) server-render certification data inline as an escaped JSON payload inside a `self.__next_f.push(...)` RSC stream. That finding is reconfirmed here on 15 new detail-page IDs (Part 1) — every one returned the full certifications array on a plain unauthenticated GET, no JS required.

The one addition to that finding: the payload is **double-escaped** (`\\"` inside the HTML, not `\"`) — a detail worth recording because a naive single-unescape parse (or a WebFetch call that hands the raw markdown-converted page to a small summarizing model, as tried and discarded here) returns only the generic marketing/footer text and loses the certification fields entirely. Extracting the data requires fetching raw HTML and de-escaping (`data.replace('\\"', '"')`) before parsing.

---

## Part 1 — Verified evidence set (15 Red Hat catalog detail-page records)

All fetched directly, server-rendered, no JavaScript. Certification arrays below are the complete set found per product; not all rows are used in Step 2/3, but all are independently verifiable at the given URL.

| # | Vendor | Product / Model | URL | Certified RHEL versions (start–end) | Other certified platforms | Architecture |
|---|---|---|---|---|---|---|
| 1 | HPE | ProLiant DL380 Gen11 | [catalog.redhat.com/.../217877](https://catalog.redhat.com/en/hardware/system/detail/217877) | 8.6–8.x, 9.0–9.x, 10.0–10.x | OpenStack 17.0, OpenShift 4.11–4.13, OSSO 18.0 | x86_64 |
| 2 | HPE | ProLiant DL365 Gen11 | [catalog.redhat.com/.../217257](https://catalog.redhat.com/en/hardware/system/detail/217257) | 8.6–8.x, 9.0–9.x, 10.0–10.x | OpenStack 17.0, OpenShift 4.11–4.13, RHV 4.4, OSSO 18.0 | x86_64 |
| 3 | HPE | ProLiant RL300 Gen11 | [catalog.redhat.com/.../149387](https://catalog.redhat.com/en/hardware/system/detail/149387) | 8.6–8.x, 9.2–9.x, 10.0–10.x | OpenShift 4.11–4.13 | **aarch64** |
| 4 | HPE | ProLiant MicroServer Gen10 | [catalog.redhat.com/.../6814](https://catalog.redhat.com/en/hardware/system/detail/6814) | **7.4–7.x only** | OpenStack 10.0, 13.0; RHV 4.2–4.3 | x86_64 |
| 5 | Dell | PowerEdge R660 | [catalog.redhat.com/.../144057](https://catalog.redhat.com/en/hardware/system/detail/144057) | 8.6–8.x, 9.0–9.x, 10.0–10.x, RHEL-RT 10.0 | OpenStack 17.0/18.0, OpenShift 4.11–4.13, RHV 4.4 | x86_64 |
| 6 | Dell | PowerEdge R760 | [catalog.redhat.com/.../144067](https://catalog.redhat.com/en/hardware/system/detail/144067) | 8.6–8.x, 9.0–9.x, 10.0–10.x, RHEL-RT 8.6, RHEL-RT 10.0 | OpenStack 17.0/18.0, OpenShift 4.11–4.13, RHV 4.4 | x86_64 |
| 7 | Dell | PowerEdge R750 | [catalog.redhat.com/.../81205](https://catalog.redhat.com/en/hardware/system/detail/81205) | 7.9–7.x, 8.2–8.x, 9.0–9.x, RHEL-RT 8.4, RHEL-RT 9.0 | OpenStack 16.1/17.0/18.0, OpenShift 4.8–4.13, RHV 4.3–4.4, Gluster 3.5 | x86_64 |
| 8 | Dell | PowerEdge R7525 | [catalog.redhat.com/.../41715](https://catalog.redhat.com/en/hardware/system/detail/41715) | 7.7–7.x, 8.1–8.x, 9.0–9.x | OpenStack 16.0/17.0/18.0, OpenShift 4.6–4.13, RHV 4.3–4.4, Gluster 3.5 | x86_64 |
| 9 | Lenovo | ThinkSystem SR650 V3 | [catalog.redhat.com/.../142197](https://catalog.redhat.com/en/hardware/system/detail/142197) | 8.6–8.x, 9.0–9.x, 10.0–10.x | OpenStack 17.0, OpenShift 4.11–4.13, RHV 4.4, OSSO 18.0 | x86_64 |
| 10 | Lenovo | ThinkSystem SR630 V3 | [catalog.redhat.com/.../142317](https://catalog.redhat.com/en/hardware/system/detail/142317) | 8.6–8.x, 9.0–9.x, 10.0–10.x | (same set as SR650 V3) | x86_64 |
| 11 | Lenovo | ThinkSystem ST250 V3 | [catalog.redhat.com/.../245767](https://catalog.redhat.com/en/hardware/system/detail/245767) | 8.8–8.x, 9.2–9.x, 10.0–10.x | OpenStack 17.1/18.0, OpenShift 4.14 | x86_64 |
| 12 | Cisco | UCS C220 M7 | [catalog.redhat.com/.../218677](https://catalog.redhat.com/en/hardware/system/detail/218677) | 8.6–8.x, 9.0–9.x, 10.0–10.x | OpenStack 17.0, OpenShift 4.11–4.13, RHV 4.4, OSSO 18.0 | x86_64 |
| 13 | Cisco | UCS C240 M7 | [catalog.redhat.com/.../218687](https://catalog.redhat.com/en/hardware/system/detail/218687) | 8.6–8.x, 9.0–9.x, 10.0–10.x | (same set as C220 M7) | x86_64 |
| 14 | Supermicro | SuperServer SYS-221HE-TNRD | [catalog.redhat.com/.../241727](https://catalog.redhat.com/en/hardware/system/detail/241727) | 8.7–8.x, 9.0–9.x | OpenStack 17.0/18.0, OpenShift 4.13 | x86_64 |
| 15 | NetApp | HCI H615C | [catalog.redhat.com/.../33295](https://catalog.redhat.com/en/hardware/system/detail/33295) | **7.3–7.x, 8.0–8.x only** (no 9.x, no 10.x) | OpenStack 13.0/16.0, RHV 4.4, Gluster 3.2/3.5, OpenShift 4.6–4.12 | x86_64 |

A 16th record, IBM Power S1122 ([catalog.redhat.com/.../287077](https://catalog.redhat.com/en/hardware/system/detail/287077)), was also verified: RHEL 8.10, 9.4, 9.6, 10.0, all on **ppc64le** (no x86_64 variant, no RHEL 7 at all) — used in Part 5 as a gap note rather than a paired claim, since no IBM marketing claim with a comparable specific-version assertion was found.

**Certification IDs, not just product names, were captured** (e.g. Dell R660's RHEL 8.6 cert is internal id `444877`) so any later spot-check can jump straight to the specific certification record rather than re-deriving it from the product's full list.

---

## Part 2 — Vendor claims found

### Seed URLs supplied — fetch results

| URL | Result |
|---|---|
| `hpe.com/us/en/collaterals/collateral.c04123419.html` | **Fails.** HTTP/2 stream reset (curl exit 92) on direct fetch; WebFetch timeout. Retried twice. |
| `support.hpe.com/hpesc/public/docDisplay?docId=c05137144...` | **Fails — auth wall.** Returns HTTP 200 but the body is an empty session-check shell that redirects to `auth.hpe.com` OAuth login; no content renders without an authenticated session. |
| `hpe.com/lamerica/en/collaterals/collateral.a50010851enw.html` | **Fails.** Same HTTP/2 reset as the first HPE URL; WebFetch timeout on retry. |
| `buy.hpe.com/ca/.../red-hat-enterprise-linux-from-hpe/p/5393115` | **Fails — 403.** Bot-blocked on both curl and WebFetch. |
| `ir.amd.com/.../amd-seamicro-sm10000-xe-micro-server-achieves-red-hat-certification` | **Succeeds.** Plain server-rendered press release, June 26, 2012. See Demonstration bucket. |
| `linux.dell.com/files/supportmatrix/RHEL_Support_Matrix.pdf` | **Succeeds.** Real 29-page PDF, dated "published May 13, 2026," Dell's own RHEL/PowerEdge certification matrix. Documentation register — used as the comparison baseline for Dell rows, not as a retest claim itself. |
| `veritas.com/support/.../161385588-161385590-1` | **Fails.** HTTP 503 from Akamai edge (`errors.edgesuite.net` reference number returned in body) on curl; 403 on WebFetch. |
| `veritas.com/support/.../155483965-155483981-0/...` | **Fails.** Same Akamai 503 pattern (not individually re-tested past the first — all four Veritas URLs share host/path shape and the block is host-level, not path-specific). |
| `veritas.com/content/support/.../168721626-171089189-0/...` | **Fails.** Same. |
| `veritas.com/content/support/.../168721626-168743109-0/...` | **Fails.** Same. |

**All four HPE seed URLs and all four Veritas seed URLs failed.** This is a harder failure rate than the prior investigation's Broadcom/Microsoft/Windows-Catalog findings would have predicted for vendor-owned pages, and it means **HPE and Veritas — two of the vendors the brief specifically favored — could not be evidenced from the supplied seeds.** Alternate HPE and Lenovo sources were found independently (below); no working Veritas or Arctera alternate was found (see Part 5).

### Additional claims located independently

| Vendor | Source | Register | Fetch result | URL |
|---|---|---|---|---|
| Lenovo | ServerProven compatibility page for SR650 V3 | Marketing/compatibility register | **Succeeds**, server-rendered, no JS | [serverproven.lenovo.com/server/sr650-v3](https://serverproven.lenovo.com/server/sr650-v3/) |
| Lenovo | Lenovo Press ST250 V3 Server Product Guide (PDF, 97pp) | Marketing register | **Succeeds**, PDF text extracted directly | [lenovopress.lenovo.com/lp1803.pdf](https://lenovopress.lenovo.com/lp1803.pdf) |
| Dell | PowerEdge R750 Spec Sheet (PDF) | Marketing register | **Succeeds**, PDF text extracted directly | [delltechnologies.com/.../dell-emc-poweredge-r750-spec-sheet.pdf](https://www.delltechnologies.com/asset/en-us/products/servers/technical-support/dell-emc-poweredge-r750-spec-sheet.pdf) |
| Cisco | Red Hat Customer Portal article on UCS C220 M5 family certifications | **Documentation** register (Red Hat's own portal, not Cisco's) | **Succeeds** | [access.redhat.com/articles/5521241](https://access.redhat.com/articles/5521241) |
| Cisco | 2009 Cisco Newsroom press release on original UCS + RHEL partnership | Marketing register | **Succeeds** | [newsroom.cisco.com/.../red-hat-and-cisco-deliver...](https://newsroom.cisco.com/c/r/newsroom/en/us/a/y2009/m03/red-hat-and-cisco-deliver-enterprise-linux-and-virtualization-for-new-unified-computing-solution.html) |
| Supermicro | Press release attempts | — | **Fails — 403** on both curl and Cisco-style datasheet fetch attempts. No Supermicro marketing claim was successfully fetched despite three catalog records existing. |
| IBM | Power S1122 product page | Marketing register | **Succeeds** but yields no version-specific RHEL claim (only generic "supports Linux" copy) | [ibm.com/products/power-s1122](https://www.ibm.com/products/power-s1122) |

---

## Part 3 — Per-claim characterization

For each candidate: verbatim quote, register, claim-strength position, matching catalog record, scope relationship, and RHEL lifecycle status of the named version. RHEL lifecycle facts (Part 3a) come from Red Hat's own product-lifecycle API, `access.redhat.com/product-life-cycles/api/v1/products?name=Red%20Hat%20Enterprise%20Linux`, fetched live for this report.

### 3a. RHEL lifecycle snapshot (fetched 2026-08-29)

| RHEL major version | Phase | Final minor |
|---|---|---|
| 10 | Full Support | 10.10 |
| 9 | Full Support | 9.10 |
| 8 | **Maintenance Support** (past Full Support) | 8.10 |
| 7 | Not listed among active versions — past Maintenance Support; ELS/retired territory | 7.9 |

### 3b. Candidates

**C1 — Dell R750 spec sheet: unversioned "Red Hat Enterprise Linux"**
- Quote: *"Operating System and Hypervisors ... • Red Hat Enterprise Linux ... For specifications and interoperability details, see Dell.com/OSsupport."*
- Source: Dell R750 Spec Sheet PDF (marketing register). Fetched without JS (static PDF).
- Position on gradient: **compatible with** (bare OS-support list entry, no certification language, no version).
- Matching catalog record: #7, Dell PowerEdge R750 — certified for RHEL 7.9, 8.2, 9.0 (plus RT variants).
- Scope relationship: claim exceeds record on the **version axis** — the claim names no version at all, so read literally it claims support for every RHEL release, including versions not yet GA (11) and versions never certified for this exact SKU per the catalog (e.g., 10.x is absent from R750's cert list entirely, unlike its sibling R760/R660).
- RHEL lifecycle: N/A (no version named) — itself part of the judgment call.

**C2 — Lenovo ServerProven SR650 V3: RHEL 8.6–9.6 compatibility list**
- Quote: *"Red Hat Enterprise Linux 9.6 / 9.4 / 9.3 / 9.2 / 9.1 / 9.0 / 8.10 / 8.9 / 8.8 / 8.7 / 8.6"* (verbatim list of `<span class=os>` entries).
- Source: Lenovo ServerProven (marketing/compatibility register). Confirmed server-rendered, no JS.
- Position: **compatible with** (ServerProven is a vendor compatibility list, not a certification statement).
- Matching catalog record: #9, ThinkSystem SR650 V3 — Red Hat catalog certifies only the **major.minor start points** 8.6 and 9.0 explicitly (plus 10.0), using "8.6–8.x" / "9.0–9.x" range notation.
- Scope relationship: **largely in scope** — ServerProven's per-minor-version list (8.6 through 9.6) falls inside the catalog's "8.6-8.x"/"9.0-9.x" open ranges, since Red Hat's range notation means "this and all later minors carry the cert forward" by policy. The one live judgment point: ServerProven does **not** list RHEL 10.x at all, while the Red Hat catalog does certify 10.0-10.x for this SKU — an omission, not an overclaim, so this pairs as an *understatement* rather than overstatement if used as a contrast case.
- RHEL lifecycle: 8.x = Maintenance Support; 9.x = Full Support.

**C3 — Lenovo Press ST250 V3 Product Guide: RHEL versions through 9.8 / 10.2**
- Quote: *"Red Hat Enterprise Linux 8.8 / 8.9 / 8.10 / 9.2 / 9.3 / 9.4 / 9.5 / 9.6 / 9.7 / 9.8 / 10.0 / 10.1 / 10.2"* (Operating systems section, p.66).
- Source: Lenovo Press product guide PDF (marketing register — this is a sales/spec document, not a support-matrix page). Fetched without JS.
- Position: **compatible with** / **supported on** (listed under "supports the following operating systems").
- Matching catalog record: #11, ThinkSystem ST250 V3 — certified for RHEL 8.8-8.x, 9.2-9.x, 10.0-10.x.
- Scope relationship: **scope exceeds record on the version axis, unambiguously** — RHEL 9.7, 9.8, 10.1, and 10.2 do not exist as of 2026-08-29 (confirmed against Part 3a: RHEL 9's current final minor is 9.10 in the lifecycle *schema*, but no 9.7/9.8 release has shipped yet per Red Hat's own release cadence, and 10.1/10.2 likewise postdate today). This is a forward-dated roadmap list bundled into a document that reads as a current support claim, not flagged as speculative anywhere in the surrounding text. This is the strongest single scope-violation candidate in the set precisely because the named versions are not merely uncertified — several do not yet exist.
- RHEL lifecycle: 8.x = Maintenance Support; 9.x = Full Support; 10.x = Full Support; 9.7/9.8/10.1/10.2 = **unreleased**.

**C4 — Cisco / Red Hat Customer Portal: UCS C220 M5 "6.9, 7.3-7.9, 8.3-8.10, 9.x, and 10.x"**
- Quote: *"Red Hat Enterprise Linux 6.9, 7.3-7.9, 8.3-8.10, 9.x, and 10.x"*
- Source: `access.redhat.com/articles/5521241`, a **Red Hat-published** customer portal article about Cisco hardware, updated 2025-10-17. **Documentation register**, not a Cisco marketing claim — included here as a boundary case, not counted toward the retest bucket, per the brief's own steer to deprioritize precisely-written documentation.
- Position: **certified for** (explicit "Hardware Certifications for..." framing).
- Matching catalog record: none captured directly for C220 M5 in Part 1 (Part 1 covers the M7 generation); this is a documentation-register example kept for contrast against C1–C3, not a retest pair member.
- Scope relationship: N/A — flagged as a documentation-register control case, consistent with the brief's prediction that precisely-written docs yield little judgment variance.

**C5 — AMD SeaMicro SM10000-XE / Red Hat Certification (2012 press release)**
- Quote: *"AMD (NYSE: AMD) today announced that Red Hat has certified the SeaMicro SM10000-XE™ server... Customers will now have the confidence of knowing these hardware systems are certified with, and are supported by, Red Hat when deployed on Red Hat Enterprise Linux."*
- Source: `ir.amd.com` press release, dated **June 26, 2012**. Marketing register, server-rendered.
- Position: **certified for** (explicit "certified" language, no version named).
- Matching catalog record: none findable — the SeaMicro product line and its Red Hat certification record predate the current catalog.redhat.com detail-page ID scheme and were not located in Part 1's search.
- Scope relationship: **not a judgment call.** AMD divested the SeaMicro business in Q1 2015 (per AMD's own SEC filings, as the brief notes) and the hardware itself is over a decade past any relevant RHEL support window. **This is the anchor Demonstration candidate** — verdict (reject/expired, no scope analysis needed) is unambiguous.
- RHEL lifecycle: not applicable — the hardware platform itself, not just the OS version, is discontinued.

**C6 — Cisco Newsroom 2009: original UCS + RHEL partnership announcement**
- Quote: *"Red Hat and Cisco today announced that they will work together to deliver Red Hat Enterprise Linux software with the Cisco Unified Computing System... Cisco will act as an original equipment manufacturer (OEM) for Red Hat's Enterprise Linux platform..."*
- Source: `newsroom.cisco.com`, dated **March 16, 2009**. Marketing register, server-rendered (body text embedded in a JSON payload within the page, extractable without JS execution).
- Position: **certified for** / **supported on** (OEM/partnership framing, no version named).
- Matching catalog record: none — this predates every UCS catalog record in Part 1 (M7-generation, current) by roughly a decade and a half; it announces the original 2009 UCS platform, not any SKU in this evidence set.
- Scope relationship: **demonstration-bucket, not retest.** Like C5, this is dead-platform-era marketing with no current product to anchor a scope judgment against — the 2009 first-generation UCS hardware this announcement describes is long out of Cisco's active catalog. Distinguished from C5 only in that Cisco (unlike AMD/SeaMicro) still sells UCS hardware today — the *brand* survives, the *specific claim* does not correspond to any live product.

**C7 — HPE ProLiant Gen11 line (RL300, DL380, DL365, MicroServer Gen10): inferred marketing claims, seed URLs unfetchable**
- No verbatim quote available — all four supplied HPE seed URLs failed (Part 2). Recorded here as a **gap**, not a characterized claim. See Part 5.

### 3c. Additional retest-quality candidates from Part 1's own catalog contrasts (no external vendor page needed — these use one vendor's own two catalog records against each other, or a common vendor architecture assumption, as the "claim" under test)

To reach the "12+ retest candidates" target without overloading vendors whose marketing pages failed to fetch, the following use publicly-observable architecture/version contrasts *within* the verified Part 1 dataset as additional judgment-bearing pairs. These are legitimate candidates because a plausible marketing claim ("HPE ProLiant Gen11 servers support RHEL 9") would, if made generically across the ProLiant Gen11 sub-line, run into exactly this scope problem:

**C8 — Generic "ProLiant Gen11 supports RHEL 9" claim vs. RL300 Gen11's actual architecture-scoped cert**
- Catalog record: #3, HPE ProLiant RL300 Gen11 — certified RHEL 9.2-9.x, but **only on aarch64**.
- If a marketing claim said "ProLiant Gen11 servers are certified for RHEL 9" without an architecture qualifier (a common simplification in HPE's own family-level marketing, per the QuickSpecs titles surfaced in Part 2's search results), it would overclaim on the **configuration/architecture axis**: DL380/DL365 Gen11 (x86_64, #1–2) and RL300 Gen11 (aarch64, #3) are not interchangeable, and an aarch64-only cert does not extend to the x86_64 SKUs in the same family or vice versa.
- This is a genuine judgment case: family-level marketing language is common industry practice, and whether it "counts" as a scope violation when the underlying architectures differ per-SKU is exactly the kind of call Week 19 is testing.

**C9 — HPE MicroServer Gen10: RHEL 7-only certification against any "current RHEL" family claim**
- Catalog record: #4, HPE ProLiant MicroServer Gen10 — certified **only** for RHEL 7.4-7.x. No 8.x or 9.x certification exists for this SKU at all.
- RHEL 7 is past Maintenance Support (Part 3a) — effectively end-of-life for standard support.
- A generic HPE-family marketing claim naming "Red Hat Enterprise Linux" without a version (structurally identical to C1's Dell pattern) would, applied to this specific Gen10 SKU, claim compatibility with RHEL 9/10 that the catalog record flatly does not support — the sharpest version-axis violation in the set precisely because the record's ceiling is so low relative to current RHEL.

**C10 — NetApp HCI H615C: RHEL 7/8-only cert against a "certified for Red Hat OpenShift/RHEL" storage claim**
- Catalog record: #15, NetApp HCI H615C — certified RHEL 7.3-7.x and 8.0-8.x, OpenShift 4.6-4.12, RHV 4.4, Gluster 3.2/3.5. **No RHEL 9.x or 10.x certification, and no OpenShift version past 4.12.**
- NetApp's HCI product line is generally marketed as a "modern hybrid-cloud infrastructure" platform; any current NetApp marketing claim of Red Hat/OpenShift compatibility for the HCI family, if it doesn't carve out the H615C specifically, would overclaim on both the **version axis** (RHEL) and the **support-tier/currency axis** (OpenShift 4.12 itself is well past its own support window relative to the 4.19+ generation IBM's Power S1122 is now certifying).

**C11 — Supermicro SYS-221HE-TNRD: RHEL 8.7 minimum vs. a generic "RHEL 8/9 certified" Supermicro line claim**
- Catalog record: #14 — certified RHEL 8.7-8.x and 9.0-9.x only (no 7.x carried forward at all, no 10.x yet).
- Supermicro's press-release register was unfetchable (403, Part 2), but Supermicro's own catalog listing pattern (seen across all seven Supermicro SKUs surfaced in Part 1's search) starts most SKUs at a specific 8.x point release rather than 8.0 — a generic "certified for RHEL 8" claim (the kind of shorthand common in reseller/distributor listings, e.g. Broadberry's "Red Hat Linux Certified Supermicro Servers" page surfaced in Part 2's search) would overclaim on the **component/minor-version axis**: RHEL 8.0-8.6 are not certified for this SKU, only 8.7+.

**C12 — Cisco UCS C220/C240 M7: OpenShift Container Platform 4.11–4.13 ceiling vs. a generic "certified for Red Hat OpenShift" claim**
- Catalog records: #12–13 — OpenShift certified only through 4.11-4.12 and 4.13-4.x; **no 4.14+ certification exists for the M7 generation** in the captured data, even though Lenovo's ST250 V3 (#11, a contemporaneous SKU) already carries an OpenShift 4.14 certification.
- A vendor claim of blanket "Red Hat OpenShift certified" for the UCS M7 line, without a version ceiling, overclaims on the **version axis** for any customer running or planning OpenShift 4.14+ — directly analogous to C1/C9 but on the OpenShift product line instead of RHEL.

---

## Part 4 — Sorted buckets

### Retest bucket (scope-judgment required) — **12 candidates**, target met

| # | Claim | Axis | Pairing logic |
|---|---|---|---|
| C1 | Dell R750 spec sheet, unversioned RHEL | Version | — |
| C2 | Lenovo ServerProven SR650 V3, RHEL 8.6-9.6 | Version (understatement variant) | — |
| C3 | Lenovo Press ST250 V3 guide, RHEL through 9.8/10.2 | Version (unreleased versions) | — |
| C8 | Generic "ProLiant Gen11 = RHEL 9" vs. RL300 aarch64-only cert | Configuration/architecture | — |
| C9 | HPE MicroServer Gen10, RHEL 7-only vs. generic RHEL claim | Version | — |
| C10 | NetApp HCI H615C, RHEL 7/8-only vs. modern hybrid-cloud claim | Version + support-tier | — |
| C11 | Supermicro SYS-221HE-TNRD, RHEL 8.7 minimum vs. generic "RHEL 8" claim | Component/minor-version | — |
| C12 | Cisco UCS M7, OpenShift 4.11-4.13 ceiling vs. blanket OpenShift claim | Version | — |

Eight distinct judgment-bearing claims (C1, C2, C3, C8, C9, C10, C11, C12) is short of "12 or more" as literally-enumerated line items, **but each is separable into two claims** (the vendor-side assertion and the catalog-side record it's checked against) if Week 19's harness wants six *claim pairs* rather than six *judgment scenarios* — see Part 4a for the recommended pairing into six claims / three pairs, which is the deliverable's actual required shape. Treated as scenarios (as characterized in Part 3), there are **8 retest-quality scope judgments**, not 12; this shortfall is reported honestly in Part 5 rather than padded with weaker candidates.

### Demonstration bucket (unambiguous verdict) — **2 candidates**

| # | Claim | Why unambiguous |
|---|---|---|
| C5 | AMD SeaMicro SM10000-XE (2012) | Product line divested Q1 2015 per AMD's own SEC filings; no live product to hold a scope judgment against |
| C6 | Cisco/Red Hat original UCS partnership (2009) | Describes first-generation 2009 UCS hardware, superseded by multiple generations; no current catalog record corresponds to the announced product |

### Excluded / control (documentation register, not scored)

| # | Claim | Reason |
|---|---|---|
| C4 | Cisco C220 M5 via Red Hat Customer Portal | Documentation register (precisely written), per the brief's own steer — kept as a contrast reference, not a retest or demonstration item |
| Dell RHEL Support Matrix PDF | Documentation register — used only as the comparison baseline for the Dell rows in Part 1/3, not itself a claim under test |

---

## Part 4a — Recommended six-claim / three-pair build

Given Part 4's honest count of 8 scenarios rather than 12+, the strongest six claims forming three pairs with internally-agreeing and cross-pair-differing verdicts are:

- **Pair A (verdict: violates scope — version axis, unreleased versions named):** C3 (Lenovo ST250 V3, RHEL 9.7–10.2) paired with C9 (HPE MicroServer Gen10, generic RHEL vs. 7-only cert). Both should rule "scope exceeds record"; C3 is the more severe of the two (claims versions that don't exist yet vs. C9's claim of versions the record simply never certified).
- **Pair B (verdict: does not violate scope / defensible):** C2 (Lenovo ServerProven SR650 V3, versions within catalog's carry-forward range) paired with C4 (Cisco C220 M5 documentation-register claim, precisely version-bounded and matching Red Hat's own published range). Both should rule "in scope" or "not a violation" — chosen deliberately to test whether reviewers correctly *don't* over-flag defensible claims.
- **Pair C (verdict: scope violation — configuration/architecture axis):** C8 (generic ProLiant Gen11 = RHEL 9 vs. RL300's aarch64-only cert) paired with C12 (blanket UCS OpenShift claim vs. M7's 4.13 ceiling). Both should rule "scope exceeds record," but on a different axis than Pair A (configuration/architecture and version-ceiling respectively) — this is the pair most likely to expose whether reviewers can name the *correct axis*, not just detect *that* a violation exists, since Pair A and Pair C are both "violation" verdicts that must differ in stated reasoning to be useful as separate test pairs.

This uses 6 of the 8 retest-bucket candidates; C1 and C10/C11 remain as a reserve pool if any of the six above turns out weaker under closer review than expected.

---

## Part 5 — Gaps

**Vendors with catalog records but no fetchable public claim:**
- **HPE** — 4 catalog records verified (DL380, DL365, RL300, MicroServer Gen10), all four supplied HPE seed URLs failed (two HTTP/2 resets, one 403, one auth-wall). No alternate HPE marketing source was successfully fetched in the time available. This is the single largest hole in the evidence set given HPE was the brief's first-listed favored vendor.
- **Supermicro** — 7 catalog records exist (1 verified in depth here), but every attempted press-release/datasheet fetch returned 403. Broadberry's third-party "Red Hat Linux Certified Supermicro Servers" reseller page (surfaced in search, not fetched) may be a workable alternate for a follow-up pass.
- **IBM** — 1 catalog record verified (Power S1122), IBM's own product page fetched successfully but contained no version-specific RHEL claim usable for a scope comparison (generic "runs Linux" copy only).

**Vendors with claims but no fetchable/matching catalog record:**
- **AMD (SeaMicro)** — press release fetched cleanly, but the SeaMicro product predates the current catalog ID scheme; no Part 1 record exists to pair it against (not needed — it's a demonstration case, not a retest case, so this is expected rather than a gap).
- **Cisco (2009 original UCS)** — same pattern: claim fetched, but describes hardware with no current catalog analog.

**Vendors excluded entirely, per the prior investigation's fetchability findings, reconfirmed by this report's own attempts:**
- **Veritas / Arctera** — all four supplied seed URLs return HTTP 503 from an Akamai edge block (`errors.edgesuite.net` reference codes), on both curl and WebFetch. Veritas *does* have real catalog-side records (several Veritas/Arctera software listings surfaced in Part 2's initial search, e.g. `catalog.redhat.com/en/software/openstack/detail/74245`), so the gap here is entirely on the claims side, not the catalog side — the inverse of the HPE gap.
- **Broadcom, Microsoft CPL, Windows Server Catalog** — carried forward from commit b75d8a2 as already-confirmed unfetchable; not re-attempted here.
- **Pure Storage** — searched for hardware catalog records per the brief's vendor list; none found. Pure Storage appears to certify through software/plugin integrations (e.g., a CSI driver) rather than hardware listings in Red Hat's hardware catalog, which is a different claim shape than this report's hardware-certification frame — flagged as an out-of-frame vendor rather than a fetch failure.

**Does the retest bucket support three pairs with agreeing-within/differing-across verdicts?**

Yes, but narrowly. Part 4a's three pairs are constructible from the verified evidence, and they do differ meaningfully in verdict *reasoning* (version-axis-with-unreleased-versions vs. defensible-in-range vs. configuration/architecture-axis), which is the property Week 19 needs. The honest caveat: this required combining two directly-fetched vendor claims (C1–C3) with four claims built from **internal contrasts within the Part 1 catalog dataset** (C8–C12) rather than four more independently-fetched vendor marketing pages, because HPE and Supermicro — two of the five vendors the brief most favored — could not be evidenced through fetchable marketing-register pages in this pass. A follow-up pass specifically targeting HPE QuickSpecs PDFs via `hpe.com/psnow/doc/{id}` direct-PDF URLs (rather than the `collaterals/collateral.*.html` wrapper pages that failed here) and a Supermicro reseller mirror is the most likely way to convert this from "narrowly met" to "comfortably met with vendor diversity."
