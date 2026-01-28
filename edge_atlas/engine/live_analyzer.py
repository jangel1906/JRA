"""
Live Game Analysis Engine
Real-time edge detection for in-progress games
Provides accurate suggestions based on live data
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from enum import Enum
import math


class LiveMarketType(Enum):
    """Live betting market types."""
    LIVE_SPREAD = "live_spread"
    LIVE_TOTAL = "live_total"
    LIVE_MONEYLINE = "live_moneyline"
    NEXT_SCORE = "next_score"
    QUARTER_TOTAL = "quarter_total"
    HALF_TOTAL = "half_total"
    TEAM_TOTAL_REST_OF_GAME = "team_total_rog"


@dataclass
class LiveGameState:
    """Current state of a live game."""
    game_id: str
    sport: str
    home_team: str
    away_team: str
    home_score: int
    away_score: int
    period: int
    clock: str
    time_remaining_seconds: int
    total_game_seconds: int
    possession: Optional[str] = None
    home_timeouts: int = 0
    away_timeouts: int = 0
    is_overtime: bool = False

    @property
    def elapsed_pct(self) -> float:
        """Percentage of game elapsed."""
        if self.total_game_seconds == 0:
            return 0.0
        elapsed = self.total_game_seconds - self.time_remaining_seconds
        return elapsed / self.total_game_seconds

    @property
    def current_total(self) -> int:
        """Current combined score."""
        return self.home_score + self.away_score

    @property
    def current_margin(self) -> int:
        """Current margin (positive = home leading)."""
        return self.home_score - self.away_score


@dataclass
class LivePaceAnalysis:
    """Pace analysis for live totals."""
    current_total: int
    elapsed_pct: float
    projected_final_total: float
    pace_per_minute: float
    pre_game_total: float
    live_total: float
    over_probability: float
    under_probability: float
    edge_over: float
    edge_under: float
    recommendation: str
    confidence: str
    factors: List[str] = field(default_factory=list)


@dataclass
class LiveSuggestion:
    """A live betting suggestion."""
    game_id: str
    game_name: str
    sport: str
    market: str
    selection: str
    current_odds: int
    edge_pct: float
    true_probability: float
    confidence: str
    rationale: str
    time_sensitivity: str  # "ACT NOW", "MONITOR", "WAIT"
    verification_notes: List[str]
    detected_at: str


class LiveGameAnalyzer:
    """
    Analyzes live games for real-time betting edges.

    Key features:
    - Pace-based total projections
    - Momentum detection
    - Time-adjusted win probabilities
    - Live spread value detection
    """

    # Sport-specific game lengths in seconds
    GAME_LENGTHS = {
        "nba": 48 * 60,      # 48 minutes
        "nfl": 60 * 60,      # 60 minutes
        "nhl": 60 * 60,      # 60 minutes
        "cbb": 40 * 60,      # 40 minutes
        "cfb": 60 * 60,      # 60 minutes
    }

    # Average points per second by sport
    AVG_PACE = {
        "nba": 228.4 / (48 * 60),   # ~0.0793 points/sec
        "nfl": 43.6 / (60 * 60),    # ~0.0121 points/sec
        "nhl": 6.2 / (60 * 60),     # ~0.00172 goals/sec
        "cbb": 147.0 / (40 * 60),   # ~0.0613 points/sec
        "cfb": 52.0 / (60 * 60),    # ~0.0144 points/sec
    }

    def __init__(self):
        self.game_states: Dict[str, List[LiveGameState]] = {}  # Track history

    def parse_game_state(self, sport: str, game_data: Dict) -> LiveGameState:
        """Parse ESPN game data into LiveGameState."""
        status = game_data.get("status", {})
        home = game_data.get("home_team", {})
        away = game_data.get("away_team", {})

        # Parse clock
        clock_str = status.get("clock", "0:00")
        period = status.get("period", 1) or 1

        # Calculate time remaining
        time_remaining = self._parse_clock(clock_str, sport, period)
        total_seconds = self.GAME_LENGTHS.get(sport, 2880)

        return LiveGameState(
            game_id=game_data.get("game_id", ""),
            sport=sport,
            home_team=home.get("name", "Home"),
            away_team=away.get("name", "Away"),
            home_score=int(home.get("score", 0) or 0),
            away_score=int(away.get("score", 0) or 0),
            period=period,
            clock=clock_str,
            time_remaining_seconds=time_remaining,
            total_game_seconds=total_seconds,
            is_overtime=period > self._get_regulation_periods(sport),
        )

    def _parse_clock(self, clock_str: str, sport: str, period: int) -> int:
        """Parse clock string to seconds remaining."""
        try:
            if ":" in clock_str:
                parts = clock_str.split(":")
                minutes = int(parts[0])
                seconds = int(parts[1]) if len(parts) > 1 else 0
                period_seconds = minutes * 60 + seconds
            else:
                period_seconds = 0
        except (ValueError, IndexError):
            period_seconds = 0

        # Calculate total remaining based on sport
        if sport == "nba":
            periods_remaining = max(0, 4 - period)
            return period_seconds + (periods_remaining * 12 * 60)
        elif sport in ["nfl", "cfb"]:
            periods_remaining = max(0, 4 - period)
            return period_seconds + (periods_remaining * 15 * 60)
        elif sport == "cbb":
            periods_remaining = max(0, 2 - period)
            return period_seconds + (periods_remaining * 20 * 60)
        elif sport == "nhl":
            periods_remaining = max(0, 3 - period)
            return period_seconds + (periods_remaining * 20 * 60)

        return period_seconds

    def _get_regulation_periods(self, sport: str) -> int:
        """Get number of regulation periods by sport."""
        return {"nba": 4, "nfl": 4, "cfb": 4, "cbb": 2, "nhl": 3}.get(sport, 4)

    def analyze_live_total(
        self,
        state: LiveGameState,
        pre_game_total: float,
        live_total: Optional[float] = None,
    ) -> LivePaceAnalysis:
        """
        Analyze live total (over/under) market.

        Uses pace-based projection to find edges in live totals.
        """
        sport = state.sport
        elapsed = state.elapsed_pct
        current = state.current_total

        # Minimum elapsed time for reliable projection
        if elapsed < 0.15:
            return LivePaceAnalysis(
                current_total=current,
                elapsed_pct=elapsed,
                projected_final_total=pre_game_total,  # Use pre-game as projection
                pace_per_minute=0,
                pre_game_total=pre_game_total,
                live_total=live_total or pre_game_total,
                over_probability=0.5,
                under_probability=0.5,
                edge_over=0,
                edge_under=0,
                recommendation="WAIT - Too early for reliable projection",
                confidence="LOW",
                factors=["Less than 15% of game elapsed"]
            )

        # Calculate current pace
        elapsed_seconds = state.total_game_seconds - state.time_remaining_seconds
        if elapsed_seconds > 0:
            pace_per_second = current / elapsed_seconds
            pace_per_minute = pace_per_second * 60
        else:
            pace_per_second = self.AVG_PACE.get(sport, 0.05)
            pace_per_minute = pace_per_second * 60

        # Project final total
        projected_final = current + (pace_per_second * state.time_remaining_seconds)

        # Apply regression toward mean (games tend to regress)
        regression_factor = 0.3  # 30% regression to pre-game expectation
        regressed_projection = (
            projected_final * (1 - regression_factor) +
            pre_game_total * regression_factor
        )

        # Use live total if available, otherwise pre-game
        target_total = live_total if live_total else pre_game_total

        # Calculate probabilities using standard deviation
        # SD decreases as game progresses (less time = less variance)
        remaining_pct = 1 - elapsed
        if sport == "nba":
            base_sd = 17
        elif sport in ["nfl", "cfb"]:
            base_sd = 11
        elif sport == "nhl":
            base_sd = 1.5
        else:
            base_sd = 12

        # Adjusted SD based on time remaining
        adjusted_sd = base_sd * math.sqrt(remaining_pct)

        # Z-score
        if adjusted_sd > 0:
            z = (target_total - regressed_projection) / adjusted_sd
        else:
            z = 0

        # Convert to probabilities (normal approximation)
        # P(Over) = P(Final > target_total)
        over_prob = self._normal_cdf(-z)  # Probability final exceeds target
        under_prob = 1 - over_prob

        # Calculate edges (vs 50% implied at -110)
        edge_over = over_prob - 0.524
        edge_under = under_prob - 0.524

        # Generate recommendation
        factors = []

        if abs(regressed_projection - target_total) > adjusted_sd:
            if regressed_projection > target_total:
                recommendation = f"OVER {target_total}"
                confidence = "HIGH"
                factors.append(f"Projected {regressed_projection:.1f} vs line {target_total}")
            else:
                recommendation = f"UNDER {target_total}"
                confidence = "HIGH"
                factors.append(f"Projected {regressed_projection:.1f} vs line {target_total}")
        elif abs(regressed_projection - target_total) > adjusted_sd * 0.5:
            if regressed_projection > target_total:
                recommendation = f"LEAN OVER {target_total}"
                confidence = "MEDIUM"
            else:
                recommendation = f"LEAN UNDER {target_total}"
                confidence = "MEDIUM"
            factors.append(f"Moderate edge detected")
        else:
            recommendation = "NO EDGE - Current pace matches line"
            confidence = "LOW"

        # Add context factors
        factors.append(f"Current pace: {pace_per_minute:.1f} pts/min")
        factors.append(f"Game {elapsed*100:.0f}% complete")

        return LivePaceAnalysis(
            current_total=current,
            elapsed_pct=elapsed,
            projected_final_total=round(regressed_projection, 1),
            pace_per_minute=round(pace_per_minute, 2),
            pre_game_total=pre_game_total,
            live_total=target_total,
            over_probability=round(over_prob, 3),
            under_probability=round(under_prob, 3),
            edge_over=round(edge_over * 100, 2),
            edge_under=round(edge_under * 100, 2),
            recommendation=recommendation,
            confidence=confidence,
            factors=factors,
        )

    def analyze_live_spread(
        self,
        state: LiveGameState,
        pre_game_spread: float,
        live_spread: Optional[float] = None,
    ) -> Dict:
        """
        Analyze live spread market.

        Considers current margin, time remaining, and expected scoring pace.
        """
        current_margin = state.current_margin
        elapsed = state.elapsed_pct
        remaining = 1 - elapsed

        target_spread = live_spread if live_spread else pre_game_spread

        # Expected points remaining for each team
        avg_pace = self.AVG_PACE.get(state.sport, 0.05)
        expected_points_remaining = avg_pace * state.time_remaining_seconds * 2  # Both teams

        # Home team expected final margin
        # Assume pace continues, plus small home advantage
        home_advantage_remaining = 0.5 * remaining  # Diminishing HCA
        expected_final_margin = current_margin + home_advantage_remaining

        # Does home cover the spread?
        # If spread is -5, home needs to win by more than 5
        cover_margin = expected_final_margin - (-target_spread)

        # SD for margin (roughly 10-15 points for full game, scaled by remaining)
        if state.sport in ["nba", "cbb"]:
            base_sd = 12
        elif state.sport in ["nfl", "cfb"]:
            base_sd = 10
        else:
            base_sd = 8

        adjusted_sd = base_sd * math.sqrt(remaining)

        if adjusted_sd > 0:
            z = cover_margin / adjusted_sd
            home_cover_prob = self._normal_cdf(z)
        else:
            home_cover_prob = 1.0 if cover_margin > 0 else 0.0

        away_cover_prob = 1 - home_cover_prob

        # Determine recommendation
        if home_cover_prob > 0.60:
            recommendation = f"{state.home_team} {target_spread}"
            edge = home_cover_prob - 0.524
        elif away_cover_prob > 0.60:
            recommendation = f"{state.away_team} +{abs(target_spread)}"
            edge = away_cover_prob - 0.524
        else:
            recommendation = "NO CLEAR EDGE"
            edge = 0

        return {
            "current_margin": current_margin,
            "pre_game_spread": pre_game_spread,
            "live_spread": target_spread,
            "expected_final_margin": round(expected_final_margin, 1),
            "home_cover_probability": round(home_cover_prob, 3),
            "away_cover_probability": round(away_cover_prob, 3),
            "recommendation": recommendation,
            "edge_pct": round(edge * 100, 2),
            "time_remaining": state.clock,
            "period": state.period,
        }

    def analyze_live_moneyline(
        self,
        state: LiveGameState,
        home_ml_odds: int,
        away_ml_odds: int,
    ) -> Dict:
        """
        Analyze live moneyline value.

        Calculates true win probability based on current state and time remaining.
        """
        margin = state.current_margin
        remaining = 1 - state.elapsed_pct

        # Base win probability from current margin
        # Each point of lead ≈ 2-3% win probability in basketball
        if state.sport in ["nba", "cbb"]:
            margin_factor = 0.025
        elif state.sport in ["nfl", "cfb"]:
            margin_factor = 0.04
        elif state.sport == "nhl":
            margin_factor = 0.15  # Goals matter more
        else:
            margin_factor = 0.03

        # Win probability increases as game progresses (less time for comeback)
        time_leverage = 1 + (1 - remaining) * 2  # More certain as game ends

        margin_impact = margin * margin_factor * time_leverage

        # Clamp probability
        base_prob = 0.5  # Even game assumption
        home_win_prob = max(0.02, min(0.98, base_prob + margin_impact))
        away_win_prob = 1 - home_win_prob

        # Calculate implied probabilities from odds
        home_implied = self._american_to_implied(home_ml_odds)
        away_implied = self._american_to_implied(away_ml_odds)

        # Find edges
        home_edge = home_win_prob - home_implied
        away_edge = away_win_prob - away_implied

        if home_edge > 0.05:
            recommendation = f"{state.home_team} ML"
            edge = home_edge
            bet_odds = home_ml_odds
        elif away_edge > 0.05:
            recommendation = f"{state.away_team} ML"
            edge = away_edge
            bet_odds = away_ml_odds
        else:
            recommendation = "NO EDGE"
            edge = 0
            bet_odds = 0

        return {
            "home_team": state.home_team,
            "away_team": state.away_team,
            "score": f"{state.home_score}-{state.away_score}",
            "home_win_probability": round(home_win_prob, 3),
            "away_win_probability": round(away_win_prob, 3),
            "home_implied": round(home_implied, 3),
            "away_implied": round(away_implied, 3),
            "home_edge_pct": round(home_edge * 100, 2),
            "away_edge_pct": round(away_edge * 100, 2),
            "recommendation": recommendation,
            "edge_pct": round(edge * 100, 2),
            "bet_odds": bet_odds,
        }

    def get_live_suggestions(
        self,
        games: List[Dict],
        sport: str,
    ) -> List[LiveSuggestion]:
        """
        Get all live betting suggestions for a list of games.

        Returns actionable suggestions sorted by edge.
        """
        suggestions = []
        timestamp = datetime.now().isoformat()

        for game in games:
            state = self.parse_game_state(sport, game)

            # Skip if game just started or nearly over
            if state.elapsed_pct < 0.1 or state.elapsed_pct > 0.95:
                continue

            odds = game.get("odds", {})
            if not odds:
                continue

            # Analyze totals
            pre_total = odds.get("over_under")
            if pre_total:
                try:
                    pre_total = float(pre_total)
                    total_analysis = self.analyze_live_total(state, pre_total)

                    if total_analysis.confidence in ["HIGH", "MEDIUM"]:
                        edge = max(total_analysis.edge_over, total_analysis.edge_under)
                        if edge > 3:  # Minimum 3% edge
                            suggestions.append(LiveSuggestion(
                                game_id=state.game_id,
                                game_name=f"{state.away_team} @ {state.home_team}",
                                sport=sport.upper(),
                                market="Live Total",
                                selection=total_analysis.recommendation,
                                current_odds=-110,
                                edge_pct=edge,
                                true_probability=max(total_analysis.over_probability,
                                                    total_analysis.under_probability),
                                confidence=total_analysis.confidence,
                                rationale="; ".join(total_analysis.factors),
                                time_sensitivity="ACT NOW" if total_analysis.confidence == "HIGH" else "MONITOR",
                                verification_notes=[
                                    f"Current: {state.current_total}",
                                    f"Projected: {total_analysis.projected_final_total}",
                                    f"Line: {pre_total}",
                                ],
                                detected_at=timestamp,
                            ))
                except (ValueError, TypeError):
                    pass

            # Analyze spread
            spread = odds.get("spread")
            if spread:
                try:
                    spread_val = float(spread)
                    spread_analysis = self.analyze_live_spread(state, spread_val)

                    if spread_analysis["edge_pct"] > 5:
                        suggestions.append(LiveSuggestion(
                            game_id=state.game_id,
                            game_name=f"{state.away_team} @ {state.home_team}",
                            sport=sport.upper(),
                            market="Live Spread",
                            selection=spread_analysis["recommendation"],
                            current_odds=-110,
                            edge_pct=spread_analysis["edge_pct"],
                            true_probability=max(spread_analysis["home_cover_probability"],
                                                spread_analysis["away_cover_probability"]),
                            confidence="HIGH" if spread_analysis["edge_pct"] > 8 else "MEDIUM",
                            rationale=f"Current margin: {spread_analysis['current_margin']}, "
                                     f"Expected final: {spread_analysis['expected_final_margin']}",
                            time_sensitivity="ACT NOW",
                            verification_notes=[
                                f"Score: {state.home_score}-{state.away_score}",
                                f"Period {state.period}, {state.clock}",
                            ],
                            detected_at=timestamp,
                        ))
                except (ValueError, TypeError):
                    pass

            # Analyze moneyline
            home_ml = odds.get("home_moneyline")
            away_ml = odds.get("away_moneyline")
            if home_ml and away_ml:
                ml_analysis = self.analyze_live_moneyline(state, home_ml, away_ml)

                if ml_analysis["edge_pct"] > 5:
                    suggestions.append(LiveSuggestion(
                        game_id=state.game_id,
                        game_name=f"{state.away_team} @ {state.home_team}",
                        sport=sport.upper(),
                        market="Live Moneyline",
                        selection=ml_analysis["recommendation"],
                        current_odds=ml_analysis["bet_odds"],
                        edge_pct=ml_analysis["edge_pct"],
                        true_probability=max(ml_analysis["home_win_probability"],
                                            ml_analysis["away_win_probability"]),
                        confidence="HIGH" if ml_analysis["edge_pct"] > 10 else "MEDIUM",
                        rationale=f"Score: {ml_analysis['score']}, "
                                 f"Win prob: {ml_analysis['home_win_probability']*100:.1f}%",
                        time_sensitivity="ACT NOW",
                        verification_notes=[
                            f"Home implied: {ml_analysis['home_implied']*100:.1f}%",
                            f"Our calc: {ml_analysis['home_win_probability']*100:.1f}%",
                        ],
                        detected_at=timestamp,
                    ))

        # Sort by edge
        suggestions.sort(key=lambda x: x.edge_pct, reverse=True)

        return suggestions

    @staticmethod
    def _normal_cdf(z: float) -> float:
        """Approximate normal CDF using error function approximation."""
        # Simple approximation
        t = 1 / (1 + 0.2316419 * abs(z))
        d = 0.3989423 * math.exp(-z * z / 2)
        p = d * t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274))))
        return 1 - p if z > 0 else p

    @staticmethod
    def _american_to_implied(odds: int) -> float:
        """Convert American odds to implied probability."""
        if odds > 0:
            return 100 / (odds + 100)
        else:
            return abs(odds) / (abs(odds) + 100)
