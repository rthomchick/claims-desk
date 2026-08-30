# Week 19 — Compatibility Claim Candidates for the Memory Retest (v2)

**Status:** Report only. No registry writes, no schema changes, no skill changes made in the course of this investigation.
**Supersedes:** the claim side (Parts 2–5) of `week19-compatibility-claim-candidates.md`. The evidence side (Part 1, the 15-record Red Hat catalog set) is reused unchanged from that report and is not re-derived here — see Part 0.
**Why this pass exists:** the prior report's C8–C12 were not claims anyone published. They were scope scenarios I built by hand from the catalog data itself, dressed as "generic marketing claims a vendor might plausibly make." Three of those five were carried into the recommended six-claim build. This pass replaces the entire fabricated set with claims that were actually fetched, quoted, and matched against a URL that resolved.
**Fetch method:** All sources fetched read-only via direct HTTP (`curl`, browser user-agent, `--http1.1` and a `Referer` header where a bare request 403'd) or `WebSearch`/`WebFetch`. No authentication, no JS execution, no write calls.

---

## Part 0 — Evidence reused from commit eb12a6a

The 15-record Red Hat catalog detail-page table (Part 1 of the prior report) is reused as-is. I independently re-fetched and re-parsed six of those records for this pass (SR650 V3 #9, SR630 V3 #10, ST250 V3 #11, R660 #5, R760 #6, R750 #7, R7525 #8) to pull exact certification IDs rather than trusting the prior table blind, and every certified-version range I recovered matches the prior report's table exactly. No corrections to Part 1 were needed. Certification IDs recovered this pass (new detail beyond the prior report, useful for spot-checks):

| SKU | Catalog URL | RHEL cert IDs (version) |
|---|---|---|
| SR650 V3 | `.../detail/142197` | 440027 (8.6-8.x), 439537 (9.0-9.x), 659337 (10.0-10.x) |
| SR630 V3 | `.../detail/142317` | 441317 (8.6-8.x), 439647 (9.0-9.x), 662377 (10.0-10.x) |
| ST250 V3 | `.../detail/245767` | 604717 (8.8-8.x), 604707 (9.2-9.x), 662747 (10.0-10.x) |
| R660 | `.../detail/144057` | 444877 (8.6-8.x), 444907 (9.0-9.x), 669267 (10.0-10.x) |
| R760 | `.../detail/144067` | 444887 (8.6-8.x), 444917 (9.0-9.x), 669277 (10.0-10.x) |
| R750 | `.../detail/81205` | 332335 (8.2-8.x), 332395 (7.9-7.x, RHEL), 422827 (9.0-9.x) — no 10.x cert exists |
| R7525 | `.../detail/41715` | 189745, 195235 (7.x/8.x), 422897 (9.0-9.x) — no 10.x cert exists |

Each product's catalog page carries a `productSpec`/`supportWebsite` link pointing at the exact Lenovo Press URL used below (e.g. ST250 V3's catalog record links to `lenovopress.lenovo.com/lp1803-thinksystem-st250-v3-server`), confirming catalog record and vendor document describe the same SKU.

---

## Part 0a — Correction to the prior pass: RHEL minor-release dates

The prior report's C3 concluded that Lenovo's ST250 V3 guide, by listing RHEL 9.7, 9.8, 10.1, and 10.2, was naming versions that "do not exist as of 2026-08-29." That conclusion was wrong, and it matters because the brief specifically asked this pass to re-adjudicate it.

The `access.redhat.com/product-life-cycles/api/v1/products` endpoint (used by the prior pass) only returns **major-version** lifecycle envelopes — it has no per-minor GA dates, and its `final_minor_release` field (e.g. "9.10" for RHEL 9) names the *eventual* final minor once that major line closes, not the *current* one. Reading it as "current latest minor" is the error the prior pass made.

Red Hat's own release-dates page, `access.redhat.com/articles/red-hat-enterprise-linux-release-dates`, carries the actual per-minor table (fetched 2026-08-29, HTTP 200, static server-rendered content, no JS):

| RHEL minor | General Availability date | Errata |
|---|---|---|
| 9.6 | 2025-05-20 | RHBA-2025:6965 |
| 9.7 | 2025-11-11 | RHBA-2025:20949 |
| 9.8 | 2026-05-19 | RHBA-2026:18586 |
| 10.0 | 2025-05-20 | RHBA-2025:6295 |
| 10.1 | 2025-11-11 | RHBA-2025:19954 |
| 10.2 | 2026-05-19 | RHBA-2026:18131 |

RHEL 9.9, 9.10, and 10.3 do not appear on the page at all — confirming 9.8 and 10.2 are the actual current-latest minors, not future placeholders in a forward-dated table. **All four versions the prior pass flagged as unreleased (9.7, 9.8, 10.1, 10.2) GA'd months before today's date.** C3 is real, current, released-version content, not a forward-looking or aspirational statement — see the aspirational screen in C3's write-up below for the reclassification.

This also means the prior report's Part 3a lifecycle table understated what "Full Support" covers: as of today, RHEL 9's Full Support line runs through 9.8 (not merely "9.x" abstractly), and RHEL 10's runs through 10.2.

---

## Part 1 — Candidates (12 found, real and independently verified)

### C1 — Dell PowerEdge R750 Spec Sheet: unversioned "Red Hat Enterprise Linux" *(carried forward from prior pass, re-verified)*

- **Quote:** *"Operating System and Hypervisors ... Canonical Ubuntu Server LTS ... Citrix Hypervisor ... Microsoft Windows Server with Hyper-V ... Red Hat Enterprise Linux ... SUSE Linux Enterprise Server ... VMware ESXi ... For specifications and interoperability details, see Dell.com/OSsupport."*
- **Source URL:** `https://www.delltechnologies.com/asset/en-us/products/servers/technical-support/dell-emc-poweredge-r750-spec-sheet.pdf`
- **Fetch method/result:** curl, Chrome UA + `Referer` header (bare request 403'd; adding `Referer: delltechnologies.com/en-us/servers/poweredge-r750.htm` returned HTTP 200, 3-page PDF, 635,595 bytes). Text extracted via `pdftotext -layout`.
- **Publisher/register:** Dell Technologies — marketing register (spec sheet).
- **Gradient position:** compatible with (bare OS list, no certification language, no version).
- **Matching Part 1 record:** #7, PowerEdge R750 — certified RHEL 7.9-7.x, 8.2-8.x, 9.0-9.x (cert IDs above). **No 10.x certification exists for this SKU at all.**
- **Scope relationship:** claim exceeds record. Version axis — unqualified "Red Hat Enterprise Linux" literally covers every RHEL release including 10.x, which this SKU has never been certified for.
- **Scope axis:** version.
- **Lifecycle of named platforms:** no version named (itself the finding).
- **Aspirational screen:** not applicable — no specific version is named, so there is nothing forward-looking to screen; this is a present-tense, unqualified claim.

### C2 — Lenovo ServerProven, SR650 V3: RHEL 8.6–9.6 compatibility list *(carried forward, re-verified live)*

- **Quote:** *"Red Hat Enterprise Linux 8.6 / 8.7 / 8.8 / 8.9 / 8.10 / 9.0 / 9.1 / 9.2 / 9.3 / 9.4 / 9.6"* (per-version `<span class="os">` entries; re-fetched 2026-08-29, byte-identical version set to the prior pass).
- **Source URL:** `https://serverproven.lenovo.com/server/sr650-v3/`
- **Fetch method/result:** curl, plain GET, HTTP 200, 2,893,851 bytes, server-rendered, no JS needed.
- **Publisher/register:** Lenovo — marketing/compatibility register (ServerProven is Lenovo's own compatibility lookup tool, not a sales document).
- **Gradient position:** compatible with.
- **Matching Part 1 record:** #9, SR650 V3 — certified 8.6-8.x, 9.0-9.x, 10.0-10.x.
- **Scope relationship:** largely in scope under the catalog's "-x" carry-forward convention, with one notable **omission**: ServerProven lists no RHEL 9.5, and stops entirely before 9.7+ and all of 10.x, while the Lenovo Press guide for the identical SKU (C-below) lists specific minors through 10.2. Two Lenovo-owned pages for the same box disagree on how far the RHEL 9 line and the 10.x line extend — an internal Lenovo inconsistency, not a vendor-vs-Red-Hat one.
- **Scope axis:** version (understatement relative to catalog, and inconsistent with Lenovo's own product guide for the same SKU).
- **Lifecycle:** 8.x = Maintenance Support; 9.x (through 9.6, the highest version this page lists) = Full Support.
- **Aspirational screen:** not aspirational — every version named has already shipped; if anything this page under-lists what is currently available.

### C3 — Lenovo Press ST250 V3 Product Guide (lp1803): RHEL through 9.8 / 10.2 *(carried forward — reclassified, no longer aspirational)*

- **Quote:** *"The ST250 V3 with Intel Pentium or Intel Xeon E processors supports the following operating systems: ... Red Hat Enterprise Linux 8.8 / Red Hat Enterprise Linux 8.9 / Red Hat Enterprise Linux 8.10 / Red Hat Enterprise Linux 9.2 / Red Hat Enterprise Linux 9.3 / Red Hat Enterprise Linux 9.4 / Red Hat Enterprise Linux 9.5 / Red Hat Enterprise Linux 9.6 / Red Hat Enterprise Linux 9.7 / Red Hat Enterprise Linux 9.8 / Red Hat Enterprise Linux 10.0 / Red Hat Enterprise Linux 10.1 / Red Hat Enterprise Linux 10.2"* (p.66/67 of the PDF; a second, near-identical list appears for the Xeon 6300-series variant).
- **Source URL:** `https://lenovopress.lenovo.com/lp1803.pdf`
- **Fetch method/result:** curl, Chrome UA, HTTP 200, 97-page PDF, 5,971,843 bytes. Text extracted via `pdftotext -layout`.
- **Publisher/register:** Lenovo Press — marketing register (product guide, not a support-matrix page).
- **Gradient position:** compatible with / supported on ("supports the following operating systems").
- **Matching Part 1 record:** #11, ST250 V3 — certified 8.8-8.x, 9.2-9.x, 10.0-10.x (cert IDs 604717 / 604707 / 662747).
- **Scope relationship:** scope exceeds record on the version axis, but **not for the reason the prior pass gave**. RHEL 9.7, 9.8, 10.1, and 10.2 are real, released versions (Part 0a) — the violation is that the catalog holds no certification record for those specific minors at all, only for the 9.2 and 10.0 starting points under Red Hat's "-x" open-range notation. Whether that notation is meant to auto-extend to 9.7/9.8/10.1/10.2 is a live judgment call, not a settled fact — this is the correct framing, replacing the prior pass's "claims versions that don't exist yet."
- **Scope axis:** version (specifically: whether the catalog's open-ended "-x" range covers minors several releases past the certified starting point).
- **Lifecycle:** 8.x = Maintenance Support; 9.x and 10.x = Full Support, with 9.8 and 10.2 (GA'd 2026-05-19) the current latest minors of each line.
- **Aspirational screen: FAILS the aspirational exclusion in one direction, passes it in another.** The prior pass's premise — "this is a forward-looking list of unreleased versions" — is false; nothing in this list is unreleased. So C3 does **not** belong in the taxonomy's aspirational/forward-looking exclusion bucket. It belongs in the ordinary scope-mismatch bucket instead: a real, current, unqualified support claim that runs ahead of what the cited certification body has actually certified. **This is the taxonomy boundary correction the brief asked for**: C3 moves from "aspirational, exclude" to "in-scope retest candidate," which changes which axis it should be reasoned about on.

### C4 — Lenovo Press SR650 V3 Product Guide (lp1601): RHEL through 10.2, two processor generations

- **Quote:** *"The SR650 V3 with 5th Gen Intel Xeon Scalable processors supports the following operating systems: ... Red Hat Enterprise Linux 8.8 / Red Hat Enterprise Linux 8.9 / Red Hat Enterprise Linux 8.10 / Red Hat Enterprise Linux 9.2 / ... / Red Hat Enterprise Linux 9.8 / Red Hat Enterprise Linux 10.0 / Red Hat Enterprise Linux 10.1 / Red Hat Enterprise Linux 10.2"* and, in the same section, a second block: *"The SR650 V3 with 4th Gen Intel Xeon Scalable processors supports the following operating systems: ... Red Hat Enterprise Linux 8.6 / Red Hat Enterprise Linux 8.7 / ... / Red Hat Enterprise Linux 9.7 / Red Hat Enterprise Linux 9.8 / Red Hat Enterprise Linux 10.0 / Red Hat Enterprise Linux 10.1 / Red Hat Enterprise Linux 10.2"* (p.150–151, "Operating system support").
- **Source URL:** `https://lenovopress.lenovo.com/lp1601.pdf`
- **Fetch method/result:** curl, Chrome UA, HTTP 200, 143-page PDF, 23,458,929 bytes. `pdftotext -layout` extraction. (Note: the correct product-guide ID for SR650 V3 is lp1601 — lp1610, the ID I first guessed by pattern-matching against ST250 V3's lp1803, actually resolves to the SR655 V3 guide, a different SKU. Caught by checking the PDF's own title page before quoting it.)
- **Publisher/register:** Lenovo Press — marketing register.
- **Gradient position:** compatible with / supported on.
- **Matching Part 1 record:** #9, SR650 V3 — certified 8.6-8.x, 9.0-9.x, 10.0-10.x (same record as C2, different Lenovo document).
- **Scope relationship:** same structural violation as C3 — the guide names specific minors (9.7, 9.8, 10.1, 10.2) beyond the catalog's certified starting points, and does so for **both** processor generations sold under the SR650 V3 name, doubling the surface area of the claim relative to a single-generation SKU like ST250 V3.
- **Scope axis:** version, plus a secondary **configuration axis**: the two processor-generation sub-variants (4th Gen vs. 5th Gen Xeon) carry different minimum-version floors (8.6 vs. 8.8) under one product name and one certification record, so a reader of the certification record alone cannot tell which processor generation the cert actually covers.
- **Lifecycle:** identical to C3 — 9.7/9.8/10.1/10.2 all GA'd and current.
- **Aspirational screen:** not aspirational, for the same reason as C3 — every version listed has shipped.

### C5 — Lenovo Press SR630 V3 Product Guide (lp1600): RHEL through 10.2, two processor generations

- **Quote:** *"The SR630 V3 with 5th Gen Intel Xeon Scalable processors supports the following operating systems: ... Red Hat Enterprise Linux 8.8 / ... / Red Hat Enterprise Linux 9.8 / Red Hat Enterprise Linux 10.0 / Red Hat Enterprise Linux 10.1 / Red Hat Enterprise Linux 10.2"* (p.122, "Operating system support"), with an equivalent 4th-Gen-Xeon block listing 8.6 through 10.2 immediately below it.
- **Source URL:** `https://lenovopress.lenovo.com/lp1600.pdf`
- **Fetch method/result:** curl, Chrome UA, HTTP 200, 95-page PDF, 19,442,294 bytes. `pdftotext -layout` extraction.
- **Publisher/register:** Lenovo Press — marketing register.
- **Gradient position:** compatible with / supported on.
- **Matching Part 1 record:** #10, SR630 V3 — certified 8.6-8.x, 9.0-9.x, 10.0-10.x (cert IDs 441317 / 439647 / 662377).
- **Scope relationship:** structurally identical to C4 (same publisher, same document template, sibling SKU in the same server family) — version-axis overrun against the catalog's open-range ceiling, plus the same processor-generation configuration ambiguity.
- **Scope axis:** version, secondary configuration axis (processor generation).
- **Lifecycle:** identical to C3/C4.
- **Aspirational screen:** not aspirational.

### C6 — Dell PowerEdge R7525 Spec Sheet: unversioned "Red Hat Enterprise Linux"

- **Quote:** *"Operating Systems & Hypervisors ... Canonical® Ubuntu® LTS ... Citrix® Hypervisor ... Microsoft® Windows Server® with Hyper-V ... Red Hat® Enterprise Linux ... SUSE® Linux Enterprise Server ... VMware® ESXi®"*
- **Source URL:** `https://www.delltechnologies.com/asset/en-us/products/servers/technical-support/dell-emc-poweredge-r7525-spec-sheet.pdf`
- **Fetch method/result:** curl, Chrome UA + `Referer` header, HTTP 200, 3-page PDF, 360,697 bytes.
- **Publisher/register:** Dell Technologies — marketing register.
- **Gradient position:** compatible with (bare list, no version, no certification language).
- **Matching Part 1 record:** #8, PowerEdge R7525 — certified 7.7-7.x, 8.1-8.x, 9.0-9.x. **No 10.x certification exists.**
- **Scope relationship:** same shape as C1 — unqualified claim exceeds record on the version axis (implicitly covers 10.x, which the record does not certify).
- **Scope axis:** version.
- **Lifecycle:** no version named.
- **Aspirational screen:** not applicable (no version named).

### C7 — Dell PowerEdge R660 Spec Sheet: unversioned "Red Hat Enterprise Linux"

- **Quote:** *"Operating System and Hypervisors ... Canonical Ubuntu Server LTS ... Microsoft Windows Server with Hyper-V ... Red Hat Enterprise Linux ... SUSE Linux Enterprise Server ... VMware ESXi ... For specifications and interoperability details, see Dell.com/OSsupport."*
- **Source URL:** `https://www.delltechnologies.com/assetlink/doc/en-us/poweredge-r660-spec-sheet-en-dl1lmt3-original.pdf` (redirect target of `.../technical-support/poweredge-r660-spec-sheet.pdf`)
- **Fetch method/result:** curl, Chrome UA + `Referer: .../servers/poweredge-r660.htm`, HTTP 200 (following redirect), 234,849 bytes.
- **Publisher/register:** Dell Technologies — marketing register.
- **Gradient position:** compatible with.
- **Matching Part 1 record:** #5, PowerEdge R660 — certified 8.6-8.x, 9.0-9.x, **10.0-10.x** (cert ID 669267 exists for this SKU, unlike R750/R7525).
- **Scope relationship:** claim still exceeds record technically (no version is named, so read literally it also claims 7.x and 11.x, neither certified), but the practical gap to "everything currently shippable" is narrower than C1/C6, because this SKU does hold a 10.x cert. **Deliberately paired against C1/C6 for this reason** — same claim text pattern, different-sized real gap depending on which catalog record it's checked against.
- **Scope axis:** version.
- **Lifecycle:** no version named.
- **Aspirational screen:** not applicable.

### C8 — Dell PowerEdge R760 Spec Sheet: unversioned "Red Hat Enterprise Linux"

- **Quote:** *"Operating System and Hypervisors ... Canonical Ubuntu Server LTS ... Microsoft Windows Server with Hyper-V ... Red Hat Enterprise Linux ... SUSE Linux Enterprise Server ... VMware ESXi ... For specifications and interoperability details, see Dell.com/OSsupport."*
- **Source URL:** `https://www.delltechnologies.com/assetlink/doc/en-us/poweredge-r760-spec-sheet-en-dl1lkoo-original.pdf` (redirect target of `.../technical-support/poweredge-r760-spec-sheet.pdf`)
- **Fetch method/result:** curl, Chrome UA + `Referer: .../servers/poweredge-r760.htm`, HTTP 200, 204,768 bytes.
- **Publisher/register:** Dell Technologies — marketing register.
- **Gradient position:** compatible with.
- **Matching Part 1 record:** #6, PowerEdge R760 — certified 8.6-8.x, 9.0-9.x, 10.0-10.x (cert ID 669277).
- **Scope relationship:** identical shape and identical verdict to C7 (R660) — same product-line sibling, same catalog cert ceiling, same text template.
- **Scope axis:** version.
- **Lifecycle:** no version named.
- **Aspirational screen:** not applicable.

### C9 — Dell PowerEdge R760 Technical Guide: "Standard operating system ... Supported (Tier-1)"

- **Quote:** *"Standard operating system   Red Hat Enterprise Linux, SUSE, Windows Server 2019 or 2022, Ubuntu, CentOS   Supported (Tier-1)"* — a row in "Table 22. Systems Management software support matrix," column header "PE mainstream."
- **Source URL:** `https://www.delltechnologies.com/asset/en-us/products/servers/technical-support/poweredge-r760-technical-guide.pdf`
- **Fetch method/result:** curl, Chrome UA + `Referer` header, `--http1.1`, HTTP 200, 17,409,343 bytes. `pdftotext -layout` extraction; row located via full-text search for "Red Hat Enterprise Linux."
- **Publisher/register:** Dell Technologies — marketing/documentation register (technical guide; more detailed than a spec sheet but still Dell-authored, not a Red Hat document).
- **Gradient position:** **supported on**, at a stated support tier — a stronger and more specific claim shape than C1/C6/C7/C8's bare compatibility list, because it asserts a support classification ("Tier-1"), not just OS presence.
- **Matching Part 1 record:** #6, PowerEdge R760 — certified 8.6-8.x, 9.0-9.x, 10.0-10.x.
- **Scope relationship:** exceeds record on **two axes at once**. Version axis: no RHEL version is named, so "Tier-1 supported" reads as covering every RHEL release. Configuration/support-tier axis: the table's own column header is "PE mainstream" — this is a **family-wide** support-tier claim (applying across the whole PowerEdge mainstream line), embedded inside a document titled for one specific SKU (R760), while the certification record it would need to be checked against exists only per-SKU. A reader cannot tell from this claim alone which mainstream SKUs the Tier-1 designation was actually validated against.
- **Scope axis:** version + configuration/support-tier (family-wide claim inside a SKU-specific document).
- **Lifecycle:** no version named.
- **Aspirational screen:** not applicable (no version named); not forward-looking language either — "Supported" is stated as current fact, not a roadmap item.

### C10 — Broadberry: "Redhat Linux Certified Supermicro Servers"

- **Quote:** *"Redhat Linux Certified Supermicro Servers"* (page title) / *"These Supermicro SuperServers have been certified and approved to run Redhat Linux"* (page lede).
- **Source URL:** `https://www.broadberry.com/redhat-linux-certified-supermicro-servers`
- **Fetch method/result:** curl, plain GET, HTTP 200, 37,127 bytes, static server-rendered HTML (product-grid portion of the page did not render in the static fetch — only the header claim and site boilerplate were retrievable this way — so this candidate is scored on the header claim alone, not any specific SKU list).
- **Publisher/register:** Broadberry Data Systems — **reseller** register (a UK/US server integrator/reseller, not Supermicro or Red Hat).
- **Gradient position:** **certified for** — explicit "certified and approved" language, the strongest gradient position of any candidate in this set, made by a party (the reseller) that does not itself hold the certification.
- **Matching Part 1 record:** #14, Supermicro SuperServer SYS-221HE-TNRD — certified RHEL 8.7-8.x, 9.0-9.x only (no 7.x, no 10.x).
- **Scope relationship:** exceeds record maximally. The claim names no SKU, no RHEL version, and generalizes "certified" across an entire Supermicro product category that Broadberry resells — a single Red Hat certification record for one specific Supermicro SKU cannot support a blanket "these servers are certified" claim about the category. This is the sharpest version of the pattern the brief predicted for resellers: "resellers generalize more aggressively than vendors, and that is where scope violations concentrate."
- **Scope axis:** version + component/SKU-identity (claim doesn't name which SuperServer models are meant; only one of Supermicro's catalog-listed SKUs has a verified cert at all in this evidence set).
- **Lifecycle:** no version named.
- **Aspirational screen:** not applicable (no version named); not forward-looking.

### C11 — Broadberry: "Fully Compatible Redhat Linux Servers" (CyberStore)

- **Quote:** *"Fully Compatible Redhat Linux Servers ... Our enterprise-grade solutions have been trusted to power some of the biggest organisations in the world."* and, further down the same page: *"There is full support for complete infrastructure initiatives, ranging from virtualisation to emerging technology areas such as cloud-native deploys designed, built and optimised for Red Hat Enterprise Linux."*
- **Source URL:** `https://www.broadberry.com/server-os/redhat-linux`
- **Fetch method/result:** curl, plain GET, HTTP 200, 111,560 bytes, static server-rendered HTML.
- **Publisher/register:** Broadberry Data Systems — reseller register (CyberStore is Broadberry's own house brand built on OEM hardware, not a single named SKU with its own Red Hat catalog listing).
- **Gradient position:** **certified for** / **compatible with**, blended — "Fully Compatible" in the heading, "designed, built and optimised for Red Hat Enterprise Linux" in the body, no version, no specific certification citation anywhere on the page.
- **Matching Part 1 record:** none directly — Broadberry's CyberStore line is not itself one of the 15 catalog SKUs. Best available comparator is #14 (Supermicro SYS-221HE-TNRD), since Broadberry's rack/tower CyberStore builds are Supermicro-based per the same site's product pages, making this a same-underlying-hardware pairing with C10 rather than an identical-record pairing.
- **Scope relationship:** exceeds any plausible record on every axis at once — no version, no SKU, and "optimised for" is a stronger engineering claim than "compatible with," asserted with zero certification citation on the page.
- **Scope axis:** version + component (no SKU named at all — the least anchored claim in the set).
- **Lifecycle:** no version named.
- **Aspirational screen:** not applicable; note the page's "cloud-native deploys" language is about deployment patterns Red Hat Enterprise Linux supports generally, not a specific future OS version, so it does not trip the forward-looking exclusion either.

### C12 — Lenovo Press ST250 V3 Product Guide (lp1803): Xeon 6300-series variant list

- **Quote:** *"The ST250 V3 with Intel Pentium or Intel Xeon 6300 series processors supports the following operating systems: ... Red Hat Enterprise Linux 8.10 / Red Hat Enterprise Linux 9.4 / Red Hat Enterprise Linux 9.5 / Red Hat Enterprise Linux 9.6 / Red Hat Enterprise Linux 9.7 / Red Hat Enterprise Linux 9.8 / Red Hat Enterprise Linux 10.0 / Red Hat Enterprise Linux 10.1 / Red Hat Enterprise Linux 10.2"* (p.67, immediately following the C3 quote in the same PDF).
- **Source URL:** `https://lenovopress.lenovo.com/lp1803.pdf` (same document as C3, different processor-variant block within it).
- **Fetch method/result:** identical fetch to C3 (same PDF, same HTTP 200 response).
- **Publisher/register:** Lenovo Press — marketing register.
- **Gradient position:** compatible with / supported on.
- **Matching Part 1 record:** #11, ST250 V3 — same single catalog record as C3 (certified 8.8-8.x, 9.2-9.x, 10.0-10.x); the catalog record does not distinguish by processor family the way the product guide does.
- **Scope relationship:** exceeds record on the version axis for the same reason as C3, **and** introduces a floor mismatch on top of it: this variant's minimum listed RHEL 8 version is 8.10, skipping 8.8/8.9 entirely, while the single catalog cert record for the whole ST250 V3 line starts at 8.8. A reader relying on the catalog record alone cannot tell that the Xeon-6300 variant's real floor, per Lenovo's own document, is one full RHEL 8 minor higher than what the certification record implies for the product name as a whole.
- **Scope axis:** version, plus a configuration axis distinct from C3/C4/C5's (here the two processor variants disagree at the *floor*, not just the ceiling).
- **Lifecycle:** identical to C3 — nothing named is unreleased.
- **Aspirational screen:** not aspirational, same finding as C3.

---

## Part 2 — Aspirational-claims screen, applied to every version-naming candidate

The taxonomy excludes forward-looking/aspirational claims (planned or unreleased platform versions presented as current). Applying this screen to every candidate above that names a specific version:

| Candidate | Named versions | All released as of 2026-08-29? | Aspirational? |
|---|---|---|---|
| C2 | RHEL 8.6–9.4, 9.6 | Yes | No |
| C3 | RHEL 8.8–9.8, 10.0–10.2 | Yes (Part 0a) | **No — corrects prior pass's "yes"** |
| C4 | RHEL 8.6–9.8, 10.0–10.2 | Yes | No |
| C5 | RHEL 8.6–9.8, 10.0–10.2 | Yes | No |
| C12 | RHEL 8.10, 9.4–9.8, 10.0–10.2 | Yes | No |

No candidate in this pass's set is genuinely aspirational — every named RHEL version had already GA'd by the fetch date. This is itself a finding worth flagging: the prior pass's single aspirational call (C3) does not survive a proper minor-release-date check, and no replacement aspirational example turned up in this pass's search either. **The retest set currently has no true positive for the aspirational-exclusion category** — that remains a gap (see Part 4).

---

## Part 3 — Six-claim / three-pair recommendation

Twelve real candidates were found, meeting the "twelve or more" target without padding. Pairing them into three verdict-agreeing-within/differing-across pairs:

**Pair A — verdict: scope exceeds record, version axis, unqualified claim vs. a record with no ceiling headroom at all.**
- **C1** (Dell R750 spec sheet, unversioned RHEL, record has no 10.x cert at all)
- **C6** (Dell R7525 spec sheet, unversioned RHEL, record has no 10.x cert at all)
- Both should rule "scope exceeds record." Chosen as the cleanest, least-ambiguous pair — no "-x" open-range judgment call is even needed here, since the ceiling gap (10.x, completely uncertified) is absolute rather than a matter of interpreting Red Hat's range notation.

**Pair B — verdict: scope exceeds record, version axis, but through the "-x" open-range interpretation question rather than an absolute ceiling gap.**
- **C3** (Lenovo Press ST250 V3, RHEL through 9.8/10.2 against a catalog record open-ended at 9.2-9.x/10.0-10.x)
- **C4** (Lenovo Press SR650 V3, same pattern, same publisher, sibling SKU)
- Both should rule "scope exceeds record — or defensible, depending on how the catalog's open-range notation is read," which is a **narrower, harder call** than Pair A: unlike C1/C6, there is no absolute gap (10.x is certified in some form for both underlying SKUs); the question is whether the certificate covers 9.7/9.8/10.1/10.2 specifically. This is deliberately the pair most likely to split reviewers, since it is genuinely arguable rather than a bare omission.

**Pair C — verdict: scope exceeds record, on axes other than plain RHEL-version-number overrun.**
- **C9** (Dell R760 technical guide, "Supported (Tier-1)" claim scoped to the whole "PE mainstream" family inside a SKU-specific document)
- **C10** (Broadberry reseller page, "certified and approved" claimed for a Supermicro product category against one SKU's certification record)
- Both should rule "scope exceeds record," but the axis is different from Pairs A/B: C9 violates on a support-tier/family-breadth axis (a family-wide claim living inside a SKU-titled document), and C10 violates on a component/SKU-identity axis (no SKU is even named). Both differ from Pairs A/B in that the *problem is not just "which RHEL version"* — it's *"which product does this even apply to."* This is the pair most likely to expose whether a reviewer can name the correct axis rather than just detecting *that* something is wrong.

This uses 6 of the 12 candidates. **Reserve pool:** C2, C5, C7, C8, C11, C12 — all independently usable if any of the six above proves weaker under closer inspection (C2 in particular is interesting as a rare *understatement* case, and C11 as the least-anchored, no-SKU-at-all claim, if the harness wants a fourth pair later).

---

## Part 4 — Gaps, honestly reported

**HPE could not be evidenced again in this pass.** Both the `collaterals/collateral.*.html` wrapper pages (per the brief, already known to fail) and the direct-PDF route (`hpe.com/psnow/doc/{id}.pdf`) were retried this pass, with a real, `WebSearch`-confirmed document ID (`a50004307enw`, HPE ProLiant DL380 Gen11 QuickSpecs). The direct-PDF route still fails: `curl` gets an HTTP/2 stream reset (`curl: (92) HTTP/2 stream 1 was not closed cleanly: INTERNAL_ERROR`) reproducibly across three attempts (default HTTP/2, forced `--http1.1`, and with retry), and `WebFetch` times out on the same URL. This is a host-level block, not a wrong-ID problem — the URL is confirmed correct via independent search, it simply cannot be fetched by either tool available in this environment. HPE remains a hole in the claims-side evidence, exactly as the prior pass found.

**No true aspirational/forward-looking candidate was found in this pass.** Part 2 shows every version-naming candidate names only already-released versions. The taxonomy's aspirational-exclusion category — a real vendor document naming a genuinely unreleased platform version as currently supported — has no verified example in either this pass or the corrected version of the prior pass's C3. If Week 19 specifically needs an aspirational-exclusion test case, that is unmet and would need a further pass (a plausible place to look: a vendor's own forward-looking roadmap page or press release announcing "will support RHEL 11," rather than a product guide's OS-support table, since product guides appear to only list versions after they exist).

**Supermicro's own marketing register is still unfetchable.** As in the prior pass, direct Supermicro press-release/datasheet URLs return 403. The Broadberry reseller pages (C10, C11) are the only Supermicro-adjacent claims-side evidence obtained in either pass, and neither names a specific Supermicro SKU.

**Dell does not publish per-minor RHEL version lists in the documents that were fetchable.** Every Dell source obtained (four spec sheets, two technical guides) uses unversioned "Red Hat Enterprise Linux" throughout — a real and structurally consistent finding, not a fetch failure, but it means the Dell side of this candidate set is version-axis-shallow (always "no version at all" rather than "a specific but wrong version") compared to the Lenovo Press side. Dell's actual versioned RHEL support matrix (`linux.dell.com/files/supportmatrix/RHEL_Support_Matrix.pdf`, used as a documentation-register baseline in the prior pass) was not re-fetched this pass since it was already confirmed and is not itself a marketing claim.

**Count against target:** 12 real candidates found, meeting "twelve or more"; six formed into three pairs per Part 3, each pair internally agreeing and differing in reasoning from the other two, as required. No fabricated text was used to reach either number.

---

## Part 5 — Carried forward unchanged

Per the brief, the demonstration bucket from the prior pass (AMD SeaMicro SM10000-XE 2012 press release; Cisco 2009 original UCS/RHEL partnership announcement) is settled and required no further work this pass. Not re-verified or re-included here; see the prior report's C5/C6 for that material.
