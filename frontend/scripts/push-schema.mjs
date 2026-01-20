import { readFileSync } from 'fs';
import { spawnSync } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

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

console.log('DATABASE_URL is set:', !!process.env.DATABASE_URL);

// Run drizzle-kit push
const result = spawnSync('npx', ['drizzle-kit', 'push'], {
  stdio: ['pipe', 'inherit', 'inherit'],
  input: '\n\n\n\n\n\n\n\n\n\n', // Send enter keys to accept defaults
  cwd: join(__dirname, '..'),
  env: process.env,
  shell: true
});

if (result.status !== 0) {
  console.error('Push failed with status:', result.status);
  process.exit(1);
}
