from sqlalchemy.orm import column_property
from sqlalchemy.sql import func
from database import db

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    players = db.relationship("Player", backref="team", cascade="all, delete")

    @property
    def top_8_players(self):
        """Helper method to get top 8 players sorted by total points."""
        # Fetch top 8 players sorted by total points directly from database or process in Python
        return sorted(self.players, key=lambda p: p.total_points, reverse=True)[:8]

    @property
    def total_runs(self):
        return round(sum(player.runs for player in self.top_8_players), 2)

    @property
    def total_wickets(self):
        return round(sum(player.wickets for player in self.top_8_players), 2)

    @property
    def total_batting_points(self):
        return round(sum(player.batting_points for player in self.top_8_players), 2)

    @property
    def total_bowling_points(self):
        return round(sum(player.bowling_points for player in self.top_8_players), 2)

    @property
    def total_player_points(self):
        return round(self.total_batting_points + self.total_bowling_points, 2)

    @property
    def total_strike_rate(self):
        """Calculate team average strike rate (using only top 8 players)."""
        top_8_valid_players = [p for p in self.top_8_players if p.strike_rate > 0]
        return round(sum(p.strike_rate for p in top_8_valid_players) / len(top_8_valid_players), 2) if top_8_valid_players else None

    @property
    def total_economy(self):
        """Calculate team average economy rate (using only top 8 players)."""
        top_8_valid_players = [p for p in self.top_8_players if p.economy > 0]
        return round(sum(p.economy for p in top_8_valid_players) / len(top_8_valid_players), 2) if top_8_valid_players else None

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    runs = db.Column(db.Integer, default=0)
    strike_rate = db.Column(db.Float, default=0.0)
    wickets = db.Column(db.Integer, default=0)
    economy = db.Column(db.Float, default=0.0)
    team_id = db.Column(db.Integer, db.ForeignKey("team.id"), nullable=False)

    @property
    def batting_points(self):
        """Calculate batting points: runs * (strike rate adjustment)."""
        return round(self.runs * (self.strike_rate / 125), 2) if self.strike_rate else 0

    @property
    def bowling_points(self):
        """Calculate bowling points: wickets * 20 * (economy rate adjustment)."""
        min_economy = max(self.economy, 2)  # Clamp to avoid too high calculations
        return round(self.wickets * 20 * (8 / min_economy), 2) if self.economy and self.wickets else 0

    @property
    def total_points(self):
        """Total points for the player: sum of batting and bowling points."""
        return round(self.batting_points + self.bowling_points, 2)