import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
import psycopg2
import requests  # only used if CMS sync is enabled

# -------------------------
# Config
# -------------------------
DATA_DIR = "data"
INPUT_FILE = os.path.join(DATA_DIR, "pos_prices.csv")   # POS export file
CMS_API_URL = os.getenv("CMS_API_URL", None)            # optional CMS endpoint
CMS_API_KEY = os.getenv("CMS_API_KEY", None)            # optional CMS auth key

# Postgres connection (matches docker-compose.yml)
DB_HOST = "postgres"
DB_PORT = 5432  # Internal Docker network port
DB_NAME = "priceupdater"
DB_USER = "n8n"
DB_PASS = "n8npass"


def generate_labels():
    # -------------------------
    # 1. Load POS export
    # -------------------------
    if not os.path.exists(INPUT_FILE):
        print(f"❌ POS export file not found: {INPUT_FILE}")
        return

    df = pd.read_csv(INPUT_FILE)

    # Validate columns
    required_cols = {"SKU", "Product Name", "CURRENT PRICE", "NEW PRICE"}
    if not required_cols.issubset(df.columns):
        print(f"❌ POS file must have columns: {required_cols}")
        return

    # Ensure NEW PRICE has default value of 0
    if df["NEW PRICE"].isna().any():
        df["NEW PRICE"] = df["NEW PRICE"].fillna(0)

    # Update CURRENT PRICE if NEW PRICE was set
    price_updates = df["NEW PRICE"] > 0
    if price_updates.any():
        # Store current prices before update
        df.loc[price_updates, "CURRENT PRICE"] = df.loc[price_updates, "NEW PRICE"]
        # Reset NEW PRICE back to 0 after applying changes
        df.loc[price_updates, "NEW PRICE"] = 0
        # Save the updated CSV back
        df.to_csv(INPUT_FILE, index=False)
        print("💰 Updated current prices with new values")

    # -------------------------
    # 2. Generate output files
    # -------------------------
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    batch_id = f"batch-{timestamp}"

    csv_out = os.path.join(DATA_DIR, f"price_labels_{timestamp}.csv")
    pdf_out = os.path.join(DATA_DIR, f"price_labels_{timestamp}.pdf")

    # Save CSV with all columns
    df.to_csv(csv_out, index=False)

    # Create output DataFrame with formatted prices
    output_df = df.copy()
    output_df['CURRENT PRICE'] = output_df['CURRENT PRICE'].apply(lambda x: f"₹{x:.2f}")
    output_df['NEW PRICE'] = output_df.apply(lambda row: f"₹{row['NEW PRICE']:.2f}" if row['NEW PRICE'] > 0 else "-", axis=1)
    
    # Save CSV with formatted prices
    output_df.to_csv(csv_out, index=False)

    # Save PDF with price comparison
    c = canvas.Canvas(pdf_out, pagesize=A4)
    y = 800

    # Add header
    header_y = y + 30
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, header_y, "SKU")
    c.drawString(150, header_y, "Product Name")
    c.drawString(400, header_y, "Current Price")
    c.drawString(500, header_y, "New Price")
    c.line(40, header_y - 5, 550, header_y - 5)  # Draw line under header

    # Add product rows
    c.setFont("Helvetica", 10)
    for _, row in df.iterrows():
        if y < 50:  # Start new page
            c.showPage()
            y = 800
            # Add header to new page
            header_y = y + 30
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, header_y, "SKU")
            c.drawString(150, header_y, "Product Name")
            c.drawString(400, header_y, "Current Price")
            c.drawString(500, header_y, "New Price")
            c.line(40, header_y - 5, 550, header_y - 5)
            c.setFont("Helvetica", 10)

        # Draw product information
        c.drawString(50, y, str(row['SKU']))
        c.drawString(150, y, str(row['Product Name']))
        c.drawString(400, y, f"₹{row['CURRENT PRICE']:.2f}")
        
        # Draw new price with different color if changed
        new_price = row['NEW PRICE']
        if new_price > 0:
            if new_price != row['CURRENT PRICE']:
                c.setFillColorRGB(1, 0, 0)  # Red for price changes
            c.drawString(500, y, f"₹{new_price:.2f}")
            c.setFillColorRGB(0, 0, 0)  # Reset to black
        else:
            c.drawString(500, y, "-")

        y -= 20

    c.save()

    print(f"✅ Generated {csv_out} and {pdf_out}")

    # -------------------------
    # 3. Log to Postgres
    # -------------------------
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
        )
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO price_update_log (batch_id, items_processed, csv_file, pdf_file, status, notes)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (batch_id, len(df), os.path.basename(csv_out), os.path.basename(pdf_out), "success", "Generated labels"),
        )
        conn.commit()
        cur.close()
        conn.close()
        print("📦 Logged update in Postgres")
    except Exception as e:
        print(f"⚠️ Failed to log in Postgres: {e}")

    # -------------------------
    # 4. Optional CMS sync
    # -------------------------
    if CMS_API_URL and CMS_API_KEY:
        try:
            response = requests.post(
                CMS_API_URL,
                headers={"Authorization": f"Bearer {CMS_API_KEY}"},
                json=df.to_dict(orient="records"),
                timeout=10,
            )
            if response.status_code == 200:
                print("🌐 Synced with CMS successfully")
            else:
                print(f"⚠️ CMS sync failed: {response.status_code} {response.text}")
        except Exception as e:
            print(f"⚠️ CMS sync error: {e}")


if __name__ == "__main__":
    generate_labels()
