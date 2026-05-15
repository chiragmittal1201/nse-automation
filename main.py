from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime
import os

# Create exports folder
if not os.path.exists("exports"):
    os.makedirs("exports")

data = []

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False,
        args=["--start-minimized"]
    )

    page = browser.new_page()

    # Open NSE page
    page.goto(
        "https://www.nseindia.com/market-data/top-gainers-losers",
        timeout=120000
    )

    # Wait for full JS loading
    page.wait_for_timeout(15000)

    # SELECT: Securities < Rs 20
    page.select_option(
        "select",
        label="Securities < Rs 20"
    )

    print("Selected: Securities < Rs 20")

    # Wait for table reload
    page.wait_for_timeout(8000)

    # Wait for rows
    page.wait_for_selector(
        "table tbody tr",
        timeout=120000
    )

    # Get rows
    rows = page.locator("table tbody tr")

    row_count = rows.count()

    print("Rows Found:", row_count)

    # Extract data
    for i in range(row_count):

        cols = rows.nth(i).locator("td")

        row_data = []

        for j in range(cols.count()):

            text = cols.nth(j).inner_text()

            row_data.append(text)

        if row_data:
            data.append(row_data)

    browser.close()

# If no data
if not data:
    print("No data found")
    exit()

# Create dataframe
df = pd.DataFrame(data)

# Save Excel
today = datetime.now().strftime("%Y-%m-%d")

filename = f"exports/securities_below_20_{today}.xlsx"

df.to_excel(filename, index=False)

print("\nExcel Saved Successfully")
print("Saved:", filename)