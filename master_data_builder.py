from playwright.sync_api import sync_playwright
import pandas as pd
import os
import glob
import re

# -----------------------------
# LOAD MASTER DATABASE
# -----------------------------

master_file = "master_data.xlsx"

if os.path.exists(master_file):

    master_df = pd.read_excel(master_file)

else:

    master_df = pd.DataFrame(columns=[

        "Symbol",

        "Company_Name",

        "Price",

        "Market_Cap_Crore",

        "Shares_Crore",

        "Outstanding_Shares",

        "Finology_URL"
    ])

existing_symbols = set(
    master_df["Symbol"].astype(str).str.upper()
)

# -----------------------------
# GET LATEST NSE FILE
# -----------------------------

files = glob.glob("exports/*.xlsx")

latest_file = max(files, key=os.path.getctime)

print(f"\nUsing NSE file: {latest_file}")

nse_df = pd.read_excel(latest_file)

# -----------------------------
# GET SYMBOLS
# -----------------------------

symbols = nse_df.iloc[:, 0].astype(str).tolist()

# -----------------------------
# FILTER MISSING SYMBOLS
# -----------------------------

missing_symbols = [
    s for s in symbols
    if s.upper() not in existing_symbols
]

print("\nMissing Symbols:")
print(missing_symbols)

# -----------------------------
# PLAYWRIGHT SCRAPER
# -----------------------------

new_rows = []

unmatched_symbols = []

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    page = browser.new_page()

    # -----------------------------
    # FORCE DESKTOP VIEWPORT
    # -----------------------------

    page.set_viewport_size({
        "width": 1920,
        "height": 1080
    })

    # -----------------------------
    # OPEN FINOLOGY
    # -----------------------------

    page.goto(
        "https://ticker.finology.in/",
        timeout=120000
    )

    # FIXED WAIT INSTEAD OF NETWORKIDLE
    page.wait_for_timeout(10000)

    # -----------------------------
    # LOOP SYMBOLS
    # -----------------------------

    for symbol in missing_symbols:

        try:

            print("\n" + "=" * 50)
            print(f"Processing: {symbol}")

            # -----------------------------
            # WAIT PAGE STABLE
            # -----------------------------

            page.wait_for_timeout(5000)

            # -----------------------------
            # SEARCH BOX
            # -----------------------------

            search_box = page.locator(
                "input.form-control"
            ).first

            search_box.click()

            search_box.press("Control+A")

            search_box.press("Backspace")

            # -----------------------------
            # TYPE SYMBOL
            # -----------------------------

            search_box.type(
                symbol,
                delay=200
            )

            page.wait_for_timeout(4000)

            # -----------------------------
            # GET ALL LINKS
            # -----------------------------

            links = page.get_by_role("link")

            count = links.count()

            found = False

            pattern = rf"\bNSE:\s*{re.escape(symbol)}\b"

            for i in range(count):

                try:

                    text = links.nth(i).inner_text()

                    if re.search(pattern, text):

                        print("\nMATCH FOUND:")
                        print(text)

                        found = True

                        company_name = (
                            text.split("\n")[0]
                            .strip()
                        )

                        # -----------------------------
                        # CLICK RESULT
                        # -----------------------------

                        links.nth(i).click()

                        # FIXED WAIT
                        page.wait_for_timeout(7000)

                        print("\nCURRENT URL:")
                        print(page.url)

                        # -----------------------------
                        # PRICE EXTRACTION
                        # -----------------------------

                        price_block = page.locator(
                            "#mainContent_clsprice"
                        ).inner_text()

                        price_match = re.search(
                            r"[\d,]+\.\d+",
                            price_block
                        )

                        if not price_match:

                            print("Price Not Found")

                            break

                        price_text = price_match.group()

                        price = float(
                            price_text.replace(",", "")
                        )

                        print(f"\nPrice: {price}")

                        # -----------------------------
                        # RATIOS TEXT
                        # -----------------------------

                        ratios_text = page.locator(
                            "#mainContent_updAddRatios"
                        ).inner_text()

                        # -----------------------------
                        # MARKET CAP
                        # -----------------------------

                        market_match = re.search(
                            r"MARKET CAP\s*₹\s*([\d,\.]+)",
                            ratios_text
                        )

                        if market_match:

                            market_cap_text = (
                                market_match.group(1)
                            )

                            market_cap_crore = float(
                                market_cap_text
                                .replace(",", "")
                            )

                        else:

                            market_cap_crore = None

                        print(
                            f"Market Cap: "
                            f"{market_cap_crore}"
                        )

                        # -----------------------------
                        # SHARES EXTRACTION
                        # -----------------------------

                        shares_match = re.search(
                            r"NO\. OF SHARES\s*([\d,\.]+)\s*Cr",
                            ratios_text
                        )

                        if not shares_match:

                            print(
                                "NO. OF SHARES Not Found"
                            )

                            break

                        shares_crore_text = (
                            shares_match.group(1)
                        )

                        shares_crore = float(
                            shares_crore_text
                            .replace(",", "")
                        )

                        outstanding_shares = (
                            shares_crore * 10000000
                        )

                        print(
                            f"Outstanding Shares: "
                            f"{outstanding_shares}"
                        )

                        # -----------------------------
                        # SAVE ROW
                        # -----------------------------

                        new_rows.append({

                            "Symbol": symbol,

                            "Company_Name":
                                company_name,

                            "Price": price,

                            "Market_Cap_Crore":
                                market_cap_crore,

                            "Shares_Crore":
                                shares_crore,

                            "Outstanding_Shares":
                                outstanding_shares,

                            "Finology_URL":
                                page.url
                        })

                        # -----------------------------
                        # RETURN HOME
                        # -----------------------------

                        page.goto(
                            "https://ticker.finology.in/",
                            timeout=120000
                        )

                        # FIXED WAIT
                        page.wait_for_timeout(7000)

                        break

                except Exception as inner_error:

                    print(
                        f"\nInner Error for {symbol}"
                    )

                    print(inner_error)

            if not found:

                print(
                    f"\nNO MATCH FOUND FOR: "
                    f"{symbol}"
                )

                unmatched_symbols.append(symbol)

        except Exception as e:

            print(f"\nERROR for {symbol}")

            print(e)

    browser.close()

# -----------------------------
# SAVE MASTER DB
# -----------------------------

if new_rows:

    new_df = pd.DataFrame(new_rows)

    final_df = pd.concat(
        [master_df, new_df],
        ignore_index=True
    )

    final_df.to_excel(
        master_file,
        index=False
    )

    print("\nMASTER DB UPDATED")

else:

    print("\nNO NEW ROWS ADDED")

# -----------------------------
# SAVE UNMATCHED SYMBOLS
# -----------------------------

if unmatched_symbols:

    unmatched_df = pd.DataFrame({

        "Unmatched_Symbols":
            unmatched_symbols
    })

    unmatched_df.to_excel(
        "unmatched_symbols.xlsx",
        index=False
    )

    print(
        "\nUNMATCHED SYMBOLS SAVED"
    )