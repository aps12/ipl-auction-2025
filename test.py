import csv
from models import Player, db

csv_file = "ipl_combined_stats_2025.csv"
print(f"Updating stats from {csv_file}...")

try:
    with open(csv_file, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            player_name = row["Player"].strip()
            print(player_name)
            # Convert values safely (float first, then int if needed)
            runs = int(float(row["Runs"])) if row["Runs"] else 0
            strike_rate = float(row["SR"]) if row["SR"] else 0.0
            wickets = int(float(row["Wkts"])) if row["Wkts"] else 0
            economy = float(row["Econ"]) if row["Econ"] else 0.0

            print(f"Player: {player_name}, Runs: {runs}, SR: {strike_rate}, Wickets: {wickets}, Econ: {economy}")

            # Find player in DB
            player = Player.query.filter_by(name=player_name).first()
            
            if player:
                player.runs = runs
                player.strike_rate = strike_rate
                player.wickets = wickets
                player.economy = economy
                print(f"✅ Updated stats for {player_name}")
            
    db.session.commit()
    print("✅ Player stats updated successfully!")
except Exception as e:
    print(f"❌ Error updating stats: {e}")
