-- Migration: Add extra_data column to payments table for CryptoBot integration
-- Date: 2025-10-24
-- Description: Adds a JSON column to store additional payment data (e.g., CryptoBot invoice_id)
-- Note: 'metadata' is a reserved word in SQLAlchemy, so we use 'extra_data' instead

-- Add extra_data column to payments table
ALTER TABLE payments ADD COLUMN IF NOT EXISTS extra_data JSONB;

-- Create index on extra_data for faster queries (optional)
CREATE INDEX IF NOT EXISTS idx_payments_extra_data ON payments USING gin (extra_data);

-- Example usage:
-- UPDATE payments SET extra_data = '{"invoice_id": "abc123"}' WHERE id = 1;
