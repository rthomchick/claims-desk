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
- **lenovopress.lenovo.com render behavior:** this PDF's own `pdfinfo` metadata records `Creator: HeadlessChrome/140.0.0.0`, `Producer: Skia/PDF m140`, `CreationDate`/`ModDate` both stamped `Sun Aug 30 22:28:55 2026 PDT` — the exact moment of this pass's fetch. `lenovopress.lenovo.com/lp1803.pdf` is not a static file; each request renders the live web page on demand via headless Chrome, so PDF metadata timestamps mark fetch time, not publication, and are not a version handle. The document's own version handle is the line printed in its body: *"This document, LP1803, was created or updated on August 25, 2026."* That date — 2026-08-25 — is after `f3c354b`'s fetch, and is the likely source of this pass's byte-size difference from `f3c354b` (see discrepancy table below).

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

- **Trailing pointer sentence, quoted in full (immediately follows the 4th Gen block's last line, "VMware ESXi 9.1"):**

```text
For a complete list of supported, certified and tested operating systems, plus additional details and links to
relevant web sites, see the Operating System Interoperability Guide:
https://lenovopress.lenovo.com/osig#servers=sr650-v3-7d75-7d76-7d77
```

- **Where the claim begins and ends:** begins at "Operating system support" (section heading), ends at the URL closing the pointer sentence above, which is now included as part of `claim_text` — structurally analogous to the Dell.com/OSsupport pointer in C7/C8, and included on the same basis. The line break before the URL and the line wrap mid-sentence ("links to / relevant web sites") are `pdftotext -layout`'s rendering of the PDF's own line wrapping, not punctuation in the source; the sentence is one continuous sentence ending at the URL.
- **Comparison against `f3c354b`'s abridged quote:** exact match on every RHEL entry in both blocks (5th Gen: 8.8 through 10.2, thirteen entries; 4th Gen: 8.6 through 10.2, seventeen entries). As with C3, `f3c354b`'s "..." elided other-vendor OS names between and after the RHEL runs, not any RHEL version. **Pair B symmetry holds**: C3's quote was already near-complete in `f3c354b`; C4's was more heavily abridged by character count, but the unelided text shows both claims' full RHEL version lists were preserved without gaps in the original report — the asymmetry was in how much *non-RHEL* text was cut, not in the completeness of the configuration-scope-relevant RHEL data itself.
- **lenovopress.lenovo.com render behavior:** this PDF's own `pdfinfo` metadata records `Creator: HeadlessChrome/140.0.0.0`, `Producer: Skia/PDF m140`, `CreationDate`/`ModDate` both stamped `Mon Aug 31 11:54:55 2026 PDT` — the exact moment of this pass's fetch. Like lp1803, `lenovopress.lenovo.com/lp1601.pdf` renders the live page on demand rather than serving a static file, so its PDF metadata marks fetch time, not publication. The document's own version handle is: *"This document, LP1601, was created or updated on August 27, 2026."* That date — 2026-08-27 — is after `f3c354b`'s fetch, and combined with the render-on-demand behavior is the likely explanation for both the byte-size and page-count discrepancies below (a page updated and re-rendered will not reproduce byte-for-byte, and headless-Chrome pagination is not guaranteed stable across renders of a page whose content changed).

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
- **`claim_text` composition:** two non-contiguous blocks, both required. Block 1 (hero heading + body) is the primary claim. Block 2 (Features span) is supporting evidence for the same claim, not a separate claim. The two blocks are recorded and must be carried separately — not joined into one continuous string — because they are not adjacent on the page (see "span adjacency" below for what sits between them).

- **Block 1 — primary claim (hero heading + body):**

```text
Fully Compatible Redhat Linux Servers
Our enterprise-grade solutions have been trusted to power some of the biggest organisations in the world. This includes the BBC, Sky, NASA, the University Oxford, the University of Cambridge, Toshiba Rolls-Royce, Toyota, Google, Virgin and many more.
```

  (The breadcrumb/header lines "Redhat Linux Servers / Home / Servers / Redhat Linux Servers" and the storage-appliance sentence immediately preceding this block — "If your business requires a stable, reliable and high performing storage appliance..." — are page-chrome and lead-in copy, not part of the claim heading itself; excluded from Block 1 on that basis.)

- **Block 2 — supporting evidence (Features subsection):**

```text
Red Hat delivers superb performance with a focus on application stability, giving you the confidence to run business-critical workloads. Security is built in and support from a leading security team is available.
You can enjoy the freedom to innovate through access to development tools, container technologies and thousands if hardware, software and cloud partners. There is full support for complete infrastructure initiatives, ranging from virtualisation to emerging technology areas such as cloud-native deploys designed, built and optimised for Red Hat Enterprise Linux.
```

(Note: "thousands if hardware" is the source page's own text — not a transcription error in this document. Preserved verbatim, typo included.)

- **Non-contiguity, explicit:** Block 1 and Block 2 are **not adjacent** on the page. Between them sit, in order: (1) a "Configure Range" / "Contact Us" call-to-action pair, and (2) a second, near-duplicate rendering of the hero block itself (a bullet list — "Transformational Approach used by Amazon, Facebook, Microsoft, Google, LinkedIn and others," "No Vendor Lockin," "3 Year Warranty," "Multi-Vendor Networking," "Compatible with all major Storage OS's" — followed by "Red Hat OS" and a re-statement of the same storage-appliance and "trusted to power" sentences already in Block 1), ending at the "Features" heading that opens Block 2. This intervening content is **not** included in `claim_text` under either block.

### C11 — are the two quoted spans contiguous, adjacent, or separated by unrelated content?

**Separated by substantial intervening content — not adjacent.** See "Non-contiguity, explicit" above for the full list of what sits between Block 1 and Block 2. In brief: a call-to-action pair, then a full duplicate re-rendering of the hero content, then the "Features" heading.

A session reading this page is reading **two distinct sections of one long marketing page**, not one contiguous claim. Block 1 is hero/headline copy; Block 2 is three paragraphs into a "Features" narrative that goes on afterward for several more paragraphs (High Availability, Virtualisation, Security, storage architecture — not quoted here as `f3c354b` did not include them and they postdate the "optimised for" sentence). `claim_text` for C11 is settled as both blocks, recorded separately, per the seeding decision above — Block 1 primary, Block 2 supporting evidence, intervening content excluded from both.

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

The two Lenovo Press PDFs show byte-size drift; C4's also shows a large page-count disagreement (143 vs. 187). Both discrepancies are recorded above, unmodified. Likely explanation, not a reconciliation: `lenovopress.lenovo.com` renders these PDFs on demand via headless Chrome at request time rather than serving a static file (see the "render behavior" note under each of C3 and C4) — each source's own body text states it was "created or updated" after `f3c354b`'s fetch (lp1803: 2026-08-25; lp1601: 2026-08-27), so this pass's fetch (2026-08-31) landed on a re-rendered, possibly content-revised page. That combination — live re-render plus a later document-update date — accounts for why byte size and, for C4, page count would differ from `f3c354b` without requiring any change to the RHEL-version content itself, which matches `f3c354b`'s quotes exactly in both documents. This is offered as the probable cause, not a verified reconciliation: the discrepancy record above stands as originally reported.

## Answers to the two settled questions

1. **C7 vs. C8 identity:** identical, character-for-character, in the OS/hypervisor bullet block and the trailing Dell.com/OSsupport pointer sentence. Confirmed above with both full texts shown side by side.
2. **C11 span adjacency:** not adjacent. Separated by a call-to-action block and a full duplicate rendering of the page's hero content, with the second span beginning three lines into a separate "Features" subsection.
