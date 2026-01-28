"""
Sport-Specific Analytics Calculators
DVOA, EPA, KenPom, Corsi, xG - Accurate implementations with real formulas

IMPORTANT: These analytics use established formulas from sports analytics research.
Some metrics (like DVOA, KenPom) require proprietary data not available via ESPN.
When proprietary data isn't available, we use proxy calculations and clearly note this.

Data Sources:
- ESPN API: Scores, records, basic stats, odds
- FTN Fantasy (ftnfantasy.com): DVOA data (subscription required)
- KenPom (kenpom.com): College basketball efficiency ($24.95/year)
- BartTorvik (barttorvik.com): Free CBB alternative
- Natural Stat Trick / MoneyPuck: NHL analytics (free)
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


@dataclass
class AnalysisResult:
    """Result of analytics calculation."""
    metric_name: str
    value: float
    interpretation: str
    edge_implication: str
    education: str
    data_source: str  # Where this data comes from
    is_estimate: bool  # True if calculated from proxy data


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

    Key Metrics:
    - DVOA: Defense-adjusted Value Over Average (Football Outsiders/FTN Fantasy)
    - EPA: Expected Points Added (based on play-by-play)
    - Success Rate: % of plays gaining expected yards for situation
    - CPOE: Completion Percentage Over Expected

    Source for real DVOA: ftnfantasy.com/stats/nfl/team-total-dvoa
    """

    # 2024 NFL Season Averages (through Week 17)
    LEAGUE_AVG = {
        "points_per_game": 22.4,
        "yards_per_game": 327.5,
        "yards_per_play": 5.4,
        "pass_yards_per_game": 212.0,
        "rush_yards_per_game": 115.5,
        "third_down_pct": 0.40,
        "red_zone_pct": 0.56,
        "turnover_margin": 0.0,
    }

    # Home Field Advantage (research-based, declining trend)
    # Was ~3 points pre-2020, now ~2.5 points
    HOME_FIELD_ADVANTAGE = 2.5

    def calculate_win_probability(self, home_team: Dict, away_team: Dict) -> float:
        """
        Calculate win probability using point differential method.

        Formula based on Pro-Football-Reference research:
        Win% = 1 / (1 + 10^(-PointDiff/8.5))

        Each point of expected margin ≈ 3% win probability shift.
        """
        # Get scoring data
        home_ppg = home_team.get("points_per_game", self.LEAGUE_AVG["points_per_game"])
        home_papg = home_team.get("points_allowed", self.LEAGUE_AVG["points_per_game"])
        away_ppg = away_team.get("points_per_game", self.LEAGUE_AVG["points_per_game"])
        away_papg = away_team.get("points_allowed", self.LEAGUE_AVG["points_per_game"])

        # Calculate expected points for each team
        # Using opponent-adjusted method: (Team Offense + Opp Defense) / 2
        home_expected = (home_ppg + away_papg) / 2
        away_expected = (away_ppg + home_papg) / 2

        # Apply home field advantage
        home_expected += self.HOME_FIELD_ADVANTAGE / 2
        away_expected -= self.HOME_FIELD_ADVANTAGE / 2

        # Point differential
        point_diff = home_expected - away_expected

        # Convert to win probability using logistic function
        # Research shows ~8.5 points = 1 standard deviation in NFL
        win_prob = 1 / (1 + 10 ** (-point_diff / 8.5))

        return round(max(0.10, min(0.90, win_prob)), 3)

    def calculate_dvoa_proxy(self, team_stats: Dict) -> AnalysisResult:
        """
        Calculate DVOA proxy from available stats.

        REAL DVOA requires play-by-play data and is proprietary to FTN Fantasy.
        This proxy uses scoring efficiency as an approximation.

        True DVOA Formula (simplified):
        DVOA = Sum of (Success Value per play - League Average) / Total Plays

        Where Success Value accounts for:
        - Down and distance
        - Field position
        - Opponent adjustment
        """
        ppg = team_stats.get("points_per_game", self.LEAGUE_AVG["points_per_game"])
        papg = team_stats.get("points_allowed", self.LEAGUE_AVG["points_per_game"])

        # Offensive efficiency proxy
        off_eff = (ppg - self.LEAGUE_AVG["points_per_game"]) / self.LEAGUE_AVG["points_per_game"]

        # Defensive efficiency proxy (lower is better, so invert)
        def_eff = (self.LEAGUE_AVG["points_per_game"] - papg) / self.LEAGUE_AVG["points_per_game"]

        # Combined (weighted equally)
        dvoa_proxy = (off_eff + def_eff) * 50  # Scale to percentage

        # Interpretation based on FTN DVOA thresholds
        if dvoa_proxy > 20:
            interpretation = "ELITE (Top 3 team)"
        elif dvoa_proxy > 10:
            interpretation = "VERY GOOD (Top 8 team)"
        elif dvoa_proxy > 0:
            interpretation = "ABOVE AVERAGE"
        elif dvoa_proxy > -10:
            interpretation = "BELOW AVERAGE"
        else:
            interpretation = "POOR (Bottom 8 team)"

        return AnalysisResult(
            metric_name="DVOA Proxy",
            value=round(dvoa_proxy, 1),
            interpretation=interpretation,
            edge_implication=(
                "Teams with high DVOA but losing record = undervalued (regression up). "
                "Teams with low DVOA but winning record = overvalued (regression down)."
            ),
            education=(
                "DVOA (Defense-adjusted Value Over Average) measures efficiency on EVERY play, "
                "adjusted for opponent, game situation, and field position. "
                "\n\nExample: A 15-yard gain on 3rd-and-10 is more valuable than on 1st-and-10. "
                "DVOA captures this context that raw stats miss."
                "\n\nFor real DVOA data: ftnfantasy.com/stats/nfl/team-total-dvoa"
            ),
            data_source="Calculated from ESPN scoring data (proxy for FTN DVOA)",
            is_estimate=True,
        )

    def calculate_epa_proxy(self, team_stats: Dict) -> AnalysisResult:
        """
        Calculate EPA proxy from available stats.

        REAL EPA requires play-by-play data.
        EPA Formula: Expected Points After Play - Expected Points Before Play

        Expected Points table (based on historical data):
        - 1st & 10 at own 20: ~0.5 expected points
        - 1st & 10 at midfield: ~2.5 expected points
        - 1st & Goal at 5: ~5.5 expected points
        """
        # Use yards per play as primary proxy (correlates ~0.7 with EPA/play)
        ypp = team_stats.get("yards_per_play", self.LEAGUE_AVG["yards_per_play"])
        third_down = team_stats.get("third_down_pct", self.LEAGUE_AVG["third_down_pct"])
        red_zone = team_stats.get("red_zone_pct", self.LEAGUE_AVG["red_zone_pct"])

        # EPA proxy formula
        ypp_factor = (ypp - self.LEAGUE_AVG["yards_per_play"]) * 0.15
        third_factor = (third_down - self.LEAGUE_AVG["third_down_pct"]) * 0.5
        rz_factor = (red_zone - self.LEAGUE_AVG["red_zone_pct"]) * 0.3

        epa_proxy = ypp_factor + third_factor + rz_factor

        if epa_proxy > 0.10:
            interpretation = "ELITE offense (Top 5)"
        elif epa_proxy > 0.05:
            interpretation = "GOOD offense (Top 10)"
        elif epa_proxy > 0:
            interpretation = "Above average"
        elif epa_proxy > -0.05:
            interpretation = "Below average"
        else:
            interpretation = "POOR offense (Bottom 10)"

        return AnalysisResult(
            metric_name="EPA/Play Proxy",
            value=round(epa_proxy, 3),
            interpretation=interpretation,
            edge_implication="High EPA teams convert opportunities efficiently - strong in close games",
            education=(
                "EPA (Expected Points Added) measures the value each play adds. "
                "\n\nExample: From 1st & 10 at your own 20, expected points is ~0.5. "
                "A 30-yard gain moves you to the 50 where expected points is ~2.5. "
                "That play added +2.0 EPA."
                "\n\nWhy it matters: A team averaging 6.5 yards/play in garbage time has "
                "worse EPA than a team averaging 5.5 yards/play in crucial situations."
            ),
            data_source="Calculated from ESPN stats (proxy for nflfastR EPA)",
            is_estimate=True,
        )

    def weather_adjustment(self, weather: Dict) -> Dict:
        """
        Calculate weather impact on scoring.

        Research-based adjustments from historical data:
        - Wind 15+ mph: Passing efficiency drops 10%, INT rate +8%
        - Wind 20+ mph: Effects roughly double
        - Rain: Total -5 to -7 points
        - Snow: Total -8 to -12 points
        - Extreme cold (<20F): Total -3 to -5 points
        """
        adjustments = {
            "total_adjustment": 0.0,
            "passing_impact": 0.0,
            "factors": [],
            "recommendation": None,
        }

        wind = weather.get("wind_speed") or 0
        condition = str(weather.get("condition", "")).lower()
        temp = weather.get("temperature")

        # Wind adjustments
        if wind >= 20:
            adjustments["total_adjustment"] -= 6
            adjustments["passing_impact"] = -20  # 20% reduction
            adjustments["factors"].append(f"Strong wind ({wind} mph): -6 points, passing game compromised")
            adjustments["recommendation"] = "UNDER is strong play; run-heavy teams favored"
        elif wind >= 15:
            adjustments["total_adjustment"] -= 3
            adjustments["passing_impact"] = -10  # 10% reduction
            adjustments["factors"].append(f"Moderate wind ({wind} mph): -3 points")

        # Precipitation
        if "snow" in condition:
            adjustments["total_adjustment"] -= 10
            adjustments["factors"].append("Snow: -10 points (major impact)")
            adjustments["recommendation"] = "Strong UNDER spot; favor rushing teams"
        elif "rain" in condition or "storm" in condition:
            adjustments["total_adjustment"] -= 6
            adjustments["factors"].append("Rain/Storm: -6 points")

        # Temperature
        if temp is not None and temp < 20:
            cold_adj = min(5, (20 - temp) / 4)
            adjustments["total_adjustment"] -= cold_adj
            adjustments["factors"].append(f"Extreme cold ({temp}°F): -{cold_adj:.1f} points")

        return adjustments

    def get_key_metrics(self, team: Dict) -> List[AnalysisResult]:
        """Get key NFL metrics for a team."""
        return [
            self.calculate_dvoa_proxy(team),
            self.calculate_epa_proxy(team),
        ]

    def analyze_matchup(self, home: Dict, away: Dict) -> Dict:
        """Full NFL matchup analysis."""
        win_prob = self.calculate_win_probability(home, away)

        return {
            "home_win_probability": win_prob,
            "away_win_probability": 1 - win_prob,
            "home_metrics": [m.__dict__ for m in self.get_key_metrics(home)],
            "away_metrics": [m.__dict__ for m in self.get_key_metrics(away)],
            "key_matchups": [],
            "injury_impact": [],
        }


class NBAAnalytics(SportAnalytics):
    """
    NBA Analytics Engine

    Key Metrics:
    - Net Rating: Offensive Rating - Defensive Rating (per 100 possessions)
    - Pace: Possessions per 48 minutes
    - eFG%: Effective Field Goal % = (FG + 0.5 * 3FG) / FGA
    - True Shooting: TS% = PTS / (2 * (FGA + 0.44 * FTA))

    Data Sources:
    - ESPN: Basic stats, records
    - NBA.com/stats: Advanced metrics (free)
    - Basketball-Reference: Historical data
    """

    # 2024-25 NBA Season Averages
    LEAGUE_AVG = {
        "pace": 100.3,           # Possessions per 48 min
        "offensive_rating": 114.8,  # Points per 100 possessions
        "defensive_rating": 114.8,
        "efg_pct": 0.544,
        "ts_pct": 0.578,
        "three_rate": 0.396,    # 3PA / FGA
    }

    # Home Court Advantage (research-based)
    # Has declined from ~3.5 pre-pandemic to ~2.5 currently
    HOME_COURT_ADVANTAGE = 2.5

    # Rest advantage research (from NBA analytics studies)
    REST_IMPACT = {
        "b2b_penalty": -2.5,      # Playing on 0 days rest
        "extra_rest_bonus": 1.0,  # 2+ days rest vs 1 day
        "travel_factor": -0.5,    # Cross-country travel
    }

    def calculate_win_probability(self, home_team: Dict, away_team: Dict) -> float:
        """
        Calculate NBA win probability using Net Rating.

        Research shows Net Rating is the single best predictor of future wins.
        Formula: Each point of net rating diff ≈ 2.7% win probability shift.
        """
        # Get ratings (default to league average if not provided)
        home_net = home_team.get("net_rating", 0)
        away_net = away_team.get("net_rating", 0)

        # Calculate rest adjustment
        home_rest = home_team.get("days_rest", 1)
        away_rest = away_team.get("days_rest", 1)
        rest_adj = self._calculate_rest_adjustment(home_rest, away_rest)

        # Total point differential expectation
        point_diff = (home_net - away_net) + self.HOME_COURT_ADVANTAGE + rest_adj

        # Convert to probability
        # NBA games have SD of ~12 points; each point ≈ 2.7% win prob
        win_prob = 0.5 + (point_diff * 0.027)

        return round(max(0.10, min(0.90, win_prob)), 3)

    def _calculate_rest_adjustment(self, home_rest: int, away_rest: int) -> float:
        """
        Calculate rest advantage in points.

        Research-backed values:
        - B2B (0 days rest): -2.5 points
        - 2+ days rest vs B2B opponent: +3.0 to +3.5 points advantage
        """
        adjustment = 0.0

        # Home team B2B
        if home_rest == 0:
            adjustment += self.REST_IMPACT["b2b_penalty"]

        # Away team B2B
        if away_rest == 0:
            adjustment -= self.REST_IMPACT["b2b_penalty"]

        # Extra rest bonus
        if home_rest >= 2 and away_rest <= 1:
            adjustment += self.REST_IMPACT["extra_rest_bonus"]
        if away_rest >= 2 and home_rest <= 1:
            adjustment -= self.REST_IMPACT["extra_rest_bonus"]

        return adjustment

    def calculate_net_rating(self, team_stats: Dict) -> AnalysisResult:
        """
        Calculate and interpret Net Rating.

        Net Rating = Offensive Rating - Defensive Rating
        Both measured per 100 possessions to normalize for pace.

        Interpretation thresholds based on historical NBA data:
        - +10: Elite (championship contender)
        - +5 to +10: Very good (home court in playoffs)
        - 0 to +5: Above average (playoff team)
        - -5 to 0: Below average (play-in/lottery)
        - Below -5: Poor (lottery team)
        """
        ortg = team_stats.get("offensive_rating", self.LEAGUE_AVG["offensive_rating"])
        drtg = team_stats.get("defensive_rating", self.LEAGUE_AVG["defensive_rating"])
        net = ortg - drtg

        if net >= 10:
            interpretation = "ELITE (Championship contender, ~65+ wins)"
        elif net >= 5:
            interpretation = "VERY GOOD (55-60 wins, top 4 seed)"
        elif net >= 0:
            interpretation = "ABOVE AVERAGE (Playoff team)"
        elif net >= -5:
            interpretation = "BELOW AVERAGE (Play-in/lottery)"
        else:
            interpretation = "POOR (Lottery team)"

        return AnalysisResult(
            metric_name="Net Rating",
            value=round(net, 1),
            interpretation=interpretation,
            edge_implication=(
                "Key insight: A +8 net rating team losing games at a 50% rate is MASSIVELY undervalued. "
                "Net rating predicts future wins better than current record."
            ),
            education=(
                "Net Rating = Offensive Rating - Defensive Rating (points per 100 possessions)."
                "\n\nWhy per 100 possessions? It normalizes for pace. A team playing fast scores more "
                "points but also allows more. Rating per 100 possessions shows TRUE efficiency."
                "\n\nHistorically, every +1 in net rating ≈ 2.5 extra wins over 82 games."
            ),
            data_source="NBA.com/stats or Basketball-Reference",
            is_estimate=False if "offensive_rating" in team_stats else True,
        )

    def calculate_pace_impact(self, team1_pace: float, team2_pace: float) -> Dict:
        """
        Calculate expected game pace and betting implications.

        Pace = Possessions per 48 minutes
        More possessions = more variance = more extreme outcomes
        """
        expected_pace = (team1_pace + team2_pace) / 2
        pace_vs_league = expected_pace - self.LEAGUE_AVG["pace"]

        # Total adjustment based on pace
        # Research: Each +1 pace ≈ +1.5 points to total
        total_adjustment = pace_vs_league * 1.5

        if expected_pace >= 105:
            style = "VERY FAST - High variance, totals often exceed line"
            recommendation = "Lean OVER; game script unpredictable"
        elif expected_pace >= 101:
            style = "ABOVE AVERAGE pace"
            recommendation = None
        elif expected_pace >= 98:
            style = "SLOW - Grind-it-out, favors unders"
            recommendation = "Lean UNDER; lower variance"
        else:
            style = "VERY SLOW - Strong under spot"
            recommendation = "UNDER is strong; expect close, low-scoring game"

        return {
            "expected_pace": round(expected_pace, 1),
            "pace_vs_league": round(pace_vs_league, 1),
            "style": style,
            "total_adjustment": round(total_adjustment, 1),
            "recommendation": recommendation,
            "education": (
                "Pace = possessions per 48 minutes. League average is ~100."
                "\n\nFast teams (105+): Hawks, Pacers historically"
                "\nSlow teams (97-): Knicks, Grizzlies historically"
                "\n\nTwo fast teams = 240+ point game; two slow teams = 210 or under"
            ),
        }

    def get_key_metrics(self, team: Dict) -> List[AnalysisResult]:
        """Get key NBA metrics."""
        return [self.calculate_net_rating(team)]

    def analyze_matchup(self, home: Dict, away: Dict) -> Dict:
        """Full NBA matchup analysis."""
        win_prob = self.calculate_win_probability(home, away)

        pace_analysis = self.calculate_pace_impact(
            home.get("pace", self.LEAGUE_AVG["pace"]),
            away.get("pace", self.LEAGUE_AVG["pace"])
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

    Key Metrics:
    - SP+ (Bill Connelly, ESPN): Tempo/opponent-adjusted efficiency
    - FPI (ESPN): Forward-looking power index
    - Strength of Schedule

    Source: SP+ data at ESPN.com (free)
    """

    # Home Field Advantage by venue type
    HFA = {
        "default": 3.0,
        "dome": 2.5,
        "altitude": 4.0,  # Colorado, BYU historically
        "hostile": 4.5,    # Death Valley, The Swamp, etc.
    }

    def calculate_win_probability(self, home_team: Dict, away_team: Dict) -> float:
        """
        Calculate CFB win probability using SP+ or FPI ratings.

        SP+ Formula: Win% = 1 / (1 + e^(-(rating_diff + HFA) / 7))

        The /7 factor comes from CFB's higher variance than NFL.
        """
        home_rating = home_team.get("sp_plus", home_team.get("fpi", 0))
        away_rating = away_team.get("sp_plus", away_team.get("fpi", 0))

        # Get appropriate HFA
        venue_type = home_team.get("venue_type", "default")
        hfa = self.HFA.get(venue_type, self.HFA["default"])

        spread = home_rating - away_rating + hfa
        win_prob = 1 / (1 + math.exp(-spread / 7))

        return round(max(0.05, min(0.95, win_prob)), 3)

    def calculate_sp_plus(self, team_stats: Dict) -> AnalysisResult:
        """
        Interpret SP+ Rating.

        SP+ is PREDICTIVE, not descriptive like polls.
        It measures HOW you played, not just whether you won.

        Thresholds:
        - +25: Elite (playoff team)
        - +15: Very good (NY6 bowl)
        - +5: Above average
        - -5 to +5: Average
        - Below -5: Below average
        """
        sp_plus = team_stats.get("sp_plus", 0)

        if sp_plus >= 25:
            interpretation = "ELITE - Playoff contender"
        elif sp_plus >= 15:
            interpretation = "VERY GOOD - NY6 bowl caliber"
        elif sp_plus >= 5:
            interpretation = "ABOVE AVERAGE - Bowl team"
        elif sp_plus >= -5:
            interpretation = "AVERAGE"
        else:
            interpretation = "BELOW AVERAGE"

        return AnalysisResult(
            metric_name="SP+ Rating",
            value=sp_plus,
            interpretation=interpretation,
            edge_implication=(
                "KEY: SP+ is PREDICTIVE. A team can win 35-34 and their SP+ DROPS because "
                "the model sees they played poorly. This creates massive betting value."
            ),
            education=(
                "SP+ (Bill Connelly, ESPN) is tempo/opponent-adjusted efficiency."
                "\n\nUnlike polls which reward wins, SP+ measures HOW you played:"
                "\n- Did you dominate possession?"
                "\n- Were your drives efficient?"
                "\n- Did you win because of 3 turnovers or actual dominance?"
                "\n\nA 6-0 team with SP+ of +5 is WORSE than a 4-2 team with SP+ of +15."
            ),
            data_source="ESPN SP+ (Bill Connelly)",
            is_estimate=False if "sp_plus" in team_stats else True,
        )

    def get_key_metrics(self, team: Dict) -> List[AnalysisResult]:
        """Get key CFB metrics."""
        return [self.calculate_sp_plus(team)]

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

    Key Metrics:
    - KenPom AdjEM: Adjusted Efficiency Margin (GOLD STANDARD)
    - AdjO: Adjusted Offensive Efficiency
    - AdjD: Adjusted Defensive Efficiency
    - Tempo: Possessions per 40 minutes

    Data Sources:
    - KenPom.com ($24.95/year) - ESSENTIAL for serious CBB betting
    - BartTorvik.com (free) - Good alternative, includes recency bias
    """

    # Home Court Advantage by Conference (research-based)
    HCA_BY_CONFERENCE = {
        "Big 12": 4.5,
        "Big Ten": 4.0,
        "SEC": 4.0,
        "ACC": 3.1,
        "Big East": 4.0,
        "Mountain West": 4.2,
        "default": 3.5,
    }

    # KenPom thresholds
    KENPOM_TIERS = {
        30: "ELITE (Final Four caliber)",
        20: "VERY GOOD (Sweet 16+)",
        10: "GOOD (Tournament team)",
        0: "AVERAGE (Bubble/NIT)",
        -10: "BELOW AVERAGE",
    }

    def calculate_win_probability(self, home_team: Dict, away_team: Dict) -> float:
        """
        Calculate CBB win probability using KenPom AdjEM.

        KenPom's formula:
        Win% = 1 / (1 + e^(-(AdjEM_diff + HCA) / 11))

        The /11 factor accounts for college basketball's high variance.
        """
        home_em = home_team.get("adj_em", 0)
        away_em = away_team.get("adj_em", 0)

        conference = home_team.get("conference", "default")
        hca = self.HCA_BY_CONFERENCE.get(conference, self.HCA_BY_CONFERENCE["default"])

        diff = home_em - away_em + hca
        win_prob = 1 / (1 + math.exp(-diff / 11))

        return round(max(0.05, min(0.95, win_prob)), 3)

    def calculate_kenpom(self, team_stats: Dict) -> AnalysisResult:
        """
        Interpret KenPom Adjusted Efficiency Margin.

        AdjEM = AdjO - AdjD
        - AdjO: Points per 100 possessions against average D-I defense
        - AdjD: Points allowed per 100 possessions against average D-I offense

        This is THE most important number in college basketball analytics.
        """
        adj_em = team_stats.get("adj_em", 0)
        adj_o = team_stats.get("adj_o")
        adj_d = team_stats.get("adj_d")

        # Determine tier
        interpretation = "BELOW AVERAGE"
        for threshold, desc in sorted(self.KENPOM_TIERS.items(), reverse=True):
            if adj_em >= threshold:
                interpretation = desc
                break

        # Build detailed interpretation
        detail = interpretation
        if adj_o and adj_d:
            if adj_o > 115:
                detail += " | Elite offense"
            if adj_d < 95:
                detail += " | Elite defense"

        return AnalysisResult(
            metric_name="KenPom AdjEM",
            value=round(adj_em, 1),
            interpretation=detail,
            edge_implication=(
                "BETTING KEY: AdjEM difference ≈ expected margin of victory."
                "\n\nIf KenPom says Team A (+20) vs Team B (+5) = 15-point difference,"
                "but the line is -10, you have 5 points of value on Team A."
            ),
            education=(
                "KenPom AdjEM is the GOLD STANDARD for college basketball."
                "\n\nFormula: AdjO - AdjD (both per 100 possessions, opponent-adjusted)"
                "\n\nWhy it works: A team beating bad teams by 20 and losing to good teams by 10 "
                "will have a mediocre AdjEM despite a winning record. The model sees through "
                "inflated records from weak schedules."
                "\n\nSource: kenpom.com ($24.95/year)"
                "\nFree alternative: barttorvik.com"
            ),
            data_source="KenPom.com (subscription) or BartTorvik.com (free)",
            is_estimate=False if "adj_em" in team_stats else True,
        )

    def get_key_metrics(self, team: Dict) -> List[AnalysisResult]:
        """Get key CBB metrics."""
        return [self.calculate_kenpom(team)]

    def analyze_matchup(self, home: Dict, away: Dict) -> Dict:
        """Full CBB matchup analysis."""
        win_prob = self.calculate_win_probability(home, away)

        home_em = home.get("adj_em", 0)
        away_em = away.get("adj_em", 0)
        conference = home.get("conference", "default")
        hca = self.HCA_BY_CONFERENCE.get(conference, self.HCA_BY_CONFERENCE["default"])

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

    Key Metrics:
    - Corsi (CF%): Shot attempt differential
    - Fenwick (FF%): Unblocked shot attempt differential
    - Expected Goals (xG): Shot quality measure
    - GSAx: Goals Saved Above Expected (goalie metric)

    Data Sources:
    - Natural Stat Trick (naturalstattrick.com) - FREE
    - MoneyPuck (moneypuck.com) - FREE
    - Hockey-Reference - historical data
    """

    # League averages (2024-25)
    LEAGUE_AVG = {
        "goals_per_game": 3.1,
        "corsi_pct": 50.0,
        "xgf_per_60": 2.8,
        "xga_per_60": 2.8,
        "save_pct": 0.905,
    }

    # Home Ice Advantage
    HOME_ICE_ADVANTAGE = 0.15  # ~0.15 goals ≈ 3% win probability

    def calculate_win_probability(self, home_team: Dict, away_team: Dict) -> float:
        """
        Calculate NHL win probability using xG differential.

        xG is the best predictor of future success in hockey.
        Each +1 xG differential ≈ 15% win probability shift.
        """
        home_xgf = home_team.get("xgf_per_60", self.LEAGUE_AVG["xgf_per_60"])
        home_xga = home_team.get("xga_per_60", self.LEAGUE_AVG["xga_per_60"])
        away_xgf = away_team.get("xgf_per_60", self.LEAGUE_AVG["xgf_per_60"])
        away_xga = away_team.get("xga_per_60", self.LEAGUE_AVG["xga_per_60"])

        # Expected goals for each team (opponent-adjusted)
        home_expected = (home_xgf + away_xga) / 2 + self.HOME_ICE_ADVANTAGE
        away_expected = (away_xgf + home_xga) / 2

        goal_diff = home_expected - away_expected

        # Each goal differential ≈ 15% win probability
        win_prob = 0.5 + (goal_diff * 0.15)

        return round(max(0.30, min(0.70, win_prob)), 3)

    def calculate_corsi(self, team_stats: Dict) -> AnalysisResult:
        """
        Calculate and interpret Corsi For % (CF%).

        Corsi = ALL shot attempts (goals + saves + misses + blocks)
        CF% = Corsi For / (Corsi For + Corsi Against)

        Why Corsi matters: It measures PROCESS over RESULTS.
        A team can have bad goaltending but still control play.
        """
        cf_pct = team_stats.get("corsi_pct", self.LEAGUE_AVG["corsi_pct"])

        if cf_pct >= 55:
            interpretation = "ELITE possession - dominating territorially"
        elif cf_pct >= 52:
            interpretation = "ABOVE AVERAGE - solid possession team"
        elif cf_pct >= 48:
            interpretation = "AVERAGE"
        elif cf_pct >= 45:
            interpretation = "BELOW AVERAGE - getting outplayed"
        else:
            interpretation = "POOR - severely outpossessed"

        return AnalysisResult(
            metric_name="Corsi For %",
            value=round(cf_pct, 1),
            interpretation=interpretation,
            edge_implication=(
                "HIGH CF% + LOW GOALS = positive regression (BET ON THEM)"
                "\nLOW CF% + HIGH GOALS = negative regression (FADE THEM)"
            ),
            education=(
                "Corsi counts ALL shot attempts: goals, saves, misses, AND blocks."
                "\n\nWhy it matters: Hockey has MASSIVE variance. A team can dominate "
                "possession but lose 1-0 on a fluky goal. Corsi sees through the noise."
                "\n\nExample: Team with 58% Corsi but only 48% of goals = UNLUCKY. "
                "Over time, they'll start winning. This is where sharp bettors find edge."
                "\n\nSource: naturalstattrick.com (free)"
            ),
            data_source="Natural Stat Trick (free) or MoneyPuck (free)",
            is_estimate=False if "corsi_pct" in team_stats else True,
        )

    def calculate_xg(self, team_stats: Dict) -> AnalysisResult:
        """
        Calculate and interpret Expected Goals (xG).

        xG assigns probability (0 to 1) to each shot based on:
        - Shot location (distance and angle)
        - Shot type (wrist, slap, deflection, etc.)
        - Pre-shot movement (pass, rebound, rush)
        - Game state (even strength, power play)

        xG is THE most predictive metric in hockey analytics.
        """
        xgf = team_stats.get("xgf_per_60", self.LEAGUE_AVG["xgf_per_60"])
        xga = team_stats.get("xga_per_60", self.LEAGUE_AVG["xga_per_60"])
        xg_diff = xgf - xga

        actual_gf = team_stats.get("gf_per_60", xgf)
        actual_ga = team_stats.get("ga_per_60", xga)

        # Calculate luck factor
        # Positive = outperforming xG (lucky)
        # Negative = underperforming xG (unlucky)
        luck_factor = (actual_gf - xgf) - (actual_ga - xga)

        if luck_factor > 0.3:
            luck_status = "OVERPERFORMING xG - expect regression DOWN"
            edge_note = "FADE this team - they're getting lucky"
        elif luck_factor < -0.3:
            luck_status = "UNDERPERFORMING xG - expect regression UP"
            edge_note = "BET ON this team - they're getting unlucky"
        else:
            luck_status = "Performing as expected"
            edge_note = "No clear regression signal"

        return AnalysisResult(
            metric_name="xG Differential",
            value=round(xg_diff, 2),
            interpretation=luck_status,
            edge_implication=edge_note,
            education=(
                "Expected Goals (xG) measures SHOT QUALITY, not just quantity."
                "\n\nHow xG works: Each shot gets a probability based on:"
                "\n- Distance from net (closer = higher xG)"
                "\n- Angle (straight on = higher xG)"
                "\n- Shot type (one-timers, rebounds = higher xG)"
                "\n- Pre-shot movement (passes increase xG)"
                "\n\nA team with 3.0 xGF but only 2.0 actual goals is UNLUCKY. "
                "Math says they'll start scoring. This is the edge."
                "\n\nSources: MoneyPuck.com, Natural Stat Trick (both free)"
            ),
            data_source="MoneyPuck or Natural Stat Trick (free)",
            is_estimate=False if "xgf_per_60" in team_stats else True,
        )

    def back_to_back_adjustment(self, is_b2b: bool) -> Dict:
        """
        Calculate back-to-back game impact.

        Research shows:
        - Teams on B2B score ~0.1 fewer goals
        - Win probability drops ~5%
        - Backup goalie likely to start
        """
        if is_b2b:
            return {
                "goal_adjustment": -0.108,
                "win_prob_impact": -0.05,
                "notes": [
                    "B2B second night - expect backup goalie",
                    "Legs will be tired, especially in 3rd period",
                    "Consider UNDER on total"
                ],
            }
        return {
            "goal_adjustment": 0,
            "win_prob_impact": 0,
            "notes": ["Rested - no adjustment needed"],
        }

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
            "critical_note": "CONFIRM STARTING GOALIES at morning skate (10:30-11:30 AM local)",
            "home_metrics": [m.__dict__ for m in self.get_key_metrics(home)],
            "away_metrics": [m.__dict__ for m in self.get_key_metrics(away)],
        }
