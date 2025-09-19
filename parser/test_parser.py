import requests
import os

def test_parser_service():
    # URL of the parser service
    url = 'http://localhost:5000/parse'
    
    # Path to the CSV file
    file_path = os.path.join('data', 'pos_prices.csv')
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return
    
    try:
        # Open the file and create the files parameter for the request
        with open(file_path, 'rb') as file:
            files = {'file': ('pos_prices.csv', file, 'text/csv')}
            
            # Send POST request
            print(f"Sending file {file_path} to {url}...")
            response = requests.post(url, files=files)
            
            # Print response
            print("\nResponse status:", response.status_code)
            print("Response body:", response.json())
            
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == '__main__':
    test_parser_service()