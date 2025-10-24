-- Add expires_at column to payments table
-- This field stores when the payment expires (typically created_at + PAYMENT_TIMEOUT_MINUTES)

ALTER TABLE payments ADD COLUMN IF NOT EXISTS expires_at TIMESTAMP;

-- Create index for faster queries on expired payments
CREATE INDEX IF NOT EXISTS idx_payments_expires_at ON payments(expires_at) WHERE status = 'pending';

-- Optional: Set expires_at for existing pending payments (10 minutes from created_at)
UPDATE payments
SET expires_at = created_at + INTERVAL '10 minutes'
WHERE expires_at IS NULL AND status = 'pending';
