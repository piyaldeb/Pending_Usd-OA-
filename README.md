# Pending_Usd-OA-

Automated Odoo report generation system that fetches pending slider count data and exports to Google Sheets.

## Features

- Automated data fetching from Odoo ERP system
- Scheduled execution via GitHub Actions (10am, 1pm, 4pm BDT)
- Direct export to Google Sheets
- Supports multiple companies (Zipper and Metal Trims)

## GitHub Actions Schedule

The workflow runs automatically at:
- **10:00 AM BDT** (4:00 AM UTC)
- **1:00 PM BDT** (7:00 AM UTC)
- **4:00 PM BDT** (10:00 AM UTC)

## Setup Instructions

### 1. Configure GitHub Secrets

Go to your repository settings: `Settings` → `Secrets and variables` → `Actions` → `New repository secret`

Add the following secrets:

#### ODOO Credentials
- **ODOO_URL**: `https://taps.odoo.com`
- **ODOO_DB**: `masbha-tex-taps-master-2093561`
- **ODOO_USERNAME**: `ranak@texzipperbd.com`
- **ODOO_PASSWORD**: `2326`

#### Google Service Account Credentials
- **GOOGLE_CREDENTIALS_JSON**: Copy the **entire JSON content** from your Google service account file

**For the Google credentials JSON:**

Copy the **entire content** of your Google service account JSON file (the one you downloaded from Google Cloud Console). It should contain fields like `type`, `project_id`, `private_key`, `client_email`, etc. Make sure to copy it exactly as-is, including all line breaks in the private key.

### 2. Verify Workflow

After setting up the secrets:
1. Go to the `Actions` tab in your repository
2. You should see the "Odoo Pending Slider Count Report" workflow
3. You can manually trigger it using "Run workflow" button to test

### 3. Google Sheets Access

Ensure your Google service account has edit access to the target Google Sheet:
- Sheet ID: `1mg4se7W0Mm2mEZYlxIVctofNJllCcpula4IQj0kuVCY`
- Share the sheet with your service account email (found in the `client_email` field of your Google credentials JSON)

## Local Development

### Prerequisites
- Python 3.11+
- pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/piyaldeb/Pending_Usd-OA-.git
cd Pending_Usd-OA-
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file:
```env
ODOO_URL=https://taps.odoo.com
ODOO_DB=masbha-tex-taps-master-2093561
ODOO_USERNAME=ranak@texzipperbd.com
ODOO_PASSWORD=2326
```

4. Add Google credentials file as `gcreds.json` in the root directory

5. Run the script:
```bash
python pending_slider_count.py
```

## Workflow Details

The GitHub Actions workflow ([.github/workflows/odoo-report.yml](.github/workflows/odoo-report.yml)):
- Runs on Ubuntu latest
- Sets up Python 3.11
- Installs dependencies from [requirements.txt](requirements.txt)
- Creates credentials from GitHub Secrets
- Executes the report generation script
- Uploads generated Excel files as artifacts (retained for 7 days)

## Output

The script generates:
- Excel files for each company
- Data is automatically pasted to Google Sheets
- Timestamps are added to track updates

## Troubleshooting

### Workflow fails with authentication error
- Verify all GitHub Secrets are correctly set
- Ensure the Google service account JSON is complete and valid

### No data in Google Sheets
- Check if the service account has edit permissions on the sheet
- Verify the Sheet ID matches in the script

### Manual trigger not working
- Go to Actions tab → Select the workflow → Click "Run workflow"

## License

MIT
