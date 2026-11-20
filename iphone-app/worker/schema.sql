-- Surrey League Compendium back office: the database
CREATE TABLE IF NOT EXISTS devices (
  token TEXT PRIMARY KEY,          -- Apple's address for one iPhone
  follow TEXT NOT NULL,            -- what that phone follows (JSON)
  env TEXT,                        -- 'production' (TestFlight/App Store) or 'sandbox' (Xcode); learnt on first send
  admin INTEGER NOT NULL DEFAULT 0,-- 1 = Steve's phone: gets every batch first, for approval
  created TEXT NOT NULL,
  updated TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS batches (
  id TEXT PRIMARY KEY,
  created TEXT NOT NULL,
  summary TEXT NOT NULL,           -- e.g. "Men's match 2 at Beckenham Place Park: results"
  status TEXT NOT NULL             -- awaiting_approval | sending | done | cancelled
);
CREATE TABLE IF NOT EXISTS deliveries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  batch TEXT NOT NULL,
  token TEXT NOT NULL,
  payload TEXT NOT NULL,           -- the APNs JSON
  is_admin INTEGER NOT NULL DEFAULT 0,
  sent INTEGER NOT NULL DEFAULT 0, -- 0 waiting, 1 sent, 2 failed
  result TEXT
);
CREATE INDEX IF NOT EXISTS deliveries_waiting ON deliveries (sent, batch);

-- Fast race-day results (20 Nov 2026)
CREATE TABLE IF NOT EXISTS announced (
  key TEXT PRIMARY KEY,            -- e.g. "2026/27|men|m3|results": these new results have been announced
  at TEXT NOT NULL,
  batch TEXT
);
CREATE TABLE IF NOT EXISTS fast_races (
  key TEXT PRIMARY KEY,            -- league match id | race, e.g. "197|Senior Men"
  first_seen TEXT NOT NULL,        -- when results first appeared in the league's feed
  dispatched_at TEXT,              -- when GitHub was last asked to write and send the notifications
  tries INTEGER NOT NULL DEFAULT 0,
  announced_at TEXT,               -- when the notifications were handed over (or found already sent)
  note TEXT
);
