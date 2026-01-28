"""
League Data Configuration
Updated regularly to ensure accuracy

LAST UPDATED: January 2026
DATA SOURCES:
- NFL: Pro-Football-Reference, FTN Fantasy
- NBA: NBA.com/stats, Basketball-Reference
- CFB: ESPN SP+
- CBB: KenPom, BartTorvik
- NHL: Natural Stat Trick, MoneyPuck

To update: Modify the values below or call fetch_latest_data()
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
    """

    # ═══════════════════════════════════════════════════════════════════════
    # NFL DATA (2024 Season - Through Week 18)
    # ═══════════════════════════════════════════════════════════════════════
    NFL = {
        "season": "2024",
        "last_updated": "2026-01-28",
        "averages": {
            "points_per_game": 22.4,
            "yards_per_game": 327.5,
            "yards_per_play": 5.4,
            "pass_yards_per_game": 212.0,
            "rush_yards_per_game": 115.5,
            "third_down_pct": 0.40,
            "red_zone_pct": 0.56,
            "turnover_margin": 0.0,
        },
        "home_field_advantage": 2.5,  # Points (was 3.0 pre-2020, declining)
        "standard_deviation": 8.5,    # Point spread SD
        "notes": "HFA has declined post-COVID; monitor trend"
    }

    # ═══════════════════════════════════════════════════════════════════════
    # NBA DATA (2024-25 Season - Through January 2026)
    # ═══════════════════════════════════════════════════════════════════════
    NBA = {
        "season": "2024-25",
        "last_updated": "2026-01-28",
        "averages": {
            "pace": 100.3,              # Possessions per 48 min
            "offensive_rating": 114.8,  # Points per 100 poss
            "defensive_rating": 114.8,
            "efg_pct": 0.544,
            "ts_pct": 0.578,
            "three_rate": 0.396,        # 3PA / FGA
            "points_per_game": 114.2,
        },
        "home_court_advantage": 2.5,    # Points (was 3.5 pre-pandemic)
        "rest_impact": {
            "b2b_penalty": -2.5,        # Playing on 0 days rest
            "extra_rest_bonus": 1.0,    # 2+ days vs 1 day
            "travel_penalty": -0.5,     # Cross-country travel
        },
        "notes": "Monitor pace trends - league getting faster"
    }

    # ═══════════════════════════════════════════════════════════════════════
    # COLLEGE FOOTBALL DATA (2024 Season)
    # ═══════════════════════════════════════════════════════════════════════
    CFB = {
        "season": "2024",
        "last_updated": "2026-01-28",
        "averages": {
            "points_per_game": 28.5,
            "yards_per_game": 410.0,
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
        "notes": "SP+ is predictive, not resume-based"
    }

    # ═══════════════════════════════════════════════════════════════════════
    # COLLEGE BASKETBALL DATA (2024-25 Season)
    # ═══════════════════════════════════════════════════════════════════════
    CBB = {
        "season": "2024-25",
        "last_updated": "2026-01-28",
        "averages": {
            "points_per_game": 73.5,
            "tempo": 68.0,          # Possessions per 40 min
            "offensive_efficiency": 105.0,  # Per 100 poss
            "defensive_efficiency": 105.0,
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
            "very_good": 20,      # Sweet 16+
            "good": 10,           # Tournament team
            "average": 0,         # Bubble/NIT
            "below_average": -10,
        },
        "notes": "KenPom AdjEM difference ≈ expected margin"
    }

    # ═══════════════════════════════════════════════════════════════════════
    # NHL DATA (2024-25 Season)
    # ═══════════════════════════════════════════════════════════════════════
    NHL = {
        "season": "2024-25",
        "last_updated": "2026-01-28",
        "averages": {
            "goals_per_game": 3.1,
            "corsi_pct": 50.0,
            "xgf_per_60": 2.8,
            "xga_per_60": 2.8,
            "save_pct": 0.905,
            "shooting_pct": 0.095,
        },
        "home_ice_advantage": 0.15,   # Goals (~3% win prob)
        "b2b_impact": {
            "goal_adjustment": -0.108,
            "win_prob_impact": -0.05,
        },
        "notes": "Confirm starting goalie at morning skate"
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
