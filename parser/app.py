from flask import Flask, request, jsonify
import pandas as pd
import psycopg2
from datetime import datetime
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Database configuration
DB_HOST = "postgres"
DB_PORT = 5432
DB_NAME = "priceupdater"
DB_USER = "n8n"
DB_PASS = "n8npass"

def get_db_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT
    )

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route("/parse", methods=["POST"])
def parse_prices():
    """Parse price data from various formats and update the system"""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        # Read directly from the file object without saving
        df = pd.read_csv(file.stream)

        # Validate required columns
        required_cols = {"SKU", "Product Name", "CURRENT PRICE", "NEW PRICE"}
        if not required_cols.issubset(df.columns):
            return jsonify({
                "error": "Invalid file format",
                "message": f"Required columns: {required_cols}"
            }), 400

        # Ensure numeric price columns
        df["CURRENT PRICE"] = pd.to_numeric(df["CURRENT PRICE"], errors="coerce")
        df["NEW PRICE"] = pd.to_numeric(df["NEW PRICE"], errors="coerce")

        # Fill NaN values with 0 in NEW PRICE
        df["NEW PRICE"] = df["NEW PRICE"].fillna(0)

        try:
            # Log the working directory and data path
            logger.info(f"Working directory: {os.getcwd()}")
            logger.info(f"Data directory contents: {os.listdir('/app/data')}")
            
            # Save to data directory with full path
            # Create a temporary file with unique name
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            output_path = os.path.join("/app/data", f"price_update_{timestamp}.csv")
            logger.info(f"Attempting to save file to: {output_path}")
            
            # Save the file
            df.to_csv(output_path, index=False, mode='w')
            logger.info("File saved successfully")

        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            return jsonify({
                "error": "Processing failed",
                "message": f"Could not save output file: {str(e)}"
            }), 500

        # Log to database
        conn = get_db_connection()
        cur = conn.cursor()
        
        timestamp = datetime.now()
        batch_id = f"parse-{timestamp.strftime('%Y%m%d-%H%M%S')}"
        
        cur.execute(
            """
            INSERT INTO price_update_log 
            (batch_id, timestamp, items_processed, status, notes)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (batch_id, timestamp, len(df), "success", f"Parsed {file.filename}")
        )
        
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({
            "message": "File processed successfully",
            "items_processed": len(df),
            "batch_id": batch_id
        })

    except Exception as e:
        logger.error(f"Error in parse_prices: {str(e)}")
        return jsonify({
            "error": "Processing failed",
            "message": str(e)
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
