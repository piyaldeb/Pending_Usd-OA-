import requests
import json
import re
import logging
import sys
import os
from datetime import date, datetime, timedelta
import gspread
from gspread_dataframe import set_with_dataframe
from google.oauth2 import service_account
import pandas as pd
from dotenv import load_dotenv
from pathlib import Path
import time
load_dotenv()
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
log = logging.getLogger()

# ========= CONFIG ==========
ODOO_URL = os.getenv("ODOO_URL")
DB = os.getenv("ODOO_DB")
USERNAME = os.getenv("ODOO_USERNAME")
PASSWORD = os.getenv("ODOO_PASSWORD")

MODEL = "mrp.report.custom"
REPORT_BUTTON_METHOD = "action_generate_xlsx_report"
REPORT_TYPE = "r_invs"

# Google Sheets config
SHEET_ID = "1mg4se7W0Mm2mEZYlxIVctofNJllCcpula4IQj0kuVCY"
COMPANY_SHEETS = {
    1: {"sheet": "Zip-Order Summery_RAW"},
    3: {"sheet": "MT-Order Summery_RAW"},
}

COMPANIES = {
    1: "Zipper",
    3: "Metal Trims",
}

download_dir = "./downloads"
os.makedirs(download_dir, exist_ok=True)

# Google Sheets setup
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = service_account.Credentials.from_service_account_file('gcreds.json', scopes=scope)
client = gspread.authorize(creds)
print("✅ Google Sheets authorized")

# ========= START SESSION ==========
session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})

# ----------------------
# Step 1: Login
login_url = f"{ODOO_URL}/web/session/authenticate"
login_payload = {
    "jsonrpc": "2.0",
    "params": {
        "db": DB,
        "login": USERNAME,
        "password": PASSWORD
    }
}
resp = session.post(login_url, json=login_payload)
resp.raise_for_status()
uid = resp.json().get("result", {}).get("uid")
print("✅ Logged in, UID =", uid)

# ----------------------
def refresh_csrf():
    resp = session.get(f"{ODOO_URL}/web")
    match = re.search(r'var odoo = {\s*csrf_token: "([A-Za-z0-9]+)"', resp.text)
    return match.group(1) if match else None

# ----------------------
def get_date_range_for_company(company_id):
    """
    Determine date range based on sheet content:
    - If sheet is blank: April 1, 2024 to today
    - If last date in col A is yesterday: yesterday to today (append mode)
    - Otherwise: April 1, 2024 to today (full refresh)
    """
    today = date.today()
    yesterday = today - timedelta(days=1)
    default_start = date(2024, 4, 1)

    sheet_name = COMPANY_SHEETS[company_id]["sheet"]

    try:
        worksheet = client.open_by_key(SHEET_ID).worksheet(sheet_name)
        col_a_values = worksheet.col_values(1)  # Get all values in column A

        # Remove header if exists
        if col_a_values and len(col_a_values) > 1:
            data_values = col_a_values[1:]  # Skip header

            # Find last non-empty value
            last_date_str = None
            for val in reversed(data_values):
                if val and val.strip():
                    last_date_str = val.strip()
                    break

            if last_date_str:
                # Try to parse the last date
                try:
                    # Try different date formats
                    for fmt in ["%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%d/%m/%Y"]:
                        try:
                            last_date = datetime.strptime(last_date_str, fmt).date()
                            break
                        except ValueError:
                            continue
                    else:
                        # Could not parse date, use default
                        print(f"⚠️ Could not parse date '{last_date_str}', using full range")
                        return default_start.isoformat(), today.isoformat(), False

                    # Check if last date is yesterday
                    if last_date == yesterday:
                        print(f"📅 Last date is yesterday ({yesterday}), fetching today only (append mode)")
                        return today.isoformat(), today.isoformat(), True
                    else:
                        print(f"📅 Last date is {last_date}, fetching full range")
                        return default_start.isoformat(), today.isoformat(), False

                except Exception as e:
                    print(f"⚠️ Error parsing date: {e}, using full range")
                    return default_start.isoformat(), today.isoformat(), False
            else:
                # No data in column A
                print(f"📅 Sheet is empty, fetching full range from April 1, 2024")
                return default_start.isoformat(), today.isoformat(), False
        else:
            # Sheet is blank or only has header
            print(f"📅 Sheet is blank, fetching full range from April 1, 2024")
            return default_start.isoformat(), today.isoformat(), False

    except Exception as e:
        print(f"⚠️ Error checking sheet: {e}, using full range")
        return default_start.isoformat(), today.isoformat(), False

# ----------------------
# Main loop for companies
for company_id, cname in COMPANIES.items():
    print(f"\n🔹 Processing company: {cname} (ID={company_id})")

    # Get date range based on sheet content
    FROM_DATE, TO_DATE, append_mode = get_date_range_for_company(company_id)
    log.info(f"Using FROM_DATE={FROM_DATE}, TO_DATE={TO_DATE}, append_mode={append_mode}")

    # Create wizard
    create_url = f"{ODOO_URL}/web/dataset/call_kw/{MODEL}/create"
    create_payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "model": MODEL,
            "method": "create",
            "args": [{}],
            "kwargs": {"context": {"uid": uid}}
        }
    }
    resp = session.post(create_url, json=create_payload)
    resp.raise_for_status()
    wizard_id = resp.json().get("result")
    print("✅ Wizard created, ID =", wizard_id)

    # Save wizard
    save_url = f"{ODOO_URL}/web/dataset/call_kw/{MODEL}/web_save"
    save_payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "model": MODEL,
            "method": "web_save",
            "args": [[], {"report_type": REPORT_TYPE, "date_from": FROM_DATE, "date_to": TO_DATE}],
            "kwargs": {
                "context": {
                    "lang": "en_US",
                    "tz": "Asia/Dhaka",
                    "uid": uid,
                    "allowed_company_ids": [company_id]
                },
                "specification": {"report_type": {}, "date_from": {}, "date_to": {}}
            }
        }
    }
    resp = session.post(save_url, json=save_payload)
    resp.raise_for_status()
    wizard_id = resp.json().get("result", [{}])[0].get("id")
    print("✅ Wizard saved, ID =", wizard_id)

    # Call report button
    button_url = f"{ODOO_URL}/web/dataset/call_button"
    button_payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "model": MODEL,
            "method": REPORT_BUTTON_METHOD,
            "args": [[wizard_id]],
            "kwargs": {
                "context": {
                    "lang": "en_US",
                    "tz": "Asia/Dhaka",
                    "uid": uid,
                    "allowed_company_ids": [company_id]
                }
            }
        }
    }
    resp = session.post(button_url, json=button_payload)
    resp.raise_for_status()
    report_info = resp.json().get("result")
    print("✅ Report info received for", cname)

    csrf_token = refresh_csrf()
    if company_id == 1:  # Zipper
        time.sleep(10)

    options = {"date_from": FROM_DATE, "date_to": TO_DATE, "company_id": company_id}
    context = {
        "lang": "en_US",
        "tz": "Asia/Dhaka",
        "uid": uid,
        "allowed_company_ids": [company_id],
        "active_model": MODEL,
        "active_id": wizard_id,
        "active_ids": [wizard_id]
    }

    REPORT_TEMPLATE = report_info.get("report_name") or "taps_manufacturing.pi_xls_template"
    report_path = f"/report/xlsx/{REPORT_TEMPLATE}?options={json.dumps(options)}&context={json.dumps(context)}"
    download_payload = {
        "data": json.dumps([report_path, "xlsx"]),
        "context": json.dumps(context),
        "token": "dummy-because-api-expects-one",
        "csrf_token": csrf_token
    }

    download_url = f"{ODOO_URL}/report/download"
    headers = {"X-CSRF-Token": csrf_token, "Referer": f"{ODOO_URL}/web"}

    try:
        resp = session.post(download_url, data=download_payload, headers=headers, timeout=60)
        if resp.status_code == 200 and "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in resp.headers.get("content-type", ""):
            filename = Path(download_dir) / f"{cname.replace(' ', '_')}_{REPORT_TYPE}_{FROM_DATE}_to_{TO_DATE}.xlsx"
            with open(filename, "wb") as f:
                f.write(resp.content)
            print(f"✅ Report downloaded for {cname}: {filename}")

            # === Load file and extract VALUE sheets only (even indexed sheets: 1, 3, 5, ...) ===
            try:
                xl = pd.ExcelFile(filename)
                sheet_names = xl.sheet_names
                print(f"📊 Excel has {len(sheet_names)} sheets: {sheet_names}")

                # Collect all value sheets (even indexed = 1, 3, 5, ... which are 2nd, 4th, 6th sheets)
                # These are the VALUE sheets (odd index = quantity, even index = value)
                all_value_data = []

                for i, sheet_name in enumerate(sheet_names):
                    # Even index (1, 3, 5...) = Value sheets
                    if i % 2 == 1:  # 1, 3, 5, 7... (0-indexed, so these are 2nd, 4th, 6th sheets)
                        df = pd.read_excel(filename, sheet_name=i)
                        if not df.empty:
                            all_value_data.append(df)
                            print(f"  ✅ Loaded VALUE sheet: {sheet_name} (index {i})")
                        else:
                            print(f"  ⚠️ Empty VALUE sheet: {sheet_name}")

                if all_value_data:
                    # Concatenate all value dataframes
                    combined_df = pd.concat(all_value_data, ignore_index=True)
                    print(f"📊 Combined {len(all_value_data)} value sheets, total rows: {len(combined_df)}")

                    # Get target worksheet
                    sheet_cfg = COMPANY_SHEETS[company_id]
                    worksheet = client.open_by_key(SHEET_ID).worksheet(sheet_cfg["sheet"])

                    if append_mode:
                        # Append after yesterday's row
                        existing_data = worksheet.get_all_values()
                        next_row = len(existing_data) + 1
                        set_with_dataframe(worksheet, combined_df, row=next_row, col=1, include_index=False, include_column_header=False)
                        print(f"✅ Appended {len(combined_df)} rows to {sheet_cfg['sheet']} starting at row {next_row}")
                    else:
                        # Clear and paste full data
                        worksheet.clear()
                        set_with_dataframe(worksheet, combined_df, row=1, col=1, include_index=False, include_column_header=True)
                        print(f"✅ Full data pasted to {sheet_cfg['sheet']}, {len(combined_df)} rows")
                else:
                    print(f"⚠️ No value data found for {cname}")

            except Exception as e:
                print(f"❌ Exception during data extraction/paste for {cname}: {e}")

        else:
            print(f"❌ Failed to download report for {cname}, status={resp.status_code}")
    except Exception as e:
        print(f"❌ Exception during download/paste for {cname}: {e}")
