-- SEO-PLAYBOOK P6: Shared viability analyses for viral growth
-- Enables shareable public pages at /analise/[hash]

CREATE TABLE IF NOT EXISTS public.shared_analyses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  hash VARCHAR(12) UNIQUE NOT NULL,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  bid_id TEXT NOT NULL,
  bid_title TEXT NOT NULL,
  bid_orgao TEXT,
  bid_uf TEXT,
  bid_valor NUMERIC,
  bid_modalidade TEXT,
  viability_score INTEGER NOT NULL CHECK (viability_score BETWEEN 0 AND 100),
  viability_level TEXT NOT NULL CHECK (viability_level IN ('alta', 'media', 'baixa')),
  viability_factors JSONB NOT NULL DEFAULT '{}'::jsonb,
  view_count INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT now(),
  expires_at TIMESTAMPTZ DEFAULT (now() + INTERVAL '30 days')
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_shared_analyses_hash ON public.shared_analyses(hash);
CREATE INDEX IF NOT EXISTS idx_shared_analyses_user ON public.shared_analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_shared_analyses_expires ON public.shared_analyses(expires_at);

-- RLS
ALTER TABLE public.shared_analyses ENABLE ROW LEVEL SECURITY;

-- Public can read any non-expired share (for the public page)
CREATE POLICY "anyone_can_read_shares"
  ON public.shared_analyses
  FOR SELECT
  USING (expires_at > now());

-- Authenticated users can create their own shares
CREATE POLICY "users_insert_own_shares"
  ON public.shared_analyses
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- RPC to atomically increment view count (avoids RLS write restrictions)
CREATE OR REPLACE FUNCTION public.increment_share_view(share_hash VARCHAR)
RETURNS void
LANGUAGE sql
SECURITY DEFINER
AS $$
  UPDATE public.shared_analyses
  SET view_count = view_count + 1
  WHERE hash = share_hash AND expires_at > now();
$$;
