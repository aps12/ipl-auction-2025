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
    fixed_players_list =  [
    "Abdul Samad", "Abhinav Manohar", "Abhishek Sharma", "Abishek Porel", "Aiden Markram", "Ajinkya Rahane", "Akash Deep", "Akash Madhwal", "Alzarri Joseph", "Amit Mishra", "Andre Russell", "Angkrish Raghuvanshi", "Anmolpreet Singh", "Anrich Nortje", "Anshul Kamboj", "Anuj Rawat", "Anukul Roy", "Arshad Khan", "Arshdeep Singh", "Arshin Atul Kulkarni", "Ashton Turner", "Ashutosh Sharma", "Atharva Taide", "Avesh Khan", "Axar Patel", "Ayush Badoni", "Azmatullah Omarzai", "B R Sharath", "Bhuvneshwar Kumar", "Cameron Green", "Darshan Nalkande", "Daryl Mitchell", "David Miller", "David Warner", "Deepak Chahar", "Deepak Hooda", "Devdutt Padikkal", "Dewald Brevis", "Dhruv Jurel", "Dinesh Karthik", "Donovan Ferreira", "Faf Du Plessis", "Gerald Coetzee", "Glenn Maxwell", "Gulbadin Naib", "Hardik Pandya", "Harpreet Bhatia", "Harpreet Brar", "Harshal Patel", "Harshit Rana", "Heinrich Klaasen", "Ishan Kishan", "Ishant Sharma", "Jake Fraser - McGurk", "Jasprit Bumrah", "Jaydev Unadkat", "Jhye Richardson", "Jitesh Sharma", "Jonny Bairstow", "Jos Buttler", "Josh Little", "K L Rahul", "Kagiso Rabada", "Kane Williamson", "Karn Sharma", "Keshav Maharaj", "Khaleel Ahmed", "Krunal Pandya", "Kuldeep Sen", "Kuldeep Yadav", "Kumar Kushagra", "Kwena Maphaka", "Lalit Yadav", "Liam Livingstone", "Lizaad Williams", "Lockie Ferguson", "Luke Wood", "M Siddharth", "MS Dhoni", "Maheesh Theekshana", "Mahipal Lomror", "Manav Suthar", "Manish Pandey", "Marco Jansen", "Marcus Stoinis", "Matheesha Pathirana", "Matt Henry", "Matthew Wade", "Mayank Agarwal", "Mayank Dagar", "Mayank Markande", "Mayank Yadav", "Mitchell Marsh", "Mitchell Santner", "Mitchell Starc", "Moeen Ali", "Mohammad Nabi", "Mohammed Siraj", "Mohit Sharma", "Mohsin Khan", "Mukesh Kumar", "Mustafizur Rahman", "Naman Dhir", "Nandre Burger", "Nathan Ellis", "Naveen-Ul-Haq", "Nehal Wadhera", "Nicholas Pooran", "Nitish Kumar Reddy", "Nitish Rana", "Noor Ahmad", "Nuwan Thushara", "Pat Cummins", "Phil Salt", "Piyush Chawla", "Prabhsimran Singh", "Prithvi Shaw", "Quinton De Kock", "Rachin Ravindra", "Rahmanullah Gurbaz", "Rahul Chahar", "Rahul Tewatia", "Rahul Tripathi", "Rajat Patidar", "Ramandeep Singh", "Rashid Khan", "Rasikh Salam", "Ravi Bishnoi", "Ravichandran Ashwin", "Ravindra Jadeja", "Reece Topley", "Richard Gleeson", "Ricky Bhui", "Rilee Rossouw", "Rinku Singh", "Rishabh Pant", "Riyan Parag", "Rohit Sharma", "Romario Shepherd", "Rovman Powell", "Ruturaj Gaikwad", "Sai Kishore", "Sai Sudharsan", "Sam Curran", "Sameer Rizwi", "Sandeep Sharma", "Sandeep Warrier", "Sanju Samson", "Sanvir Singh", "Saurav Chauhan", "Shahbaz Ahmed", "Shahrukh Khan", "Shai Hope", "Shams Mulani", "Shardul Thakur", "Shashank Singh", "Shikhar Dhawan", "Shimron Hetmyer", "Shivam Dube", "Shivam Singh", "Shreyas Gopal", "Shreyas Iyer", "Shubham Dubey", "Shubman Gill", "Sikandar Raza", "Simarjeet Singh", "Spencer Johnson", "Sumit Kumar", "Sunil Narine", "Suryakumar Yadav", "Suyash S Prabhudessai", "Swapnil Singh", "T Natarajan", "Tanush Kotian", "Tilak Varma", "Tim David", "Tom Kohler- Cadmore", "Travis Head", "Trent Boult", "Tristan Stubbs", "Tushar Deshpande", "Umesh Yadav", "Vaibhav Arora", "Varun Chakaravarthy", "Venkatesh Iyer", "Vidwath Kaverappa", "Vijay Shankar", "Vijayakanth Viyaskanth", "Virat Kohli", "Vyshak Vijaykumar", "Washington Sundar", "Will Jacks", "Wriddhiman Saha", "Yash Dayal", "Yash Thakur", "Yashasvi Jaiswal", "Yudhvir Singh", "Yuzvendra Chahal"
    ]

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