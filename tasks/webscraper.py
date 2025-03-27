import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager



def update_database_from_live_data(merged_df):
    """Updates the database with IPL stats from live data."""
    
    from app import app
    from models import Player, Team, db
    import pandas as pd

    with app.app_context():
        try:
            for _, row in merged_df.iterrows():
                # 🔹 Extract player name from CSV
                player_name = row["Player"].strip()

                # 🔹 Find the player in DB to get the team
                player = Player.query.filter(Player.name.ilike(player_name)).first()

                if not player:
                    print(f"⚠️ Skipping {player_name}: Player not found in DB.")
                    continue

                # 🔹 Get player's team from the database
                team_id = player.team_id
                team = Team.query.get(team_id) if team_id else None
                team_name = team.name if team else "Unknown"

                # 🔹 Extract numerical stats safely
                try:
                    runs = int(float(row["Runs"])) if pd.notna(row["Runs"]) else 0
                    strike_rate = float(row["SR"]) if pd.notna(row["SR"]) else 0.0
                    wickets = int(float(row["Wkts"])) if pd.notna(row["Wkts"]) else 0
                    economy = float(row["Econ"]) if pd.notna(row["Econ"]) else 0.0
                except ValueError:
                    print(f"⚠️ Invalid data for {player_name}, skipping row.")
                    continue

                # 🔹 Update player stats
                player.runs = runs
                player.strike_rate = strike_rate
                player.wickets = wickets
                player.economy = economy

                print(f"✅ Updated stats for {player_name} (Team: {team_name})")

            # 🔹 Commit all changes
            db.session.commit()
            print("✅ Live data updated successfully in the database!")

        except Exception as e:
            # 🔹 Comprehensive error handling
            db.session.rollback()  # Rollback on error
            print(f"❌ Error updating database: {e}")
            # Optionally, you could log the full traceback for debugging
            import traceback
            traceback.print_exc()



def update_live_data():
    """Fetch live IPL data, update the database, and save to CSV."""
    def get_ipl_stats(stat_type):
        """Scrape IPL 2025 Batting or Bowling stats in headless mode."""

        # options = webdriver.ChromeOptions()
        # options.add_argument("--headless=new")  # New headless mode
        # options.add_argument("--disable-gpu")
        # options.add_argument("--no-sandbox")
        # options.add_argument("--disable-dev-shm-usage")
        # options.add_argument("--window-size=1920,1080")  
        # options.add_argument("--disable-blink-features=AutomationControlled")  # Bypass bot detection
        # options.add_argument("--log-level=3")  # Suppress logs

        # # Add user agent to appear more like a real browser
        # options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        # # Experimental options to improve headless reliability
        # options.add_experimental_option("excludeSwitches", ["enable-automation"])
        # options.add_experimental_option('useAutomationExtension', False)

        # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager

        def setup_chrome_driver():
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            return driver
        
        driver = setup_chrome_driver()
        driver.implicitly_wait(30)  # Adjust wait time as needed

        try:
            driver.get("https://www.iplt20.com/stats/2024")

            # Wait until the page loads
            time.sleep(3)
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "statsTable"))
            )
            print("✅ IPL Stats page loaded!")

            if stat_type == "Bowling":
                try:
                    time.sleep(2)
                    dropdown = WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable((By.XPATH, "//div[@class='customSelecBox statsTypeFilter']"))
                    )
                    dropdown.click()
                    time.sleep(2)

                    bowler_option = WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable((By.XPATH, "//span[@class='cSBListFItems bowFItem']"))
                    )
                    bowler_option.click()
                    time.sleep(2)

                    WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable((By.XPATH, "//div[@class='cSBListItems bowlers ng-binding ng-scope selected'][1]"))
                    ).click()
                    print("✅ Switched to Bowling Stats")

                except Exception as e:
                    print(f"⚠️ Error selecting Bowling Stats: {e}")

            # Click on "View All"
            try:
                if stat_type == "Bowling":
                    time.sleep(4)
                    view_all_button = WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located((By.XPATH, "//div[@id='bowlingTAB']//a[contains(text(),'View All')]"))
                    )
                    driver.execute_script("arguments[0].scrollIntoView(true);", view_all_button)
                    driver.execute_script("arguments[0].click();", view_all_button)
                    time.sleep(4)
                    print("✅ Clicked 'View All' for Bowling stats.")
                else:
                    time.sleep(4)
                    view_all_button = WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located((By.XPATH, "//a[contains(@ng-click, 'showAllBattingStatsList()')]"))
                    )
                    driver.execute_script("arguments[0].scrollIntoView(true);", view_all_button)
                    driver.execute_script("arguments[0].click();", view_all_button)

                time.sleep(4)
                print("✅ Clicked 'View All' for stats.")

                # Wait for stats table to fully load
                WebDriverWait(driver, 40).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "st-table"))
                )
            except Exception as e:
                print(f"⚠️ Error clicking 'View All': {e}")

            # Scrape stats
            soup = BeautifulSoup(driver.page_source, "html.parser")
            table = soup.find("table", class_="st-table statsTable ng-scope")

            if not table:
                print(f"❌ No table found for {stat_type}! Taking screenshot for debugging.")
                driver.save_screenshot("debug_screenshot.png")
                driver.quit()
                return None

            headers = [th.get_text(strip=True) for th in table.find_all("th")]

            rows = []
            for tr in table.find_all("tr")[1:]:
                row = [td.get_text(strip=True) for td in tr.find_all("td")]
                if row:
                    rows.append(row)

            driver.quit()

            df = pd.DataFrame(rows, columns=headers)
            return df

        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            driver.quit()
            return None

    batting_df = get_ipl_stats("Batting")
    bowling_df = get_ipl_stats("Bowling")

    if batting_df is None or bowling_df is None:
        print("❌ Failed to fetch data")

    batting_cols = ["Player", "Runs", "SR"]
    bowling_cols = ["Player", "Wkts", "Econ"]

    batting_df = batting_df[batting_cols]
    bowling_df = bowling_df[bowling_cols]

    merged_df = pd.merge(batting_df, bowling_df, on="Player", how="outer")

    def clean_player_names_in_dataframe(merged_df):
        """
        Remove team abbreviations from the Player column in the DataFrame
        
        Parameters:
        merged_df (pd.DataFrame): Input DataFrame with Player column
        
        Returns:
        pd.DataFrame: DataFrame with cleaned player names
        """
        # List of team abbreviations to remove
        team_abbrevs = ['SRH', 'LSG', 'KKR', 'PBKS', 'DC', 'RCB', 'GT', 'MI', 'CSK', 'RR']
        
        # Create a copy of the DataFrame to avoid modifying the original
        df = merged_df.copy()
        
        # Function to clean individual player name
        def clean_name(name):
            # Remove team abbreviations
            cleaned_name = name
            for abbrev in team_abbrevs:
                cleaned_name = cleaned_name.replace(abbrev, '').strip()
            return cleaned_name
        
        # Apply cleaning to the Player column
        df['Player'] = df['Player'].apply(clean_name)
        
        return df
    merged_df_clean = clean_player_names_in_dataframe(merged_df)
    merged_df_clean.to_csv("ipl_combined_stats_2025.csv", index=False)
    print("✅ Merged stats saved to ipl_combined_stats_2025.csv")



    update_database_from_live_data(merged_df_clean)


def update_stats():
    import csv
    from app import app  
    from models import Player, Team, db

    """Read stats from CSV and update the database."""
    csv_file = "ipl_combined_stats_2025.csv"
    print(f"📊 Updating stats from {csv_file}...")

    try:
        with app.app_context():
            with open(csv_file, "r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:

                    # 🔹 Extract player name from CSV
                    player_name = row["Player"].strip()

                    # 🔹 Find the player in DB to get the team
                    player = Player.query.filter(Player.name.ilike(player_name)).first()

                    if not player:
                        print(f"⚠️ Skipping {player_name}: Player not found in DB.")
                        continue

                    # 🔹 Get player's team from the database
                    team_id = player.team_id
                    team = Team.query.get(team_id) if team_id else None
                    team_name = team.name if team else "Unknown"

                    print(f"✅ Found {player_name} in DB, Team: {team_name}")

                    # 🔹 Extract numerical stats safely
                    try:
                        runs = int(float(row["Runs"])) if row["Runs"].strip() else 0
                        strike_rate = float(row["SR"]) if row["SR"].strip() else 0.0
                        wickets = int(float(row["Wkts"])) if row["Wkts"].strip() else 0
                        economy = float(row["Econ"]) if row["Econ"].strip() else 0.0
                    except ValueError:
                        print(f"⚠️ Invalid data for {player_name}, skipping row.")
                        continue

                    # 🔹 Update player stats
                    player.runs = runs
                    player.strike_rate = strike_rate
                    player.wickets = wickets
                    player.economy = economy

                    print(f"✅ Updated stats for {player_name} ({team_name})")

                db.session.commit()
                print("✅ Player stats updated successfully!")

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error updating stats: {e}")
