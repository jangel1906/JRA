"""
League Data Configuration
Updated regularly to ensure accuracy

LAST UPDATED: January 28, 2026
DATA SOURCES (Web-Verified):
- NFL: Pro-Football-Reference, StatMuse, TeamRankings
- NBA: Basketball-Reference, NBA.com/stats, NBAStuffer
- CFB: ESPN SP+, TeamRankings, NCAA.com
- CBB: KenPom.com ($24.95/yr), BartTorvik (free alternative)
- NHL: Hockey-Reference, NHL.com, MoneyPuck, Natural Stat Trick

VERIFICATION LINKS:
- NFL Stats: https://www.pro-football-reference.com/years/2024/
- NBA Stats: https://www.basketball-reference.com/leagues/NBA_2025.html
- NHL Stats: https://www.hockey-reference.com/leagues/stats.html
- CBB Stats: https://kenpom.com/ (subscription required)

To update: Modify the values below or use DataUpdater methods
"""

from datetime import datetime, date
from typing import Dict, Optional
import json
import os

# Track when data was last updated
LAST_UPDATED = "2026-01-28"
SEASON_YEAR = "2025-26"  # Current season


class LeagueData:
    """
    Central repository for league averages and constants.
    Update these values each week/month for accurate analysis.

    Data verified via web search on January 28, 2026.
    """

    # ═══════════════════════════════════════════════════════════════════════
    # NFL DATA (2025 Season - Playoffs Underway)
    # Source: Pro-Football-Reference, StatMuse, ESPN
    # ═══════════════════════════════════════════════════════════════════════
    NFL = {
        "season": "2025",
        "last_updated": "2026-01-28",
        "averages": {
            "points_per_game": 22.8,      # Slight increase from 21.4 in 2024
            "yards_per_game": 330.0,
            "yards_per_play": 5.5,
            "pass_yards_per_game": 205.0,
            "rush_yards_per_game": 125.0,
            "third_down_pct": 0.40,
            "red_zone_pct": 0.56,
            "turnover_margin": 0.0,
        },
        "home_field_advantage": 2.5,  # Points (was 3.0 pre-2020, declining)
        "standard_deviation": 8.5,    # Point spread SD
        "playoff_status": "Divisional Round",
        "notes": "Bears 11-6 at 25.9 PPG (9th); Playoffs underway Jan 2026"
    }

    # ═══════════════════════════════════════════════════════════════════════
    # NBA DATA (2025-26 Season - Through January 28, 2026)
    # Source: Basketball-Reference, NBA.com, FOX Sports
    # ═══════════════════════════════════════════════════════════════════════
    NBA = {
        "season": "2025-26",
        "last_updated": "2026-01-28",
        "averages": {
            "pace": 101.9,              # HIGHEST IN 30 YEARS of play-by-play data
            "offensive_rating": 114.3,  # Near all-time high (114.5 was record)
            "defensive_rating": 114.3,
            "efg_pct": 0.545,
            "ts_pct": 0.580,
            "three_rate": 0.400,        # 3PA / FGA
            "points_per_game": 116.5,   # High scoring era continues
        },
        "home_court_advantage": 2.5,    # Points (was 3.5 pre-pandemic)
        "rest_impact": {
            "b2b_penalty": -2.5,        # Playing on 0 days rest
            "extra_rest_bonus": 1.0,    # 2+ days vs 1 day
            "travel_penalty": -0.5,     # Cross-country travel
        },
        "top_teams": {
            "Thunder": "35-8 (as of mid-Jan)",
            "top_ortg": "123.4+",       # Elite offenses at 120+ ORtg
        },
        "notes": "Record pace; 6th efficiency record in 8 years likely"
    }

    # ═══════════════════════════════════════════════════════════════════════
    # COLLEGE FOOTBALL DATA (2025 Season - Bowl Season Complete)
    # Source: ESPN SP+, TeamRankings, NCAA.com
    # ═══════════════════════════════════════════════════════════════════════
    CFB = {
        "season": "2025",
        "last_updated": "2026-01-28",
        "averages": {
            "points_per_game": 28.8,
            "yards_per_game": 415.0,
        },
        "home_field_advantage": {
            "default": 3.0,
            "dome": 2.5,
            "altitude": 4.0,     # Colorado, BYU, Air Force
            "hostile": 4.5,      # Death Valley, The Swamp, etc.
            "neutral": 0.0,
        },
        "conference_adjustments": {
            "SEC": 1.5,          # Typically underrated by polls
            "Big Ten": 1.0,
            "Big 12": 0.5,
            "ACC": 0.0,
            "Pac-12": 0.0,       # Now smaller conference
        },
        "notes": "2025 bowl season complete; CFP expanded format"
    }

    # ═══════════════════════════════════════════════════════════════════════
    # COLLEGE BASKETBALL DATA (2025-26 Season - Through Jan 16, 2026)
    # Source: KenPom.com, BartTorvik
    # ═══════════════════════════════════════════════════════════════════════
    CBB = {
        "season": "2025-26",
        "last_updated": "2026-01-28",
        "games_tracked": 3490,          # Through Jan 16, 2026
        "averages": {
            "points_per_game": 74.0,
            "tempo": 68.5,              # Possessions per 40 min
            "offensive_efficiency": 105.5,  # Per 100 poss (league avg)
            "defensive_efficiency": 105.5,
        },
        "home_court_advantage_by_conference": {
            "Big 12": 4.5,
            "Big Ten": 4.0,
            "SEC": 4.0,
            "Big East": 4.0,
            "Mountain West": 4.2,
            "ACC": 3.1,
            "default": 3.5,
        },
        "kenpom_thresholds": {
            "elite": 30,          # Final Four caliber
            "very_good": 24,      # Sweet 16+ (Louisville at +24.14)
            "good": 10,           # Tournament team
            "average": 0,         # Bubble/NIT
            "below_average": -10,
        },
        "preseason_top5": ["Houston", "Florida", "Purdue", "Kentucky", "UConn"],
        "notes": "KenPom AdjEM difference ≈ expected margin; Alabama top-15 tempo 6 straight years"
    }

    # ═══════════════════════════════════════════════════════════════════════
    # NHL DATA (2025-26 Season - Through January 2026)
    # Source: Hockey-Reference, NHL.com, MoneyPuck
    # ═══════════════════════════════════════════════════════════════════════
    NHL = {
        "season": "2025-26",
        "last_updated": "2026-01-28",
        "averages": {
            "goals_per_game": 3.1,      # League continues high-scoring trend
            "corsi_pct": 50.0,
            "xgf_per_60": 2.85,
            "xga_per_60": 2.85,
            "save_pct": 0.900,          # Lower save % era continues
            "shooting_pct": 0.100,
        },
        "home_ice_advantage": 0.15,   # Goals (~3% win prob)
        "b2b_impact": {
            "goal_adjustment": -0.108,
            "win_prob_impact": -0.05,
        },
        "stat_leaders": {
            "goals": "Jani Nyman (SEA) - 38",
            "assists": "Matthew Wood (NSH) - 52",
            "wins": "Joey Daccord (SEA) - 35",
        },
        "notes": "Sorokin leads HD save%; Confirm starting goalie at morning skate"
    }

    @classmethod
    def get_nfl(cls) -> Dict:
        """Get NFL league data."""
        return cls.NFL

    @classmethod
    def get_nba(cls) -> Dict:
        """Get NBA league data."""
        return cls.NBA

    @classmethod
    def get_cfb(cls) -> Dict:
        """Get CFB league data."""
        return cls.CFB

    @classmethod
    def get_cbb(cls) -> Dict:
        """Get CBB league data."""
        return cls.CBB

    @classmethod
    def get_nhl(cls) -> Dict:
        """Get NHL league data."""
        return cls.NHL

    @classmethod
    def get_data_age_days(cls) -> int:
        """Get how many days since data was updated."""
        last = datetime.strptime(LAST_UPDATED, "%Y-%m-%d").date()
        today = date.today()
        return (today - last).days

    @classmethod
    def is_data_stale(cls, max_age_days: int = 7) -> bool:
        """Check if data is older than max_age_days."""
        return cls.get_data_age_days() > max_age_days

    @classmethod
    def get_freshness_status(cls) -> Dict:
        """Get data freshness status for all sports."""
        age = cls.get_data_age_days()

        if age <= 3:
            status = "FRESH"
            color = "green"
        elif age <= 7:
            status = "CURRENT"
            color = "yellow"
        else:
            status = "STALE - UPDATE RECOMMENDED"
            color = "red"

        return {
            "last_updated": LAST_UPDATED,
            "season": SEASON_YEAR,
            "age_days": age,
            "status": status,
            "color": color,
            "sports": {
                "nfl": cls.NFL["last_updated"],
                "nba": cls.NBA["last_updated"],
                "cfb": cls.CFB["last_updated"],
                "cbb": cls.CBB["last_updated"],
                "nhl": cls.NHL["last_updated"],
            }
        }


class DataUpdater:
    """
    Utility for updating league data.
    Can be extended to fetch from APIs.
    """

    CONFIG_FILE = os.path.join(os.path.dirname(__file__), "custom_data.json")

    @classmethod
    def save_custom_data(cls, sport: str, data: Dict) -> bool:
        """Save custom/updated data for a sport."""
        try:
            existing = {}
            if os.path.exists(cls.CONFIG_FILE):
                with open(cls.CONFIG_FILE, "r") as f:
                    existing = json.load(f)

            existing[sport] = {
                "data": data,
                "updated_at": datetime.now().isoformat(),
            }

            with open(cls.CONFIG_FILE, "w") as f:
                json.dump(existing, f, indent=2)

            return True
        except Exception:
            return False

    @classmethod
    def load_custom_data(cls, sport: str) -> Optional[Dict]:
        """Load custom data if available."""
        try:
            if os.path.exists(cls.CONFIG_FILE):
                with open(cls.CONFIG_FILE, "r") as f:
                    data = json.load(f)
                    if sport in data:
                        return data[sport]["data"]
        except Exception:
            pass
        return None

    @classmethod
    def update_nfl_averages(
        cls,
        points_per_game: float = None,
        yards_per_game: float = None,
        home_field_advantage: float = None,
    ) -> Dict:
        """Update NFL averages."""
        updates = {}
        if points_per_game:
            updates["points_per_game"] = points_per_game
        if yards_per_game:
            updates["yards_per_game"] = yards_per_game
        if home_field_advantage:
            updates["home_field_advantage"] = home_field_advantage

        if updates:
            current = LeagueData.NFL.copy()
            current["averages"].update(updates)
            current["last_updated"] = datetime.now().strftime("%Y-%m-%d")
            cls.save_custom_data("nfl", current)

        return updates

    @classmethod
    def update_nba_averages(
        cls,
        pace: float = None,
        offensive_rating: float = None,
        home_court_advantage: float = None,
    ) -> Dict:
        """Update NBA averages."""
        updates = {}
        if pace:
            updates["pace"] = pace
        if offensive_rating:
            updates["offensive_rating"] = offensive_rating
            updates["defensive_rating"] = offensive_rating  # League avg O = D
        if home_court_advantage:
            updates["home_court_advantage"] = home_court_advantage

        if updates:
            current = LeagueData.NBA.copy()
            current["averages"].update(updates)
            current["last_updated"] = datetime.now().strftime("%Y-%m-%d")
            cls.save_custom_data("nba", current)

        return updates


def print_data_status():
    """Print current data freshness status."""
    status = LeagueData.get_freshness_status()

    print("\n" + "=" * 50)
    print("EDGE ATLAS - DATA FRESHNESS STATUS")
    print("=" * 50)
    print(f"Last Updated: {status['last_updated']}")
    print(f"Season: {status['season']}")
    print(f"Age: {status['age_days']} days")
    print(f"Status: {status['status']}")
    print("\nBy Sport:")
    for sport, updated in status['sports'].items():
        print(f"  {sport.upper()}: {updated}")
    print("=" * 50)


if __name__ == "__main__":
    print_data_status()
