## vendor_compat-compatibility-01 — repetition 2

The claim asserts operating system and hypervisor support across five distinct platforms: Canonical Ubuntu Server LTS, Microsoft Windows Server with Hyper-V, Red Hat Enterprise Linux, SUSE Linux Enterprise Server, and VMware ESXi. The registry holds exactly one evidence record, [cbc76faa-2e83-4837-84b7-1796698d9546], and that record covers only one of those five platforms. The verdict is therefore partial: the claim is substantiated for the Red Hat Enterprise Linux line item and unsubstantiated for the other four.

Applying the Evidence Standard element by element to the Red Hat Enterprise Linux portion, [cbc76faa-2e83-4837-84b7-1796698d9546] satisfies every element. A certification record link is present (the Red Hat Hardware Catalog system detail record). The platform is named ("Red Hat Enterprise Linux"). The platform version is named distinctly from the platform itself ("8.6-8.x, 9.0-9.x, 10.0-10.x, RHEL-RT 10.0" — recorded here verbatim as the vendor publishes it, not normalized). The certified component revision is named ("PowerEdge R660"). And the deterministic lifecycle hygiene check returns `platform_lifecycle_status: current`, meaning the platform version has not passed the last lifecycle phase included in a standard support subscription. The Red Hat Enterprise Linux line item clears the standard in full.

The remaining four platforms fail the standard at its first element. There is no certification record link for Canonical Ubuntu Server LTS, for Microsoft Windows Server with Hyper-V, for SUSE Linux Enterprise Server, or for VMware ESXi. They consequently also fail the second, third, and fourth elements: no platform version is named distinctly for any of them, either in the evidence or in the claim text itself (the claim names bare product families — "Canonical Ubuntu Server LTS", "Red Hat Enterprise Linux" — with no version identifiers), and no certified component revision is tied to any of them. The claim's own referral to Dell.com/OSsupport for "specifications and interoperability details" is a pointer to an unlinked destination, not a certification record, and does not supply any element of the standard. Four fifths of the claim's platform coverage rests on no evidence in the registry.

Currency policy: this is a compatibility-type claim, not a compliance-type claim, and no external currency policy governs it. The Evidence Standard's own terms govern currency here, and they are self-contained — they define staleness by lifecycle phase rather than by elapsed calendar time, and they specify that phases available only as a separately purchased add-on (Red Hat ELS, Microsoft ESU, and equivalents) count as expired for claim purposes. Against that test the evidence passes on the strength of the `current` lifecycle status. Two currency observations are nonetheless worth recording. First, [cbc76faa-2e83-4837-84b7-1796698d9546] carries no evidence date (`has_evidence_date: false`); the Evidence Standard does not require one, so this is not a failure against the standard, but it does mean the certification record cannot be independently re-aged and the `current` determination cannot be re-derived from the record alone. Second, the version range "8.6-8.x" spans minor-version streams whose continued coverage depends on which stream is being relied upon — trailing RHEL 8 minor streams are reachable only through Extended Update Support or Extended Life Cycle Support, which this standard expressly counts as expired. The `current` status is correct for the range taken as a whole, but it should not be read as certifying every minor version inside that range under a standard subscription.

No prior ruling context exists for this product and claim_type, so there is no divergence to explain. This ruling reasons from the evidence in the registry alone.


## vendor_compat-compatibility-02 — repetition 1

vendor_compat-compatibility-02 asserts compatibility across five distinct platform families: Canonical Ubuntu Server LTS, Microsoft Windows Server with Hyper-V, Red Hat Enterprise Linux, SUSE Linux Enterprise Server, and VMware ESXi. The registry carries exactly one evidence item, [8a48e9c6-9cae-4ed9-b60d-7e5952a9898f], and it reaches exactly one of those five. The verdict is therefore partially rather than substantiated or not_substantiated: the Red Hat Enterprise Linux limb clears the Evidence Standard on its own terms, and the other four limbs have no evidence behind them at all.

**Red Hat Enterprise Linux limb — meets the standard, element by element.** [8a48e9c6-9cae-4ed9-b60d-7e5952a9898f] satisfies each of the five elements the Evidence Standard enumerates. *Certification record link present*: the item links to the Red Hat Ecosystem Catalog hardware certification record at system detail 144067, which is a first-party certification record from the platform vendor rather than a vendor self-assertion. *Platform named*: "Red Hat Enterprise Linux". *Platform version named distinctly from the platform itself*: the version field carries `8.6-8.x, 9.0-9.x, 10.0-10.x, RHEL-RT 8.6, RHEL-RT 10.0`, which is a genuine version designation held separately from the platform name — this element is not satisfied merely by a platform name that happens to contain a word like "LTS", and here it is properly satisfied. *Certified component revision named*: "PowerEdge R760". *Lifecycle*: addressed below.

**Currency-policy application.** Stating this explicitly, as required: no external currency or evidence-age policy applies to this claim, and the Evidence Standard's own terms govern the currency question. The Standard supplies its own lifecycle test — a platform version must not have "passed the last lifecycle phase included in a standard support subscription," with the parenthetical carve-out that add-on-only phases such as Red Hat ELS or Microsoft ESU "count as expired for claim purposes." Applying that test to the versions in [8a48e9c6-9cae-4ed9-b60d-7e5952a9898f]: the 9.x and 10.x streams sit in full or maintenance support, and the 8.x stream remains inside maintenance support, which is included in a standard RHEL subscription rather than sold as an ELS add-on. No cited version depends on an add-on-only phase to remain in support, so none is deemed expired under the carve-out. The `platform_lifecycle_status` hygiene check independently returns `current`, and `is_expired` returns null (no expiry_date recorded), consistent with that reading.

**Evidence-date gap — noted, not disqualifying.** The `has_evidence_date` hygiene check returns false: [8a48e9c6-9cae-4ed9-b60d-7e5952a9898f] records no date on which the catalog record was captured. An evidence date is not one of the five elements the Evidence Standard requires for a compatibility claim, so its absence does not defeat the RHEL limb. It does mean the certification record's freshness cannot be confirmed from the registry alone, and the lifecycle conclusion above rests on the platform vendor's published lifecycle phases rather than on a dated capture. This is a real weakness in the record and should be closed by recording an evidence_date, but it does not change the verdict. The `has_sample_size` check returns null and is not applicable to a compatibility claim, which turns on certification rather than sampling.

**The four unevidenced limbs.** Canonical Ubuntu Server LTS, Microsoft Windows Server with Hyper-V, SUSE Linux Enterprise Server, and VMware ESXi are named in the claim but supported by no evidence item in the registry. For each of these, every element of the Evidence Standard fails, not merely one: there is no certification record link, no certified component revision tied to that platform, and no lifecycle determination is possible because no version exists to test. The distinctness element fails on the face of the claim text as well — "Canonical Ubuntu Server LTS", "Microsoft Windows Server with Hyper-V", "SUSE Linux Enterprise Server", and "VMware ESXi" are product-line names, and "LTS" is a release-cadence designation, not a version named distinctly from the platform. The claim's closing referral, "For specifications and interoperability details, see Dell.com/OSsupport," does not cure this. A pointer to a general support landing page is not a certification record for any named platform version; it identifies where evidence might be found rather than supplying it, and it cannot be evaluated against the lifecycle test because it resolves to no specific version. These four limbs are unsubstantiated on the present record.

**Consistency check.** `get_claim_status` returns `latest_ruling: null` — this claim carries no ruling history — and the claim's registry `status` remains `unverified`. The registry `risk_class` is `medium`, with the recorded risk factor "certification record, platform version, and current lifecycle status all present"; that factor is accurate as to the RHEL limb only, and should not be read as covering the claim's full five-platform scope. Per this configuration, no prior ruling context exists to diverge from, so this ruling reasons solely from the evidence above and no divergence explanation is required.


## vendor_compat-compatibility-02 — repetition 2

The claim text of vendor_compat-compatibility-02 asserts operating system and
hypervisor compatibility across five distinct platform families: Canonical Ubuntu
Server LTS, Microsoft Windows Server with Hyper-V, Red Hat Enterprise Linux, SUSE
Linux Enterprise Server, and VMware ESXi. The registry holds exactly one evidence
record for this claim, [8a48e9c6-9cae-4ed9-b60d-7e5952a9898f]. The Evidence
Standard is applied per named platform, because each of its elements — certification
record link, platform named, platform version named distinctly, certified component
revision named, lifecycle phase — is a property of a specific platform, not of the
claim as a whole. A single record therefore cannot discharge the standard for four
platforms it does not mention.

**Red Hat Enterprise Linux — meets the standard.** Evidence
[8a48e9c6-9cae-4ed9-b60d-7e5952a9898f] satisfies every element in turn. The
certification record link is present and resolves to the Red Hat Ecosystem Catalog
system detail page. The platform is named ("Red Hat Enterprise Linux"). The platform
version is named distinctly from the platform itself ("8.6-8.x, 9.0-9.x, 10.0-10.x,
RHEL-RT 8.6, RHEL-RT 10.0") rather than being folded into the platform name. The
certified component revision is named ("PowerEdge R760"). The deterministic hygiene
check returns `platform_lifecycle_status: current`, so the version has not passed the
last lifecycle phase included in a standard support subscription.

**Currency-policy application.** No external currency policy is named as governing
this claim type, and none was located for it. The Evidence Standard's own terms
therefore govern currency, and they do so through a lifecycle test rather than an
age-of-evidence test: the operative question is whether the platform version has
passed the last lifecycle phase carried by a standard support subscription, with
add-on-only phases such as Red Hat ELS or Microsoft ESU counting as expired. That
test is satisfied for the RHEL portion. Consequently the absent `evidence_date`
(hygiene check `has_evidence_date: false`) and the absent `expiry_date` are not
substantiation defects here — the standard does not require either field, and
currency is established by lifecycle phase instead. They do, however, mean the
record carries no self-dating, so it cannot be re-verified as current from its own
contents; re-verification requires re-reading the catalog record. The same reasoning
disposes of `has_sample_size` and `is_expired`, both null: the standard imposes no
sample-size element on compatibility claims.

**One narrowing caveat within the RHEL portion.** The certified range includes
pinned minor versions — specifically RHEL-RT 8.6 — whose continued support at that
exact minor pin depends on Extended Update Support, which is a separately purchased
add-on and which the Evidence Standard expressly directs be treated as expired for
claim purposes. The range as written also spans 8.x, 9.x, and 10.x, which are within
standard maintenance support, and the hygiene check evaluates the version field as
`current` on that basis. I rely on that deterministic result for the overall RHEL
verdict, but the pinned RHEL-RT 8.6 entry should not be read as independently
substantiated at that specific minor version, and the Scope Note reflects this.

**The four remaining platforms — not substantiated.** Canonical Ubuntu Server LTS,
Microsoft Windows Server with Hyper-V, SUSE Linux Enterprise Server, and VMware ESXi
have no linked evidence whatsoever. For each, the standard fails at the first
element: there is no certification record link. It then fails at every subsequent
element as well — no platform version is named for any of them, and no certified
component revision is tied to any of them. "Ubuntu Server LTS" as written in the
claim compounds this: "LTS" designates a release channel, not a version, so even the
claim text does not name a platform version distinctly from the platform itself, as
the standard requires. "Windows Server with Hyper-V" is likewise unversioned. The
claim's own trailing pointer to Dell.com/OSsupport does not cure this. It is a
navigational reference rather than a certification record, it is not linked as
evidence in the registry, and it is not among the evidence returned by
`check_substantiation`; I therefore did not treat it as evidence.

**On the recorded risk factor.** The claim carries `risk_class: medium` with the
single risk factor "certification record, platform version, and current lifecycle
status all present." That characterization is accurate as applied to evidence
[8a48e9c6-9cae-4ed9-b60d-7e5952a9898f] in isolation, but it should not be read as
extending across the claim, since it describes the one platform that is documented
and is silent on the four that are not. Read at claim level it would materially
overstate coverage.

A verdict of `partially` follows: one of five named platform families is fully
substantiated against the Evidence Standard, and four carry no evidence at all.
`substantiated` would misrepresent four-fifths of the claim's surface;
`not_substantiated` would understate a RHEL record that cleanly meets every element
of the standard. No escalation is warranted, as the deficiency is a straightforward
absence of evidence rather than a conflict, ambiguity, or contested interpretation.


## vendor_compat-compatibility-03 — repetition 1

The claim enumerates 27 operating system versions across five platform families: Microsoft Windows Server (2), Red Hat Enterprise Linux (13), SUSE Linux Enterprise Server (5), Ubuntu (3), and VMware ESXi (4). Exactly one evidence record is linked, [abd992b2-2aac-4b63-9aab-16b1ede4805a], and its `platform` field names a single platform: Red Hat Enterprise Linux. The ruling therefore splits along that line.

**Red Hat Enterprise Linux portion — meets the standard.** Applying the Evidence Standard element by element to [abd992b2-2aac-4b63-9aab-16b1ede4805a]: (1) certification record link present — the hygiene check `has_evidence_link` returns true and the record resolves to the Red Hat Ecosystem Catalog; (2) platform named — "Red Hat Enterprise Linux"; (3) platform version named distinctly from the platform itself — "8.8-8.x, 9.2-9.x, 10.0-10.x" is carried in a separate `platform_version` field and is not merely a restatement of the platform name; (4) certified component revision named — "ThinkSystem ST250 V3"; (5) lifecycle — the hygiene check `platform_lifecycle_status` returns "current" for the versions cited. All 13 RHEL versions asserted in the claim (8.8, 8.9, 8.10, 9.2 through 9.8, 10.0, 10.1, 10.2) fall nominally inside the ranges recorded in [abd992b2-2aac-4b63-9aab-16b1ede4805a].

**Non-RHEL portion — no evidence at all.** The 14 remaining versions (Windows Server 2022 and 2025; SLES 15 SP5, SP6, SP7, 15 Xen SP5, and 16; Ubuntu 22.04, 24.04, and 26.04 LTS; ESXi 8.0 U2, 8.0 U3, 9.0, and 9.1) are supported by no evidence record whatsoever. This is not a weak-evidence finding but an absent-evidence finding: elements (1) through (5) of the Evidence Standard cannot be scored for these platforms because there is nothing to score. A majority of the platform families asserted in the claim are unsubstantiated, which is why the verdict is `partially` rather than `substantiated`.

**Currency-policy application.** No external currency policy is named for this claim or claim type, so the Evidence Standard's own terms govern currency. Under those terms the operative test is whether a platform version has passed the last lifecycle phase included in a standard support subscription, with add-on-only phases such as Red Hat ELS or Microsoft ESU counting as expired. For the RHEL portion, the deterministic check reports "current" and I do not disturb that. Two limits on that finding should be recorded. First, `has_evidence_date` is false and `is_expired` is null for [abd992b2-2aac-4b63-9aab-16b1ede4805a], so the "current" determination cannot be pinned to an as-of date and cannot be independently re-verified from the record as stored; any later re-review will have to re-derive currency rather than rely on this one. Second, the superseded RHEL 8.x and 9.x minor versions in the list are the entries most exposed to the add-on clause, since continued support for a superseded minor version is characteristically an Extended Update Support entitlement rather than part of a standard subscription; the record's open-ended "8.x"/"9.x"/"10.x" range notation does not distinguish these cases. For the Windows Server entries the ESU clause named in the standard cannot be evaluated at all, because no Windows evidence exists.

**Two further scope gaps.** The claim conditions support on "Intel Pentium or Intel Xeon E processors," but the `scope` field of [abd992b2-2aac-4b63-9aab-16b1ede4805a] states the catalog record carries no configuration scope beyond the certified system and version ranges (architecture: x86_64). The processor-family qualifier is thus neither confirmed nor contradicted by the evidence. Separately, the range endpoints "8.x", "9.x", and "10.x" are open-ended, so coverage of the newest minors asserted (9.7, 9.8, 10.1, 10.2) rests on an unbounded range rather than on enumerated per-version certifications.

No prior ruling context exists for this product and claim type, so there is no divergence to explain; this claim was assessed solely on the evidence linked to it.


## vendor_compat-compatibility-03 — repetition 2

The claim asserts ST250 V3 support for 27 distinct operating system versions across five platform families: Microsoft Windows Server (2), Red Hat Enterprise Linux (13), SUSE Linux Enterprise Server (5), Ubuntu (3), and VMware ESXi (4). Exactly one evidence record is linked, [abd992b2-2aac-4b63-9aab-16b1ede4805a], and it is single-platform. The verdict is therefore driven by a coverage gap, not by a defect in the evidence that exists.

**Red Hat Enterprise Linux portion — meets the Evidence Standard.** Evidence [abd992b2-2aac-4b63-9aab-16b1ede4805a] satisfies each element of the standard in turn: a certification record link is present (`has_evidence_link: true`); the platform is named ("Red Hat Enterprise Linux"); the platform version is named distinctly from the platform itself ("8.8-8.x, 9.2-9.x, 10.0-10.x", recorded in a separate field from the platform name, so the standard's "distinctly" requirement is met rather than merely inferable); and the certified component revision is named ("ThinkSystem ST250 V3"), matching the component in the claim text. The version ranges in [abd992b2-2aac-4b63-9aab-16b1ede4805a] span all 13 RHEL versions enumerated in the claim — 8.8 through 8.10 fall inside 8.8-8.x, 9.2 through 9.8 inside 9.2-9.x, and 10.0 through 10.2 inside 10.0-10.x.

**Currency-policy application.** No external currency policy has been supplied to this review and none is referenced by the claim, the registry record, or evidence [abd992b2-2aac-4b63-9aab-16b1ede4805a]; accordingly, the Evidence Standard's own lifecycle terms govern the currency question. Those terms require that the platform version not have passed the last lifecycle phase included in a standard support subscription, and count add-on-only phases (Red Hat ELS, Microsoft ESU) as expired. Applying that test to the RHEL portion: `platform_lifecycle_status` returns `current` for the certified ranges, and the ranges are open-ended at the top of each major version, so the certified RHEL scope has not passed a standard-subscription phase and is not in add-on-only territory. Two secondary observations, neither of which changes the verdict but both of which are recorded because the standard's own terms invite them. First, the lifecycle signal is evaluated at the range level; individual older minor releases inside those ranges — specifically RHEL 8.8 and 8.9, which are superseded minor releases whose continued coverage depends on Extended Update Support — could fall on the add-on-only side of the standard's test if assessed per-minor-version rather than per-range. Second, evidence [abd992b2-2aac-4b63-9aab-16b1ede4805a] carries no evidence date (`has_evidence_date: false`), so the currency determination rests on the catalog record's live state rather than on a dated snapshot that could be re-verified as of a fixed point. The Evidence Standard does not require an evidence date, so this is not a failure against the standard, but it does mean the currency finding is not independently reproducible from the registry record alone.

**Non-Red Hat portion — unsubstantiated.** Fourteen of the 27 asserted OS versions have no linked evidence whatsoever: Windows Server 2022 and 2025; SLES 15 SP5, 15 SP6, 15 SP7, 15 Xen SP5, and 16; Ubuntu 22.04 LTS, 24.04 LTS, and 26.04 LTS; and VMware ESXi 8.0 U2, 8.0 U3, 9.0, and 9.1. For each of these the Evidence Standard fails at its first element — no certification record link is present, and consequently no platform version, no certified component revision, and no lifecycle status are established for them either. Evidence [abd992b2-2aac-4b63-9aab-16b1ede4805a] cannot be stretched to cover them: its own `scope` field limits it to the certified system and version ranges on x86_64, and a Red Hat catalog certification is not probative of Microsoft, SUSE, Canonical, or Broadcom/VMware support. The `lenovopress.lenovo.com/lp1803.pdf` URL appearing in that scope field is identified as the *claim source* — the document the claim text was drawn from — not as a certification record for the non-Red Hat platforms, and a vendor's own datasheet would not satisfy a standard whose first element is a certification record in any event.

The registry `risk_factors` note "certification record, platform version, and current lifecycle status all present" is accurate as to the RHEL evidence but should not be read as a statement about the claim as a whole; it reflects the one evidence row on file, not the 14 asserted versions that have no row. Because a substantial, separable majority of the claim is unsupported while a well-defined portion fully meets the standard, `partially` is the correct verdict rather than `substantiated` or `not_substantiated`. To reach `substantiated`, the claim would need certification records for each remaining platform family, each naming platform, platform version distinctly, and the ST250 V3 component revision, and each passing the standard's lifecycle test — or the claim text would need to be narrowed to the RHEL versions actually certified in [abd992b2-2aac-4b63-9aab-16b1ede4805a].


## vendor_compat-compatibility-04 — repetition 1

**Currency-policy application.** This is a `compatibility`-type claim, not a
`compliance`-type claim, so no external compliance currency policy is invoked.
I record explicitly that no separate external currency policy governs this
ruling; currency is governed by the Evidence Standard's own terms — namely its
final clause on lifecycle phase, including its instruction that phases available
only as a separately purchased add-on (Red Hat ELS, Microsoft ESU) count as
expired for claim purposes.

**What the evidence does support.** Evidence
[020ff7ec-700f-4988-905a-6e9d4f55b739] satisfies four of the five elements of
the Evidence Standard cleanly, for the Red Hat Enterprise Linux portion of the
claim only:

1. *Certification record link present* — yes; the evidence resolves to a Red Hat
   Ecosystem Catalog certified-system detail record. Hygiene check
   `has_evidence_link: true`.
2. *Platform named* — yes; `platform` is recorded as "Red Hat Enterprise Linux".
3. *Platform version named distinctly from the platform itself* — yes;
   `platform_version` is carried in its own field as "8.6-8.x, 9.0-9.x,
   10.0-10.x", not folded into the platform string.
4. *Certified component revision named* — yes; `component_revision` is
   "ThinkSystem SR650 V3", matching the product named throughout the claim text.
5. *Lifecycle* — the deterministic hygiene check reports
   `platform_lifecycle_status: "current"`, which I accept at the level it was
   evaluated (the RHEL 8 / 9 / 10 major families). See the caveat below.

On that basis the RHEL-family portion of the claim is supported at family level
by a genuine, on-point certification record.

**Primary reason the claim is only partially substantiated: platform coverage
gap.** The claim enumerates roughly 72 operating-system line items across the
two processor-generation lists, spanning five distinct platform families:
Microsoft Windows / Windows Server, Red Hat Enterprise Linux, SUSE Linux
Enterprise Server (including the Xen variants), Ubuntu, and VMware ESXi. Evidence
[020ff7ec-700f-4988-905a-6e9d4f55b739] is a Red Hat certification record and
names exactly one platform: "Red Hat Enterprise Linux". It therefore reaches only
the ~30 RHEL line items and supports **none** of the ~42 non-RHEL line items —
Windows 10 (x64), Windows 11, Windows Server 2019 / 2022 / 2025, SLES 15 SP4–SP7,
SLES 15 Xen SP4 / SP5, SLES 16, Ubuntu 20.04 / 22.04 / 24.04 / 26.04 LTS, and
VMware ESXi 7.0 U3 / 8.0 / 8.0 U1 / 8.0 U2 / 8.0 U3 / 9.0 / 9.1.

The Evidence Standard is written per-platform: it requires a certification
record link with *the* platform named and *the* platform version named. A Red Hat
certification cannot discharge that requirement for Microsoft, SUSE, Canonical,
or Broadcom/VMware platforms; each needs its own certification record (e.g.
Windows Server Catalog, SUSE YES Certified, Ubuntu Certified Hardware, VMware
Compatibility Guide). Four of the five platform families asserted in the claim
currently have zero registered evidence. That is the controlling defect and is
why the verdict is `partially` rather than `substantiated`.

**Secondary defect: the evidence cannot discriminate between the two processor
generations.** The claim makes two *different* assertions — one OS list for the
SR650 V3 with 5th Gen Intel Xeon Scalable processors, a different and broader
list for the 4th Gen configuration. The 5th Gen list deliberately omits RHEL 8.6,
8.7, 9.0 and 9.1, which the 4th Gen list includes. The evidence records
`component_revision` only as "ThinkSystem SR650 V3", with a `scope` note stating
the catalog record asserts "no configuration scope beyond the certified system and
version ranges (architecture: x86_64)" — i.e. no processor-generation
differentiation at all, and a single flat range of "8.6-8.x" that is broader than
what the 5th Gen list claims. The evidence does not contradict either list, but
it is not scoped finely enough to confirm the per-generation distinction the
claim draws. The RHEL portion is therefore supported at the system-and-family
level, not at the per-generation level the claim asserts.

**Lifecycle caveat on enumerated minor versions.** I accept the hygiene check's
`platform_lifecycle_status: "current"` for the RHEL 8 / 9 / 10 major families.
However, the evidence expresses coverage as open-ended family ranges ("8.6-8.x",
"9.0-9.x", "10.0-10.x"), whereas the claim enumerates *specific minor versions*
including RHEL 8.6, 8.7, 8.8, 8.9, 9.0, 9.1, 9.2 and 9.3. Under a standard Red Hat
subscription, entitlement tracks the current minor release of the major stream;
continued support for a superseded minor release requires separately purchased
Extended Update Support / ELS. The Evidence Standard states directly that phases
"available only as a separately purchased add-on, such as Red Hat ELS or
Microsoft ESU, count as expired for claim purposes." The family-level range in
[020ff7ec-700f-4988-905a-6e9d4f55b739] does not establish per-minor-version
currency for those superseded entries, so the older enumerated minors are not
independently substantiated even within the RHEL portion.

**Additional hygiene observations.** Evidence
[020ff7ec-700f-4988-905a-6e9d4f55b739] carries no `evidence_date`
(`has_evidence_date: false`) and no `expiry_date`, so its currency rests on the
live state of the catalog page rather than on a dated, reproducible snapshot; a
future reader cannot verify what the record said when it was relied upon. The
claim text itself defers to an external Lenovo Operating System Interoperability
Guide for "a complete list of supported, certified and tested operating systems,"
but that guide is not registered as evidence and so was not available to this
review. `get_claim_status` reports `latest_ruling: null` and claim status
`unverified`; there is no ruling history for this claim, and therefore no prior
ruling to diverge from or explain divergence against.

**Recommended remediation.** Register a per-platform certification record for
each of the four unevidenced platform families; register evidence that is scoped
to processor generation so the two OS lists can be told apart; and either narrow
the enumerated RHEL minor versions to those inside standard-subscription support
or add dated evidence for the ELS/EUS-only minors. Adding an `evidence_date` to
the existing record would close the remaining hygiene gap.


## vendor_compat-compatibility-04 — repetition 2

**Currency-policy application.** No external currency or evidence-refresh policy document was available to this session; none is referenced by the registry record or returned by `check_substantiation`. Accordingly, the Evidence Standard's own terms govern currency for this ruling — specifically its closing clause, which requires that the platform version "has not passed the last lifecycle phase included in a standard support subscription," and which expressly counts phases "available only as a separately purchased add-on, such as Red Hat ELS or Microsoft ESU" as expired for claim purposes. Every currency finding below is applied under that clause and no other.

**1. The Evidence Standard is met, but only for the Red Hat subset.** Evidence [020ff7ec-700f-4988-905a-6e9d4f55b739] satisfies four of the standard's five structural elements on its face: a certification record link is present (`has_evidence_link: true`), the platform is named ("Red Hat Enterprise Linux"), the platform version is named distinctly from the platform itself ("8.6-8.x, 9.0-9.x, 10.0-10.x"), and a certified component revision is named ("ThinkSystem SR650 V3"), which matches the SR650 V3 system in the claim text. This is genuine substantiation — for Red Hat Enterprise Linux and nothing else.

**2. Four of the five claimed OS families have no cited evidence at all.** The claim asserts support for Microsoft Windows (10 x64, 11, Server 2019, Server 2022, Server 2025), SUSE Linux Enterprise Server (15 SP4–SP7, 15 Xen SP4/SP5, 16), Ubuntu (20.04, 22.04, 24.04, 26.04 LTS), and VMware ESXi (7.0 U3, 8.0, 8.0 U1/U2/U3, 9.0, 9.1) in addition to RHEL. Evidence [020ff7ec-700f-4988-905a-6e9d4f55b739] is the only evidence linked to this claim, and it is a Red Hat catalog record covering the Red Hat platform exclusively. For the Windows, SLES, Ubuntu, and ESXi assertions there is therefore no certification record link present — the first and threshold element of the Evidence Standard fails outright for those families. This is the primary basis for the verdict: the claim as written is substantially broader than the single record supporting it.

**3. The processor-generation split is not substantiated by [020ff7ec-700f-4988-905a-6e9d4f55b739].** The claim does not state one support matrix; it states two materially different ones, conditioned on whether the SR650 V3 is fitted with 4th Gen or 5th Gen Intel Xeon Scalable processors. The asymmetries are load-bearing — RHEL 8.6, 8.7, 9.0 and 9.1 are claimed for 4th Gen but deliberately omitted from the 5th Gen list, as are SLES 15 SP4, 15 Xen SP4, ESXi 8.0 and ESXi 8.0 U1. The scope field of [020ff7ec-700f-4988-905a-6e9d4f55b739] states that the catalog record carries "no configuration scope beyond the certified system and version ranges (architecture: x86_64)." It records a single flat range against the system as a whole and makes no processor-generation distinction. The evidence therefore cannot substantiate either matrix as generation-specific, and in particular cannot support the narrower 5th Gen list being narrower, nor the broader 4th Gen list being broader.

**4. Range notation does not substantiate each enumerated minor version.** The claim enumerates specific RHEL minor releases (8.6 through 8.10, 9.0 through 9.8, 10.0 through 10.2). Evidence [020ff7ec-700f-4988-905a-6e9d4f55b739] expresses its coverage as open-ended ranges — "8.6-8.x, 9.0-9.x, 10.0-10.x". The Evidence Standard requires the platform version to be "named distinctly," and an open-ended "9.x" does not distinctly name any particular minor release. This matters most for the forward-looking minors in the claim (RHEL 9.7, 9.8, 10.1, 10.2), which a range wildcard anticipates rather than certifies. Even within the Red Hat family, per-minor substantiation is weaker than the family-level substantiation found in point 1.

**5. Lifecycle currency cannot be confirmed per-version, and the aggregate check masks this.** The hygiene checks return `platform_lifecycle_status: "current"`, but that is a single aggregate verdict computed over a bundled multi-version range, not a per-minor-version determination. The Evidence Standard's expiry rule is inherently version-specific: it asks whether *the* platform version has passed the last phase included in a standard subscription. Under Red Hat's release model, older minor releases such as RHEL 8.6, 8.7, 9.0 and 9.1 are ordinarily served beyond their standard window only through a separately purchased add-on — precisely the category the Evidence Standard directs be treated as expired. I do not assert as established fact that those specific minors have expired, because [020ff7ec-700f-4988-905a-6e9d4f55b739] carries no per-version lifecycle breakdown that would let me verify it. The finding is that the aggregate "current" status cannot be relied upon to clear each enumerated minor individually, and the oldest claimed minors are the ones at risk under the standard's add-on clause.

**6. Absent evidence_date leaves the currency determination unanchored.** `has_evidence_date` is `false`, and `expiry_date` is null. The Evidence Standard does not enumerate an evidence date among its required elements, so this is not an independent failure and I do not treat it as one. It is, however, a material hygiene weakness here specifically because the standard's fifth element is time-dependent: without a date on the certification record, the "current" lifecycle status has no point in time to which it can be anchored, and cannot be re-verified as the claimed minors age. `sample_size` and `baseline` are null, but neither is required by this claim type's standard, so neither bears on the verdict.

**7. Unreviewed onward reference.** The claim text closes by directing readers to the Lenovo Operating System Interoperability Guide for "a complete list of supported, certified and tested operating systems." That URL is part of the claim, not linked evidence, and was not evaluated as evidence. It cannot cure the gaps in points 2–4; if the Windows, SLES, Ubuntu, and ESXi assertions are to be substantiated, certification records for those platforms need to be attached to this claim as evidence in their own right.

**Divergence from prior ruling context.** None to explain: no prior ruling context exists for this product and claim_type, and `get_claim_status` returns `latest_ruling: null`, so this ruling is not measured against any earlier position. Claim status remains `unverified`.

**Why "partially" rather than "not_substantiated" or "escalate."** The Red Hat family-level assertion is genuinely backed by a conforming certification record naming platform, distinct version range, and component revision, so a blanket rejection would understate what the evidence establishes. But the claim's Windows, SLES, Ubuntu and ESXi assertions, its two generation-specific matrices, and its individually enumerated minor versions all outrun that single record. "partially" is the accurate reading. No escalation trigger is present — the deficiencies are ordinary evidence gaps that additional certification records would close, not ambiguities in the standard itself.


## vendor_compat-compatibility-05 — repetition 1

The claim under review reads: "Redhat Linux Certified Supermicro Servers / These Supermicro SuperServers have been certified and approved to run Redhat Linux."

**Element-by-element application of the Evidence Standard to evidence [69dd88be-fa8b-4b2a-bb8f-2012d9cd9cd7]:**

1. *Certification record link present* — Met. Evidence [69dd88be-fa8b-4b2a-bb8f-2012d9cd9cd7] links to a Red Hat Ecosystem Catalog hardware certification record (system detail 241727), which is the first-party certifying authority for the platform named in the claim.
2. *Platform named* — Met. Evidence [69dd88be-fa8b-4b2a-bb8f-2012d9cd9cd7] names the platform as Red Hat Enterprise Linux.
3. *Platform version named distinctly from the platform itself* — Met. Evidence [69dd88be-fa8b-4b2a-bb8f-2012d9cd9cd7] carries the platform version as a separate field with the value `8.7-8.x, 9.0-9.x`, recorded distinctly from the platform name rather than folded into it.
4. *Certified component revision named* — Met. Evidence [69dd88be-fa8b-4b2a-bb8f-2012d9cd9cd7] names the certified component revision as Supermicro SuperServer SYS-221HE-TNRD — a single, specific system model.
5. *Platform version has not passed the last lifecycle phase included in a standard support subscription* — Met, as set out under currency policy below.

**Currency-policy application (stated explicitly).** A specific external policy governs currency here rather than the Evidence Standard's own terms alone: the Red Hat Enterprise Linux Life Cycle policy, which the Evidence Standard incorporates by reference through its parenthetical naming Red Hat ELS as an add-on phase that "count[s] as expired for claim purposes." Under that policy, the phases bundled into a standard RHEL subscription are Full Support and Maintenance Support; Extended Life Cycle Support (ELS) is a separately purchased add-on and therefore does not count toward currency. Both version ranges certified in evidence [69dd88be-fa8b-4b2a-bb8f-2012d9cd9cd7] remain within Maintenance Support and have not entered ELS, so neither has passed the last subscription-included phase. This is consistent with the deterministic hygiene check returned by `check_substantiation`, which reports `platform_lifecycle_status: current`. The currency element is therefore satisfied, and it is satisfied on subscription-included phases only — not on any add-on entitlement.

**Why the verdict is `partially` rather than `substantiated`.** Every element of the Evidence Standard is met, but the standard governs what the evidence must contain, not how far the claim text may reach. The claim as written is materially broader than evidence [69dd88be-fa8b-4b2a-bb8f-2012d9cd9cd7] supports, in three independent respects:

- **Plural systems vs. one certified model.** The claim asserts certification for "Supermicro SuperServers" (plural) and is headlined "Supermicro Servers," implying a family or range of models. Evidence [69dd88be-fa8b-4b2a-bb8f-2012d9cd9cd7] names exactly one certified component revision, SYS-221HE-TNRD. A Red Hat catalog certification attaches to the specific system it was granted for; it does not extend to sibling or successor SuperServer models. Nothing in the record substantiates the plural.
- **Unqualified "Redhat Linux" vs. bounded version ranges.** The claim names the platform with no version qualifier, which reads as all Red Hat Enterprise Linux. Evidence [69dd88be-fa8b-4b2a-bb8f-2012d9cd9cd7] certifies `8.7-8.x, 9.0-9.x` only. RHEL releases outside those ranges — earlier 8.x minors below 8.7, RHEL 7 and prior, and any major release after 9 — are outside the certification and unsupported by the record.
- **Architecture is unstated in the claim but bounded in the evidence.** The scope field of evidence [69dd88be-fa8b-4b2a-bb8f-2012d9cd9cd7] limits the record to architecture x86_64. The claim carries no such limit.

Separately, the hygiene checks report `has_evidence_date: false` for evidence [69dd88be-fa8b-4b2a-bb8f-2012d9cd9cd7]. An evidence date is not an element of this claim type's Evidence Standard, so its absence is not a substantiation failure and does not by itself reduce the verdict. It is recorded here as a durability weakness: without a capture date, the currency determination above cannot later be re-verified as of the moment the record was read, and the claim will need re-checking against the Red Hat Enterprise Linux Life Cycle policy before RHEL 8.x transitions to ELS. `has_sample_size` and `is_expired` return null and are not applicable to a compatibility claim resting on a single certification record.

The verdict is therefore `partially`: the certification is genuine, current, and fully documented for one system on two bounded version ranges, while the claim as phrased generalizes it to an unbounded set of servers and an unbounded set of RHEL versions. Narrowing the claim text to name SYS-221HE-TNRD and the certified version ranges would bring it fully within the evidence.

No prior ruling context was available to this session, and the registry carries no earlier ruling on this claim, so there is no divergence to explain. The analysis above rests solely on evidence [69dd88be-fa8b-4b2a-bb8f-2012d9cd9cd7] and the Evidence Standard quoted verbatim above.


## vendor_compat-compatibility-05 — repetition 2

**All five elements of the Evidence Standard are met by evidence [69dd88be-fa8b-4b2a-bb8f-2012d9cd9cd7].**

1. *Certification record link present* — the Red Hat Ecosystem Catalog record at `catalog.redhat.com/en/hardware/system/detail/241727`. This is a first-party certification record published by the platform vendor, not a vendor-of-the-component self-assertion.
2. *Platform named* — "Red Hat Enterprise Linux".
3. *Platform version named distinctly from the platform itself* — "8.7-8.x, 9.0-9.x", recorded separately from the platform name rather than restating it, which is what this element exists to test.
4. *Certified component revision named* — "Supermicro SuperServer SYS-221HE-TNRD", a specific model designation rather than a product family.
5. *Platform version has not passed the last lifecycle phase included in a standard support subscription* — the hygiene check returns `platform_lifecycle_status: "current"`. Both certified ranges remain inside phases carried by a standard RHEL subscription (8.x in Maintenance Support, 9.x in Full/Maintenance Support). The Standard's carve-out for add-on-only phases is therefore **not** triggered: neither range depends on separately purchased Red Hat ELS, so neither counts as expired for claim purposes.

**Currency-policy application.** No external currency policy is registered against this claim or claim type in the Claims Desk registry. Accordingly, the Evidence Standard's own terms govern currency here — specifically its final clause on lifecycle phase, applied by reference to Red Hat's published Enterprise Linux life-cycle phases as the vendor publishes them. Under those terms, as applied above in element 5, the certified platform versions are current and the claim is not time-barred.

**Why the verdict is `partially` rather than `substantiated`.** The Evidence Standard's elements are satisfied, but the claim *as written* asserts more than [69dd88be-fa8b-4b2a-bb8f-2012d9cd9cd7] covers, in two independent respects:

- **Hardware plurality.** The claim is worded in the plural throughout — "Redhat Linux Certified Supermicro Servers" and "These Supermicro SuperServers have been certified" — asserting a set of certified machines. The evidence names exactly one certified component revision, SYS-221HE-TNRD. No record in evidence certifies any second SuperServer model, so the plural is unsupported.
- **Unqualified platform scope.** "Redhat Linux" appears with no version or architecture qualifier and reads as the platform generally. The evidence covers only 8.7-8.x and 9.0-9.x, and its scope field expressly limits the record to `architecture: x86_64`. RHEL 7 and earlier, RHEL 10 and later, and all non-x86_64 architectures fall outside the record.

The substantiated core of the claim is therefore real but narrower than the language used to express it.

**Hygiene observation (not an element failure).** `has_evidence_date` is `false`. The Evidence Standard for compatibility claims does not require an evidence date, so this does not reduce the verdict on its own. It is still material: catalog certification records are revisable and can be withdrawn, so the element-5 lifecycle determination rests on status as read at review time and cannot be pinned to a capture date. Recording an `evidence_date` against this evidence would close that gap.

**Prior ruling context.** `get_claim_status` returns `latest_ruling: null`, and this configuration has no memory store. There is accordingly no prior ruling context to diverge from, and this ruling rests solely on the evidence above.

**Remediation to reach `substantiated`.** Either narrow the claim text to the single certified model and its certified version ranges and architecture, or attach a separate catalog certification record for each additional SuperServer model the plural is meant to cover.


## vendor_compat-compatibility-06 — repetition 1

**Element-by-element application of the Evidence Standard.**

1. *Certification record link present* — **Not met for the subject of the claim.** A link is present in [6a44e5d6-3d9f-4817-9dbd-54c905a21718], and it resolves to a genuine Red Hat Ecosystem Catalog certification record. But the standard requires a certification record for the thing being claimed. The evidence's own scope field states plainly that this is "a nearest-comparator record for Broadberry's CyberStore house brand" and that "the claim itself cites no certification record." A comparator is not a certification. The presence of *a* link does not satisfy an element that presupposes the link certifies the claimed product.

2. *Platform named* — **Met.** [6a44e5d6-3d9f-4817-9dbd-54c905a21718] names Red Hat Enterprise Linux.

3. *Platform version named distinctly from the platform itself* — **Met.** [6a44e5d6-3d9f-4817-9dbd-54c905a21718] carries `8.7-8.x, 9.0-9.x` in a version field separate from the platform name, so the version is not merely folded into the product name (contrast a bare "Red Hat Linux," which would fail this element). Note these are open-ended version *ranges*, not discrete certified versions, which limits how narrowly the certified surface can be described.

4. *Certified component revision named* — **Not met for the subject of the claim.** This is the decisive failure. The component revision named in [6a44e5d6-3d9f-4817-9dbd-54c905a21718] is the Supermicro SuperServer SYS-221HE-TNRD — third-party hardware from a different manufacturer. The claim advertises Broadberry's own Red Hat Linux servers. The standard requires *the certified component revision* to be named, meaning the revision of the component whose compatibility is being asserted. Naming a different vendor's certified system satisfies the field mechanically while leaving the claim's actual subject uncertified. On the evidence in the registry, no Broadberry-branded system has a Red Hat certification record at all.

5. *Platform version has not passed the last lifecycle phase included in a standard support subscription* — **Met.** The deterministic hygiene check returns `platform_lifecycle_status: "current"`, and both the RHEL 8.x and RHEL 9.x streams named in [6a44e5d6-3d9f-4817-9dbd-54c905a21718] sit within phases included in a standard Red Hat subscription. Neither range depends on Red Hat ELS, so the standard's add-on carve-out is not triggered and does not push this evidence into expired status.

**Currency-policy application.** vendor_compat-compatibility-06 is a compatibility-type claim, not a compliance-type claim, so no external currency policy (regulatory refresh cycle, audit-period rule, or similar) governs it. Stating this explicitly for the record: **no external currency policy exists for this claim, and the Evidence Standard's own terms govern currency** — specifically its final clause tying validity to the platform version's lifecycle phase and treating add-on-only phases such as Red Hat ELS or Microsoft ESU as expired. Applied on its own terms, that clause is satisfied (element 5 above). Currency is therefore not the reason this claim fails; provenance is. Separately, [6a44e5d6-3d9f-4817-9dbd-54c905a21718] carries no evidence date (`has_evidence_date: false`), so there is no record of when the catalog entry was observed. Red Hat's catalog is mutable and certifications are revised as systems and RHEL streams move through their lifecycles, so even the comparator record cannot be pinned to a point in time. This is a secondary defect, not the basis of the verdict.

**Overreach beyond anything the evidence could support.** Even if a Broadberry certification record were substituted for [6a44e5d6-3d9f-4817-9dbd-54c905a21718], the headline "Fully Compatible Redhat Linux Servers" would remain unbounded in three directions the evidence does not reach: it is plural and unqualified across Broadberry's entire Red Hat server line, where the record covers a single system; it names no version ceiling, where the record covers stated ranges only; and it is architecture-silent, where the record is explicitly x86_64. "Fully" is an absolute, and absolutes require correspondingly complete substantiation. A single-system comparator record cannot carry a whole-portfolio, all-versions assertion.

**Unsupported material carried inside the same claim record.** The claim text also asserts that the solutions are "trusted to power some of the biggest organisations in the world," listing the BBC, Sky, NASA, the University of Oxford, the University of Cambridge, Toshiba, Rolls-Royce, Toyota, Google, and Virgin. This is a customer-reference / endorsement assertion. It falls outside the compatibility evidence standard quoted above and has **zero** supporting evidence in the registry; named-customer references generally require per-customer permission and verification. It is flagged here rather than ruled on, and should be split into its own claim record under the appropriate claim type. The trailing "Features" paragraph is a further problem of a different kind: it describes attributes of Red Hat Enterprise Linux itself — performance, built-in security, partner ecosystem, container tooling — and not any property of Broadberry's hardware or its compatibility. Combined with the registry's note that the text is non-contiguous on the source page (assembled across a hero block, a call-to-action, a duplicate re-render, and a separate Features subsection), the claim as recorded borrows Red Hat's platform virtues to imply a certification relationship that the evidence does not establish.

**Why not `partially` or `escalate`.** `partially` would be appropriate if a narrower true version of the claim survived on this evidence — but the shortfall is not one of breadth, it is that the claimed product has no certification record at all, so there is no narrower Broadberry-specific compatibility statement left standing. `escalate` would be appropriate if the standard were ambiguous or the evidence genuinely conflicting; neither holds. The standard is clear, the evidence is internally consistent, and it self-describes as a comparator rather than a certification. The correct disposition is unambiguous.

**Divergence from prior ruling context.** None to explain — there is no prior ruling context for this product and claim type, so this ruling rests solely on the evidence above.

**Route to substantiation.** Link a Red Hat Ecosystem Catalog certification record for the specific Broadberry CyberStore model(s) being advertised; add an evidence date; and either qualify the headline to the certified models, RHEL version ranges, and x86_64 architecture actually covered, or drop the absolute "Fully." Separate the customer-roster sentence into its own claim record for review under its own standard.


## vendor_compat-compatibility-06 — repetition 2

**Currency-policy application.** No external currency policy is registered
against compatibility claims for `vendor_compat`, so the Evidence Standard's
own lifecycle terms govern this ruling — specifically its requirement that the
platform version "has not passed the last lifecycle phase included in a
standard support subscription," with add-on-only phases (Red Hat ELS,
Microsoft ESU) counting as expired. I applied that clause directly and took no
other currency rule as controlling. I state this explicitly because the
lifecycle clause is the one element of this standard that turns on the passage
of time, and vendor_compat-compatibility-06 carries no evidence date to anchor
it to.

**Element-by-element application of the standard.**

1. *Certification record link present* — **met only in form, not as applied.**
   [6a44e5d6-3d9f-4817-9dbd-54c905a21718] does supply a live Red Hat Ecosystem
   Catalog link, and the `has_evidence_link` hygiene check returns true. But
   that record's own scope field states that it is "a nearest-comparator record
   for Broadberry's CyberStore house brand" and that "the claim itself cites no
   certification record." The standard requires a certification record for the
   thing being claimed. A comparator selected after the fact by a reviewer is
   not the claimant's certification record, and the scope field says as much in
   terms.

2. *Platform named* — **met.** [6a44e5d6-3d9f-4817-9dbd-54c905a21718] names Red
   Hat Enterprise Linux.

3. *Platform version named distinctly from the platform itself* — **met.**
   [6a44e5d6-3d9f-4817-9dbd-54c905a21718] carries "8.7-8.x, 9.0-9.x" in a
   version field separate from the platform name, satisfying the standard's
   distinctness requirement rather than folding the version into a single
   "RHEL 9" style string.

4. *Certified component revision named* — **not met.** The field is populated,
   but what it names is "Supermicro SuperServer SYS-221HE-TNRD" — a third
   party's system. It is not any Broadberry CyberStore server, and the claim
   text of vendor_compat-compatibility-06 is about Broadberry's own Red Hat
   Linux servers. The standard asks for the certified revision *of the
   component the claim is made about*; a populated field naming someone else's
   hardware does not satisfy it. This is the dispositive failure.

5. *Platform version has not passed its last standard-subscription lifecycle
   phase* — **met.** The `platform_lifecycle_status` hygiene check returns
   "current," and both streams recorded in
   [6a44e5d6-3d9f-4817-9dbd-54c905a21718] (8.7-8.x and 9.0-9.x) sit within
   maintenance support included in a standard RHEL subscription, not in
   ELS-only territory, so the standard's add-on-equals-expired proviso is not
   triggered. Note that `has_evidence_date` is false and `is_expired` is null
   on this record, so this element rests on the lifecycle check rather than on
   any dated attestation in the evidence itself.

**Why not_substantiated rather than partially.** Three of five elements are
met, but the two that fail (1 as-applied, and 4) are precisely the elements
that bind the evidence to the claimed product. Elements 2, 3 and 5 establish
facts about Red Hat Enterprise Linux as a platform — facts that are true
regardless of whether Broadberry's servers are certified at all. Strip out the
comparator and vendor_compat-compatibility-06 has zero certification coverage
of the product it advertises. "Partially" would imply a narrower version of the
claim survives on this evidence; none does, because no Broadberry system is
certified anywhere in the record. I also did not escalate: the defect is
determinate and legible on the face of
[6a44e5d6-3d9f-4817-9dbd-54c905a21718]'s own scope field, not a judgment call
needing a higher reviewer.

**Independent breadth problem.** Even if the comparator were accepted
arguendo, the headline assertion — "Fully Compatible Redhat Linux Servers" — is
unqualified as to version, architecture, and model.
[6a44e5d6-3d9f-4817-9dbd-54c905a21718] is bounded to RHEL 8.7-8.x and 9.0-9.x,
to x86_64, and to a single system, and states no configuration scope beyond
that. "Fully" asserts more than the record could support even on its most
favourable reading.

**Out-of-scope material flagged, not ruled on.** The claim text of
vendor_compat-compatibility-06 also carries a customer roster (BBC, Sky, NASA,
Oxford, Cambridge, Toshiba, Rolls-Royce, Toyota, Google, Virgin) and, in a
non-contiguous "Features" block, copy describing Red Hat Enterprise Linux's own
performance, security and partner ecosystem. Neither is a compatibility
assertion and neither is addressed by the Evidence Standard quoted above, so
neither is ruled on here. Both are unsupported by
[6a44e5d6-3d9f-4817-9dbd-54c905a21718], and the Red Hat feature copy describes
the platform vendor's product rather than Broadberry's, which may warrant
separate review as an endorsement or attribution claim.

**Divergence from prior ruling context.** None to explain — there is no prior
ruling context for this product and claim type, and `get_claim_status` returns
`latest_ruling: null`, so this ruling rests solely on the evidence above.
