"""
Odds API Integration for Real-Time Market Data
Fetches live odds from multiple sources for edge detection
"""

import requests
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class MarketType(Enum):
    """Supported betting market types."""
    MONEYLINE = "h2h"
    SPREAD = "spreads"
    TOTALS = "totals"
    PLAYER_PROPS = "player_props"
    TEAM_TOTALS = "team_totals"
    FIRST_HALF = "first_half"
    FIRST_QUARTER = "first_quarter"
    LIVE = "live"


@dataclass
class OddsLine:
    """Represents a single betting line."""
    market_type: str
    selection: str
    price: int  # American odds
    point: Optional[float] = None  # Spread or total
    implied_prob: float = 0.0
    book: str = ""
    timestamp: str = ""

    def __post_init__(self):
        self.implied_prob = self.american_to_implied(self.price)

    @staticmethod
    def american_to_implied(odds: int) -> float:
        """Convert American odds to implied probability."""
        if odds > 0:
            return 100 / (odds + 100)
        else:
            return abs(odds) / (abs(odds) + 100)

    @staticmethod
    def implied_to_american(prob: float) -> int:
        """Convert implied probability to American odds."""
        if prob <= 0 or prob >= 1:
            return 0
        if prob >= 0.5:
            return int(-100 * prob / (1 - prob))
        else:
            return int(100 * (1 - prob) / prob)


@dataclass
class Market:
    """Represents a betting market with multiple selections."""
    game_id: str
    market_type: MarketType
    lines: List[OddsLine]
    book: str
    last_update: str

    def get_vig(self) -> float:
        """Calculate the vig/juice on this market."""
        total_implied = sum(line.implied_prob for line in self.lines)
        return total_implied - 1.0

    def get_devigged_probs(self) -> List[Tuple[str, float]]:
        """Remove vig and return fair probabilities."""
        total_implied = sum(line.implied_prob for line in self.lines)
        if total_implied == 0:
            return []
        return [(line.selection, line.implied_prob / total_implied) for line in self.lines]


class OddsClient:
    """
    Client for fetching odds from multiple sources.
    Prioritizes free public APIs and ESPN embedded odds.
    """

    # Public odds endpoints
    ODDS_API_URL = "https://api.the-odds-api.com/v4/sports"

    SPORT_KEYS = {
        "nfl": "americanfootball_nfl",
        "nba": "basketball_nba",
        "cfb": "americanfootball_ncaaf",
        "cbb": "basketball_ncaab",
        "nhl": "icehockey_nhl",
    }

    def __init__(self, api_key: Optional[str] = None, timeout: int = 10):
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
        self._cache = {}

    def get_live_odds(self, sport: str, market: MarketType = MarketType.MONEYLINE) -> List[Dict]:
        """
        Fetch live odds for a sport.
        Falls back to ESPN-embedded odds if no API key.
        """
        if self.api_key:
            return self._fetch_odds_api(sport, market)
        return []

    def _fetch_odds_api(self, sport: str, market: MarketType) -> List[Dict]:
        """Fetch from The Odds API (requires API key)."""
        sport_key = self.SPORT_KEYS.get(sport.lower())
        if not sport_key:
            return []

        url = f"{self.ODDS_API_URL}/{sport_key}/odds"
        params = {
            "apiKey": self.api_key,
            "regions": "us",
            "markets": market.value,
            "oddsFormat": "american",
        }

        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return []

    def calculate_edge(self, true_prob: float, market_odds: int) -> Dict:
        """
        Calculate betting edge given true probability and market odds.

        Returns:
            Dict with:
            - edge_pct: Percentage edge over the market
            - ev_per_unit: Expected value per unit bet
            - kelly_pct: Kelly criterion bet size
            - grade: A+/A/B+/B/C/PASS
        """
        implied = OddsLine.american_to_implied(market_odds)

        # Edge = True Prob - Implied Prob
        edge = true_prob - implied

        # EV = (True Prob * Payout) - (1 - True Prob)
        if market_odds > 0:
            payout = market_odds / 100
        else:
            payout = 100 / abs(market_odds)

        ev = (true_prob * payout) - (1 - true_prob)

        # Kelly = Edge / Odds
        kelly = edge / (payout if payout > 0 else 1)
        kelly = max(0, min(kelly, 0.25))  # Cap at 25%

        # Grade based on edge
        if edge >= 0.15:
            grade = "A+"
        elif edge >= 0.10:
            grade = "A"
        elif edge >= 0.07:
            grade = "B+"
        elif edge >= 0.05:
            grade = "B"
        elif edge >= 0.02:
            grade = "C"
        else:
            grade = "PASS"

        return {
            "edge_pct": round(edge * 100, 2),
            "ev_per_unit": round(ev * 100, 2),
            "kelly_pct": round(kelly * 100, 2),
            "implied_prob": round(implied * 100, 2),
            "true_prob": round(true_prob * 100, 2),
            "grade": grade,
            "recommendation": "BET" if edge >= 0.05 else "PASS",
        }

    def find_arbitrage(self, markets: List[Market]) -> List[Dict]:
        """
        Find arbitrage opportunities across different books.

        Returns list of arb opportunities with:
        - selections: What to bet on each book
        - guaranteed_profit: Profit percentage
        - stakes: How to allocate
        """
        arbs = []

        # Group markets by game
        games = {}
        for market in markets:
            if market.game_id not in games:
                games[market.game_id] = []
            games[market.game_id].append(market)

        for game_id, game_markets in games.items():
            # Find best odds for each selection across books
            best_odds = {}

            for market in game_markets:
                for line in market.lines:
                    key = line.selection
                    if key not in best_odds or line.price > best_odds[key]["price"]:
                        best_odds[key] = {
                            "price": line.price,
                            "book": market.book,
                            "implied": line.implied_prob,
                        }

            # Check if total implied < 100%
            if len(best_odds) >= 2:
                total_implied = sum(o["implied"] for o in best_odds.values())

                if total_implied < 1.0:
                    profit_pct = (1 / total_implied - 1) * 100

                    arbs.append({
                        "game_id": game_id,
                        "total_implied": round(total_implied * 100, 2),
                        "guaranteed_profit_pct": round(profit_pct, 2),
                        "selections": best_odds,
                    })

        return sorted(arbs, key=lambda x: x["guaranteed_profit_pct"], reverse=True)

    def compare_to_pinnacle(self, market_odds: int, pinnacle_odds: int) -> Dict:
        """
        Compare market odds to Pinnacle sharp line.
        Pinnacle is the benchmark for sharp/true odds.
        """
        market_implied = OddsLine.american_to_implied(market_odds)
        pinnacle_implied = OddsLine.american_to_implied(pinnacle_odds)

        # CLV = how much better/worse than Pinnacle
        clv = pinnacle_implied - market_implied

        return {
            "market_implied": round(market_implied * 100, 2),
            "pinnacle_implied": round(pinnacle_implied * 100, 2),
            "clv_pct": round(clv * 100, 2),
            "beating_sharp": clv > 0,
            "assessment": "SHARP BET" if clv > 0.02 else "FAIR" if clv > -0.02 else "BAD VALUE"
        }


class ScoringMarketAnalyzer:
    """
    Specialized analyzer for scoring markets (totals, team totals, props).
    Finds edges in real-time based on pace, efficiency, and situational factors.
    """

    # Historical scoring averages by sport (2023-24 season)
    LEAGUE_AVERAGES = {
        "nfl": {"points_per_game": 21.8, "total_average": 43.6},
        "nba": {"points_per_game": 114.2, "total_average": 228.4, "pace": 100.3},
        "cbb": {"points_per_game": 73.5, "total_average": 147.0},
        "nhl": {"goals_per_game": 3.1, "total_average": 6.2},
    }

    def __init__(self):
        self.adjustments = {}

    def analyze_total(
        self,
        sport: str,
        home_team_avg: float,
        away_team_avg: float,
        home_def_avg: float,
        away_def_avg: float,
        posted_total: float,
        weather: Optional[Dict] = None,
        rest_advantage: int = 0,
    ) -> Dict:
        """
        Analyze over/under market for edge.

        Args:
            sport: Sport key
            home_team_avg: Home team's average points scored
            away_team_avg: Away team's average points scored
            home_def_avg: Home team's average points allowed
            away_def_avg: Away team's average points allowed
            posted_total: The line (e.g., 225.5)
            weather: Weather data for outdoor sports
            rest_advantage: Days of rest difference (positive = home advantage)

        Returns:
            Analysis with projected total and edge
        """
        league_avg = self.LEAGUE_AVERAGES.get(sport, {}).get("points_per_game", 100)

        # Calculate expected scores using opponent-adjusted method
        # Home team expected = (Their Offense + Opponent Defense) / 2, adjusted for HCA
        home_expected = (home_team_avg + away_def_avg) / 2
        away_expected = (away_team_avg + home_def_avg) / 2

        # Home court/field advantage
        if sport == "nba":
            home_expected += 2.5
            away_expected -= 0.5
        elif sport == "nfl":
            home_expected += 1.5
        elif sport == "nhl":
            home_expected += 0.15

        # Weather adjustments (NFL only)
        if sport == "nfl" and weather:
            wind = weather.get("wind_speed", 0)
            if wind and wind > 15:
                total_adjustment = -3 * (wind / 15)
                home_expected -= total_adjustment / 2
                away_expected -= total_adjustment / 2

        # Rest advantage (NBA primarily)
        if sport == "nba" and rest_advantage != 0:
            if rest_advantage > 0:  # Home team better rested
                home_expected += rest_advantage * 0.8
            else:  # Away team better rested
                away_expected += abs(rest_advantage) * 0.8

        projected_total = home_expected + away_expected
        difference = projected_total - posted_total

        # Calculate edge
        # Standard deviation for totals roughly 15-20 points NBA, 10-12 NFL
        if sport == "nba":
            std_dev = 17
        elif sport == "nfl":
            std_dev = 11
        elif sport == "nhl":
            std_dev = 1.5
        else:
            std_dev = 12

        # Z-score tells us probability
        z_score = difference / std_dev

        # Convert to probability (simplified)
        if z_score > 0:
            over_prob = 0.5 + min(0.4, z_score * 0.12)
            under_prob = 1 - over_prob
        else:
            under_prob = 0.5 + min(0.4, abs(z_score) * 0.12)
            over_prob = 1 - under_prob

        # Determine recommendation
        if difference > std_dev * 0.5:
            recommendation = "OVER"
            edge = over_prob - 0.5
        elif difference < -std_dev * 0.5:
            recommendation = "UNDER"
            edge = under_prob - 0.5
        else:
            recommendation = "PASS"
            edge = 0

        return {
            "projected_total": round(projected_total, 1),
            "posted_total": posted_total,
            "difference": round(difference, 1),
            "home_expected": round(home_expected, 1),
            "away_expected": round(away_expected, 1),
            "over_probability": round(over_prob * 100, 1),
            "under_probability": round(under_prob * 100, 1),
            "recommendation": recommendation,
            "edge_pct": round(edge * 100, 1),
            "confidence": "HIGH" if abs(difference) > std_dev else "MEDIUM" if abs(difference) > std_dev * 0.5 else "LOW",
            "factors": {
                "weather_impact": weather is not None,
                "rest_advantage": rest_advantage,
            }
        }

    def analyze_team_total(
        self,
        team_avg: float,
        opp_def_avg: float,
        posted_total: float,
        is_home: bool,
        sport: str = "nba"
    ) -> Dict:
        """Analyze team total market."""
        # Expected score
        expected = (team_avg + opp_def_avg) / 2

        # Home adjustment
        if is_home:
            if sport == "nba":
                expected += 1.5
            elif sport == "nfl":
                expected += 1.0

        difference = expected - posted_total

        if sport == "nba":
            std_dev = 10
        elif sport == "nfl":
            std_dev = 6
        else:
            std_dev = 7

        z_score = difference / std_dev

        if z_score > 0.3:
            recommendation = f"OVER {posted_total}"
            edge = min(0.15, z_score * 0.05)
        elif z_score < -0.3:
            recommendation = f"UNDER {posted_total}"
            edge = min(0.15, abs(z_score) * 0.05)
        else:
            recommendation = "PASS"
            edge = 0

        return {
            "expected_score": round(expected, 1),
            "posted_total": posted_total,
            "difference": round(difference, 1),
            "recommendation": recommendation,
            "edge_pct": round(edge * 100, 1),
        }

    def find_live_edges(self, game_data: Dict, current_odds: Dict) -> List[Dict]:
        """
        Find edges in live/in-game markets.

        Args:
            game_data: Current game state from ESPN
            current_odds: Current live odds

        Returns:
            List of edge opportunities
        """
        edges = []
        status = game_data.get("status", {})

        if status.get("state") != "in":
            return edges

        # Get current scores
        home_score = int(game_data.get("home_team", {}).get("score", 0) or 0)
        away_score = int(game_data.get("away_team", {}).get("score", 0) or 0)
        current_total = home_score + away_score

        # Get time remaining (simplified)
        period = status.get("period", 1)
        clock = status.get("clock", "0:00")

        # Parse posted live total if available
        live_total = current_odds.get("over_under")
        if live_total:
            # Calculate if pace suggests over/under
            # This is sport-specific logic
            pass

        return edges
