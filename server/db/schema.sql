create table claims (
    claim_id uuid primary key default gen_random_uuid(),
    product_key text not null,           -- e.g. 'kalder_resolve', matches kalder_data_model.py PRODUCTS keys
    claim_type text not null check (claim_type in ('performance', 'comparative', 'compliance', 'superlative', 'compatibility')),
    claim_text text not null,
    status text not null default 'unverified' check (status in ('unverified', 'substantiated', 'insufficient', 'expired')),
    record_status text not null default 'active' check (record_status in ('active', 'deleted')),
    claim_slug text not null unique,     -- stable, human-readable address: {product_key}-{claim_type}-{NN}, never reused
    risk_class text check (risk_class in ('low', 'medium', 'high', 'prohibited')),
    risk_factors jsonb,                  -- structured factors driving the risk_class, not just the label
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    written_by_session text              -- nullable; Managed Agents session.id, see column comment below
);

create table evidence_links (
    evidence_id uuid primary key default gen_random_uuid(),
    claim_id uuid not null references claims(claim_id) on delete cascade,
    evidence_url text,
    evidence_date date,
    sample_size integer,                 -- nullable; only populated for performance/comparative claims
    baseline text,                       -- nullable; comparison basis or baseline named
    expiry_date date,                    -- nullable; populated for compliance/superlative claims
    scope text,                          -- nullable; configuration/support-tier detail that doesn't decompose into columns. Version/revision facts do NOT go here.
    platform text,                       -- nullable; compatibility claims only. Certified platform/OS name, e.g. 'Red Hat Enterprise Linux'.
    platform_version text,               -- nullable; compatibility claims only. Certified version range, e.g. '9.0-9.x'. Deterministic checks read this, not scope.
    component_revision text,             -- nullable; compatibility claims only. SKU, firmware, or driver revision covered. Deterministic checks read this, not scope.
    created_at timestamptz not null default now(),
    written_by_session text              -- nullable; Managed Agents session.id, see column comment below
);

comment on column claims.written_by_session is
    'Managed Agents session.id of the session that wrote this row, when written by an agent session. Null for rows written by hand, by seed scripts, or before this column existed. Closes the attribution half of Week 18''s f16.';
comment on column evidence_links.written_by_session is
    'Managed Agents session.id of the session that wrote this row, when written by an agent session. Null for rows written by hand, by seed scripts, or before this column existed. Closes the attribution half of Week 18''s f16.';
comment on column evidence_links.scope is
    'Configuration and support-tier detail that does not decompose into columns. Does NOT carry version/revision facts once platform/platform_version/component_revision are populated.';
comment on column evidence_links.platform is
    'Compatibility claims: certified platform/OS name, e.g. ''Red Hat Enterprise Linux''. Version and revision facts live here and in platform_version/component_revision, not in scope.';
comment on column evidence_links.platform_version is
    'Stores the certification record''s range notation verbatim as the vendor publishes it (e.g. ''9.0-9.x'', ''8.6-8.x''). Not normalized. The major version is parsed as the leading digit run, so the vendor''s own format must be preserved.';
comment on column evidence_links.component_revision is
    'Compatibility claims: SKU, firmware, or driver revision covered. Deterministic checks read this field, not scope.';

create table review_rulings (
    ruling_id uuid primary key default gen_random_uuid(),
    claim_id uuid not null references claims(claim_id),  -- no cascade: rulings survive a soft-deleted claim (d1)
    ruling text not null check (ruling in ('approved', 'rejected', 'escalated')),
    rationale text,
    reviewed_by text,                    -- 'system' for MCP-tool-driven, agent identifier for Week 18 review agent
    created_at timestamptz not null default now()
);

create view active_claims as
select * from claims where record_status = 'active';

create table platform_lifecycle (
    platform text not null,              -- e.g. 'Red Hat Enterprise Linux'
    major_version text not null,         -- '8', '9', '10'
    standard_support_end date,           -- end of the last phase included
                                          -- in a standard subscription
    phase_name text,                     -- the phase that date belongs to,
                                          -- recorded so the threshold is
                                          -- auditable rather than a bare date
    source_url text not null,
    retrieved_at timestamptz not null,
    primary key (platform, major_version)
);

comment on table platform_lifecycle is
    'Populated once, Week 19. No refresh mechanism exists. Rows are accurate as of retrieved_at and go stale silently. Any consumer must treat retrieved_at as a currency bound on its own conclusion.';
