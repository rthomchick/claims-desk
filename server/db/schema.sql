create table claims (
    claim_id uuid primary key default gen_random_uuid(),
    product_key text not null,           -- e.g. 'kalder_resolve', matches kalder_data_model.py PRODUCTS keys
    claim_type text not null check (claim_type in ('performance', 'comparative', 'compliance', 'superlative')),
    claim_text text not null,
    status text not null default 'unverified' check (status in ('unverified', 'substantiated', 'insufficient', 'expired')),
    risk_class text check (risk_class in ('low', 'medium', 'high', 'prohibited')),
    risk_factors jsonb,                  -- structured factors driving the risk_class, not just the label
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table evidence_links (
    evidence_id uuid primary key default gen_random_uuid(),
    claim_id uuid not null references claims(claim_id) on delete cascade,
    evidence_url text,
    evidence_date date,
    sample_size integer,                 -- nullable; only populated for performance/comparative claims
    baseline text,                       -- nullable; comparison basis or baseline named
    expiry_date date,                    -- nullable; populated for compliance/superlative claims
    created_at timestamptz not null default now()
);

create table review_rulings (
    ruling_id uuid primary key default gen_random_uuid(),
    claim_id uuid not null references claims(claim_id) on delete cascade,
    ruling text not null check (ruling in ('approved', 'rejected', 'escalated')),
    rationale text,
    reviewed_by text,                    -- 'system' for MCP-tool-driven, agent identifier for Week 18 review agent
    created_at timestamptz not null default now()
);
