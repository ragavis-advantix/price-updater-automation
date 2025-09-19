import requests

url = "http://localhost:5678/webhook-test/price-update"

# Path to your real dummy data file
file_path = r"C:\Users\advantix-user-003\Documents\Price Updater - Task 1\data\pos_prices.csv"

files = {"file": open(file_path, "rb")}

response = requests.post(url, files=files)
print(response.text)
