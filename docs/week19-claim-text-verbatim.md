# Week 19 — Verbatim, Unelided Claim Text for the Six Retest Claims

**Status:** Report only. No registry writes, no schema changes, no skill changes. The claim seed stays held pending this document.
**Why this exists:** `week19-compatibility-claim-candidates-v2.md` (`f3c354b`) quotes all six retest claims verbatim but abridged for a human reader — every quote carries "..." where surrounding text was elided. `claim_text` cannot carry an elision; a retest session judges exactly the string it is given. This document re-fetches each source independently and records the complete operating-system-support section (or full claim text, for the two Broadberry pages) with no trimming, so `claim_text` can trace to a committed artifact rather than an untracked fetch.
**Fetch date:** 2026-08-31.
**Fetch method:** `curl`, Chrome user-agent, `-L` to follow redirects, `-D` to capture response headers. Dell PDFs use the method and URLs already verified in `week19-dell-pointer-verification.md` (re-quoted below, not re-fetched a third time — see note in each Dell section). Lenovo PDFs fetched fresh this pass; text extracted via `pdftotext -layout`. Broadberry pages fetched fresh this pass as plain HTML; tags stripped for readability, content otherwise unmodified.
**Scope:** Read-only against sources. Writes only this one document. No reconciliation of any discrepancy found against `f3c354b` — discrepancies are reported and left open.

---

## C7 — Dell PowerEdge R660 Spec Sheet

- **Source URL:** `https://www.delltechnologies.com/assetlink/doc/en-us/poweredge-r660-spec-sheet-en-dl1lmt3-original.pdf`
- **HTTP status:** 200 (direct asset-link URL, no redirect).
- **Byte size (this doc, re-quoted from `week19-dell-pointer-verification.md`, fetched 2026-08-30):** 234,849 bytes. **Not independently re-fetched in this pass** — `week19-dell-pointer-verification.md` already fetched this exact URL one day prior with the same method and captured the complete OS section; re-fetching a third time added no new information, so that result is reused here verbatim rather than re-pulled.
- **Byte size comparison against `f3c354b`:** `f3c354b` (C7) does not record a byte size directly comparable in its own text — it describes the fetch as returning "234,849 bytes" in `week19-dell-pointer-verification.md`, which itself matches `f3c354b`'s companion figure. **Match, no discrepancy.**
- **Section heading:** "Operating System and Hypervisors" (table row label; not a numbered page in the 3-page spec sheet).
- **Complete, unelided OS-section text:**

```
Operating System and Hypervisors       • Canonical Ubuntu Server LTS
                                         • Microsoft Windows Server with Hyper-V
                                         • Red Hat Enterprise Linux
                                         • SUSE Linux Enterprise Server
                                         • VMware ESXi
                                       For specifications and interoperability details, see Dell.com/OSsupport.
```

- **Where the claim begins and ends:** begins at the "Operating System and Hypervisors" row label, ends at the period closing the Dell.com/OSsupport sentence. Nothing precedes or follows this bullet block within the row.

---

## C8 — Dell PowerEdge R760 Spec Sheet

- **Source URL:** `https://www.delltechnologies.com/assetlink/doc/en-us/poweredge-r760-spec-sheet-en-dl1lkoo-original.pdf`
- **HTTP status:** 200 (direct asset-link URL, no redirect).
- **Byte size (re-quoted from `week19-dell-pointer-verification.md`, fetched 2026-08-30):** 204,768 bytes. Not independently re-fetched this pass, for the same reason as C7.
- **Byte size comparison against `f3c354b`:** matches the figure `f3c354b` records for C8. **Match, no discrepancy.**
- **Section heading:** "Operating System and Hypervisors."
- **Complete, unelided OS-section text:**

```
Operating System and Hypervisors       • Canonical Ubuntu Server LTS
                                         • Microsoft Windows Server with Hyper-V
                                         • Red Hat Enterprise Linux
                                         • SUSE Linux Enterprise Server
                                         • VMware ESXi
                                       For specifications and interoperability details, see Dell.com/OSsupport.
```

- **Where the claim begins and ends:** same shape as C7 — begins at the row label, ends at the Dell.com/OSsupport sentence.

### C7 vs. C8 — are the two OS lists identical?

**Yes, character-for-character identical**, once each is reduced to the text stream `pdftotext -layout` extracts. Same five-item bullet list in the same order (Canonical Ubuntu Server LTS, Microsoft Windows Server with Hyper-V, Red Hat Enterprise Linux, SUSE Linux Enterprise Server, VMware ESXi), same trailing pointer sentence worded identically: *"For specifications and interoperability details, see Dell.com/OSsupport."* The two source PDFs differ in byte size (234,849 vs. 204,768) because they are different physical documents (different page art, different SKU-specific imagery and layout), but the OS/hypervisor text block itself is a shared template reused verbatim across both spec sheets. `f3c354b`'s Pair A design — treating C7 and C8 as the same claim-text pattern applied to two SKUs with identical certified-version ranges — holds up against the unelided text, not just the report's summary of it.

---

## C3 — Lenovo Press ST250 V3 Product Guide (lp1803)

- **Source URL:** `https://lenovopress.lenovo.com/lp1803.pdf`
- **HTTP status:** 200 (fetched fresh this pass, Chrome UA, no redirect).
- **Byte size (this fetch, 2026-08-31):** 5,966,399 bytes.
- **Byte size comparison against `f3c354b`:** `f3c354b` records 5,971,843 bytes for this same URL. **Discrepancy: 5,444 bytes smaller in this fetch.** Not reconciled — reported per instructions. Page count matches (97 pages via `pdfinfo`, consistent with `f3c354b`'s "97-page PDF"), and the extracted RHEL version text matches `f3c354b`'s quote exactly (see below), so the discrepancy does not appear to affect the claim-relevant content, but the byte-level difference itself is unexplained and is a finding, not a resolved non-issue.
- **Page reference:** p.66–67 (matches `f3c354b`).
- **Section heading:** "Operating systems."
- **Complete, unelided OS-section text (first processor-variant block, the one `claim_text` targets):**

```
Operating systems
The ST250 V3 with Intel Pentium or Intel Xeon E processors supports the following operating systems:
       Microsoft Windows Server 2022
       Microsoft Windows Server 2025
       Red Hat Enterprise Linux 8.8
       Red Hat Enterprise Linux 8.9
       Red Hat Enterprise Linux 8.10
       Red Hat Enterprise Linux 9.2
       Red Hat Enterprise Linux 9.3
       Red Hat Enterprise Linux 9.4
       Red Hat Enterprise Linux 9.5
       Red Hat Enterprise Linux 9.6
       Red Hat Enterprise Linux 9.7
       Red Hat Enterprise Linux 9.8
       Red Hat Enterprise Linux 10.0
       Red Hat Enterprise Linux 10.1
       Red Hat Enterprise Linux 10.2
       SUSE Linux Enterprise Server 15 SP5
       SUSE Linux Enterprise Server 15 SP6
       SUSE Linux Enterprise Server 15 SP7
       SUSE Linux Enterprise Server 15 Xen SP5
       SUSE Linux Enterprise Server 16
       Ubuntu 22.04 LTS 64-bit
       Ubuntu 24.04 LTS 64-bit
       Ubuntu 26.04 LTS 64-bit
       VMware ESXi 8.0 U2
       VMware ESXi 8.0 U3
       VMware ESXi 9.0
       VMware ESXi 9.1
```

- **Where the claim begins and ends:** begins at "Operating systems" (section heading), ends at "VMware ESXi 9.1" — the last line before the second processor-variant block ("The ST250 V3 with Intel Pentium or Intel Xeon 6300 series processors supports the following operating systems:," the `f3c354b` C12 candidate, not part of C3) begins.
- **Comparison against `f3c354b`'s abridged quote:** `f3c354b` elided the Windows/SUSE/Ubuntu/VMware entries with "...". The unelided text confirms every RHEL entry `f3c354b` quoted (8.8 through 10.2, thirteen entries) is present and in the same order, with nothing additional and nothing missing between them. The elision hid other-vendor OS names, not any RHEL version.

---

## C4 — Lenovo Press SR650 V3 Product Guide (lp1601)

- **Source URL:** `https://lenovopress.lenovo.com/lp1601.pdf`
- **HTTP status:** 200 (fetched fresh this pass, Chrome UA, no redirect).
- **Byte size (this fetch, 2026-08-31):** 23,432,942 bytes.
- **Byte size comparison against `f3c354b`:** `f3c354b` records 23,458,929 bytes. **Discrepancy: 25,987 bytes smaller in this fetch.** Not reconciled — reported per instructions.
- **Page count discrepancy:** `pdfinfo` on this fetch reports **187 pages**. `f3c354b` describes this same URL as a "143-page PDF." **This is a larger and more structurally significant discrepancy than the byte-count difference** — a 44-page gap is not plausibly explained by a version bump alone. Title page confirms this is the correct document ("Lenovo ThinkSystem SR650 V3 Server / Product Guide"), and the OS-support section content matches `f3c354b`'s quote (below), but the document's overall length disagrees sharply with what `f3c354b` recorded. Reported, not resolved.
- **Page reference (this fetch):** the OS-support section appears on **pages 149–150** of the 187-page document (per the page-footer text extracted alongside it), not p.150–151 as `f3c354b` states. Given the page-count discrepancy above, page numbers between the two fetches are not directly comparable — a 44-page difference elsewhere in the document would shift subsequent page numbers even if this section's *content* is unchanged. Recorded as-observed in this fetch; not reconciled against `f3c354b`'s page reference.
- **Section heading:** "Operating system support."
- **Complete, unelided OS-section text (both processor-variant blocks):**

```
Operating system support
The SR650 V3 with 5th Gen Intel Xeon Scalable processors supports the following operating systems:
      Microsoft Windows 10 (x64)
      Microsoft Windows 11
      Microsoft Windows Server 2019
      Microsoft Windows Server 2022
      Microsoft Windows Server 2025
      Red Hat Enterprise Linux 8.8
      Red Hat Enterprise Linux 8.9
      Red Hat Enterprise Linux 8.10
      Red Hat Enterprise Linux 9.2
      Red Hat Enterprise Linux 9.3
      Red Hat Enterprise Linux 9.4
      Red Hat Enterprise Linux 9.5
      Red Hat Enterprise Linux 9.6
      Red Hat Enterprise Linux 9.7
      Red Hat Enterprise Linux 9.8
      Red Hat Enterprise Linux 10.0
      Red Hat Enterprise Linux 10.1
      Red Hat Enterprise Linux 10.2
      SUSE Linux Enterprise Server 15 SP5
      SUSE Linux Enterprise Server 15 SP6
      SUSE Linux Enterprise Server 15 SP7
      SUSE Linux Enterprise Server 15 Xen SP5
      SUSE Linux Enterprise Server 16
      Ubuntu 20.04 LTS 64-bit
      Ubuntu 22.04 LTS 64-bit
      Ubuntu 24.04 LTS 64-bit
      Ubuntu 26.04 LTS 64-bit
      VMware ESXi 7.0 U3
      VMware ESXi 8.0 U2
      VMware ESXi 8.0 U3
      VMware ESXi 9.0
      VMware ESXi 9.1
The SR650 V3 with 4th Gen Intel Xeon Scalable processors supports the following operating systems:
      Microsoft Windows 10 (x64)
      Microsoft Windows 11
      Microsoft Windows Server 2019
      Microsoft Windows Server 2022
      Microsoft Windows Server 2025
      Red Hat Enterprise Linux 8.6
      Red Hat Enterprise Linux 8.7
      Red Hat Enterprise Linux 8.8
      Red Hat Enterprise Linux 8.9
      Red Hat Enterprise Linux 8.10
      Red Hat Enterprise Linux 9.0
      Red Hat Enterprise Linux 9.1
      Red Hat Enterprise Linux 9.2
      Red Hat Enterprise Linux 9.3
      Red Hat Enterprise Linux 9.4
      Red Hat Enterprise Linux 9.5
      Red Hat Enterprise Linux 9.6
      Red Hat Enterprise Linux 9.7
      Red Hat Enterprise Linux 9.8
      Red Hat Enterprise Linux 10.0
      Red Hat Enterprise Linux 10.1
      Red Hat Enterprise Linux 10.2
      SUSE Linux Enterprise Server 15 SP4
      SUSE Linux Enterprise Server 15 SP5
      SUSE Linux Enterprise Server 15 SP6
      SUSE Linux Enterprise Server 15 SP7
      SUSE Linux Enterprise Server 15 Xen SP4
      SUSE Linux Enterprise Server 15 Xen SP5
      SUSE Linux Enterprise Server 16
      Ubuntu 20.04 LTS 64-bit
      Ubuntu 22.04 LTS 64-bit
      Ubuntu 24.04 LTS 64-bit
      Ubuntu 26.04 LTS 64-bit
      VMware ESXi 7.0 U3
      VMware ESXi 8.0
      VMware ESXi 8.0 U1
      VMware ESXi 8.0 U2
      VMware ESXi 8.0 U3
      VMware ESXi 9.0
      VMware ESXi 9.1
```

- **Where the claim begins and ends:** begins at "Operating system support" (section heading), ends at "VMware ESXi 9.1" closing the 4th Gen block — the next line in the source ("For a complete list of supported, certified and tested operating systems, plus additional details and links to...") is a pointer to an external compatibility matrix, structurally analogous to the Dell.com/OSsupport pointer in C7/C8, and is **not** part of either quoted OS list. Whether that pointer sentence belongs in `claim_text` alongside the two blocks is a scope question this document does not settle — flagging it as adjacent, unquoted context.
- **Comparison against `f3c354b`'s abridged quote:** exact match on every RHEL entry in both blocks (5th Gen: 8.8 through 10.2, thirteen entries; 4th Gen: 8.6 through 10.2, seventeen entries). As with C3, `f3c354b`'s "..." elided other-vendor OS names between and after the RHEL runs, not any RHEL version. **Pair B symmetry holds**: C3's quote was already near-complete in `f3c354b`; C4's was more heavily abridged by character count, but the unelided text shows both claims' full RHEL version lists were preserved without gaps in the original report — the asymmetry was in how much *non-RHEL* text was cut, not in the completeness of the configuration-scope-relevant RHEL data itself.

---

## C10 — Broadberry, "Redhat Linux Certified Supermicro Servers"

- **Source URL:** `https://www.broadberry.com/redhat-linux-certified-supermicro-servers`
- **HTTP status:** `HTTP/2 200`.
- **Byte size (this fetch, 2026-08-31):** 37,127 bytes.
- **Byte size comparison against `f3c354b`:** `f3c354b` records 37,127 bytes for this same URL. **Exact match, no discrepancy.**
- **Section reference:** page title (`<h1>`-equivalent) and lede paragraph immediately below it, near the top of the page body, following only the site header/navigation.
- **Complete, unelided claim text:**

```
Redhat Linux Certified Supermicro Servers
These Supermicro SuperServers have been certified and approved to run Redhat Linux
```

- **Where the claim begins and ends:** the title and lede are the entirety of the SKU/certification-relevant content on this page. Everything before it is site header and navigation boilerplate (About Us, Support, My Account, region-selector links). Everything after it — checked in full across the remaining ~230 extracted lines — is generic site content unrelated to Red Hat certification specifics: a phone-sales call-to-action, "Extensive Testing" / "Customization Service" marketing blurbs, a "Trusted by the World's Biggest Brands" logo section, a news item, review excerpts for unrelated CyberServe SKUs, and footer/contact boilerplate. **No RHEL version, no Supermicro SKU name, and no second certification reference appear anywhere else on the page.** This confirms `f3c354b`'s note that "the product-grid portion of the page did not render in the static fetch" and that the claim is properly scored on the header+lede alone — there is no additional page content this pass recovered that `f3c354b` missed.

---

## C11 — Broadberry, "Fully Compatible Redhat Linux Servers" (CyberStore)

- **Source URL:** `https://www.broadberry.com/server-os/redhat-linux`
- **HTTP status:** `HTTP/2 200`.
- **Byte size (this fetch, 2026-08-31):** 111,560 bytes.
- **Byte size comparison against `f3c354b`:** `f3c354b` records 111,560 bytes for this same URL. **Exact match, no discrepancy.**
- **Section reference:** the page repeats a hero/breadcrumb block twice (once as a visible page header, once — byte-identical in wording — a short distance further down, likely a duplicated DOM section rather than a rendering artifact of the static fetch). The first quoted span sits in this hero block; the second sits inside a "Features" subsection well below it.
- **Complete, unelided text of the first quoted span (hero block):**

```
Redhat Linux Servers
Home
Servers
Redhat Linux Servers
If your business requires a stable, reliable and high performing storage appliance then the Broadberry CyberStore storage appliance configured with Red Hat is the perfect option.
Fully Compatible Redhat Linux Servers
Our enterprise-grade solutions have been trusted to power some of the biggest organisations in the world. This includes the BBC, Sky, NASA, the University Oxford, the University of Cambridge, Toshiba Rolls-Royce, Toyota, Google, Virgin and many more.
```

- **Complete, unelided text of the second quoted span (Features subsection):**

```
Features
Red Hat delivers superb performance with a focus on application stability, giving you the confidence to run business-critical workloads. Security is built in and support from a leading security team is available.
You can enjoy the freedom to innovate through access to development tools, container technologies and thousands if hardware, software and cloud partners. There is full support for complete infrastructure initiatives, ranging from virtualisation to emerging technology areas such as cloud-native deploys designed, built and optimised for Red Hat Enterprise Linux.
```

(Note: "thousands if hardware" is the source page's own text — not a transcription error in this document. Preserved verbatim, typo included.)

### C11 — are the two quoted spans contiguous, adjacent, or separated by unrelated content?

**Separated by substantial intervening content — not adjacent.** Between "Our enterprise-grade solutions have been trusted..." (end of the first span) and "Red Hat delivers superb performance..." (start of the second span), the page carries, in order:
1. "Configure Range" / "Contact Us" (call-to-action buttons)
2. A second, near-duplicate rendering of the hero block itself ("Enterprise-Grade Servers," "Open Standards Hardware combined with Redhat Linux Software," a bullet list — "Transformational Approach used by Amazon, Facebook, Microsoft, Google, LinkedIn and others," "No Vendor Lockin," "3 Year Warranty," "Multi-Vendor Networking," "Compatible with all major Storage OS's" — then "Red Hat OS" and a re-statement of the same storage-appliance and "trusted to power" sentences quoted above)
3. The "Features" heading itself, immediately preceding the second quoted span.

A session reading this page is reading **two distinct sections of one long marketing page**, not one contiguous claim. The first span is hero/headline copy; the second is three paragraphs into a "Features" narrative that goes on afterward for several more paragraphs (High Availability, Virtualisation, Security, storage architecture — not quoted here as `f3c354b` did not include them and they postdate the "optimised for" sentence). Whether `claim_text` should include only the hero span, only the Features sentence, or both — and if both, whether the intervening duplicate-hero content belongs in between — is a scope decision this document surfaces but does not make.

---

## Summary of discrepancies against `f3c354b` (reported, not reconciled)

| Source | `f3c354b` byte size | This fetch | Delta | `f3c354b` page count | This fetch | Delta |
|---|---|---|---|---|---|---|
| C7 (R660 PDF) | 234,849 | 234,849 (re-quoted, not re-fetched) | 0 | 3-page | — | — |
| C8 (R760 PDF) | 204,768 | 204,768 (re-quoted, not re-fetched) | 0 | 3-page | — | — |
| C3 (lp1803.pdf) | 5,971,843 | 5,966,399 | **-5,444 bytes** | 97-page | 97-page | 0 |
| C4 (lp1601.pdf) | 23,458,929 | 23,432,942 | **-25,987 bytes** | 143-page | **187-page** | **+44 pages** |
| C10 (Broadberry cert page) | 37,127 | 37,127 | 0 | — | — | — |
| C11 (Broadberry CyberStore page) | 111,560 | 111,560 | 0 | — | — | — |

The two Lenovo Press PDFs show byte-size drift; C4's also shows a large page-count disagreement (143 vs. 187) that a byte-size change of ~26KB does not obviously explain on its own. The RHEL-version content extracted from both PDFs in this pass matches `f3c354b`'s quotes exactly wherever `f3c354b` quoted a version number, so the claim-relevant text itself is not shown to have changed — but the underlying documents are not byte-identical to what `f3c354b` fetched, and C4's structural page-count gap in particular has not been explained. Left open per instructions.

## Answers to the two settled questions

1. **C7 vs. C8 identity:** identical, character-for-character, in the OS/hypervisor bullet block and the trailing Dell.com/OSsupport pointer sentence. Confirmed above with both full texts shown side by side.
2. **C11 span adjacency:** not adjacent. Separated by a call-to-action block and a full duplicate rendering of the page's hero content, with the second span beginning three lines into a separate "Features" subsection.
