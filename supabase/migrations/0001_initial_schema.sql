-- Initial Schema for FinLit Application

-- Enable UUID generation if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Users Table
CREATE TABLE public.users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT, -- Store hashed passwords if not using Supabase Auth directly for local users
  role TEXT NOT NULL DEFAULT 'student', -- 'student', 'instructor', 'admin'
  profile JSONB, -- Flexible JSON field for additional user details
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Set up RLS for users table
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow logged-in users to view their own user data" ON public.users FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Allow users to update their own user data" ON public.users FOR UPDATE USING (auth.uid() = id);
-- Admin policy (requires custom JWT claims or backend logic to verify role)
-- CREATE POLICY "Admins can manage all users" ON public.users FOR ALL USING (auth.role() = 'admin');

-- 2. Portfolios Table
CREATE TABLE public.portfolios (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
  balance NUMERIC(15,2) DEFAULT 10000.00 NOT NULL,
  total_value NUMERIC(15,2), -- Calculated: balance + sum(holdings_value)
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Set up RLS for portfolios table
ALTER TABLE public.portfolios ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Students own their portfolio" ON public.portfolios FOR ALL USING (auth.uid() = user_id);

-- Index for faster user_id lookups
CREATE INDEX idx_portfolios_user_id ON public.portfolios(user_id);

-- 3. Trades Table
CREATE TABLE public.trades (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  portfolio_id UUID REFERENCES public.portfolios(id) ON DELETE CASCADE,
  symbol TEXT NOT NULL,
  quantity INTEGER NOT NULL CHECK (quantity > 0),
  price NUMERIC(10,2) NOT NULL CHECK (price >= 0),
  side TEXT NOT NULL CHECK (side IN ('BUY', 'SELL')),
  executed_at TIMESTAMPTZ DEFAULT NOW()
);

-- Set up RLS for trades table
ALTER TABLE public.trades ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Students can see their own trades" ON public.trades FOR SELECT USING (EXISTS (SELECT 1 FROM public.portfolios WHERE id = portfolio_id AND user_id = auth.uid()));
CREATE POLICY "Students can insert their own trades" ON public.trades FOR INSERT WITH CHECK (EXISTS (SELECT 1 FROM public.portfolios WHERE id = portfolio_id AND user_id = auth.uid()));

-- Index for faster portfolio_id lookups
CREATE INDEX idx_trades_portfolio_id ON public.trades(portfolio_id);

-- 4. Market Events Table
CREATE TABLE public.market_events (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  event_type TEXT NOT NULL, -- e.g., 'interest_rate_change', 'market_crash', 'earnings_report'
  description TEXT,
  impact JSONB, -- Structured data about impact on different assets (e.g., {'AAPL': {'price_change': 0.05}})
  event_date TIMESTAMPTZ DEFAULT NOW()
);

-- Set up RLS for market_events table (read-only for authenticated users)
ALTER TABLE public.market_events ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow all authenticated users to read market events" ON public.market_events FOR SELECT USING (auth.role() = 'authenticated');

-- 5. Webinars Table
CREATE TABLE public.webinars (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  instructor_id UUID REFERENCES public.users(id) ON DELETE SET NULL, -- If instructor is deleted, set to NULL
  topic TEXT NOT NULL,
  description TEXT,
  scheduled_at TIMESTAMPTZ NOT NULL,
  duration_minutes INTEGER NOT NULL DEFAULT 60,
  recording_url TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Set up RLS for webinars table
ALTER TABLE public.webinars ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow all authenticated users to read webinars" ON public.webinars FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Instructors can manage their own webinars" ON public.webinars FOR ALL USING (auth.uid() = instructor_id);

-- 6. Chatbot Interactions Table
CREATE TABLE public.chatbot_interactions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
  query TEXT NOT NULL,
  response TEXT NOT NULL,
  feedback INTEGER CHECK (feedback BETWEEN 1 AND 5), -- Optional feedback rating
  interaction_at TIMESTAMPTZ DEFAULT NOW()
);

-- Set up RLS for chatbot_interactions table
ALTER TABLE public.chatbot_interactions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Students can see and insert their own chatbot interactions" ON public.chatbot_interactions FOR ALL USING (auth.uid() = user_id);

-- Optional: Function to update `updated_at` column automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to relevant tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON public.users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_portfolios_updated_at BEFORE UPDATE ON public.portfolios FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
