import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { neon } from '@neondatabase/serverless';

const __dirname = dirname(fileURLToPath(import.meta.url));
const envPath = join(__dirname, '..', '.env.local');

// Read .env.local and set environment variables
const envContent = readFileSync(envPath, 'utf-8');
envContent.split('\n').forEach(line => {
  const trimmed = line.trim();
  if (trimmed && !trimmed.startsWith('#')) {
    const [key, ...valueParts] = trimmed.split('=');
    const value = valueParts.join('=');
    process.env[key] = value;
  }
});

const sql = neon(process.env.DATABASE_URL);

const createTablesSQL = `
-- Create user table
CREATE TABLE IF NOT EXISTS "user" (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE,
  email_verified BOOLEAN NOT NULL DEFAULT FALSE,
  image TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create session table
CREATE TABLE IF NOT EXISTS session (
  id TEXT PRIMARY KEY,
  expires_at TIMESTAMP NOT NULL,
  token TEXT NOT NULL UNIQUE,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
  ip_address TEXT,
  user_agent TEXT,
  user_id TEXT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE
);

-- Create account table
CREATE TABLE IF NOT EXISTS account (
  id TEXT PRIMARY KEY,
  account_id TEXT NOT NULL,
  provider_id TEXT NOT NULL,
  user_id TEXT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
  access_token TEXT,
  refresh_token TEXT,
  id_token TEXT,
  access_token_expires_at TIMESTAMP,
  refresh_token_expires_at TIMESTAMP,
  scope TEXT,
  password TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create verification table
CREATE TABLE IF NOT EXISTS verification (
  id TEXT PRIMARY KEY,
  identifier TEXT NOT NULL,
  value TEXT NOT NULL,
  expires_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_session_user_id ON session(user_id);
CREATE INDEX IF NOT EXISTS idx_session_token ON session(token);
CREATE INDEX IF NOT EXISTS idx_account_user_id ON account(user_id);
CREATE INDEX IF NOT EXISTS idx_user_email ON "user"(email);
`;

async function main() {
  console.log('Creating Better Auth tables...');
  try {
    // Create user table
    await sql`
      CREATE TABLE IF NOT EXISTS "user" (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        email_verified BOOLEAN NOT NULL DEFAULT FALSE,
        image TEXT,
        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMP NOT NULL DEFAULT NOW()
      )
    `;
    console.log('Created user table');

    // Create session table
    await sql`
      CREATE TABLE IF NOT EXISTS session (
        id TEXT PRIMARY KEY,
        expires_at TIMESTAMP NOT NULL,
        token TEXT NOT NULL UNIQUE,
        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
        ip_address TEXT,
        user_agent TEXT,
        user_id TEXT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE
      )
    `;
    console.log('Created session table');

    // Create account table
    await sql`
      CREATE TABLE IF NOT EXISTS account (
        id TEXT PRIMARY KEY,
        account_id TEXT NOT NULL,
        provider_id TEXT NOT NULL,
        user_id TEXT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
        access_token TEXT,
        refresh_token TEXT,
        id_token TEXT,
        access_token_expires_at TIMESTAMP,
        refresh_token_expires_at TIMESTAMP,
        scope TEXT,
        password TEXT,
        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMP NOT NULL DEFAULT NOW()
      )
    `;
    console.log('Created account table');

    // Create verification table
    await sql`
      CREATE TABLE IF NOT EXISTS verification (
        id TEXT PRIMARY KEY,
        identifier TEXT NOT NULL,
        value TEXT NOT NULL,
        expires_at TIMESTAMP NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMP NOT NULL DEFAULT NOW()
      )
    `;
    console.log('Created verification table');

    // Create indexes
    await sql`CREATE INDEX IF NOT EXISTS idx_session_user_id ON session(user_id)`;
    await sql`CREATE INDEX IF NOT EXISTS idx_session_token ON session(token)`;
    await sql`CREATE INDEX IF NOT EXISTS idx_account_user_id ON account(user_id)`;
    await sql`CREATE INDEX IF NOT EXISTS idx_user_email ON "user"(email)`;
    console.log('Created indexes');

    console.log('All tables created successfully!');
  } catch (error) {
    console.error('Error creating tables:', error);
    process.exit(1);
  }
}

main();
