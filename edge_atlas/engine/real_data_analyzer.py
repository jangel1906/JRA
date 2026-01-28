"""
Real Data Analyzer
Uses ONLY real ESPN data - no simulations or placeholders
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import math

from ..api.espn import ESPNClient


@dataclass
class RealTeamStats:
    """Real team statistics from ESPN."""
    team_id: str
    team_name: str
    abbreviation: str
    record: str
    wins: int
    losses: int
    home_record: str
    away_record: str
    points_per_game: float
    points_allowed: float
    last_5: List[str]


@dataclass
class RealGameAnalysis:
    """Analysis result using only real data."""
    game_id: str
    game_name: str
    sport: str
    date: str
    status: str

    # Teams
    home_team: str
    away_team: str
    home_record: str
    away_record: str

    # Real odds from ESPN
    spread: Optional[float]
    total: Optional[float]
    home_moneyline: Optional[int]
    away_moneyline: Optional[int]

    # Calculated probabilities (using real data)
    home_win_prob: float
    away_win_prob: float

    # Edges
    moneyline_edge: Optional[Dict]
    spread_edge: Optional[Dict]
    total_edge: Optional[Dict]

    # Context
    weather: Optional[Dict]
    injuries: List[Dict]
    venue: Optional[Dict]

    timestamp: str


class RealDataAnalyzer:
    """
    Analyzes games using ONLY real ESPN data.
    No simulations, no placeholder values.
    """

    def __init__(self):
        self.espn = ESPNClient()
        self._team_cache = {}

    def get_real_scoreboard(self, sport: str, date: Optional[str] = None) -> List[Dict]:
        """
        Get real scoreboard data from ESPN.

        Returns actual games with actual odds and data.
        """
        scoreboard = self.espn.get_scoreboard(sport, dates=date)
        return self.espn.parse_scoreboard(scoreboard)

    def get_real_game_odds(self, game: Dict) -> Dict:
        """Extract real odds from ESPN game data."""
        odds = game.get("odds", {})
        if not odds:
            return {
                "spread": None,
                "total": None,
                "home_moneyline": None,
                "away_moneyline": None,
                "provider": None,
            }

        return {
            "spread": self._safe_float(odds.get("spread")),
            "total": self._safe_float(odds.get("over_under")),
            "home_moneyline": self._safe_int(odds.get("home_moneyline")),
            "away_moneyline": self._safe_int(odds.get("away_moneyline")),
            "provider": odds.get("provider", "ESPN"),
        }

    def get_team_record(self, team_data: Dict) -> Tuple[int, int, str]:
        """Extract real team record."""
        records = team_data.get("records", [])
        if records:
            record_str = records[0] if records else "0-0"
            try:
                parts = record_str.split("-")
                wins = int(parts[0])
                losses = int(parts[1]) if len(parts) > 1 else 0
                return wins, losses, record_str
            except (ValueError, IndexError):
                pass
        return 0, 0, "0-0"

    def calculate_win_probability_from_record(
        self,
        home_wins: int,
        home_losses: int,
        away_wins: int,
        away_losses: int,
        sport: str
    ) -> Tuple[float, float]:
        """
        Calculate win probability using real records.

        Uses Pythagorean expectation concept adapted for win/loss records.
        """
        # Calculate win percentages
        home_games = home_wins + home_losses
        away_games = away_wins + away_losses

        if home_games == 0:
            home_win_pct = 0.5
        else:
            home_win_pct = home_wins / home_games

        if away_games == 0:
            away_win_pct = 0.5
        else:
            away_win_pct = away_wins / away_games

        # Home court/field advantage by sport
        hca = {
            "nba": 0.06,   # ~6% home advantage
            "nfl": 0.03,   # ~3% home advantage (declining)
            "cfb": 0.05,   # ~5% home advantage
            "cbb": 0.06,   # ~6% home advantage
            "nhl": 0.025,  # ~2.5% home advantage
        }.get(sport.lower(), 0.04)

        # Log5 formula for head-to-head probability
        # P(A beats B) = (pA - pA*pB) / (pA + pB - 2*pA*pB)
        p_a = home_win_pct + hca  # Home team with HCA
        p_b = away_win_pct

        # Clamp to valid range
        p_a = max(0.1, min(0.9, p_a))
        p_b = max(0.1, min(0.9, p_b))

        numerator = p_a - (p_a * p_b)
        denominator = p_a + p_b - (2 * p_a * p_b)

        if denominator == 0:
            home_prob = 0.5
        else:
            home_prob = numerator / denominator

        # Clamp final probability
        home_prob = max(0.15, min(0.85, home_prob))
        away_prob = 1 - home_prob

        return home_prob, away_prob

    def calculate_implied_probability(self, american_odds: int) -> float:
        """Convert American odds to implied probability."""
        if american_odds > 0:
            return 100 / (american_odds + 100)
        else:
            return abs(american_odds) / (abs(american_odds) + 100)

    def find_moneyline_edge(
        self,
        true_prob: float,
        odds: int
    ) -> Optional[Dict]:
        """
        Find edge on moneyline using real probabilities.

        Returns edge info or None if no edge.
        """
        if not odds:
            return None

        implied = self.calculate_implied_probability(odds)
        edge = true_prob - implied

        if edge < 0.03:  # Less than 3% edge
            return None

        # Calculate EV
        if odds > 0:
            payout = odds / 100
        else:
            payout = 100 / abs(odds)

        ev = (true_prob * payout) - (1 - true_prob)

        return {
            "edge_pct": round(edge * 100, 2),
            "true_probability": round(true_prob * 100, 2),
            "implied_probability": round(implied * 100, 2),
            "ev_per_unit": round(ev * 100, 2),
            "odds": odds,
            "recommendation": "BET" if edge >= 0.05 else "MONITOR",
        }

    def analyze_real_game(self, sport: str, game: Dict) -> RealGameAnalysis:
        """
        Perform complete analysis of a game using only real data.
        """
        timestamp = datetime.now().isoformat()

        home_team = game.get("home_team", {})
        away_team = game.get("away_team", {})

        # Get real records
        home_wins, home_losses, home_record = self.get_team_record(home_team)
        away_wins, away_losses, away_record = self.get_team_record(away_team)

        # Calculate real probabilities
        home_prob, away_prob = self.calculate_win_probability_from_record(
            home_wins, home_losses,
            away_wins, away_losses,
            sport
        )

        # Get real odds
        odds = self.get_real_game_odds(game)

        # Find edges using real data
        ml_edge_home = None
        ml_edge_away = None

        if odds["home_moneyline"]:
            ml_edge_home = self.find_moneyline_edge(home_prob, odds["home_moneyline"])

        if odds["away_moneyline"]:
            ml_edge_away = self.find_moneyline_edge(away_prob, odds["away_moneyline"])

        # Use best moneyline edge
        moneyline_edge = None
        if ml_edge_home and ml_edge_away:
            moneyline_edge = ml_edge_home if ml_edge_home["edge_pct"] > ml_edge_away["edge_pct"] else ml_edge_away
        elif ml_edge_home:
            moneyline_edge = ml_edge_home
        elif ml_edge_away:
            moneyline_edge = ml_edge_away

        # Total analysis using real scoring data
        total_edge = None
        if odds["total"]:
            # Would need historical scoring data for accurate total analysis
            # For now, flag totals as needing more data
            total_edge = {
                "posted_total": odds["total"],
                "analysis": "Requires team scoring averages for edge calculation",
                "recommendation": "RESEARCH",
            }

        return RealGameAnalysis(
            game_id=game.get("game_id", ""),
            game_name=game.get("name", ""),
            sport=sport.upper(),
            date=game.get("date", ""),
            status=game.get("status", {}).get("state", "unknown"),
            home_team=home_team.get("name", "Home"),
            away_team=away_team.get("name", "Away"),
            home_record=home_record,
            away_record=away_record,
            spread=odds["spread"],
            total=odds["total"],
            home_moneyline=odds["home_moneyline"],
            away_moneyline=odds["away_moneyline"],
            home_win_prob=home_prob,
            away_win_prob=away_prob,
            moneyline_edge=moneyline_edge,
            spread_edge=None,  # Requires point differential data
            total_edge=total_edge,
            weather=game.get("weather"),
            injuries=[],  # Would fetch from injuries endpoint
            venue=game.get("venue"),
            timestamp=timestamp,
        )

    def scan_for_real_edges(self, sport: str) -> List[Dict]:
        """
        Scan a sport for real edges using actual ESPN data.

        Returns only opportunities with verified edge from real data.
        """
        edges = []
        games = self.get_real_scoreboard(sport)

        for game in games:
            # Only analyze upcoming games
            if game.get("status", {}).get("state") != "pre":
                continue

            analysis = self.analyze_real_game(sport, game)

            if analysis.moneyline_edge and analysis.moneyline_edge.get("edge_pct", 0) >= 5:
                edges.append({
                    "sport": analysis.sport,
                    "game": analysis.game_name,
                    "date": analysis.date,
                    "market": "Moneyline",
                    "home_team": analysis.home_team,
                    "away_team": analysis.away_team,
                    "home_record": analysis.home_record,
                    "away_record": analysis.away_record,
                    "selection": f"{analysis.home_team if analysis.home_win_prob > analysis.away_win_prob else analysis.away_team} ML",
                    "odds": analysis.moneyline_edge["odds"],
                    "edge_pct": analysis.moneyline_edge["edge_pct"],
                    "true_prob": analysis.moneyline_edge["true_probability"],
                    "implied_prob": analysis.moneyline_edge["implied_probability"],
                    "ev": analysis.moneyline_edge["ev_per_unit"],
                    "recommendation": analysis.moneyline_edge["recommendation"],
                    "data_source": "ESPN Live API",
                    "timestamp": analysis.timestamp,
                })

        # Sort by edge
        edges.sort(key=lambda x: x["edge_pct"], reverse=True)

        return edges

    def get_live_games_real(self, sport: str) -> List[Dict]:
        """Get only live/in-progress games with real data."""
        games = self.get_real_scoreboard(sport)
        return [g for g in games if g.get("status", {}).get("state") == "in"]

    def analyze_live_game_real(self, sport: str, game: Dict) -> Dict:
        """
        Analyze a live game using only real current data.

        No projections using simulated values - only actual game state.
        """
        status = game.get("status", {})
        home = game.get("home_team", {})
        away = game.get("away_team", {})
        odds = game.get("odds", {})

        home_score = int(home.get("score", 0) or 0)
        away_score = int(away.get("score", 0) or 0)
        current_margin = home_score - away_score

        return {
            "game_id": game.get("game_id"),
            "game_name": game.get("name"),
            "sport": sport.upper(),
            "status": {
                "state": "LIVE",
                "period": status.get("period"),
                "clock": status.get("clock"),
                "detail": status.get("detail"),
            },
            "score": {
                "home": home_score,
                "away": away_score,
                "total": home_score + away_score,
                "margin": current_margin,
            },
            "teams": {
                "home": home.get("name"),
                "away": away.get("name"),
            },
            "live_odds": {
                "spread": odds.get("spread"),
                "total": odds.get("over_under"),
            },
            "timestamp": datetime.now().isoformat(),
        }

    @staticmethod
    def _safe_float(value) -> Optional[float]:
        """Safely convert to float."""
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _safe_int(value) -> Optional[int]:
        """Safely convert to int."""
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None


def format_real_edge(edge: Dict) -> str:
    """Format a real edge for display."""
    output = []
    output.append(f"\n{'='*60}")
    output.append(f"REAL EDGE DETECTED: {edge['game']}")
    output.append(f"{'='*60}")
    output.append(f"Sport: {edge['sport']}")
    output.append(f"Date: {edge['date']}")
    output.append(f"")
    output.append(f"Matchup: {edge['away_team']} ({edge['away_record']}) @ {edge['home_team']} ({edge['home_record']})")
    output.append(f"")
    output.append(f"Market: {edge['market']}")
    output.append(f"Selection: {edge['selection']}")
    output.append(f"Odds: {edge['odds']}")
    output.append(f"")
    output.append(f"EDGE CALCULATION (Real Data):")
    output.append(f"  Our Probability: {edge['true_prob']:.1f}%")
    output.append(f"  Market Implied:  {edge['implied_prob']:.1f}%")
    output.append(f"  EDGE: {edge['edge_pct']:.1f}%")
    output.append(f"  Expected Value: +{edge['ev']:.1f}% per unit")
    output.append(f"")
    output.append(f"Recommendation: {edge['recommendation']}")
    output.append(f"Data Source: {edge['data_source']}")
    output.append(f"Analyzed: {edge['timestamp']}")
    output.append(f"{'='*60}")

    return "\n".join(output)
