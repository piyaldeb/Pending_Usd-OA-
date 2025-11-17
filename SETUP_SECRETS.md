# GitHub Secrets Setup Guide

Follow these steps to configure GitHub Secrets for the automated workflow:

## Step-by-Step Instructions

### 1. Navigate to Repository Settings
1. Go to https://github.com/piyaldeb/Pending_Usd-OA-
2. Click on **Settings** tab (top right)
3. In the left sidebar, click **Secrets and variables** → **Actions**

### 2. Add Each Secret

Click the **New repository secret** button and add the following secrets one by one:

---

#### Secret 1: ODOO_URL
- **Name**: `ODOO_URL`
- **Value**: `https://taps.odoo.com`

---

#### Secret 2: ODOO_DB
- **Name**: `ODOO_DB`
- **Value**: `masbha-tex-taps-master-2093561`

---

#### Secret 3: ODOO_USERNAME
- **Name**: `ODOO_USERNAME`
- **Value**: `ranak@texzipperbd.com`

---

#### Secret 4: ODOO_PASSWORD
- **Name**: `ODOO_PASSWORD`
- **Value**: `2326`

---

#### Secret 5: GOOGLE_CREDENTIALS_JSON
- **Name**: `GOOGLE_CREDENTIALS_JSON`
- **Value**: Copy the **ENTIRE** content from your Google service account JSON file

**Important for Google Credentials:**
1. Open your Google service account JSON file (e.g., `genuine-citron-445708-e6-ae49be462a95.json`)
2. Select **ALL** the content (Ctrl+A)
3. Copy it (Ctrl+C)
4. Paste it into the Value field
5. Make sure the JSON is complete with all curly braces `{` and `}`

The JSON should start with:
```
{
  "type": "service_account",
  "project_id": "...",
```

And end with:
```
  "universe_domain": "googleapis.com"
}
```

---

### 3. Verify All Secrets Are Added

After adding all 5 secrets, you should see them listed:
- ✅ ODOO_URL
- ✅ ODOO_DB
- ✅ ODOO_USERNAME
- ✅ ODOO_PASSWORD
- ✅ GOOGLE_CREDENTIALS_JSON

### 4. Test the Workflow

1. Go to the **Actions** tab in your repository
2. Click on "Odoo Pending Slider Count Report" workflow
3. Click **Run workflow** button (on the right)
4. Select the `main` branch
5. Click **Run workflow**

The workflow should start running. You can monitor its progress in real-time.

### 5. Check Google Sheets Access

Make sure your Google Sheet is shared with the service account:
1. Open your Google Sheet: https://docs.google.com/spreadsheets/d/1mg4se7W0Mm2mEZYlxIVctofNJllCcpula4IQj0kuVCY
2. Click **Share** button
3. Add the service account email (found in `client_email` field of your Google JSON)
4. Grant **Editor** access

## Automated Schedule

Once configured, the workflow will run automatically at:
- **10:00 AM Bangladesh Time** (4:00 AM UTC)
- **1:00 PM Bangladesh Time** (7:00 AM UTC)
- **4:00 PM Bangladesh Time** (10:00 AM UTC)

## Troubleshooting

### Workflow fails immediately
- Check that all 5 secrets are added correctly
- Verify secret names match exactly (case-sensitive)

### Authentication errors
- Double-check the GOOGLE_CREDENTIALS_JSON is the complete JSON
- Ensure no extra spaces or characters were added

### No data in Google Sheets
- Verify the service account has Editor access to the sheet
- Check the Sheet ID in the script matches your sheet

### Need Help?
- Check the workflow logs in the Actions tab
- Review the README.md for more details
- Ensure your Google credentials file has the necessary API permissions

## Next Steps

After setup is complete:
1. Monitor the first automated run
2. Check Google Sheets for updated data
3. Verify timestamps are being updated
4. Review downloaded Excel files in the Actions artifacts (if needed)
