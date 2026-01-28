"""
Sport-Specific Analytics Calculators
DVOA, EPA, KenPom, Corsi, xG and more explained and calculated
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from abc import ABC, abstractmethod
import math


@dataclass
class TeamStats:
    """Universal team statistics container."""
    team_id: str
    team_name: str
    wins: int = 0
    losses: int = 0
    points_for: float = 0.0
    points_against: float = 0.0
    home_record: str = ""
    away_record: str = ""
    streak: str = ""
    # Sport-specific will add more


@dataclass
class AnalysisResult:
    """Result of analytics calculation."""
    metric_name: str
    value: float
    interpretation: str
    edge_implication: str
    education: str  # Explanation for user learning


class SportAnalytics(ABC):
    """Base class for sport-specific analytics."""

    @abstractmethod
    def calculate_win_probability(self, home_team: Dict, away_team: Dict) -> float:
        """Calculate win probability for home team."""
        pass

    @abstractmethod
    def get_key_metrics(self, team: Dict) -> List[AnalysisResult]:
        """Get key analytical metrics for a team."""
        pass

    @abstractmethod
    def analyze_matchup(self, home: Dict, away: Dict) -> Dict:
        """Full matchup analysis."""
        pass


class NFLAnalytics(SportAnalytics):
    """
    NFL Analytics Engine
    Metrics: DVOA, EPA, Success Rate, Yards per Play
    """

    # League averages (2024 season estimates)
    LEAGUE_AVG_POINTS = 21.8
    LEAGUE_AVG_YARDS = 330
    LEAGUE_AVG_EPA = 0.0  # By definition

    def calculate_win_probability(self, home_team: Dict, away_team: Dict) -> float:
        """
        Calculate win probability using power ratings.

        Formula: Win% = 1 / (1 + 10^((away_rating - home_rating - HFA) / 10))

        Home Field Advantage (HFA) = ~2.5 points historically, declining in recent years
        """
        home_rating = home_team.get("power_rating", 0)
        away_rating = away_team.get("power_rating", 0)
        hfa = 2.5  # Home field advantage in points

        # Convert point spread to win probability
        spread = home_rating - away_rating + hfa
        # Using logistic approximation
        win_prob = 1 / (1 + math.exp(-spread / 6))

        return round(win_prob, 3)

    def calculate_dvoa(self, team_stats: Dict) -> AnalysisResult:
        """
        Calculate/interpret DVOA (Defense-adjusted Value Over Average).

        DVOA measures play-by-play efficiency adjusted for opponent and situation.

        Interpretation:
        - +10% = Team is 10% better than league average
        - For offense: POSITIVE is better
        - For defense: NEGATIVE is better (allowing fewer points)
        """
        # In practice, DVOA requires play-by-play data
        # This is a simplified proxy using available stats
        points_per_game = team_stats.get("points_per_game", self.LEAGUE_AVG_POINTS)
        points_allowed = team_stats.get("points_allowed", self.LEAGUE_AVG_POINTS)

        # Simplified efficiency calculation
        off_efficiency = (points_per_game - self.LEAGUE_AVG_POINTS) / self.LEAGUE_AVG_POINTS
        def_efficiency = (self.LEAGUE_AVG_POINTS - points_allowed) / self.LEAGUE_AVG_POINTS

        total_dvoa = (off_efficiency + def_efficiency) * 50  # Scale to percentage

        if total_dvoa > 15:
            interpretation = "ELITE - Top 5 team"
        elif total_dvoa > 5:
            interpretation = "ABOVE AVERAGE - Playoff caliber"
        elif total_dvoa > -5:
            interpretation = "AVERAGE"
        elif total_dvoa > -15:
            interpretation = "BELOW AVERAGE - Struggling"
        else:
            interpretation = "POOR - Bottom tier"

        return AnalysisResult(
            metric_name="DVOA (Simplified)",
            value=round(total_dvoa, 1),
            interpretation=interpretation,
            edge_implication="Teams with elite DVOA but mediocre records are undervalued",
            education=(
                "DVOA (Defense-adjusted Value Over Average) measures efficiency on every play, "
                "adjusted for opponent strength and game situation. A 6-4 team with +15% DVOA "
                "is better than their record suggests and likely to improve."
            )
        )

    def calculate_epa(self, play_data: Dict) -> AnalysisResult:
        """
        Calculate/interpret EPA (Expected Points Added).

        EPA measures how each play changes the expected points based on situation.
        """
        # Simplified EPA estimate
        yards_per_play = play_data.get("yards_per_play", 5.5)
        success_rate = play_data.get("success_rate", 0.45)

        # EPA correlates with yards per play and success rate
        epa_estimate = (yards_per_play - 5.5) * 0.1 + (success_rate - 0.45) * 2

        if epa_estimate > 0.15:
            interpretation = "ELITE offense"
        elif epa_estimate > 0.05:
            interpretation = "Above average"
        elif epa_estimate > -0.05:
            interpretation = "League average"
        else:
            interpretation = "Below average"

        return AnalysisResult(
            metric_name="EPA/Play Estimate",
            value=round(epa_estimate, 3),
            interpretation=interpretation,
            edge_implication="High EPA teams are efficient; look for mismatches vs low EPA defenses",
            education=(
                "EPA (Expected Points Added) measures how each play changes expected points. "
                "A 15-yard gain on 3rd-and-10 adds more EPA than the same gain on 1st-and-10 "
                "because it sustains a drive. EPA captures quality over quantity."
            )
        )

    def weather_adjustment(self, weather: Dict) -> Dict:
        """
        Calculate weather impact on scoring.

        Wind >15 mph: -10% passing, +8% INTs
        Wind >20 mph: Effects double
        Heavy rain: Totals -6 points
        Snow: Totals -10 points
        """
        adjustments = {
            "total_adjustment": 0,
            "passing_adjustment": 0,
            "factors": []
        }

        wind = weather.get("wind_speed", 0)
        condition = weather.get("condition", "").lower()
        temp = weather.get("temperature", 70)

        if wind and wind > 15:
            wind_factor = -3 * (wind / 15)
            adjustments["total_adjustment"] += wind_factor
            adjustments["passing_adjustment"] = -10 * (wind / 15)
            adjustments["factors"].append(f"Wind {wind}mph: {wind_factor:.1f} points")

        if "rain" in condition or "storm" in condition:
            adjustments["total_adjustment"] -= 6
            adjustments["factors"].append("Rain/Storm: -6 points")

        if "snow" in condition:
            adjustments["total_adjustment"] -= 10
            adjustments["factors"].append("Snow: -10 points")

        if temp and temp < 32:
            cold_factor = (32 - temp) / 10
            adjustments["total_adjustment"] -= cold_factor
            adjustments["factors"].append(f"Cold ({temp}F): -{cold_factor:.1f} points")

        return adjustments

    def get_key_metrics(self, team: Dict) -> List[AnalysisResult]:
        """Get key NFL metrics for a team."""
        metrics = []
        metrics.append(self.calculate_dvoa(team))
        metrics.append(self.calculate_epa(team))
        return metrics

    def analyze_matchup(self, home: Dict, away: Dict) -> Dict:
        """Full NFL matchup analysis."""
        win_prob = self.calculate_win_probability(home, away)
        home_metrics = self.get_key_metrics(home)
        away_metrics = self.get_key_metrics(away)

        return {
            "home_win_probability": win_prob,
            "away_win_probability": 1 - win_prob,
            "home_metrics": [m.__dict__ for m in home_metrics],
            "away_metrics": [m.__dict__ for m in away_metrics],
            "key_matchups": [],
            "injury_impact": [],
        }


class NBAAnalytics(SportAnalytics):
    """
    NBA Analytics Engine
    Metrics: Net Rating, Pace, eFG%, True Shooting, Rest Advantage
    """

    LEAGUE_AVG_PACE = 100.3
    LEAGUE_AVG_ORTG = 114.2
    LEAGUE_AVG_DRTG = 114.2

    # Rest advantage values
    REST_ADVANTAGES = {
        (2, 0): 3.0,   # 2+ days rest vs B2B
        (1, 0): 2.0,   # 1 day rest vs B2B
        (2, 1): 1.5,   # 2+ days vs 1 day
        (0, 2): -3.0,  # B2B vs 2+ days rest
    }

    def calculate_win_probability(self, home_team: Dict, away_team: Dict) -> float:
        """
        Calculate NBA win probability using net rating and rest.

        Net Rating is the best single predictor of team quality.
        """
        home_net = home_team.get("net_rating", 0)
        away_net = away_team.get("net_rating", 0)

        # Home court advantage ~2.5 points
        hca = 2.5

        # Rest advantage
        home_rest = home_team.get("days_rest", 1)
        away_rest = away_team.get("days_rest", 1)
        rest_adj = self._calculate_rest_adjustment(home_rest, away_rest)

        # Net rating difference + adjustments
        diff = home_net - away_net + hca + rest_adj

        # Convert to probability (each point ~3% win probability)
        win_prob = 0.5 + (diff * 0.03)
        win_prob = max(0.05, min(0.95, win_prob))

        return round(win_prob, 3)

    def _calculate_rest_adjustment(self, home_rest: int, away_rest: int) -> float:
        """Calculate rest advantage in points."""
        # B2B = 0 days rest
        if home_rest >= 2 and away_rest == 0:
            return 3.0
        elif home_rest >= 1 and away_rest == 0:
            return 2.0
        elif home_rest == 0 and away_rest >= 2:
            return -3.0
        elif home_rest == 0 and away_rest >= 1:
            return -2.0
        return 0.0

    def calculate_pace_impact(self, team1_pace: float, team2_pace: float) -> Dict:
        """
        Calculate expected game pace and its implications.

        High pace = more possessions = more variance = higher totals
        """
        expected_pace = (team1_pace + team2_pace) / 2
        pace_vs_league = expected_pace - self.LEAGUE_AVG_PACE

        if expected_pace > 104:
            style = "FAST - High scoring likely"
            total_adjustment = +5
        elif expected_pace > 100:
            style = "MODERATE pace"
            total_adjustment = 0
        else:
            style = "SLOW - Grind-it-out game"
            total_adjustment = -5

        return {
            "expected_pace": round(expected_pace, 1),
            "pace_vs_league": round(pace_vs_league, 1),
            "style": style,
            "total_adjustment": total_adjustment,
            "education": (
                "Pace measures possessions per 48 minutes. Higher pace = more shots = "
                "more points AND more variance. Two fast teams (108+ pace each) create "
                "high-scoring games; two slow teams create unders."
            )
        }

    def calculate_net_rating(self, team_stats: Dict) -> AnalysisResult:
        """
        Calculate and interpret Net Rating.

        Net Rating = Offensive Rating - Defensive Rating
        Best single predictor of team quality.
        """
        ortg = team_stats.get("offensive_rating", self.LEAGUE_AVG_ORTG)
        drtg = team_stats.get("defensive_rating", self.LEAGUE_AVG_DRTG)
        net = ortg - drtg

        if net > 8:
            interpretation = "ELITE - Championship contender"
        elif net > 4:
            interpretation = "Very good - Deep playoff team"
        elif net > 0:
            interpretation = "Above average - Playoff team"
        elif net > -4:
            interpretation = "Below average - Play-in territory"
        else:
            interpretation = "Poor - Lottery team"

        return AnalysisResult(
            metric_name="Net Rating",
            value=round(net, 1),
            interpretation=interpretation,
            edge_implication="High net rating with bad record = buy low opportunity",
            education=(
                "Net Rating = Offensive Rating - Defensive Rating (points per 100 possessions). "
                "A +8 net rating team should win ~65% of games long-term. If their actual record "
                "is worse, they're due for positive regression—this is where value lives."
            )
        )

    def get_key_metrics(self, team: Dict) -> List[AnalysisResult]:
        """Get key NBA metrics."""
        return [self.calculate_net_rating(team)]

    def analyze_matchup(self, home: Dict, away: Dict) -> Dict:
        """Full NBA matchup analysis."""
        win_prob = self.calculate_win_probability(home, away)

        pace_analysis = self.calculate_pace_impact(
            home.get("pace", self.LEAGUE_AVG_PACE),
            away.get("pace", self.LEAGUE_AVG_PACE)
        )

        return {
            "home_win_probability": win_prob,
            "away_win_probability": 1 - win_prob,
            "pace_analysis": pace_analysis,
            "rest_situation": {
                "home_rest": home.get("days_rest"),
                "away_rest": away.get("days_rest"),
            },
            "home_metrics": [m.__dict__ for m in self.get_key_metrics(home)],
            "away_metrics": [m.__dict__ for m in self.get_key_metrics(away)],
        }


class CFBAnalytics(SportAnalytics):
    """
    College Football Analytics
    Metrics: SP+, FPI, Strength of Schedule
    """

    def calculate_win_probability(self, home_team: Dict, away_team: Dict) -> float:
        """Calculate CFB win probability using SP+/FPI ratings."""
        home_rating = home_team.get("sp_plus", 0)
        away_rating = away_team.get("sp_plus", 0)
        hfa = 3.0  # CFB home field is stronger than NFL

        spread = home_rating - away_rating + hfa
        win_prob = 1 / (1 + math.exp(-spread / 7))

        return round(win_prob, 3)

    def get_key_metrics(self, team: Dict) -> List[AnalysisResult]:
        """Get key CFB metrics."""
        sp_plus = team.get("sp_plus", 0)

        if sp_plus > 20:
            interp = "Elite - Playoff contender"
        elif sp_plus > 10:
            interp = "Very good - NY6 bowl level"
        elif sp_plus > 0:
            interp = "Above average"
        else:
            interp = "Below average"

        return [AnalysisResult(
            metric_name="SP+ Rating",
            value=sp_plus,
            interpretation=interp,
            edge_implication="SP+ is PREDICTIVE, not resume-based. A team can win ugly and drop.",
            education=(
                "SP+ (Bill Connelly, ESPN) is a tempo- and opponent-adjusted efficiency rating. "
                "Unlike polls, SP+ doesn't care about close wins—it measures HOW you played. "
                "A team winning 35-34 in garbage time gets penalized; this creates betting value."
            )
        )]

    def analyze_matchup(self, home: Dict, away: Dict) -> Dict:
        """Full CFB matchup analysis."""
        return {
            "home_win_probability": self.calculate_win_probability(home, away),
            "away_win_probability": 1 - self.calculate_win_probability(home, away),
            "home_metrics": [m.__dict__ for m in self.get_key_metrics(home)],
            "away_metrics": [m.__dict__ for m in self.get_key_metrics(away)],
        }


class CBBAnalytics(SportAnalytics):
    """
    College Basketball Analytics
    Metrics: KenPom AdjEM, BartTorvik, NET Rankings
    """

    # Home court advantages by conference
    HCA_BY_CONFERENCE = {
        "Big 12": 5.5,
        "Big Ten": 4.0,
        "SEC": 4.0,
        "ACC": 3.1,
        "Big East": 4.2,
        "default": 3.5,
    }

    def calculate_win_probability(self, home_team: Dict, away_team: Dict) -> float:
        """Calculate CBB win probability using KenPom AdjEM."""
        home_em = home_team.get("adj_em", 0)
        away_em = away_team.get("adj_em", 0)

        conference = home_team.get("conference", "default")
        hca = self.HCA_BY_CONFERENCE.get(conference, 3.5)

        diff = home_em - away_em + hca
        win_prob = 1 / (1 + math.exp(-diff / 11))

        return round(win_prob, 3)

    def calculate_kenpom(self, team_stats: Dict) -> AnalysisResult:
        """
        Interpret KenPom Adjusted Efficiency Margin.

        AdjEM = AdjO - AdjD
        - AdjO: Points per 100 possessions vs average defense
        - AdjD: Points allowed per 100 possessions vs average offense
        """
        adj_em = team_stats.get("adj_em", 0)
        adj_o = team_stats.get("adj_o", 100)
        adj_d = team_stats.get("adj_d", 100)

        if adj_em > 25:
            interp = "ELITE - Final Four caliber"
        elif adj_em > 15:
            interp = "Very good - Sweet 16 level"
        elif adj_em > 5:
            interp = "Tournament team"
        elif adj_em > 0:
            interp = "Bubble team"
        else:
            interp = "Below average"

        return AnalysisResult(
            metric_name="KenPom AdjEM",
            value=round(adj_em, 1),
            interpretation=interp,
            edge_implication="Compare AdjEM to betting line implied margin",
            education=(
                "KenPom's Adjusted Efficiency Margin (AdjEM) = Adjusted Offense - Adjusted Defense, "
                "both measured as points per 100 possessions against an average opponent. "
                "AdjEM difference between teams approximates the expected margin of victory. "
                "If KenPom says Team A is 10 points better but the line is -6, there's value on A."
            )
        )

    def get_key_metrics(self, team: Dict) -> List[AnalysisResult]:
        """Get key CBB metrics."""
        return [self.calculate_kenpom(team)]

    def analyze_matchup(self, home: Dict, away: Dict) -> Dict:
        """Full CBB matchup analysis."""
        win_prob = self.calculate_win_probability(home, away)

        # Calculate expected margin
        home_em = home.get("adj_em", 0)
        away_em = away.get("adj_em", 0)
        conference = home.get("conference", "default")
        hca = self.HCA_BY_CONFERENCE.get(conference, 3.5)

        expected_margin = home_em - away_em + hca

        return {
            "home_win_probability": win_prob,
            "away_win_probability": 1 - win_prob,
            "expected_margin": round(expected_margin, 1),
            "home_court_value": hca,
            "home_metrics": [m.__dict__ for m in self.get_key_metrics(home)],
            "away_metrics": [m.__dict__ for m in self.get_key_metrics(away)],
        }


class NHLAnalytics(SportAnalytics):
    """
    NHL Analytics Engine
    Metrics: Corsi, Fenwick, Expected Goals (xG), GSAx
    """

    LEAGUE_AVG_GOALS = 3.1

    def calculate_win_probability(self, home_team: Dict, away_team: Dict) -> float:
        """Calculate NHL win probability using xG differential."""
        home_xgf = home_team.get("xgf_per_60", 2.8)
        home_xga = home_team.get("xga_per_60", 2.8)
        away_xgf = away_team.get("xgf_per_60", 2.8)
        away_xga = away_team.get("xga_per_60", 2.8)

        # Home ice advantage ~0.15 goals
        hia = 0.15

        home_expected = (home_xgf + away_xga) / 2 + hia
        away_expected = (away_xgf + home_xga) / 2

        # Convert to win probability using Poisson-ish approximation
        goal_diff = home_expected - away_expected
        win_prob = 0.5 + (goal_diff * 0.15)
        win_prob = max(0.3, min(0.7, win_prob))

        return round(win_prob, 3)

    def calculate_corsi(self, team_stats: Dict) -> AnalysisResult:
        """
        Calculate/interpret Corsi (CF%).

        Corsi = Shot attempts including shots, misses, blocks
        CF% = Corsi For / (Corsi For + Corsi Against)
        CF% > 55% = Elite possession team
        """
        cf_pct = team_stats.get("corsi_pct", 50.0)

        if cf_pct > 55:
            interp = "ELITE possession - controlling play"
        elif cf_pct > 52:
            interp = "Above average - solid possession team"
        elif cf_pct > 48:
            interp = "Average"
        else:
            interp = "Below average - getting outplayed"

        return AnalysisResult(
            metric_name="Corsi For %",
            value=round(cf_pct, 1),
            interpretation=interp,
            edge_implication="High CF% teams with low goals = positive regression candidate",
            education=(
                "Corsi counts ALL shot attempts (goals, saves, misses, blocks). "
                "A team with 55% Corsi is generating 55% of total shot attempts—they're "
                "controlling play. If they're not scoring, that's bad luck, not bad play. "
                "Bet on them to improve."
            )
        )

    def calculate_xg(self, team_stats: Dict) -> AnalysisResult:
        """
        Calculate/interpret Expected Goals (xG).

        xG assigns probability (0-1) to each shot based on:
        - Shot distance and angle
        - Shot type (wrist, slap, etc.)
        - Pre-shot movement (pass, rebound)
        """
        xgf = team_stats.get("xgf_per_60", 2.8)
        xga = team_stats.get("xga_per_60", 2.8)
        xg_diff = xgf - xga

        actual_gf = team_stats.get("gf_per_60", xgf)
        actual_ga = team_stats.get("ga_per_60", xga)

        # Check for under/over performance
        luck_factor = (actual_gf - xgf) - (actual_ga - xga)

        if luck_factor > 0.3:
            luck_assessment = "OVERPERFORMING - regression down likely"
        elif luck_factor < -0.3:
            luck_assessment = "UNDERPERFORMING - regression UP likely (BET ON THEM)"
        else:
            luck_assessment = "Performing as expected"

        return AnalysisResult(
            metric_name="xG Differential",
            value=round(xg_diff, 2),
            interpretation=luck_assessment,
            edge_implication="Underperforming xG = BUY; Overperforming xG = SELL",
            education=(
                "Expected Goals (xG) measures shot quality, not just quantity. "
                "A team with high xG but low actual goals is unlucky—regression to the mean "
                "suggests they'll start scoring. This is a prime betting edge."
            )
        )

    def back_to_back_adjustment(self, is_b2b: bool) -> Dict:
        """
        Calculate back-to-back game impact.

        Teams average 0.108 fewer points on B2B second nights
        ~5% decreased win probability
        """
        if is_b2b:
            return {
                "adjustment": -0.108,
                "win_prob_impact": -0.05,
                "note": "B2B second night - expect backup goalie, tired legs",
            }
        return {"adjustment": 0, "win_prob_impact": 0, "note": "Rested"}

    def get_key_metrics(self, team: Dict) -> List[AnalysisResult]:
        """Get key NHL metrics."""
        return [
            self.calculate_corsi(team),
            self.calculate_xg(team),
        ]

    def analyze_matchup(self, home: Dict, away: Dict) -> Dict:
        """Full NHL matchup analysis."""
        win_prob = self.calculate_win_probability(home, away)

        return {
            "home_win_probability": win_prob,
            "away_win_probability": 1 - win_prob,
            "goalie_note": "CRITICAL: Confirm starting goalies at morning skate",
            "home_metrics": [m.__dict__ for m in self.get_key_metrics(home)],
            "away_metrics": [m.__dict__ for m in self.get_key_metrics(away)],
        }
