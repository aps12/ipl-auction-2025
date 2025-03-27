from sqlalchemy.orm import column_property
from sqlalchemy.sql import func
from database import db

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    players = db.relationship("Player", backref="team", cascade="all, delete")

    @property
    def total_runs(self):
        return round(sum(player.runs for player in self.players), 2)

    @property
    def total_wickets(self):
        return round(sum(player.wickets for player in self.players), 2)

    @property
    def total_batting_points(self):
        return round(sum(player.batting_points for player in self.players), 2)

    @property
    def total_bowling_points(self):
        return round(sum(player.bowling_points for player in self.players), 2)

    @property
    def total_player_points(self):
        return round(self.total_batting_points + self.total_bowling_points, 2)

    @property
    def total_strike_rate(self):
        """Calculate team average strike rate (excluding players with 0 strike rate)."""
        valid_players = [p for p in self.players if p.strike_rate > 0]
        return round(sum(p.strike_rate for p in valid_players) / len(valid_players), 2) if valid_players else 0

    @property
    def total_economy(self):
        """Calculate team average economy rate (excluding players with 0 economy)."""
        valid_players = [p for p in self.players if p.economy > 0]
        return round(sum(p.economy for p in valid_players) / len(valid_players), 2) if valid_players else 0


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
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
        return round(self.wickets * 20 * (8 / self.economy), 2) if self.economy and self.wickets else 0

    @property
    def total_points(self):
        """Total points for the player: sum of batting and bowling points."""
        return round(self.batting_points + self.bowling_points, 2)
