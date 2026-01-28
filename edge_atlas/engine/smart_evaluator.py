"""
Smart Evaluator - Human-Like Analysis Engine
Provides accurate, real-person evaluation of betting opportunities
NO simulated data - only real ESPN data with intelligent analysis
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import math

from ..api.espn import ESPNClient


@dataclass
class SmartPick:
    """A smart, human-evaluated betting pick."""
    game_id: str
    sport: str
    matchup: str
    date: str

    # The pick
    selection: str
    market: str
    odds: Optional[int]

    # Human-like evaluation
    confidence_level: str  # "HIGH", "MEDIUM", "LOW", "PASS"
    edge_assessment: str
    reasoning: str
    key_factors: List[str]
    concerns: List[str]

    # Numbers (from real data)
    true_probability: float
    implied_probability: float
    edge_pct: float

    # Sizing
    recommended_units: float
    max_risk: str

    # Verification
    data_quality: str
    last_updated: str


class SmartEvaluator:
    """
    Evaluates betting opportunities like a real professional handicapper.

    Key principles:
    1. Only use REAL data from ESPN
    2. Apply genuine analytical reasoning
    3. Be CONSERVATIVE - most games have no edge
    4. Explain WHY in plain language
    5. Acknowledge uncertainty
    """

    def __init__(self):
        self.espn = ESPNClient()

    def evaluate_game(self, sport: str, game: Dict) -> SmartPick:
        """
        Perform a comprehensive, human-like evaluation of a game.
        """
        home = game.get("home_team", {})
        away = game.get("away_team", {})
        odds = game.get("odds", {})

        # Extract real data
        home_name = home.get("name", "Home")
        away_name = away.get("name", "Away")
        home_record = self._get_record(home)
        away_record = self._get_record(away)

        # Parse records into wins/losses
        home_w, home_l = self._parse_record(home_record)
        away_w, away_l = self._parse_record(away_record)

        # Calculate real win probability
        home_prob, away_prob = self._calculate_probability(
            home_w, home_l, away_w, away_l, sport
        )

        # Get market odds
        home_ml = self._safe_int(odds.get("home_moneyline"))
        away_ml = self._safe_int(odds.get("away_moneyline"))
        spread = self._safe_float(odds.get("spread"))
        total = self._safe_float(odds.get("over_under"))

        # Evaluate each market
        ml_eval = self._evaluate_moneyline(
            home_name, away_name, home_prob, away_prob, home_ml, away_ml
        )
        spread_eval = self._evaluate_spread(
            home_name, away_name, home_w, home_l, away_w, away_l, spread, sport
        )
        total_eval = self._evaluate_total(
            home_name, away_name, home, away, total, sport, game.get("weather")
        )

        # Pick the best opportunity (or PASS)
        best = self._pick_best_opportunity(ml_eval, spread_eval, total_eval)

        # Build human-like reasoning
        key_factors = []
        concerns = []

        # Analyze the matchup like a real handicapper
        if home_w > home_l:
            key_factors.append(f"{home_name} has winning record ({home_record})")
        else:
            concerns.append(f"{home_name} struggling ({home_record})")

        if away_w > away_l:
            key_factors.append(f"{away_name} has winning record ({away_record})")
        else:
            concerns.append(f"{away_name} struggling ({away_record})")

        # Home/away factors
        key_factors.append(f"Home court advantage for {home_name}")

        # Weather for outdoor sports
        weather = game.get("weather")
        if weather and sport in ["nfl", "cfb"]:
            wind = weather.get("wind_speed")
            if wind and wind > 15:
                concerns.append(f"High wind ({wind} mph) could impact scoring")
                key_factors.append("Weather favors UNDER")

        # Generate reasoning
        reasoning = self._generate_reasoning(
            best, home_name, away_name, home_record, away_record, key_factors, concerns
        )

        # Determine confidence
        if best["edge_pct"] >= 8:
            confidence = "HIGH"
            units = 2.0
        elif best["edge_pct"] >= 5:
            confidence = "MEDIUM"
            units = 1.0
        elif best["edge_pct"] >= 3:
            confidence = "LOW"
            units = 0.5
        else:
            confidence = "PASS"
            units = 0.0

        return SmartPick(
            game_id=game.get("game_id", ""),
            sport=sport.upper(),
            matchup=f"{away_name} @ {home_name}",
            date=game.get("date", ""),
            selection=best["selection"],
            market=best["market"],
            odds=best["odds"],
            confidence_level=confidence,
            edge_assessment=f"{best['edge_pct']:.1f}% edge" if best["edge_pct"] > 0 else "No edge",
            reasoning=reasoning,
            key_factors=key_factors,
            concerns=concerns,
            true_probability=best["true_prob"],
            implied_probability=best["implied_prob"],
            edge_pct=best["edge_pct"],
            recommended_units=units,
            max_risk="2% of bankroll",
            data_quality="LIVE" if game.get("status", {}).get("state") == "in" else "REAL-TIME",
            last_updated=datetime.now().isoformat(),
        )

    def _evaluate_moneyline(
        self,
        home_name: str,
        away_name: str,
        home_prob: float,
        away_prob: float,
        home_ml: Optional[int],
        away_ml: Optional[int],
    ) -> Dict:
        """Evaluate moneyline opportunity."""
        if not home_ml or not away_ml:
            return {
                "market": "Moneyline",
                "selection": "NO LINE",
                "odds": None,
                "true_prob": 0.5,
                "implied_prob": 0.5,
                "edge_pct": 0,
            }

        home_implied = self._odds_to_prob(home_ml)
        away_implied = self._odds_to_prob(away_ml)

        home_edge = home_prob - home_implied
        away_edge = away_prob - away_implied

        if home_edge > away_edge:
            return {
                "market": "Moneyline",
                "selection": f"{home_name} ML",
                "odds": home_ml,
                "true_prob": home_prob,
                "implied_prob": home_implied,
                "edge_pct": home_edge * 100,
            }
        else:
            return {
                "market": "Moneyline",
                "selection": f"{away_name} ML",
                "odds": away_ml,
                "true_prob": away_prob,
                "implied_prob": away_implied,
                "edge_pct": away_edge * 100,
            }

    def _evaluate_spread(
        self,
        home_name: str,
        away_name: str,
        home_w: int,
        home_l: int,
        away_w: int,
        away_l: int,
        spread: Optional[float],
        sport: str,
    ) -> Dict:
        """Evaluate spread opportunity."""
        if spread is None:
            return {
                "market": "Spread",
                "selection": "NO LINE",
                "odds": -110,
                "true_prob": 0.5,
                "implied_prob": 0.524,
                "edge_pct": 0,
            }

        # Calculate expected margin based on records
        home_games = home_w + home_l
        away_games = away_w + away_l

        if home_games == 0 or away_games == 0:
            expected_margin = 0
        else:
            home_win_pct = home_w / home_games
            away_win_pct = away_w / away_games

            # Expected margin scales with win% difference
            # Each 10% win% difference ≈ 3 points in most sports
            pct_diff = home_win_pct - away_win_pct

            if sport in ["nba", "cbb"]:
                expected_margin = pct_diff * 30 + 2.5  # HCA
            elif sport in ["nfl", "cfb"]:
                expected_margin = pct_diff * 20 + 2.5
            else:
                expected_margin = pct_diff * 25 + 2

        # Compare to spread
        # Negative spread means home is favored
        cover_margin = expected_margin - (-spread)

        # Standard deviation for covers ~10-12 points
        if sport in ["nba", "cbb"]:
            std_dev = 12
        else:
            std_dev = 10

        # Calculate cover probability
        z = cover_margin / std_dev
        home_cover_prob = self._normal_cdf(z)

        implied = 0.524  # -110 implies 52.4%

        if home_cover_prob > 0.5:
            return {
                "market": "Spread",
                "selection": f"{home_name} {spread}",
                "odds": -110,
                "true_prob": home_cover_prob,
                "implied_prob": implied,
                "edge_pct": (home_cover_prob - implied) * 100,
            }
        else:
            away_cover_prob = 1 - home_cover_prob
            return {
                "market": "Spread",
                "selection": f"{away_name} +{abs(spread)}",
                "odds": -110,
                "true_prob": away_cover_prob,
                "implied_prob": implied,
                "edge_pct": (away_cover_prob - implied) * 100,
            }

    def _evaluate_total(
        self,
        home_name: str,
        away_name: str,
        home: Dict,
        away: Dict,
        total: Optional[float],
        sport: str,
        weather: Optional[Dict],
    ) -> Dict:
        """Evaluate total (over/under) opportunity."""
        if total is None:
            return {
                "market": "Total",
                "selection": "NO LINE",
                "odds": -110,
                "true_prob": 0.5,
                "implied_prob": 0.524,
                "edge_pct": 0,
            }

        # Without detailed scoring data, we can only evaluate based on context
        # Weather, pace, etc.

        adjustment = 0
        factors = []

        if weather and sport in ["nfl", "cfb"]:
            wind = weather.get("wind_speed", 0)
            if wind and wind > 15:
                adjustment -= 3
                factors.append("wind")
            if wind and wind > 20:
                adjustment -= 3

            condition = str(weather.get("condition", "")).lower()
            if "rain" in condition or "storm" in condition:
                adjustment -= 6
                factors.append("rain")
            if "snow" in condition:
                adjustment -= 10
                factors.append("snow")

        # Apply weather adjustment
        adjusted_expectation = total + adjustment

        # If we expect fewer points than the line, lean under
        if adjustment < -3:
            over_prob = 0.4  # Lean under
        elif adjustment > 3:
            over_prob = 0.6  # Lean over
        else:
            over_prob = 0.5  # No edge

        implied = 0.524

        if over_prob > 0.5:
            return {
                "market": "Total",
                "selection": f"OVER {total}",
                "odds": -110,
                "true_prob": over_prob,
                "implied_prob": implied,
                "edge_pct": (over_prob - implied) * 100,
            }
        else:
            return {
                "market": "Total",
                "selection": f"UNDER {total}",
                "odds": -110,
                "true_prob": 1 - over_prob,
                "implied_prob": implied,
                "edge_pct": ((1 - over_prob) - implied) * 100,
            }

    def _pick_best_opportunity(
        self,
        ml_eval: Dict,
        spread_eval: Dict,
        total_eval: Dict,
    ) -> Dict:
        """Pick the best opportunity or PASS."""
        options = [ml_eval, spread_eval, total_eval]
        best = max(options, key=lambda x: x["edge_pct"])

        if best["edge_pct"] < 3:  # Minimum 3% edge to consider
            return {
                "market": "None",
                "selection": "PASS - No edge found",
                "odds": None,
                "true_prob": 0.5,
                "implied_prob": 0.5,
                "edge_pct": 0,
            }

        return best

    def _generate_reasoning(
        self,
        best: Dict,
        home_name: str,
        away_name: str,
        home_record: str,
        away_record: str,
        key_factors: List[str],
        concerns: List[str],
    ) -> str:
        """Generate human-like reasoning for the pick."""
        if best["edge_pct"] < 3:
            return (
                f"Looking at {away_name} ({away_record}) @ {home_name} ({home_record}), "
                f"I don't see a clear edge here. The market seems fairly priced. "
                f"This is a game to PASS on - better opportunities will come."
            )

        selection = best["selection"]
        edge = best["edge_pct"]
        market = best["market"]

        reasoning = f"My analysis of {away_name} ({away_record}) @ {home_name} ({home_record}):\n\n"

        reasoning += f"SELECTION: {selection}\n\n"

        reasoning += "KEY FACTORS:\n"
        for factor in key_factors[:3]:
            reasoning += f"• {factor}\n"

        if concerns:
            reasoning += "\nCONCERNS:\n"
            for concern in concerns[:2]:
                reasoning += f"• {concern}\n"

        reasoning += f"\nEDGE ASSESSMENT:\n"
        reasoning += f"I calculate a {edge:.1f}% edge on this {market.lower()} bet. "

        if edge >= 8:
            reasoning += "This is a strong opportunity - the market appears to be mispricing this game."
        elif edge >= 5:
            reasoning += "This is a solid spot with reasonable value."
        else:
            reasoning += "The edge is marginal but worth a small play."

        return reasoning

    def _calculate_probability(
        self,
        home_w: int,
        home_l: int,
        away_w: int,
        away_l: int,
        sport: str,
    ) -> Tuple[float, float]:
        """Calculate win probability from real records."""
        home_games = home_w + home_l
        away_games = away_w + away_l

        # Handle early season / no games
        if home_games < 3:
            home_win_pct = 0.5
        else:
            home_win_pct = home_w / home_games

        if away_games < 3:
            away_win_pct = 0.5
        else:
            away_win_pct = away_w / away_games

        # Home court advantage by sport
        hca = {
            "nba": 0.06,
            "nfl": 0.03,
            "cfb": 0.05,
            "cbb": 0.06,
            "nhl": 0.025,
        }.get(sport.lower(), 0.04)

        # Log5 method
        p_a = min(0.9, max(0.1, home_win_pct + hca))
        p_b = min(0.9, max(0.1, away_win_pct))

        numerator = p_a - (p_a * p_b)
        denominator = p_a + p_b - (2 * p_a * p_b)

        if denominator == 0:
            home_prob = 0.5
        else:
            home_prob = numerator / denominator

        home_prob = max(0.15, min(0.85, home_prob))

        return home_prob, 1 - home_prob

    def _get_record(self, team: Dict) -> str:
        """Get team record from ESPN data."""
        records = team.get("records", [])
        if records:
            return records[0]
        return "0-0"

    def _parse_record(self, record: str) -> Tuple[int, int]:
        """Parse record string into wins/losses."""
        try:
            parts = record.split("-")
            wins = int(parts[0])
            losses = int(parts[1]) if len(parts) > 1 else 0
            return wins, losses
        except (ValueError, IndexError):
            return 0, 0

    def _odds_to_prob(self, odds: int) -> float:
        """Convert American odds to probability."""
        if odds > 0:
            return 100 / (odds + 100)
        else:
            return abs(odds) / (abs(odds) + 100)

    @staticmethod
    def _normal_cdf(z: float) -> float:
        """Approximate normal CDF."""
        t = 1 / (1 + 0.2316419 * abs(z))
        d = 0.3989423 * math.exp(-z * z / 2)
        p = d * t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274))))
        return 1 - p if z > 0 else p

    @staticmethod
    def _safe_int(value) -> Optional[int]:
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _safe_float(value) -> Optional[float]:
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None


def format_smart_pick(pick: SmartPick) -> str:
    """Format a smart pick for display."""
    output = []
    output.append("\n" + "=" * 70)
    output.append(f"EDGE ATLAS ANALYSIS: {pick.matchup}")
    output.append("=" * 70)

    output.append(f"\nSport: {pick.sport}")
    output.append(f"Date: {pick.date}")
    output.append(f"Data Quality: {pick.data_quality}")

    output.append("\n" + "-" * 70)
    output.append("SELECTION")
    output.append("-" * 70)
    output.append(f"\n{pick.selection}")
    output.append(f"Market: {pick.market}")
    if pick.odds:
        output.append(f"Odds: {pick.odds}")

    output.append("\n" + "-" * 70)
    output.append("CONFIDENCE")
    output.append("-" * 70)
    output.append(f"\nLevel: {pick.confidence_level}")
    output.append(f"Edge: {pick.edge_assessment}")
    output.append(f"Recommended: {pick.recommended_units} units (max {pick.max_risk})")

    output.append("\n" + "-" * 70)
    output.append("REASONING")
    output.append("-" * 70)
    output.append(f"\n{pick.reasoning}")

    if pick.key_factors:
        output.append("\n" + "-" * 70)
        output.append("KEY FACTORS")
        output.append("-" * 70)
        for factor in pick.key_factors:
            output.append(f"+ {factor}")

    if pick.concerns:
        output.append("\n" + "-" * 70)
        output.append("CONCERNS")
        output.append("-" * 70)
        for concern in pick.concerns:
            output.append(f"- {concern}")

    output.append("\n" + "-" * 70)
    output.append("NUMBERS")
    output.append("-" * 70)
    output.append(f"True Probability: {pick.true_probability*100:.1f}%")
    output.append(f"Market Implied: {pick.implied_probability*100:.1f}%")
    output.append(f"Edge: {pick.edge_pct:.1f}%")

    output.append(f"\nLast Updated: {pick.last_updated}")
    output.append("=" * 70)

    return "\n".join(output)
