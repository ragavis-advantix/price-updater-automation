-- Create a table to log each price update batch
CREATE TABLE IF NOT EXISTS price_update_log (
    id SERIAL PRIMARY KEY,
    batch_id VARCHAR(50) NOT NULL,      -- unique run ID, e.g. 2025-09-18-001
    timestamp TIMESTAMP DEFAULT NOW(),  -- when the batch was processed
    items_processed INT,                -- number of products updated
    csv_file VARCHAR(255),              -- filename of generated CSV
    pdf_file VARCHAR(255),              -- filename of generated PDF
    status VARCHAR(20) DEFAULT 'pending', -- success / failed / pending
    notes TEXT                          -- extra info (e.g. CMS sync result)
);

-- Optional: table for raw product price records (if you want to store them)
CREATE TABLE IF NOT EXISTS product_prices (
    id SERIAL PRIMARY KEY,
    sku VARCHAR(50) NOT NULL,
    product_name TEXT NOT NULL,
    old_price NUMERIC(10,2),
    new_price NUMERIC(10,2),
    batch_id VARCHAR(50) REFERENCES price_update_log(batch_id)
);
