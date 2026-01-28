"""
Edge Detection Engine
Scans markets to find betting edges in real-time
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from ..api.espn import ESPNClient
from ..api.odds import OddsClient, ScoringMarketAnalyzer, MarketType
from ..verification.engine import VerificationEngine
from ..analytics.sports import (
    NFLAnalytics, NBAAnalytics, CFBAnalytics, CBBAnalytics, NHLAnalytics
)
from .confidence import ConfidenceEngine, BetRecommendation


@dataclass
class EdgeOpportunity:
    """Represents a detected edge opportunity."""
    sport: str
    game_id: str
    game_name: str
    market_type: str
    selection: str
    edge_pct: float
    true_prob: float
    market_prob: float
    odds: int
    confidence: float
    grade: str
    recommendation: BetRecommendation
    verification_summary: str
    detected_at: str


class EdgeDetector:
    """
    Main edge detection engine.
    Scans ESPN live data and finds betting opportunities.
    """

    SPORT_ANALYTICS = {
        "nfl": NFLAnalytics,
        "nba": NBAAnalytics,
        "cfb": CFBAnalytics,
        "cbb": CBBAnalytics,
        "nhl": NHLAnalytics,
    }

    def __init__(self, odds_api_key: Optional[str] = None):
        self.espn = ESPNClient()
        self.odds = OddsClient(api_key=odds_api_key)
        self.verification = VerificationEngine()
        self.confidence = ConfidenceEngine()
        self.scoring_analyzer = ScoringMarketAnalyzer()

    def scan_sport(self, sport: str, market_types: Optional[List[str]] = None) -> List[EdgeOpportunity]:
        """
        Scan a sport for edge opportunities.

        Args:
            sport: nfl, nba, cfb, cbb, nhl
            market_types: Optional list of markets to scan (spread, total, moneyline)

        Returns:
            List of EdgeOpportunity objects sorted by edge
        """
        if market_types is None:
            market_types = ["moneyline", "spread", "total"]

        edges = []
        timestamp = datetime.now().isoformat()

        # Get analytics engine for this sport
        analytics_class = self.SPORT_ANALYTICS.get(sport.lower())
        if not analytics_class:
            return edges
        analytics = analytics_class()

        # Fetch upcoming games
        scoreboard = self.espn.get_scoreboard(sport)
        games = self.espn.parse_scoreboard(scoreboard)

        for game in games:
            if game["status"]["state"] not in ["pre", "in"]:
                continue

            game_edges = self._analyze_game(
                sport, game, analytics, market_types, timestamp
            )
            edges.extend(game_edges)

        # Sort by edge percentage descending
        edges.sort(key=lambda x: x.edge_pct, reverse=True)

        return edges

    def scan_all_sports(self) -> Dict[str, List[EdgeOpportunity]]:
        """Scan all supported sports for edges."""
        results = {}
        for sport in self.SPORT_ANALYTICS.keys():
            edges = self.scan_sport(sport)
            if edges:
                results[sport] = edges
        return results

    def _analyze_game(
        self,
        sport: str,
        game: Dict,
        analytics,
        market_types: List[str],
        timestamp: str
    ) -> List[EdgeOpportunity]:
        """Analyze a single game for edges across market types."""
        edges = []

        home = game.get("home_team", {})
        away = game.get("away_team", {})
        odds = game.get("odds", {})

        if not home or not away:
            return edges

        # Get injuries for context
        home_injuries = self.espn.get_team_injuries(sport, home.get("id", ""))
        away_injuries = self.espn.get_team_injuries(sport, away.get("id", ""))

        # Analyze moneyline
        if "moneyline" in market_types and odds:
            ml_edge = self._analyze_moneyline(
                sport, game, home, away, odds, analytics, timestamp,
                home_injuries, away_injuries
            )
            if ml_edge:
                edges.append(ml_edge)

        # Analyze spread
        if "spread" in market_types and odds and odds.get("spread"):
            spread_edge = self._analyze_spread(
                sport, game, home, away, odds, analytics, timestamp
            )
            if spread_edge:
                edges.append(spread_edge)

        # Analyze totals (scoring markets)
        if "total" in market_types and odds and odds.get("over_under"):
            total_edges = self._analyze_total(
                sport, game, home, away, odds, analytics, timestamp
            )
            edges.extend(total_edges)

        return edges

    def _analyze_moneyline(
        self,
        sport: str,
        game: Dict,
        home: Dict,
        away: Dict,
        odds: Dict,
        analytics,
        timestamp: str,
        home_injuries: List,
        away_injuries: List,
    ) -> Optional[EdgeOpportunity]:
        """Analyze moneyline market for edge."""
        home_ml = odds.get("home_moneyline")
        away_ml = odds.get("away_moneyline")

        if not home_ml or not away_ml:
            return None

        # Calculate true probability using analytics
        home_stats = {"power_rating": 0, "net_rating": 0}  # Would be populated from real data
        away_stats = {"power_rating": 0, "net_rating": 0}

        true_prob_home = analytics.calculate_win_probability(home_stats, away_stats)

        # Calculate market implied
        market_prob_home = self._american_to_implied(home_ml)

        # Calculate edge
        edge = true_prob_home - market_prob_home

        # Run verification
        verification_result = self.verification.run_full_verification(
            sport=sport,
            event_id=game.get("game_id", ""),
            espn_data=game,
            odds_data=odds,
            injury_data=home_injuries + away_injuries,
            true_prob=true_prob_home,
            market_prob=market_prob_home,
        )

        # Generate CE% inputs
        ce_inputs = {
            "source_agreement": 0.7 if verification_result.passed else 0.3,
            "freshness": 1.0 if game["status"]["state"] == "pre" else 0.8,
            "liquidity": 0.8,
            "resolution_clarity": 1.0,
            "volatility": 0.1,
        }

        # Determine which side to bet
        if edge > 0.05:  # Edge on home
            selection = home.get("name", "Home")
            bet_odds = home_ml
            true_prob = true_prob_home
            market_prob = market_prob_home
        elif (1 - true_prob_home) - (1 - market_prob_home) > 0.05:  # Edge on away
            selection = away.get("name", "Away")
            bet_odds = away_ml
            true_prob = 1 - true_prob_home
            market_prob = 1 - market_prob_home
            edge = true_prob - market_prob
        else:
            return None  # No edge

        # Generate recommendation
        recommendation = self.confidence.generate_recommendation(
            selection=selection,
            market_type="Moneyline",
            odds=bet_odds,
            true_probability=true_prob,
            verification_passed=verification_result.passed,
            ce_inputs=ce_inputs,
            timestamp=timestamp,
        )

        if recommendation.recommendation == "PASS":
            return None

        return EdgeOpportunity(
            sport=sport.upper(),
            game_id=game.get("game_id", ""),
            game_name=game.get("name", ""),
            market_type="Moneyline",
            selection=selection,
            edge_pct=round(edge * 100, 2),
            true_prob=round(true_prob, 3),
            market_prob=round(market_prob, 3),
            odds=bet_odds,
            confidence=recommendation.ce_pct,
            grade=recommendation.grade.value,
            recommendation=recommendation,
            verification_summary=verification_result.get_summary(),
            detected_at=timestamp,
        )

    def _analyze_spread(
        self,
        sport: str,
        game: Dict,
        home: Dict,
        away: Dict,
        odds: Dict,
        analytics,
        timestamp: str,
    ) -> Optional[EdgeOpportunity]:
        """Analyze spread market for edge."""
        spread = odds.get("spread")
        if not spread:
            return None

        try:
            spread_value = float(spread)
        except (ValueError, TypeError):
            return None

        # Calculate expected margin using analytics
        # For now, simplified calculation
        home_stats = {}
        away_stats = {}
        matchup = analytics.analyze_matchup(home_stats, away_stats)

        expected_margin = matchup.get("expected_margin", 0)

        # Compare to spread
        spread_diff = expected_margin - (-spread_value)  # Negative because spread is from home perspective

        if abs(spread_diff) < 2:  # Less than 2 point difference
            return None

        # Determine which side has value
        if spread_diff > 2:  # Home covering
            selection = f"{home.get('name', 'Home')} {spread_value}"
            edge = min(0.15, spread_diff * 0.03)  # Rough conversion
        else:  # Away covering
            selection = f"{away.get('name', 'Away')} +{-spread_value}"
            edge = min(0.15, abs(spread_diff) * 0.03)

        if edge < 0.05:
            return None

        # Generate recommendation
        ce_inputs = {
            "source_agreement": 0.7,
            "freshness": 0.9,
            "liquidity": 0.8,
            "resolution_clarity": 1.0,
            "volatility": 0.15,
        }

        recommendation = self.confidence.generate_recommendation(
            selection=selection,
            market_type="Spread",
            odds=-110,  # Standard spread juice
            true_probability=0.5 + edge,
            verification_passed=True,
            ce_inputs=ce_inputs,
            timestamp=timestamp,
        )

        if recommendation.recommendation == "PASS":
            return None

        return EdgeOpportunity(
            sport=sport.upper(),
            game_id=game.get("game_id", ""),
            game_name=game.get("name", ""),
            market_type="Spread",
            selection=selection,
            edge_pct=round(edge * 100, 2),
            true_prob=round(0.5 + edge, 3),
            market_prob=0.524,  # -110 implied
            odds=-110,
            confidence=recommendation.ce_pct,
            grade=recommendation.grade.value,
            recommendation=recommendation,
            verification_summary="Spread analysis complete",
            detected_at=timestamp,
        )

    def _analyze_total(
        self,
        sport: str,
        game: Dict,
        home: Dict,
        away: Dict,
        odds: Dict,
        analytics,
        timestamp: str,
    ) -> List[EdgeOpportunity]:
        """Analyze totals (over/under) market for edge."""
        edges = []

        total = odds.get("over_under")
        if not total:
            return edges

        try:
            posted_total = float(total)
        except (ValueError, TypeError):
            return edges

        # Get team scoring data (simplified - would use real stats)
        home_ppg = 110.0  # Placeholder
        away_ppg = 108.0
        home_def = 112.0
        away_def = 110.0

        # Weather for outdoor sports
        weather = game.get("weather")

        # Analyze using scoring market analyzer
        analysis = self.scoring_analyzer.analyze_total(
            sport=sport,
            home_team_avg=home_ppg,
            away_team_avg=away_ppg,
            home_def_avg=home_def,
            away_def_avg=away_def,
            posted_total=posted_total,
            weather=weather,
        )

        if analysis["recommendation"] == "PASS":
            return edges

        # Create edge opportunity
        selection = f"{'OVER' if analysis['recommendation'] == 'OVER' else 'UNDER'} {posted_total}"
        edge = analysis["edge_pct"] / 100

        if edge < 0.05:
            return edges

        ce_inputs = {
            "source_agreement": 0.8,
            "freshness": 0.9,
            "liquidity": 0.9,
            "resolution_clarity": 1.0,
            "volatility": 0.1 if analysis["confidence"] == "HIGH" else 0.2,
        }

        recommendation = self.confidence.generate_recommendation(
            selection=selection,
            market_type="Total",
            odds=-110,
            true_probability=0.5 + edge,
            verification_passed=True,
            ce_inputs=ce_inputs,
            timestamp=timestamp,
        )

        if recommendation.recommendation == "BET":
            edges.append(EdgeOpportunity(
                sport=sport.upper(),
                game_id=game.get("game_id", ""),
                game_name=game.get("name", ""),
                market_type="Total",
                selection=selection,
                edge_pct=round(edge * 100, 2),
                true_prob=round(0.5 + edge, 3),
                market_prob=0.524,
                odds=-110,
                confidence=recommendation.ce_pct,
                grade=recommendation.grade.value,
                recommendation=recommendation,
                verification_summary=f"Projected: {analysis['projected_total']} vs Line: {posted_total}",
                detected_at=timestamp,
            ))

        return edges

    def find_live_edges(self, sport: str) -> List[EdgeOpportunity]:
        """Find edges in live/in-game markets."""
        edges = []
        timestamp = datetime.now().isoformat()

        live_games = self.espn.get_live_games(sport)

        for game in live_games:
            # Get game details for live analysis
            details = self.espn.get_game_details(sport, game.get("game_id", ""))

            # Analyze live situations
            # This would include:
            # - Current score vs expected pace
            # - Time-adjusted totals
            # - Live spread movements
            # - Player prop updates

        return edges

    @staticmethod
    def _american_to_implied(odds: int) -> float:
        """Convert American odds to implied probability."""
        if odds > 0:
            return 100 / (odds + 100)
        else:
            return abs(odds) / (abs(odds) + 100)
