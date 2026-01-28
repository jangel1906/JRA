"""
Educational Output Formatter
Formats all outputs with education-first approach
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from ..engine.confidence import BetRecommendation, BetGrade


class OutputFormatter:
    """
    Formats output following ATLAS V5.0 specification.
    Education-first, showing calculations and WHY picks win.
    """

    # ANSI color codes for terminal
    COLORS = {
        "green": "\033[92m",
        "red": "\033[91m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "cyan": "\033[96m",
        "magenta": "\033[95m",
        "bold": "\033[1m",
        "reset": "\033[0m",
    }

    GRADE_COLORS = {
        BetGrade.A_PLUS: "green",
        BetGrade.A: "green",
        BetGrade.B_PLUS: "cyan",
        BetGrade.B: "blue",
        BetGrade.C: "yellow",
        BetGrade.PASS: "red",
    }

    def __init__(self, use_colors: bool = True):
        self.use_colors = use_colors

    def color(self, text: str, color: str) -> str:
        """Apply color to text if colors enabled."""
        if not self.use_colors:
            return text
        return f"{self.COLORS.get(color, '')}{text}{self.COLORS['reset']}"

    def format_activation(self) -> str:
        """Format system activation message."""
        return """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚡ EDGE ATLAS V5.0 APEX — MASTER EDITION — ONLINE
🔍 VERIFICATION ENGINE: 9-LAYER PROTOCOL ACTIVE
📡 INTELLIGENCE: ESPN Live API • Real-Time Data
📚 EDUCATION MODE: COMPREHENSIVE
🏈 SPORTS: NFL • NBA • CFB • CBB • NHL

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MENU OPTIONS:
[1] OMNISCIENT MARKET SCAN — Scan for highest-edge opportunities
[2] LIVE IN-GAME ANALYSIS — Real-time live game edges
[3] SPORT DEEP DIVE — Analyze specific sport
[4] GAME ANALYSIS — Analyze specific game
[5] LEARN MODE — Teach any analytics concept
[6] PORTFOLIO CHECK — Review active positions

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    def format_recommendation(self, rec: BetRecommendation) -> str:
        """Format a complete bet recommendation."""
        grade_color = self.GRADE_COLORS.get(rec.grade, "reset")

        # Build the output
        output = []
        output.append("━" * 60)
        output.append(self.color(f"📊 {rec.market_type.upper()} ANALYSIS", "bold"))
        output.append("━" * 60)

        # Selection and odds
        output.append(f"\n🎯 Selection: {self.color(rec.selection, 'cyan')}")
        output.append(f"📈 Odds: {rec.odds}")

        # Probabilities
        output.append(f"\n📐 PROBABILITY ANALYSIS:")
        output.append(f"   Market Implied: {rec.market_probability*100:.1f}%")
        output.append(f"   Our Calculation: {self.color(f'{rec.true_probability*100:.1f}%', 'green')}")
        output.append(f"   Edge: {self.color(f'{rec.edge_pct:.1f}%', 'green' if rec.edge_pct > 5 else 'yellow')}")

        # Confidence Engine
        output.append(f"\n🔬 CONFIDENCE ENGINE:")
        output.append(f"   CE%: {rec.ce_pct}%")
        output.append(f"   Grade: {self.color(rec.grade.value, grade_color)}")
        output.append(f"   Kelly%: {rec.kelly_pct}%")

        # Recommendation
        if rec.recommendation == "BET":
            output.append(f"\n✅ RECOMMENDATION: {self.color('BET', 'green')}")
            output.append(f"   Position Size: {rec.position_size_pct:.1f}% of bankroll")
        else:
            output.append(f"\n❌ RECOMMENDATION: {self.color('PASS', 'red')}")
            output.append(f"   Reason: {rec.rationale}")

        # Education
        output.append(f"\n📚 WHY THIS {'WINS' if rec.recommendation == 'BET' else 'IS A PASS'}:")
        for line in rec.education.split('\n'):
            output.append(f"   {line}")

        # Risk factors
        if rec.risk_factors:
            output.append(f"\n⚠️ RISK FACTORS:")
            for risk in rec.risk_factors:
                output.append(f"   • {risk}")

        output.append(f"\n⏰ Analysis Time: {rec.timestamp}")
        output.append("━" * 60)

        return "\n".join(output)

    def format_edge_scan(self, edges: List[Dict]) -> str:
        """Format results of an edge scan."""
        if not edges:
            return self.color("\n❌ No edges found meeting minimum criteria (5% edge, verification passed)\n", "yellow")

        output = []
        output.append("\n" + "━" * 70)
        output.append(self.color("🔍 EDGE SCAN RESULTS", "bold"))
        output.append("━" * 70)
        output.append(f"\n📊 Found {len(edges)} opportunities:\n")

        for i, edge in enumerate(edges[:10], 1):  # Show top 10
            grade_color = "green" if edge.get("grade") in ["A+", "A"] else "cyan" if edge.get("grade") == "B+" else "yellow"

            output.append(f"{i}. {self.color(edge.get('game_name', 'Unknown'), 'cyan')}")
            output.append(f"   Sport: {edge.get('sport', 'Unknown')} | Market: {edge.get('market_type', 'Unknown')}")
            output.append(f"   Selection: {self.color(edge.get('selection', ''), 'bold')}")
            edge_pct = edge.get('edge_pct', 0)
            confidence = edge.get('confidence', 0)
            edge_str = f"{edge_pct:.1f}%"
            output.append(f"   Edge: {self.color(edge_str, 'green')} | "
                         f"Grade: {self.color(edge.get('grade', 'N/A'), grade_color)} | "
                         f"CE: {confidence:.1f}%")
            output.append(f"   Verification: {edge.get('verification_summary', 'N/A')}")
            output.append("")

        output.append("━" * 70)
        return "\n".join(output)

    def format_live_suggestions(self, suggestions: List[Any]) -> str:
        """Format live game suggestions."""
        if not suggestions:
            return self.color("\n❌ No live edges currently available\n", "yellow")

        output = []
        output.append("\n" + "━" * 70)
        output.append(self.color("🔴 LIVE BETTING SUGGESTIONS", "bold"))
        output.append("━" * 70)
        output.append(f"\n⚡ {len(suggestions)} live opportunities found:\n")

        for i, sugg in enumerate(suggestions[:5], 1):  # Top 5 live
            urgency_color = "red" if sugg.time_sensitivity == "ACT NOW" else "yellow"

            output.append(f"{i}. {self.color(sugg.game_name, 'cyan')}")
            output.append(f"   {self.color(sugg.time_sensitivity, urgency_color)} | "
                         f"{sugg.sport} | {sugg.market}")
            output.append(f"   🎯 {self.color(sugg.selection, 'bold')}")
            output.append(f"   Edge: {self.color(f'{sugg.edge_pct:.1f}%', 'green')} | "
                         f"Confidence: {sugg.confidence}")
            output.append(f"   Rationale: {sugg.rationale}")

            if sugg.verification_notes:
                output.append(f"   Notes: {' | '.join(sugg.verification_notes)}")
            output.append("")

        output.append("━" * 70)
        return "\n".join(output)

    def format_verification_result(self, result: Dict) -> str:
        """Format verification result."""
        output = []
        output.append("\n" + "━" * 60)
        output.append(self.color("🔍 9-LAYER VERIFICATION REPORT", "bold"))
        output.append("━" * 60)

        output.append(f"\nSport: {result.get('sport', 'Unknown')} | Event: {result.get('event_id', 'Unknown')}")
        output.append(f"Status: {self.color('PASSED', 'green') if result.get('passed') else self.color('FAILED', 'red')}")
        output.append(f"Summary: {result.get('summary', '')}\n")

        for layer in result.get("layers", []):
            status_icon = layer.get("status", "○")
            output.append(f"Layer {layer.get('layer', '?')}: {layer.get('name', 'Unknown')} [{status_icon}]")
            for check in layer.get("checks", []):
                output.append(f"   {check.get('status', '○')} {check.get('name', '')}: {check.get('detail', '')}")

        if result.get("warnings"):
            output.append(f"\n⚠️ Warnings:")
            for warning in result["warnings"]:
                output.append(f"   • {warning}")

        if result.get("blockers"):
            output.append(f"\n🚫 Blockers:")
            for blocker in result["blockers"]:
                output.append(f"   • {blocker}")

        output.append("\n" + "━" * 60)
        return "\n".join(output)

    def format_education(self, topic: str, content: str) -> str:
        """Format educational content."""
        output = []
        output.append("\n" + "━" * 60)
        output.append(self.color(f"📚 LEARN: {topic.upper()}", "bold"))
        output.append("━" * 60)
        output.append("")
        output.append(content)
        output.append("\n" + "━" * 60)
        return "\n".join(output)

    def format_game_analysis(self, analysis: Dict) -> str:
        """Format complete game analysis."""
        output = []
        output.append("\n" + "━" * 70)
        output.append(self.color(f"🏆 GAME ANALYSIS: {analysis.get('game_name', 'Unknown')}", "bold"))
        output.append("━" * 70)

        # Teams
        output.append(f"\n📊 MATCHUP:")
        output.append(f"   {analysis.get('home_team', 'Home')} vs {analysis.get('away_team', 'Away')}")
        output.append(f"   Date/Time: {analysis.get('date', 'TBD')}")

        # Win probabilities
        output.append(f"\n🎲 WIN PROBABILITIES:")
        home_prob = analysis.get('home_win_probability', 0.5)
        output.append(f"   Home: {home_prob*100:.1f}%")
        output.append(f"   Away: {(1-home_prob)*100:.1f}%")

        # Odds comparison
        if analysis.get('odds'):
            odds = analysis['odds']
            output.append(f"\n💰 CURRENT ODDS:")
            output.append(f"   Spread: {odds.get('spread', 'N/A')}")
            output.append(f"   Total: {odds.get('over_under', 'N/A')}")
            output.append(f"   Home ML: {odds.get('home_moneyline', 'N/A')}")
            output.append(f"   Away ML: {odds.get('away_moneyline', 'N/A')}")

        # Key metrics
        if analysis.get('metrics'):
            output.append(f"\n📈 KEY METRICS:")
            for metric in analysis['metrics']:
                output.append(f"   {metric.get('name', '')}: {metric.get('value', '')}")
                output.append(f"      → {metric.get('interpretation', '')}")

        # Recommendations
        if analysis.get('recommendations'):
            output.append(f"\n✅ RECOMMENDATIONS:")
            for rec in analysis['recommendations']:
                output.append(f"   • {rec}")

        output.append("\n" + "━" * 70)
        return "\n".join(output)

    def format_scoreboard(self, games: List[Dict], sport: str) -> str:
        """Format scoreboard/upcoming games."""
        output = []
        output.append("\n" + "━" * 70)
        output.append(self.color(f"📺 {sport.upper()} GAMES", "bold"))
        output.append("━" * 70)

        if not games:
            output.append("\nNo games found.")
            return "\n".join(output)

        for game in games[:15]:  # Limit to 15
            status = game.get("status", {})
            state = status.get("state", "pre")

            if state == "in":
                state_display = self.color("🔴 LIVE", "red")
            elif state == "post":
                state_display = "✅ FINAL"
            else:
                state_display = "📅 UPCOMING"

            home = game.get("home_team", {})
            away = game.get("away_team", {})

            output.append(f"\n{state_display} {game.get('short_name', game.get('name', 'Unknown'))}")

            if state in ["in", "post"]:
                output.append(f"   Score: {away.get('name', 'Away')} {away.get('score', 0)} - "
                             f"{home.get('score', 0)} {home.get('name', 'Home')}")
                if state == "in":
                    output.append(f"   {status.get('detail', '')}")
            else:
                output.append(f"   {game.get('date', 'TBD')}")

            odds = game.get("odds")
            if odds:
                output.append(f"   Line: {odds.get('spread', 'N/A')} | O/U: {odds.get('over_under', 'N/A')}")

        output.append("\n" + "━" * 70)
        return "\n".join(output)
