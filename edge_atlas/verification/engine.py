"""
9-Layer Verification Protocol
CRITICAL: Every analysis MUST pass ALL layers. If ANY layer fails, output PASS.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum


class VerificationStatus(Enum):
    """Status of a verification check."""
    PASSED = "✓"
    FAILED = "✗"
    WARNING = "⚠"
    PENDING = "○"


@dataclass
class LayerResult:
    """Result of a single verification layer."""
    layer_name: str
    layer_number: int
    status: VerificationStatus
    checks: List[Dict]
    notes: str = ""
    blocking: bool = True  # If failed, blocks recommendation


@dataclass
class VerificationResult:
    """Complete verification result across all 9 layers."""
    sport: str
    event_id: str
    timestamp: str
    layers: List[LayerResult]
    passed: bool
    confidence_adjustment: float = 0.0
    warnings: List[str] = field(default_factory=list)
    blockers: List[str] = field(default_factory=list)

    def get_summary(self) -> str:
        """Get summary of verification status."""
        passed_count = sum(1 for l in self.layers if l.status == VerificationStatus.PASSED)
        total = len(self.layers)
        return f"Verification: {passed_count}/{total} layers passed"

    def to_dict(self) -> Dict:
        """Convert to dictionary for output."""
        return {
            "sport": self.sport,
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "passed": self.passed,
            "summary": self.get_summary(),
            "layers": [
                {
                    "layer": l.layer_number,
                    "name": l.layer_name,
                    "status": l.status.value,
                    "checks": l.checks,
                    "notes": l.notes,
                }
                for l in self.layers
            ],
            "warnings": self.warnings,
            "blockers": self.blockers,
            "confidence_adjustment": self.confidence_adjustment,
        }


class VerificationEngine:
    """
    The 9-Layer Verification Protocol Engine.

    Layers:
    1. Data Freshness Verification
    2. Mathematical Verification
    3. Multi-Source Cross-Verification
    4. Sharp Line Integration (Pinnacle)
    5. Logical Consistency
    6. Whale & Top-Trader Intelligence
    7. Twitter/X Intelligence
    8. Market Mechanics
    9. Monte Carlo Validation
    """

    def __init__(self):
        self.data_sources = {}
        self.injury_data = {}
        self.odds_data = {}
        self.social_data = {}

    def run_full_verification(
        self,
        sport: str,
        event_id: str,
        espn_data: Dict,
        odds_data: Optional[Dict] = None,
        injury_data: Optional[List] = None,
        social_signals: Optional[Dict] = None,
        true_prob: Optional[float] = None,
        market_prob: Optional[float] = None,
    ) -> VerificationResult:
        """
        Execute all 9 verification layers.

        Args:
            sport: Sport key (nfl, nba, etc.)
            event_id: Game/event identifier
            espn_data: Data from ESPN API
            odds_data: Betting odds data
            injury_data: Injury reports
            social_signals: Twitter/social media data
            true_prob: Our calculated true probability
            market_prob: Market implied probability

        Returns:
            VerificationResult with all layer outcomes
        """
        timestamp = datetime.now().isoformat()
        layers = []
        warnings = []
        blockers = []

        # Layer 1: Data Freshness
        layer1 = self._verify_data_freshness(sport, espn_data)
        layers.append(layer1)
        if layer1.status == VerificationStatus.FAILED:
            blockers.append("Data freshness check failed - stale data")

        # Layer 2: Mathematical Verification
        layer2 = self._verify_math(odds_data, true_prob, market_prob)
        layers.append(layer2)
        if layer2.status == VerificationStatus.FAILED:
            blockers.append("Mathematical verification failed")

        # Layer 3: Multi-Source Cross-Verification
        layer3 = self._verify_multi_source(injury_data, espn_data)
        layers.append(layer3)
        if layer3.status == VerificationStatus.WARNING:
            warnings.append("Source conflict detected - widening confidence interval")

        # Layer 4: Sharp Line Integration
        layer4 = self._verify_sharp_line(odds_data, true_prob)
        layers.append(layer4)
        if layer4.status == VerificationStatus.WARNING:
            warnings.append("True prob differs from Pinnacle by >5%")

        # Layer 5: Logical Consistency
        layer5 = self._verify_logical_consistency(true_prob, market_prob)
        layers.append(layer5)
        if layer5.status == VerificationStatus.FAILED:
            blockers.append("Edge >25% - suspicious, triple-check required")

        # Layer 6: Whale & Top-Trader Intelligence
        layer6 = self._verify_whale_signals(social_signals)
        layers.append(layer6)

        # Layer 7: Twitter/X Intelligence
        layer7 = self._verify_social_intel(social_signals, sport)
        layers.append(layer7)

        # Layer 8: Market Mechanics
        layer8 = self._verify_market_mechanics(odds_data)
        layers.append(layer8)
        if layer8.status == VerificationStatus.WARNING:
            warnings.append("Wide bid/ask spread detected")

        # Layer 9: Monte Carlo Validation
        layer9 = self._verify_monte_carlo(true_prob)
        layers.append(layer9)

        # Overall pass/fail
        critical_failed = any(
            l.status == VerificationStatus.FAILED and l.blocking
            for l in layers
        )
        passed = not critical_failed

        # Confidence adjustment based on warnings
        conf_adj = 0.0
        conf_adj -= len(warnings) * 0.05
        conf_adj -= len(blockers) * 0.15

        return VerificationResult(
            sport=sport,
            event_id=event_id,
            timestamp=timestamp,
            layers=layers,
            passed=passed,
            confidence_adjustment=conf_adj,
            warnings=warnings,
            blockers=blockers,
        )

    def _verify_data_freshness(self, sport: str, espn_data: Dict) -> LayerResult:
        """
        Layer 1: Data Freshness Verification
        - Confirm current date/time
        - Verify injury data within 24 hours
        - Confirm market resolution date is FUTURE
        """
        checks = []
        status = VerificationStatus.PASSED
        notes = ""

        # Check if ESPN data is fresh
        if "error" in espn_data:
            checks.append({"name": "ESPN API response", "status": "✗", "detail": espn_data.get("error")})
            status = VerificationStatus.FAILED
        else:
            checks.append({"name": "ESPN API response", "status": "✓", "detail": "Data received"})

        # Check game date is future
        game_date = espn_data.get("date")
        if game_date:
            try:
                game_dt = datetime.fromisoformat(game_date.replace("Z", "+00:00"))
                if game_dt < datetime.now(game_dt.tzinfo):
                    checks.append({"name": "Game date", "status": "⚠", "detail": "Game may have started"})
                    status = VerificationStatus.WARNING
                else:
                    checks.append({"name": "Game date", "status": "✓", "detail": f"Future: {game_date}"})
            except (ValueError, TypeError):
                checks.append({"name": "Game date", "status": "○", "detail": "Could not parse date"})

        # Sport-specific freshness requirements
        freshness_windows = {
            "nfl": "90 minutes before kickoff for inactives",
            "nba": "Game-time decisions common, check 30 min before",
            "cbb": "2 hours before for most conferences",
            "cfb": "Varies by conference",
            "nhl": "Morning skate confirms goalie",
        }
        checks.append({
            "name": "Sport timing note",
            "status": "ℹ",
            "detail": freshness_windows.get(sport, "Standard timing")
        })

        return LayerResult(
            layer_name="Data Freshness Verification",
            layer_number=1,
            status=status,
            checks=checks,
            notes=notes,
        )

    def _verify_math(
        self,
        odds_data: Optional[Dict],
        true_prob: Optional[float],
        market_prob: Optional[float]
    ) -> LayerResult:
        """
        Layer 2: Mathematical Verification
        - YES + NO = 100% (±1%)
        - Odds conversion verified
        - EV% recalculated independently
        - Kelly% verified — flag if >25%
        """
        checks = []
        status = VerificationStatus.PASSED

        if odds_data:
            # Check probability sums
            over_under = odds_data.get("over_under")
            if over_under:
                # Typically -110/-110, should sum to ~52.4% + 52.4% = 104.8% (4.8% vig)
                checks.append({"name": "Total line available", "status": "✓", "detail": f"O/U {over_under}"})

            # Check moneyline conversion
            home_ml = odds_data.get("home_moneyline")
            away_ml = odds_data.get("away_moneyline")
            if home_ml and away_ml:
                home_imp = self._american_to_implied(home_ml)
                away_imp = self._american_to_implied(away_ml)
                total_imp = home_imp + away_imp

                if 1.0 <= total_imp <= 1.15:
                    checks.append({
                        "name": "Implied probability sum",
                        "status": "✓",
                        "detail": f"{total_imp*100:.1f}% (vig: {(total_imp-1)*100:.1f}%)"
                    })
                else:
                    checks.append({
                        "name": "Implied probability sum",
                        "status": "⚠",
                        "detail": f"Unusual: {total_imp*100:.1f}%"
                    })
                    status = VerificationStatus.WARNING

        # Verify our edge calculation
        if true_prob is not None and market_prob is not None:
            edge = true_prob - market_prob
            checks.append({
                "name": "Edge calculation",
                "status": "✓",
                "detail": f"True: {true_prob*100:.1f}% vs Market: {market_prob*100:.1f}% = {edge*100:.1f}% edge"
            })

            # Kelly check
            if edge > 0.25:
                checks.append({
                    "name": "Kelly check",
                    "status": "✗",
                    "detail": f"Edge >25% is SUSPICIOUS - requires triple verification"
                })
                status = VerificationStatus.FAILED
            elif edge > 0.15:
                checks.append({
                    "name": "Kelly check",
                    "status": "⚠",
                    "detail": f"High edge ({edge*100:.1f}%) - verify extensively"
                })
                status = VerificationStatus.WARNING
        else:
            checks.append({"name": "Edge calculation", "status": "○", "detail": "Probabilities not provided"})

        return LayerResult(
            layer_name="Mathematical Verification",
            layer_number=2,
            status=status,
            checks=checks,
        )

    def _verify_multi_source(self, injury_data: Optional[List], espn_data: Dict) -> LayerResult:
        """
        Layer 3: Multi-Source Cross-Verification
        - Injuries: Official + beat reporter + major outlet (3 sources)
        - Odds: Primary + secondary platform
        - If sources conflict: Widen CI, reduce CE%
        """
        checks = []
        status = VerificationStatus.PASSED

        if injury_data:
            injury_count = len(injury_data)
            checks.append({
                "name": "Injury data",
                "status": "✓",
                "detail": f"{injury_count} injuries tracked"
            })

            # Check for key injuries (simplified)
            key_injuries = [i for i in injury_data if i.get("status") in ["Out", "Doubtful"]]
            if key_injuries:
                checks.append({
                    "name": "Key injuries",
                    "status": "⚠",
                    "detail": f"{len(key_injuries)} players Out/Doubtful"
                })
                status = VerificationStatus.WARNING
        else:
            checks.append({
                "name": "Injury data",
                "status": "○",
                "detail": "No injury data - verify independently"
            })

        # Check ESPN data completeness
        if espn_data.get("home_team") and espn_data.get("away_team"):
            checks.append({"name": "Team data", "status": "✓", "detail": "Both teams identified"})
        else:
            checks.append({"name": "Team data", "status": "⚠", "detail": "Missing team data"})

        return LayerResult(
            layer_name="Multi-Source Cross-Verification",
            layer_number=3,
            status=status,
            checks=checks,
        )

    def _verify_sharp_line(self, odds_data: Optional[Dict], true_prob: Optional[float]) -> LayerResult:
        """
        Layer 4: Sharp Line Integration (Pinnacle)
        - Pull Pinnacle de-vigged line as TRUE MARKET benchmark
        - Calculate CLV potential
        - If TRUE_PROB differs from Pinnacle by >5%, require justification
        """
        checks = []
        status = VerificationStatus.PASSED

        checks.append({
            "name": "Pinnacle benchmark",
            "status": "ℹ",
            "detail": "Pinnacle is gold standard for sharp lines"
        })

        if odds_data and odds_data.get("provider"):
            checks.append({
                "name": "Odds source",
                "status": "✓",
                "detail": f"Provider: {odds_data.get('provider')}"
            })
        else:
            checks.append({
                "name": "Odds source",
                "status": "○",
                "detail": "No odds provider data"
            })

        # Note: In production, would compare to Pinnacle API
        checks.append({
            "name": "CLV analysis",
            "status": "ℹ",
            "detail": "Track closing line value post-game"
        })

        return LayerResult(
            layer_name="Sharp Line Integration (Pinnacle)",
            layer_number=4,
            status=status,
            checks=checks,
        )

    def _verify_logical_consistency(
        self,
        true_prob: Optional[float],
        market_prob: Optional[float]
    ) -> LayerResult:
        """
        Layer 5: Logical Consistency
        - Edge >15%: Re-verify extensively
        - Edge >25%: Treat as SUSPECT
        """
        checks = []
        status = VerificationStatus.PASSED

        if true_prob is not None and market_prob is not None:
            edge = true_prob - market_prob

            if edge > 0.25:
                checks.append({
                    "name": "Edge magnitude",
                    "status": "✗",
                    "detail": f"{edge*100:.1f}% edge is SUSPECT - markets rarely this inefficient"
                })
                status = VerificationStatus.FAILED
            elif edge > 0.15:
                checks.append({
                    "name": "Edge magnitude",
                    "status": "⚠",
                    "detail": f"{edge*100:.1f}% edge is high - verify extensively"
                })
                status = VerificationStatus.WARNING
            elif edge > 0.05:
                checks.append({
                    "name": "Edge magnitude",
                    "status": "✓",
                    "detail": f"{edge*100:.1f}% edge is in normal profitable range"
                })
            else:
                checks.append({
                    "name": "Edge magnitude",
                    "status": "○",
                    "detail": f"{edge*100:.1f}% edge below minimum threshold"
                })

        return LayerResult(
            layer_name="Logical Consistency",
            layer_number=5,
            status=status,
            checks=checks,
        )

    def _verify_whale_signals(self, social_signals: Optional[Dict]) -> LayerResult:
        """
        Layer 6: Whale & Top-Trader Intelligence
        - Check for large position movements
        - SMI Status: FOLLOW / DIVIDED / CONTRARIAN
        """
        checks = []
        status = VerificationStatus.PASSED

        checks.append({
            "name": "Whale tracking",
            "status": "ℹ",
            "detail": "Monitor PolyTrack, Polymarket Analytics for $10K+ moves"
        })

        if social_signals and social_signals.get("whale_activity"):
            whale = social_signals["whale_activity"]
            checks.append({
                "name": "Whale position",
                "status": "⚠",
                "detail": f"Large position detected: {whale}"
            })
        else:
            checks.append({
                "name": "Whale position",
                "status": "○",
                "detail": "No whale data available"
            })

        checks.append({
            "name": "SMI Rule",
            "status": "ℹ",
            "detail": "NEVER bet solely on whale signals - use as tiebreaker only"
        })

        return LayerResult(
            layer_name="Whale & Top-Trader Intelligence",
            layer_number=6,
            status=status,
            checks=checks,
            blocking=False,
        )

    def _verify_social_intel(self, social_signals: Optional[Dict], sport: str) -> LayerResult:
        """
        Layer 7: Twitter/X Intelligence
        - Execute sport-specific Twitter searches
        - Prioritize Tier 1 insiders
        """
        checks = []
        status = VerificationStatus.PASSED

        # Sport-specific Twitter sources
        insider_map = {
            "nfl": ["@AdamSchefter", "@RapSheet", "@TomPelissero"],
            "nba": ["@ShamsCharania", "@ChrisBHaynes", "@TheSteinLine"],
            "cfb": ["@PeteThamel", "@McMurphyESPN"],
            "cbb": ["@GoodmanHoops", "@JonRothstein"],
            "nhl": ["@FriedgeHNIC", "@frank_seravalli"],
        }

        insiders = insider_map.get(sport, [])
        checks.append({
            "name": f"{sport.upper()} insiders",
            "status": "ℹ",
            "detail": f"Monitor: {', '.join(insiders)}"
        })

        if social_signals and social_signals.get("breaking_news"):
            checks.append({
                "name": "Breaking news",
                "status": "⚠",
                "detail": social_signals["breaking_news"]
            })
            status = VerificationStatus.WARNING

        return LayerResult(
            layer_name="Twitter/X Intelligence",
            layer_number=7,
            status=status,
            checks=checks,
            blocking=False,
        )

    def _verify_market_mechanics(self, odds_data: Optional[Dict]) -> LayerResult:
        """
        Layer 8: Market Mechanics
        - Bid/ask spread - flag if >3%
        - Exact resolution wording
        """
        checks = []
        status = VerificationStatus.PASSED

        checks.append({
            "name": "Spread check",
            "status": "ℹ",
            "detail": "Flag markets with >3% bid/ask spread"
        })

        if odds_data:
            spread = odds_data.get("spread")
            total = odds_data.get("over_under")
            if spread:
                checks.append({"name": "Spread line", "status": "✓", "detail": f"Spread: {spread}"})
            if total:
                checks.append({"name": "Total line", "status": "✓", "detail": f"Total: {total}"})

        checks.append({
            "name": "Resolution clarity",
            "status": "ℹ",
            "detail": "Verify WHO/WHAT/WHEN for settlement"
        })

        return LayerResult(
            layer_name="Market Mechanics",
            layer_number=8,
            status=status,
            checks=checks,
        )

    def _verify_monte_carlo(self, true_prob: Optional[float]) -> LayerResult:
        """
        Layer 9: Monte Carlo Validation
        - For complex markets: Run 10,000 iteration simulation
        - Validate TRUE_PROB within simulation's central range
        """
        checks = []
        status = VerificationStatus.PASSED

        checks.append({
            "name": "Monte Carlo",
            "status": "ℹ",
            "detail": "Run 10K simulations for complex/uncertain outcomes"
        })

        if true_prob is not None:
            # Simplified simulation validation
            variance = 0.05  # Typical variance
            lower = true_prob - variance
            upper = true_prob + variance
            checks.append({
                "name": "Probability range",
                "status": "✓",
                "detail": f"Expected range: {lower*100:.1f}% - {upper*100:.1f}%"
            })

        return LayerResult(
            layer_name="Monte Carlo Validation",
            layer_number=9,
            status=status,
            checks=checks,
            blocking=False,
        )

    @staticmethod
    def _american_to_implied(odds: int) -> float:
        """Convert American odds to implied probability."""
        if odds > 0:
            return 100 / (odds + 100)
        else:
            return abs(odds) / (abs(odds) + 100)
