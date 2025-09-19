import os
import time
import hashlib
from generate_labels import generate_labels

def get_file_hash(filepath):
    """Calculate MD5 hash of file contents"""
    if not os.path.exists(filepath):
        return None
    
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def watch_for_changes():
    """Watch for changes in the input file and generate labels only when it changes"""
    input_file = "data/pos_prices.csv"
    print("🔍 Starting to watch for changes...")
    print(f"👀 Watching file: {input_file}")
    last_hash = None

    # Initial check
    if os.path.exists(input_file):
        print(f"📄 Found input file: {input_file}")
        generate_labels()
    
    while True:
        current_hash = get_file_hash(input_file)
        
        if current_hash != last_hash:
            if current_hash is not None:  # File exists
                print(f"💡 Changes detected in {input_file}")
                generate_labels()
                last_hash = current_hash
            time.sleep(2)  # Wait a bit to ensure file is fully written
        
        time.sleep(5)  # Check every 5 seconds

if __name__ == "__main__":
    print("🔍 Watching for changes in POS prices file...")
    watch_for_changes()