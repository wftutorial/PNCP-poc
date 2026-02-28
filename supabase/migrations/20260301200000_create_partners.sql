-- STORY-323: Revenue Share Tracking — Partner + Referral tables
-- AC1: partners table
-- AC2: partner_referrals table
-- AC3: RLS policies

-- ============================================================================
-- AC1: Partners table
-- ============================================================================
CREATE TABLE IF NOT EXISTS partners (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,              -- ex: "triunfo-legis"
    contact_email TEXT NOT NULL,
    contact_name TEXT,
    stripe_coupon_id TEXT,                  -- Stripe coupon linked to partner
    revenue_share_pct NUMERIC(5,2) DEFAULT 25.00,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'pending')),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Index for slug lookups (signup flow)
CREATE INDEX IF NOT EXISTS idx_partners_slug ON partners(slug);
-- Index for status filtering (admin dashboard)
CREATE INDEX IF NOT EXISTS idx_partners_status ON partners(status);

-- ============================================================================
-- AC2: Partner referrals table
-- ============================================================================
CREATE TABLE IF NOT EXISTS partner_referrals (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    partner_id UUID NOT NULL REFERENCES partners(id),
    referred_user_id UUID NOT NULL REFERENCES auth.users(id),
    signup_at TIMESTAMPTZ DEFAULT now(),
    converted_at TIMESTAMPTZ,              -- when user subscribed to paid plan
    churned_at TIMESTAMPTZ,                -- when user cancelled
    monthly_revenue NUMERIC(10,2),         -- subscription monthly value
    revenue_share_amount NUMERIC(10,2),    -- revenue_share_pct * monthly_revenue
    UNIQUE(partner_id, referred_user_id)   -- prevent duplicate referrals
);

-- Index for partner dashboard queries
CREATE INDEX IF NOT EXISTS idx_partner_referrals_partner_id ON partner_referrals(partner_id);
-- Index for user lookup (webhook flow)
CREATE INDEX IF NOT EXISTS idx_partner_referrals_referred_user_id ON partner_referrals(referred_user_id);

-- ============================================================================
-- AC4: Add referred_by_partner_id to profiles
-- ============================================================================
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS referred_by_partner_id UUID REFERENCES partners(id);
CREATE INDEX IF NOT EXISTS idx_profiles_referred_by_partner ON profiles(referred_by_partner_id)
    WHERE referred_by_partner_id IS NOT NULL;

-- ============================================================================
-- AC3: RLS Policies
-- ============================================================================

-- Enable RLS
ALTER TABLE partners ENABLE ROW LEVEL SECURITY;
ALTER TABLE partner_referrals ENABLE ROW LEVEL SECURITY;

-- Partners: admin/service_role can do everything
CREATE POLICY partners_admin_all ON partners
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.id = auth.uid()
            AND profiles.is_admin = true
        )
    );

-- Partners: partner (matched by contact_email) can read their own record
CREATE POLICY partners_self_read ON partners
    FOR SELECT USING (
        contact_email = (
            SELECT email FROM auth.users WHERE id = auth.uid()
        )
    );

-- Partner referrals: admin can do everything
CREATE POLICY partner_referrals_admin_all ON partner_referrals
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.id = auth.uid()
            AND profiles.is_admin = true
        )
    );

-- Partner referrals: partner can see their own referrals
CREATE POLICY partner_referrals_partner_read ON partner_referrals
    FOR SELECT USING (
        partner_id IN (
            SELECT p.id FROM partners p
            WHERE p.contact_email = (
                SELECT email FROM auth.users WHERE id = auth.uid()
            )
        )
    );

-- Service role bypass (for backend operations)
CREATE POLICY partners_service_role ON partners
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY partner_referrals_service_role ON partner_referrals
    FOR ALL USING (auth.role() = 'service_role');
