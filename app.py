from flask import Flask, render_template, request, redirect, url_for, flash
from flask_migrate import Migrate
from config import Config
from database import init_db, db
from models import Team, Player
from tasks.webscraper import update_live_data, update_stats
import json 

# Initialize Flask App
app = Flask(__name__, template_folder='templates')
app.config.from_object(Config)

# Initialize the database with Flask
init_db(app)

# Initialize Flask-Migrate for schema migrations
migrate = Migrate(app, db)

import pandas as pd

def load_players_from_csv(csv_file_path="players.csv"):
    try:
        # Read the CSV file into a pandas DataFrame
        df = pd.read_csv(csv_file_path)
        
        # Extract the 'players' column into a list
        player_list = df['players'].tolist()
        
        print(f"Successfully loaded {len(player_list)} players from '{csv_file_path}'.")
        return player_list
    except FileNotFoundError:
        print(f"Error: The file '{csv_file_path}' was not found.")
        raise  # Re-raise the FileNotFoundError
    except KeyError:
        print(f"Error: The CSV file does not have a column named 'players'.")
        raise  # Re-raise the KeyError
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise  # Re-raise any other unexpected errors

# Homepage with visualizations
@app.route("/")
def home():
    # Fetch all teams from the database
    teams = Team.query.all()

    # Sort teams by total points (descending)
    sorted_teams = sorted(teams, key=lambda t: t.total_player_points, reverse=True)

    # Debugging: Print team and player points
    for team in sorted_teams:
        print(f"Team: {team.name}, Total Points: {team.total_player_points}")
        for player in sorted(team.players, key=lambda p: p.total_points, reverse=True):  # Sort players within teams
            print(f"  Player: {player.name}, Runs: {player.runs}, SR: {player.strike_rate}, Wickets: {player.wickets}, Econ: {player.economy}, Total Points: {player.total_points}")

    # Prepare visualization data for Chart.js
    visualization_data = {
        "teams": [team.name for team in sorted_teams],
        "totals": [team.total_player_points for team in sorted_teams],
    }

    # Pass sorted teams and visualization data to the template
    return render_template("home.html", teams=sorted_teams, visualization_data=visualization_data)



# Route for adding teams and assigning players to them
@app.route("/add_teams", methods=["GET", "POST"])
def add_teams():
    if request.method == "POST":
        # Get form data
        team_name = request.form.get("team_name")
        selected_players_json = request.form.get("selected_players")

        # Try to parse the JSON of selected players
        try:
            player_names = json.loads(selected_players_json) if selected_players_json else []
        except json.JSONDecodeError:
            player_names = []

        # Input validation
        if not team_name or not player_names:
            flash("Team name and players are required.", "danger")
            return redirect(url_for("add_teams"))

        # Check if the team already exists
        existing_team = Team.query.filter_by(name=team_name).first()
        if existing_team:
            flash(f"Team {team_name} already exists!", "danger")
            return redirect(url_for("add_teams"))

        # Create and save new team
        team = Team(name=team_name)
        db.session.add(team)

        # Add selected players to the team
        for player_name in player_names:
            player = Player(name=player_name, team=team)
            db.session.add(player)

        db.session.commit()
        flash(f"Team {team_name} added successfully!", "success")
        return redirect(url_for("add_teams"))

    # Fetch all teams from the database
    teams = Team.query.options(db.joinedload(Team.players)).all()

    # Fixed list of players to choose from
    fixed_players_list = load_players_from_csv()

    return render_template("add_teams.html", fixed_players_list=fixed_players_list, teams=teams)


@app.route("/delete_team/<int:team_id>", methods=["POST"])
def delete_team(team_id):
    team = Team.query.get(team_id)
    if team:
        db.session.delete(team)
        db.session.commit()
        flash(f"Team {team.name} has been deleted.", "success")
    else:
        flash("Team not found!", "danger")
    return redirect(url_for("add_teams"))



# Route for showing points for each team and updating stats
import threading
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash
from models import Player, db


@app.route("/edit_team/<int:team_id>", methods=["GET", "POST"])
def edit_team(team_id):
    team = Team.query.get_or_404(team_id)

    if request.method == "POST":
        team_name = request.form.get("team_name")
        selected_players_json = request.form.get("selected_players")

        try:
            player_names = json.loads(selected_players_json) if selected_players_json else []
        except json.JSONDecodeError:
            player_names = []

        if not team_name or not player_names:
            flash("Team name and players are required.", "danger")
            return redirect(url_for("edit_team", team_id=team_id))

        # Update team name
        team.name = team_name

        # Fetch current players assigned to the team
        existing_players = {player.name: player for player in team.players}

        # Players that should be assigned to the team
        new_players = []
        for player_name in player_names:
            if player_name in existing_players:
                # Player already in the team, keep them
                new_players.append(existing_players[player_name])
            else:
                # Check if player exists elsewhere
                player = Player.query.filter_by(name=player_name).first()
                if player:
                    if player.team_id:  
                        flash(f"Player {player_name} is already in another team!", "danger")
                        return redirect(url_for("edit_team", team_id=team_id))
                    else:
                        player.team_id = team_id  # Assign to this team
                else:
                    player = Player(name=player_name, team_id=team_id)  # Create new player
                    db.session.add(player)
                
                new_players.append(player)

        # Remove players no longer in the team
        removed_players = [p for p in existing_players.values() if p.name not in player_names]
        for player in removed_players:
            # Check if the player is in any other team
            other_teams_count = Player.query.filter(Player.name == player.name, Player.team_id != team_id).count()
            if other_teams_count == 0:
                db.session.delete(player)  # Delete player from database
            else:
                player.team_id = None  # Unassign player from this team (if model allows NULL)

        # Update team's players
        team.players = new_players

        db.session.commit()
        flash(f"Team {team_name} updated successfully!", "success")
        return redirect(url_for("edit_team", team_id=team_id))

    # Fetch current players
    current_players = [player.name for player in team.players]

    # Fixed list of players
    fixed_players_list = load_players_from_csv()

    return render_template("edit_team.html", 
                           team=team, 
                           current_players=current_players, 
                           fixed_players_list=fixed_players_list)



@app.route('/show_points', methods=['GET', 'POST'])
def show_points():
    if request.method == 'POST':
        if 'update_live_data' in request.form:
            update_live_data()  # Function to update from API
        elif 'update_from_csv' in request.form:
            update_stats()  # Function to update from CSV

        # Redirect to avoid form resubmission on refresh & add success flag
        return redirect(url_for('show_points', update_success=True))

    # Fetch teams & players for display
    teams = Team.query.all()
    return render_template('show_points.html', teams=teams)



# Run the Flask application
if __name__ == "__main__":
    app.run(debug=True)