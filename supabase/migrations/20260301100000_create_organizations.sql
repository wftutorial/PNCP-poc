-- STORY-322: Organizations support (consultoria/agency multi-user accounts)
-- Creates organizations and organization_members tables with full RLS

-- ============================================================================
-- Helper: ensure public.update_updated_at() exists
-- (first defined in 001_profiles_and_sessions.sql — guard against missing)
-- ============================================================================

CREATE OR REPLACE FUNCTION public.update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Table: organizations
-- ============================================================================

CREATE TABLE public.organizations (
  id          UUID        DEFAULT gen_random_uuid() PRIMARY KEY,
  name        TEXT        NOT NULL,
  logo_url    TEXT,
  owner_id    UUID        NOT NULL REFERENCES auth.users(id) ON DELETE RESTRICT,
  max_members INT         NOT NULL DEFAULT 5,
  plan_type   TEXT        NOT NULL DEFAULT 'consultoria',
  stripe_customer_id TEXT,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  public.organizations IS 'STORY-322: Multi-user organizations for consultoria/agency accounts';
COMMENT ON COLUMN public.organizations.owner_id    IS 'User who created and owns the organization (cannot be deleted while org exists)';
COMMENT ON COLUMN public.organizations.max_members IS 'Maximum number of members allowed (enforced at application level)';
COMMENT ON COLUMN public.organizations.plan_type   IS 'Billing plan type for the organization';

-- ============================================================================
-- Table: organization_members
-- ============================================================================

CREATE TABLE public.organization_members (
  id          UUID        DEFAULT gen_random_uuid() PRIMARY KEY,
  org_id      UUID        NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
  user_id     UUID        NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  role        TEXT        NOT NULL DEFAULT 'member'
                            CHECK (role IN ('owner', 'admin', 'member')),
  invited_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  accepted_at TIMESTAMPTZ,
  UNIQUE(org_id, user_id)
);

COMMENT ON TABLE  public.organization_members IS 'STORY-322: Members of an organization with role-based access';
COMMENT ON COLUMN public.organization_members.role        IS 'Role within the org: owner (full control), admin (manage members), member (read-only team access)';
COMMENT ON COLUMN public.organization_members.invited_at  IS 'Timestamp when invitation was sent';
COMMENT ON COLUMN public.organization_members.accepted_at IS 'Timestamp when invitation was accepted; NULL means pending';

-- ============================================================================
-- Indexes
-- ============================================================================

CREATE INDEX idx_organizations_owner
  ON public.organizations(owner_id);

CREATE INDEX idx_org_members_org
  ON public.organization_members(org_id);

CREATE INDEX idx_org_members_user
  ON public.organization_members(user_id);

-- ============================================================================
-- Auto-update updated_at trigger for organizations
-- ============================================================================

CREATE TRIGGER tr_organizations_updated_at
  BEFORE UPDATE ON public.organizations
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at();

-- ============================================================================
-- Row Level Security — organizations
-- ============================================================================

ALTER TABLE public.organizations ENABLE ROW LEVEL SECURITY;

-- Owner can see their own organization
CREATE POLICY "Org owner can view organization"
  ON public.organizations
  FOR SELECT
  USING (auth.uid() = owner_id);

-- Admins (members with role='admin') can also view the organization
CREATE POLICY "Org admins can view organization"
  ON public.organizations
  FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM public.organization_members om
      WHERE om.org_id  = public.organizations.id
        AND om.user_id = auth.uid()
        AND om.role    IN ('owner', 'admin')
        AND om.accepted_at IS NOT NULL
    )
  );

-- Owner can create organizations
CREATE POLICY "Owner can insert organization"
  ON public.organizations
  FOR INSERT
  WITH CHECK (auth.uid() = owner_id);

-- Owner can update their organization
CREATE POLICY "Owner can update organization"
  ON public.organizations
  FOR UPDATE
  USING (auth.uid() = owner_id)
  WITH CHECK (auth.uid() = owner_id);

-- Service role full access to organizations
CREATE POLICY "Service role full access on organizations"
  ON public.organizations
  FOR ALL
  USING (auth.role() = 'service_role');

-- ============================================================================
-- Row Level Security — organization_members
-- ============================================================================

ALTER TABLE public.organization_members ENABLE ROW LEVEL SECURITY;

-- Users can see their own membership record (any org)
CREATE POLICY "Users can view own membership"
  ON public.organization_members
  FOR SELECT
  USING (auth.uid() = user_id);

-- Org owner and admins can see all members of the org
CREATE POLICY "Org owner/admin can view all members"
  ON public.organization_members
  FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM public.organization_members om
      WHERE om.org_id  = public.organization_members.org_id
        AND om.user_id = auth.uid()
        AND om.role    IN ('owner', 'admin')
        AND om.accepted_at IS NOT NULL
    )
  );

-- Org owner and admins can invite (insert) new members
CREATE POLICY "Org owner/admin can insert members"
  ON public.organization_members
  FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.organization_members om
      WHERE om.org_id  = public.organization_members.org_id
        AND om.user_id = auth.uid()
        AND om.role    IN ('owner', 'admin')
        AND om.accepted_at IS NOT NULL
    )
    OR
    -- Allow owner to add the first member row (bootstrap: owner adds themselves)
    EXISTS (
      SELECT 1 FROM public.organizations o
      WHERE o.id       = public.organization_members.org_id
        AND o.owner_id = auth.uid()
    )
  );

-- Org owner and admins can remove members
CREATE POLICY "Org owner/admin can delete members"
  ON public.organization_members
  FOR DELETE
  USING (
    EXISTS (
      SELECT 1 FROM public.organization_members om
      WHERE om.org_id  = public.organization_members.org_id
        AND om.user_id = auth.uid()
        AND om.role    IN ('owner', 'admin')
        AND om.accepted_at IS NOT NULL
    )
    OR
    -- Users can remove themselves (leave org)
    auth.uid() = user_id
  );

-- Service role full access to organization_members
CREATE POLICY "Service role full access on organization_members"
  ON public.organization_members
  FOR ALL
  USING (auth.role() = 'service_role');

-- ============================================================================
-- Grants
-- ============================================================================

GRANT SELECT, INSERT, UPDATE, DELETE ON public.organizations        TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.organization_members TO authenticated;

GRANT ALL ON public.organizations        TO service_role;
GRANT ALL ON public.organization_members TO service_role;

-- ============================================================================
-- Verification
-- ============================================================================

DO $$
BEGIN
  RAISE NOTICE 'STORY-322: organizations tables created successfully';
END $$;
