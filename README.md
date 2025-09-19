# Smart Price Updater

An automated workflow to update POS (Point of Sale) product prices daily.  
The system integrates with Google Sheets, processes price changes, updates records, generates CSV reports, sends notifications via email, and logs every update into a Postgres database.

---

## 📖 Features

- ⏰ **Daily Scheduling** – Automatically runs every 24 hours  
- 📊 **Google Sheets Integration** – Reads & updates POS price lists  
- 🔎 **Smart Price Parsing** – Detects and calculates price changes  
- 📂 **File Export** – Generates updated CSV files for distribution  
- 📧 **Email Notifications** – Sends updated price list to stakeholders  
- 🗄️ **Database Logging** – Inserts update records into Postgres for tracking  

---

## 🛠️ Tech Stack

- **n8n** – Workflow automation engine  
- **Docker & Docker Compose** – Containerized deployment  
- **Postgres** – Database for logging updates  
- **Google Sheets API** – For fetching and updating data  
- **Gmail API** – For sending email notifications  
- **Python** – Helper scripts (e.g., file handling)  
- **NGINX** – Reverse proxy (optional for deployment)  

---

## ⚙️ Setup Instructions

### 1. Clone the Repo
```bash
git clone https://github.com/ragavis-advantix/price-updater-automation.git
cd price-updater-automation
```


### 2. Start Services with Docker
```js
docker-compose up -d
```

### 3.Import Workflow into n8n
  - Open the n8n dashboard
  
  * Import My workflow.json
  
  + Configure credentials for:
  
    - Google Sheets
    
    * Gmail
    
    + Postgres

## 4.Verify Workflow
- Ensure database logs are updating

* Check that emails are being delivered with attachments

+ Confirm updated sheet values in Google Sheets

---

## 📝 Development Notes
- Customization:

    * Update docker-compose.yml for different DB credentials

    + Modify send_file.py if you want to change email formatting or attachments

- Scaling:

    * Additional nodes (e.g., Slack notifications, S3 storage) can be added in n8n

    + Can be deployed behind NGINX for secure remote access

- Testing:

    * Use test_prices.xlsx for sample data runs

    + Logs in Postgres help track workflow runs and debug issues

---
 
## 👨‍💻 Author
**Ragavi**


📧 Email: ragavis@advantixagi.com
