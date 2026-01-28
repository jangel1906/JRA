"""
ESPN Live API Integration
Real-time sports data for NFL, NBA, CFB, CBB, NHL
"""

import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json


class ESPNClient:
    """
    ESPN API Client for live sports data.

    Endpoints used:
    - scoreboard: Live scores and game status
    - teams: Team information and rosters
    - injuries: Injury reports
    - odds: Betting lines (when available)
    """

    BASE_URL = "https://site.api.espn.com/apis/site/v2/sports"

    SPORT_CONFIGS = {
        "nfl": {"sport": "football", "league": "nfl"},
        "nba": {"sport": "basketball", "league": "nba"},
        "cfb": {"sport": "football", "league": "college-football"},
        "cbb": {"sport": "basketball", "league": "mens-college-basketball"},
        "nhl": {"sport": "hockey", "league": "nhl"},
    }

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "EDGE-ATLAS/5.0",
            "Accept": "application/json"
        })
        self._cache = {}
        self._cache_ttl = 60  # seconds

    def _get_url(self, sport_key: str, endpoint: str) -> str:
        """Build API URL for given sport and endpoint."""
        config = self.SPORT_CONFIGS.get(sport_key.lower())
        if not config:
            raise ValueError(f"Unknown sport: {sport_key}")
        return f"{self.BASE_URL}/{config['sport']}/{config['league']}/{endpoint}"

    def _fetch(self, url: str, params: Optional[Dict] = None) -> Dict:
        """Fetch data from ESPN API with caching."""
        cache_key = f"{url}:{json.dumps(params or {}, sort_keys=True)}"
        now = datetime.now()

        if cache_key in self._cache:
            cached_data, cached_time = self._cache[cache_key]
            if (now - cached_time).seconds < self._cache_ttl:
                return cached_data

        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            self._cache[cache_key] = (data, now)
            return data
        except requests.RequestException as e:
            return {"error": str(e), "timestamp": now.isoformat()}

    def get_scoreboard(self, sport: str, dates: Optional[str] = None) -> Dict:
        """
        Get live scoreboard data.

        Args:
            sport: nfl, nba, cfb, cbb, nhl
            dates: Optional date string YYYYMMDD (defaults to today)

        Returns:
            Dict with events, each containing:
            - id: Game ID
            - name: Matchup name
            - date: Game datetime
            - status: Game status (pre, in, post)
            - competitors: Teams with scores
            - odds: Betting lines if available
        """
        url = self._get_url(sport, "scoreboard")
        params = {}
        if dates:
            params["dates"] = dates
        return self._fetch(url, params)

    def get_game_details(self, sport: str, game_id: str) -> Dict:
        """Get detailed game information including play-by-play if live."""
        url = self._get_url(sport, f"summary")
        params = {"event": game_id}
        return self._fetch(url, params)

    def get_team_info(self, sport: str, team_id: str) -> Dict:
        """Get team information including roster and stats."""
        url = self._get_url(sport, f"teams/{team_id}")
        return self._fetch(url)

    def get_injuries(self, sport: str) -> Dict:
        """Get injury reports for all teams in a league."""
        url = self._get_url(sport, "injuries")
        return self._fetch(url)

    def get_news(self, sport: str, limit: int = 10) -> Dict:
        """Get latest news articles."""
        url = self._get_url(sport, "news")
        params = {"limit": limit}
        return self._fetch(url, params)

    def get_standings(self, sport: str) -> Dict:
        """Get current standings."""
        url = self._get_url(sport, "standings")
        return self._fetch(url)

    def get_teams(self, sport: str) -> Dict:
        """Get all teams in a league."""
        url = self._get_url(sport, "teams")
        return self._fetch(url)

    def parse_scoreboard(self, data: Dict) -> List[Dict]:
        """
        Parse scoreboard data into structured game objects.

        Returns list of games with:
        - game_id: Unique identifier
        - name: "Team A vs Team B"
        - date: ISO datetime
        - status: pre/in/post
        - home_team: {id, name, abbreviation, score}
        - away_team: {id, name, abbreviation, score}
        - odds: {spread, total, moneyline} if available
        - venue: {name, city, state}
        - broadcast: TV network if available
        """
        games = []
        events = data.get("events", [])

        for event in events:
            game = {
                "game_id": event.get("id"),
                "name": event.get("name"),
                "short_name": event.get("shortName"),
                "date": event.get("date"),
                "status": self._parse_status(event.get("status", {})),
                "home_team": None,
                "away_team": None,
                "odds": None,
                "venue": None,
                "broadcast": None,
                "weather": None,
            }

            competitions = event.get("competitions", [{}])
            if competitions:
                comp = competitions[0]

                # Parse teams
                for team_data in comp.get("competitors", []):
                    team_info = self._parse_team(team_data)
                    if team_data.get("homeAway") == "home":
                        game["home_team"] = team_info
                    else:
                        game["away_team"] = team_info

                # Parse odds
                odds_data = comp.get("odds", [])
                if odds_data:
                    game["odds"] = self._parse_odds(odds_data[0])

                # Parse venue
                venue = comp.get("venue", {})
                if venue:
                    game["venue"] = {
                        "name": venue.get("fullName"),
                        "city": venue.get("address", {}).get("city"),
                        "state": venue.get("address", {}).get("state"),
                        "indoor": venue.get("indoor", False),
                    }

                # Parse broadcast
                broadcasts = comp.get("broadcasts", [])
                if broadcasts:
                    game["broadcast"] = broadcasts[0].get("names", [])

                # Weather (outdoor sports)
                weather = comp.get("weather", {})
                if weather:
                    game["weather"] = {
                        "temperature": weather.get("temperature"),
                        "condition": weather.get("displayValue"),
                        "wind_speed": weather.get("windSpeed"),
                    }

            games.append(game)

        return games

    def _parse_status(self, status: Dict) -> Dict:
        """Parse game status."""
        status_type = status.get("type", {})
        return {
            "state": status_type.get("state", "pre"),
            "completed": status_type.get("completed", False),
            "description": status_type.get("description", ""),
            "detail": status_type.get("detail", ""),
            "clock": status.get("displayClock"),
            "period": status.get("period"),
        }

    def _parse_team(self, team_data: Dict) -> Dict:
        """Parse team competitor data."""
        team = team_data.get("team", {})
        return {
            "id": team.get("id"),
            "name": team.get("displayName"),
            "abbreviation": team.get("abbreviation"),
            "logo": team.get("logo"),
            "score": team_data.get("score"),
            "winner": team_data.get("winner"),
            "records": [r.get("summary") for r in team_data.get("records", [])],
        }

    def _parse_odds(self, odds_data: Dict) -> Dict:
        """Parse betting odds data."""
        return {
            "provider": odds_data.get("provider", {}).get("name"),
            "spread": odds_data.get("spread"),
            "spread_winner": odds_data.get("spreadWinner"),
            "over_under": odds_data.get("overUnder"),
            "home_moneyline": odds_data.get("homeTeamOdds", {}).get("moneyLine"),
            "away_moneyline": odds_data.get("awayTeamOdds", {}).get("moneyLine"),
            "details": odds_data.get("details"),
        }

    def get_live_games(self, sport: str) -> List[Dict]:
        """Get only games currently in progress."""
        scoreboard = self.get_scoreboard(sport)
        games = self.parse_scoreboard(scoreboard)
        return [g for g in games if g["status"]["state"] == "in"]

    def get_upcoming_games(self, sport: str, days_ahead: int = 7) -> List[Dict]:
        """Get upcoming games within specified days."""
        all_games = []
        today = datetime.now()

        for i in range(days_ahead):
            date = today + timedelta(days=i)
            date_str = date.strftime("%Y%m%d")
            scoreboard = self.get_scoreboard(sport, dates=date_str)
            games = self.parse_scoreboard(scoreboard)

            for game in games:
                if game["status"]["state"] == "pre":
                    all_games.append(game)

        return all_games

    def get_team_injuries(self, sport: str, team_id: str) -> List[Dict]:
        """Get injuries for a specific team."""
        injuries_data = self.get_injuries(sport)
        team_injuries = []

        for team in injuries_data.get("injuries", []):
            if team.get("team", {}).get("id") == team_id:
                for injury in team.get("injuries", []):
                    team_injuries.append({
                        "player": injury.get("athlete", {}).get("displayName"),
                        "position": injury.get("athlete", {}).get("position", {}).get("abbreviation"),
                        "status": injury.get("status"),
                        "injury_type": injury.get("type", {}).get("description"),
                        "details": injury.get("details", {}).get("detail"),
                        "return_date": injury.get("details", {}).get("returnDate"),
                    })

        return team_injuries


class ESPNDataFreshness:
    """Track and validate data freshness for verification."""

    def __init__(self, client: ESPNClient):
        self.client = client
        self.fetch_times = {}

    def fetch_with_timestamp(self, sport: str, endpoint: str, **kwargs) -> Dict:
        """Fetch data and record timestamp."""
        now = datetime.now()

        if endpoint == "scoreboard":
            data = self.client.get_scoreboard(sport, **kwargs)
        elif endpoint == "injuries":
            data = self.client.get_injuries(sport)
        elif endpoint == "news":
            data = self.client.get_news(sport, **kwargs)
        else:
            data = {}

        key = f"{sport}:{endpoint}"
        self.fetch_times[key] = now

        return {
            "data": data,
            "fetched_at": now.isoformat(),
            "freshness_seconds": 0,
        }

    def is_data_fresh(self, sport: str, endpoint: str, max_age_seconds: int = 300) -> bool:
        """Check if cached data is still fresh."""
        key = f"{sport}:{endpoint}"
        if key not in self.fetch_times:
            return False

        age = (datetime.now() - self.fetch_times[key]).seconds
        return age < max_age_seconds

    def get_data_age(self, sport: str, endpoint: str) -> Optional[int]:
        """Get age of cached data in seconds."""
        key = f"{sport}:{endpoint}"
        if key not in self.fetch_times:
            return None
        return (datetime.now() - self.fetch_times[key]).seconds
