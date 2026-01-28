"""
EDGE ATLAS V5.0 APEX - MASTER EDITION
Main Agent Orchestrator

The Omniscient Prediction Market & Sports Betting Domination System
Real-Time Verified • Education-First
NFL • NBA • College Football • College Basketball • NHL
"""

import sys
from datetime import datetime
from typing import Dict, List, Optional, Any

from .api.espn import ESPNClient, ESPNDataFreshness
from .api.odds import OddsClient, ScoringMarketAnalyzer
from .verification.engine import VerificationEngine
from .analytics.sports import (
    NFLAnalytics, NBAAnalytics, CFBAnalytics, CBBAnalytics, NHLAnalytics
)
from .engine.confidence import ConfidenceEngine, PositionManager
from .engine.edge_detector import EdgeDetector
from .engine.live_analyzer import LiveGameAnalyzer
from .engine.real_data_analyzer import RealDataAnalyzer
from .engine.smart_evaluator import SmartEvaluator, format_smart_pick
from .utils.formatter import OutputFormatter


class EdgeAtlasAgent:
    """
    EDGE ATLAS V5.0 APEX - MASTER EDITION

    Primary Directive: Maximum Edge + Real-Time Verification + User Education

    Capabilities:
    - Real-time ESPN data fetching
    - 9-layer verification protocol
    - Sport-specific analytics (DVOA, KenPom, xG, etc.)
    - Confidence Engine edge detection
    - Live in-game analysis
    - Educational output for every recommendation
    """

    VERSION = "5.0.0"
    CODENAME = "APEX MASTER EDITION"

    SUPPORTED_SPORTS = {
        "nfl": "NFL Football",
        "nba": "NBA Basketball",
        "cfb": "College Football",
        "cbb": "College Basketball",
        "nhl": "NHL Hockey",
    }

    ANALYTICS_CLASSES = {
        "nfl": NFLAnalytics,
        "nba": NBAAnalytics,
        "cfb": CFBAnalytics,
        "cbb": CBBAnalytics,
        "nhl": NHLAnalytics,
    }

    # Educational content library
    EDUCATION_TOPICS = {
        "dvoa": """
DVOA (Defense-adjusted Value Over Average)
==========================================

WHAT IT IS:
DVOA measures play-by-play efficiency, adjusting for opponent strength and game situation.
Developed by Football Outsiders, now at FTN Fantasy.

HOW TO READ IT:
• +10% DVOA = Team is 10% better than league average
• For OFFENSE: POSITIVE is better (scoring more efficiently)
• For DEFENSE: NEGATIVE is better (allowing fewer efficient plays)

WHY IT MATTERS FOR BETTING:
DVOA identifies teams that are BETTER or WORSE than their record suggests.
- A 6-4 team with +15% DVOA is undervalued—they've been unlucky
- A 7-3 team with -5% DVOA is overvalued—they've been lucky

Example: In 2023, the Lions started 3-3 but had elite DVOA. They finished 12-5.
Betting on teams with strong DVOA but mediocre records = long-term profit.
""",
        "epa": """
EPA (Expected Points Added)
============================

WHAT IT IS:
EPA measures how each play changes expected points based on down, distance, and field position.

THE KEY INSIGHT:
A 15-yard gain on 3rd-and-10 from your own 20 adds MORE value than the same gain
on 1st-and-10 from the opponent's 5. EPA captures this context.

HOW TO USE IT:
• EPA/Play > 0.10 = Elite offense
• EPA/Play < -0.05 = Struggling offense
• Compare EPA to yards—a team with high yards but low EPA is padding stats in garbage time

BETTING APPLICATION:
High EPA teams are consistently efficient. When they face low EPA defenses,
the matchup favors the offense more than raw stats suggest.
""",
        "kenpom": """
KenPom Ratings (College Basketball)
===================================

WHAT IT IS:
Ken Pomeroy's efficiency ratings, the gold standard for college basketball analytics.

KEY METRICS:
• AdjO (Adjusted Offense): Points per 100 possessions vs average defense
• AdjD (Adjusted Defense): Points allowed per 100 possessions vs average offense
• AdjEM (Efficiency Margin): AdjO - AdjD = Net rating

HOW TO USE FOR BETTING:
The difference in AdjEM between two teams approximates the expected margin.

Example:
- Team A: AdjEM +20
- Team B: AdjEM +5
- Neutral court expected margin: 15 points for Team A
- Home court: Add 3-4 points for home team

If the line is Team A -10, you have 5 points of value on Team A.

Source: kenpom.com ($24.95/year) - Essential for serious CBB betting
Free Alternative: barttorvik.com
""",
        "corsi": """
Corsi & Expected Goals (NHL)
=============================

CORSI (CF%):
Counts ALL shot attempts—goals, saves, misses, and blocks.
• CF% > 55% = Elite possession team
• CF% < 45% = Getting dominated

WHY IT MATTERS:
Corsi measures "process" over results. A team can have bad goaltending but still
control play. Over time, process wins out.

EXPECTED GOALS (xG):
Assigns probability (0-1) to each shot based on:
- Shot location (distance, angle)
- Shot type (wrist, slap, deflection)
- Pre-shot movement (pass, rebound)

THE EDGE:
Teams UNDERPERFORMING xG (high xGF, low actual goals) = positive regression candidate
Teams OVERPERFORMING xG (low xGF, high actual goals) = fade candidate

This is where sharp bettors find edge in hockey.
""",
        "clv": """
Closing Line Value (CLV)
========================

WHAT IT IS:
Did you beat the final (closing) line? The closing line represents the market's
best estimate of true probability after all information is priced in.

WHY IT'S THE REAL SCORECARD:
• Winning at bad odds = LUCK (will regress)
• Losing at good odds = SMART (will profit long-term)

Example:
- You bet Cowboys -3 on Tuesday at -110
- Line closes at Cowboys -4.5 on Sunday
- You got 1.5 points of CLV = YOU WIN LONG-TERM

Professional bettors track CLV religiously. A bettor with positive CLV will
profit over thousands of bets, even with a 48% win rate.

Track your CLV. It's the only metric that predicts future success.
""",
        "kelly": """
Kelly Criterion
===============

WHAT IT IS:
A formula for optimal bet sizing that maximizes long-term growth.

THE FORMULA:
Kelly% = (bp - q) / b

Where:
- b = decimal odds - 1
- p = probability of winning
- q = probability of losing (1-p)

EXAMPLE:
You have 55% edge on a +100 (even money) bet:
- b = 1
- p = 0.55
- q = 0.45
- Kelly% = (1 × 0.55 - 0.45) / 1 = 10%

IMPORTANT:
Full Kelly is AGGRESSIVE. Most professionals use 1/4 to 1/2 Kelly.
- 1/4 Kelly = smoother ride, still solid growth
- Full Kelly = maximum growth, extreme variance

ATLAS V5.0 uses Half-Kelly capped at grade-appropriate levels.
"""
    }

    def __init__(self, odds_api_key: Optional[str] = None, bankroll: float = 10000):
        """Initialize the Edge Atlas Agent."""
        self.espn = ESPNClient()
        self.espn_fresh = ESPNDataFreshness(self.espn)
        self.odds = OddsClient(api_key=odds_api_key)
        self.verification = VerificationEngine()
        self.confidence = ConfidenceEngine()
        self.edge_detector = EdgeDetector(odds_api_key=odds_api_key)
        self.live_analyzer = LiveGameAnalyzer()
        self.scoring_analyzer = ScoringMarketAnalyzer()
        self.position_manager = PositionManager(bankroll)
        self.formatter = OutputFormatter()
        self.real_analyzer = RealDataAnalyzer()
        self.smart_evaluator = SmartEvaluator()

        # Initialize analytics engines
        self.analytics = {
            sport: cls() for sport, cls in self.ANALYTICS_CLASSES.items()
        }

    def activate(self) -> str:
        """Display activation message and menu."""
        return self.formatter.format_activation()

    def scan_all_markets(self) -> str:
        """
        [1] OMNISCIENT MARKET SCAN
        Scan all sports for edge opportunities using REAL ESPN data.
        Smart evaluation like a real handicapper - no simulations.
        """
        output = []
        output.append("\n" + "=" * 70)
        output.append("EDGE ATLAS V5.0 - SMART MARKET SCAN")
        output.append("Real Data | Human-Like Evaluation | No Simulations")
        output.append("=" * 70)
        output.append(f"Scan Time: {datetime.now().isoformat()}")
        output.append("Data Source: ESPN Live API")
        output.append("=" * 70)

        all_picks = []

        for sport, sport_name in self.SUPPORTED_SPORTS.items():
            output.append(f"\nScanning {sport_name}...")

            try:
                # Get real games from ESPN
                games = self.real_analyzer.get_real_scoreboard(sport)
                upcoming = [g for g in games if g.get("status", {}).get("state") == "pre"]

                if not upcoming:
                    output.append(f"  No upcoming {sport.upper()} games found")
                    continue

                output.append(f"  Found {len(upcoming)} upcoming games")

                # Evaluate each game with smart analysis
                for game in upcoming[:5]:  # Top 5 per sport
                    pick = self.smart_evaluator.evaluate_game(sport, game)
                    if pick.confidence_level != "PASS":
                        all_picks.append(pick)

            except Exception as e:
                output.append(f"  Error scanning {sport}: {str(e)}")

        output.append("\n" + "=" * 70)

        if all_picks:
            # Sort by edge
            all_picks.sort(key=lambda x: x.edge_pct, reverse=True)

            output.append(f"\nFOUND {len(all_picks)} EDGE OPPORTUNITIES:")
            output.append("=" * 70)

            for pick in all_picks[:10]:  # Top 10
                output.append(format_smart_pick(pick))
        else:
            output.append("\nNO EDGES FOUND MEETING CRITERIA")
            output.append("\nThis is NORMAL - sharp markets don't offer easy edges.")
            output.append("Most games are fairly priced. Be patient.")
            output.append("\nRemember: One excellent bet beats ten mediocre ones.")

        return "\n".join(output)

    def scan_sport(self, sport: str) -> str:
        """
        [3] SPORT DEEP DIVE
        Scan a specific sport for edges.
        """
        sport = sport.lower()
        if sport not in self.SUPPORTED_SPORTS:
            return f"Unknown sport: {sport}. Supported: {', '.join(self.SUPPORTED_SPORTS.keys())}"

        edges = self.edge_detector.scan_sport(sport)

        edge_dicts = []
        for edge in edges:
            edge_dicts.append({
                "sport": edge.sport,
                "game_id": edge.game_id,
                "game_name": edge.game_name,
                "market_type": edge.market_type,
                "selection": edge.selection,
                "edge_pct": edge.edge_pct,
                "confidence": edge.confidence,
                "grade": edge.grade,
                "verification_summary": edge.verification_summary,
            })

        return self.formatter.format_edge_scan(edge_dicts)

    def get_live_suggestions(self, sport: Optional[str] = None) -> str:
        """
        [2] LIVE IN-GAME ANALYSIS
        Get real-time suggestions for live games using actual game state.
        No simulated data - only real ESPN live data.
        """
        output = []
        output.append("\n" + "=" * 70)
        output.append("EDGE ATLAS V5.0 - LIVE GAME ANALYSIS")
        output.append("Real-Time Data | In-Progress Games Only")
        output.append("=" * 70)
        output.append(f"Scan Time: {datetime.now().isoformat()}")
        output.append("=" * 70)

        all_live = []
        sports_to_scan = [sport.lower()] if sport else list(self.SUPPORTED_SPORTS.keys())

        for s in sports_to_scan:
            try:
                live_games = self.real_analyzer.get_live_games_real(s)

                if live_games:
                    output.append(f"\n{s.upper()}: {len(live_games)} live game(s)")

                    for game in live_games:
                        analysis = self.real_analyzer.analyze_live_game_real(s, game)
                        all_live.append(analysis)

                        # Display live game info
                        output.append(f"\n  LIVE: {analysis['game_name']}")
                        output.append(f"  Score: {analysis['teams']['away']} {analysis['score']['away']} - "
                                     f"{analysis['score']['home']} {analysis['teams']['home']}")
                        output.append(f"  {analysis['status'].get('detail', '')}")

                        if analysis['live_odds'].get('spread'):
                            output.append(f"  Live Spread: {analysis['live_odds']['spread']}")
                        if analysis['live_odds'].get('total'):
                            output.append(f"  Live Total: {analysis['live_odds']['total']}")

            except Exception as e:
                output.append(f"\n{s.upper()}: Error - {str(e)}")

        if not all_live:
            output.append("\nNo live games currently in progress.")
            output.append("Check back when games are being played.")

        # Also get live suggestions from the live analyzer
        if all_live:
            output.append("\n" + "-" * 70)
            output.append("LIVE BETTING ANALYSIS")
            output.append("-" * 70)

            for s in sports_to_scan:
                live_games = self.espn.get_live_games(s)
                if live_games:
                    suggestions = self.live_analyzer.get_live_suggestions(live_games, s)
                    if suggestions:
                        for sugg in suggestions[:3]:  # Top 3 per sport
                            output.append(f"\n  {sugg.time_sensitivity}: {sugg.game_name}")
                            output.append(f"  Selection: {sugg.selection}")
                            output.append(f"  Edge: {sugg.edge_pct:.1f}% | Confidence: {sugg.confidence}")
                            output.append(f"  Rationale: {sugg.rationale}")

        output.append("\n" + "=" * 70)
        return "\n".join(output)

    def analyze_game(self, sport: str, game_id: str) -> str:
        """
        [4] GAME ANALYSIS
        Deep analysis of a specific game.
        """
        sport = sport.lower()
        if sport not in self.SUPPORTED_SPORTS:
            return f"Unknown sport: {sport}"

        # Get game details
        details = self.espn.get_game_details(sport, game_id)

        if "error" in details:
            return f"Error fetching game: {details['error']}"

        # Get analytics engine
        analytics = self.analytics.get(sport)

        # Parse game data
        game_info = details.get("header", {}).get("competitions", [{}])[0]
        competitors = game_info.get("competitors", [])

        home_team = None
        away_team = None
        for comp in competitors:
            if comp.get("homeAway") == "home":
                home_team = comp
            else:
                away_team = comp

        if not home_team or not away_team:
            return "Could not parse game data"

        # Run matchup analysis
        home_stats = {}  # Would populate from real data
        away_stats = {}

        matchup = analytics.analyze_matchup(home_stats, away_stats) if analytics else {}

        # Get injuries
        home_injuries = self.espn.get_team_injuries(sport, home_team.get("team", {}).get("id", ""))
        away_injuries = self.espn.get_team_injuries(sport, away_team.get("team", {}).get("id", ""))

        # Build analysis
        analysis = {
            "game_name": f"{away_team.get('team', {}).get('displayName', 'Away')} @ "
                        f"{home_team.get('team', {}).get('displayName', 'Home')}",
            "home_team": home_team.get("team", {}).get("displayName", "Home"),
            "away_team": away_team.get("team", {}).get("displayName", "Away"),
            "date": game_info.get("date", "TBD"),
            "home_win_probability": matchup.get("home_win_probability", 0.5),
            "odds": details.get("odds", {}),
            "metrics": matchup.get("home_metrics", []) + matchup.get("away_metrics", []),
            "recommendations": [],
            "home_injuries": home_injuries,
            "away_injuries": away_injuries,
        }

        return self.formatter.format_game_analysis(analysis)

    def get_scoreboard(self, sport: str) -> str:
        """Get current scoreboard for a sport."""
        sport = sport.lower()
        if sport not in self.SUPPORTED_SPORTS:
            return f"Unknown sport: {sport}"

        scoreboard = self.espn.get_scoreboard(sport)
        games = self.espn.parse_scoreboard(scoreboard)

        return self.formatter.format_scoreboard(games, sport)

    def learn(self, topic: str) -> str:
        """
        [5] LEARN MODE
        Teach analytics concepts.
        """
        topic = topic.lower()

        if topic in self.EDUCATION_TOPICS:
            return self.formatter.format_education(topic.upper(), self.EDUCATION_TOPICS[topic])

        # List available topics
        available = ", ".join(self.EDUCATION_TOPICS.keys())
        return f"Topic '{topic}' not found.\n\nAvailable topics: {available}"

    def verify_bet(
        self,
        sport: str,
        game_id: str,
        true_prob: float,
        market_prob: float
    ) -> str:
        """Run 9-layer verification on a potential bet."""
        sport = sport.lower()

        # Fetch fresh data
        scoreboard = self.espn.get_scoreboard(sport)
        games = self.espn.parse_scoreboard(scoreboard)

        game_data = None
        for game in games:
            if game.get("game_id") == game_id:
                game_data = game
                break

        if not game_data:
            return "Game not found"

        # Run verification
        result = self.verification.run_full_verification(
            sport=sport,
            event_id=game_id,
            espn_data=game_data,
            odds_data=game_data.get("odds"),
            true_prob=true_prob,
            market_prob=market_prob,
        )

        return self.formatter.format_verification_result(result.to_dict())

    def run_interactive(self):
        """Run interactive command loop."""
        print(self.activate())

        while True:
            try:
                command = input("\n📊 Enter command (or 'help'): ").strip().lower()

                if command in ["exit", "quit", "q"]:
                    print("\n👋 EDGE ATLAS signing off. Protect your capital!")
                    break

                elif command in ["1", "scan", "market scan"]:
                    print("\n🔍 Scanning all markets...")
                    print(self.scan_all_markets())

                elif command in ["2", "live"]:
                    print("\n🔴 Getting live suggestions...")
                    print(self.get_live_suggestions())

                elif command.startswith("3 ") or command.startswith("sport "):
                    sport = command.split(" ", 1)[1] if " " in command else ""
                    if sport:
                        print(f"\n🔍 Scanning {sport.upper()}...")
                        print(self.scan_sport(sport))
                    else:
                        print("Usage: sport <nfl|nba|cfb|cbb|nhl>")

                elif command.startswith("score"):
                    parts = command.split()
                    sport = parts[1] if len(parts) > 1 else "nba"
                    print(self.get_scoreboard(sport))

                elif command.startswith("5 ") or command.startswith("learn "):
                    topic = command.split(" ", 1)[1] if " " in command else ""
                    if topic:
                        print(self.learn(topic))
                    else:
                        print(f"Available topics: {', '.join(self.EDUCATION_TOPICS.keys())}")

                elif command in ["help", "h", "?"]:
                    print("""
EDGE ATLAS V5.0 COMMANDS:
━━━━━━━━━━━━━━━━━━━━━━━━━
1 / scan        - Scan all markets for edges
2 / live        - Get live in-game suggestions
3 <sport>       - Deep dive on specific sport (nfl, nba, cfb, cbb, nhl)
score <sport>   - Get current scoreboard
learn <topic>   - Learn an analytics concept
                  Topics: dvoa, epa, kenpom, corsi, clv, kelly

help            - Show this help
exit            - Exit EDGE ATLAS
""")

                else:
                    print("Unknown command. Type 'help' for available commands.")

            except KeyboardInterrupt:
                print("\n\n👋 EDGE ATLAS signing off. Protect your capital!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")


def main():
    """Main entry point."""
    agent = EdgeAtlasAgent()
    agent.run_interactive()


if __name__ == "__main__":
    main()
