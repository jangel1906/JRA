"""
Confidence Engine (CE%) - V5.0 Enhanced
Calculates confidence percentage and bet sizing recommendations
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum


class BetGrade(Enum):
    """Bet grade based on CE%."""
    A_PLUS = "A+"
    A = "A"
    B_PLUS = "B+"
    B = "B"
    C = "C"
    PASS = "PASS"


@dataclass
class BetRecommendation:
    """Complete bet recommendation with sizing and rationale."""
    selection: str
    market_type: str
    odds: int
    true_probability: float
    market_probability: float
    edge_pct: float
    ce_pct: float
    grade: BetGrade
    position_size_pct: float
    kelly_pct: float
    recommendation: str  # BET or PASS
    rationale: str
    education: str
    risk_factors: List[str]
    timestamp: str


class ConfidenceEngine:
    """
    CE% Formula (V5.0 Enhanced):

    CE% = 100 × clamp(
      0.10 (Base)
      + 0.20×SAS (Source Agreement Score)
      + 0.15×TTSS (Top-Trader Signal Score)
      + 0.15×FS (Freshness Score)
      + 0.12×LQS (Liquidity Score)
      + 0.12×RCS (Resolution Clarity Score)
      + 0.08×PCLS (Pinnacle CLV Score)
      + 0.08×NSA (News/Social Alignment)
      - 0.20×VP (Volatility Penalty)
    , 0, 1)
    """

    # Weights for CE% calculation
    WEIGHTS = {
        "base": 0.10,
        "source_agreement": 0.20,
        "top_trader": 0.15,
        "freshness": 0.15,
        "liquidity": 0.12,
        "resolution_clarity": 0.12,
        "pinnacle_clv": 0.08,
        "news_social": 0.08,
        "volatility_penalty": 0.20,
    }

    # Grade thresholds
    GRADE_THRESHOLDS = {
        90: BetGrade.A_PLUS,
        80: BetGrade.A,
        70: BetGrade.B_PLUS,
        65: BetGrade.B,
        50: BetGrade.C,
        0: BetGrade.PASS,
    }

    # Position sizing by grade
    POSITION_SIZES = {
        BetGrade.A_PLUS: (0.03, 0.05),  # 3-5% bankroll
        BetGrade.A: (0.02, 0.03),       # 2-3%
        BetGrade.B_PLUS: (0.01, 0.02),  # 1-2%
        BetGrade.B: (0.005, 0.01),      # 0.5-1%
        BetGrade.C: (0, 0),             # PASS
        BetGrade.PASS: (0, 0),
    }

    def __init__(self):
        self.min_edge_threshold = 0.05  # 5% minimum edge

    def calculate_ce(
        self,
        source_agreement: float = 0.5,
        top_trader_signal: float = 0.5,
        freshness: float = 1.0,
        liquidity: float = 0.8,
        resolution_clarity: float = 1.0,
        pinnacle_clv: float = 0.5,
        news_social: float = 0.5,
        volatility: float = 0.0,
    ) -> float:
        """
        Calculate Confidence Engine percentage.

        All inputs should be 0-1 scale:
        - 0 = worst
        - 0.5 = neutral
        - 1 = best

        Volatility is a penalty (higher = worse)
        """
        ce = (
            self.WEIGHTS["base"]
            + self.WEIGHTS["source_agreement"] * source_agreement
            + self.WEIGHTS["top_trader"] * top_trader_signal
            + self.WEIGHTS["freshness"] * freshness
            + self.WEIGHTS["liquidity"] * liquidity
            + self.WEIGHTS["resolution_clarity"] * resolution_clarity
            + self.WEIGHTS["pinnacle_clv"] * pinnacle_clv
            + self.WEIGHTS["news_social"] * news_social
            - self.WEIGHTS["volatility_penalty"] * volatility
        )

        # Clamp to 0-1
        ce = max(0, min(1, ce))

        return round(ce * 100, 1)

    def get_grade(self, ce_pct: float) -> BetGrade:
        """Get bet grade from CE%."""
        for threshold, grade in sorted(self.GRADE_THRESHOLDS.items(), reverse=True):
            if ce_pct >= threshold:
                return grade
        return BetGrade.PASS

    def get_position_size(self, grade: BetGrade, kelly_pct: float) -> float:
        """
        Get recommended position size.

        Uses fraction of Kelly (typically 1/4 to 1/2 Kelly for safety).
        """
        min_size, max_size = self.POSITION_SIZES.get(grade, (0, 0))

        if grade in [BetGrade.C, BetGrade.PASS]:
            return 0.0

        # Use half-Kelly, capped at grade maximum
        half_kelly = kelly_pct / 2
        recommended = max(min_size, min(half_kelly, max_size))

        return round(recommended, 3)

    def calculate_kelly(self, true_prob: float, odds: int) -> float:
        """
        Calculate Kelly Criterion bet size.

        Kelly% = (bp - q) / b
        where:
        - b = decimal odds - 1
        - p = probability of winning
        - q = probability of losing (1-p)
        """
        if odds > 0:
            decimal_odds = 1 + (odds / 100)
        else:
            decimal_odds = 1 + (100 / abs(odds))

        b = decimal_odds - 1
        p = true_prob
        q = 1 - p

        kelly = (b * p - q) / b if b > 0 else 0
        kelly = max(0, min(kelly, 0.25))  # Cap at 25%

        return round(kelly, 4)

    def generate_recommendation(
        self,
        selection: str,
        market_type: str,
        odds: int,
        true_probability: float,
        verification_passed: bool,
        ce_inputs: Dict,
        timestamp: str,
    ) -> BetRecommendation:
        """
        Generate complete bet recommendation.

        Args:
            selection: What to bet on (team name, over/under, etc.)
            market_type: Type of market (moneyline, spread, total, etc.)
            odds: American odds
            true_probability: Our calculated true probability
            verification_passed: Whether 9-layer verification passed
            ce_inputs: Dict of CE% component scores
            timestamp: Current timestamp

        Returns:
            Complete BetRecommendation
        """
        # Calculate market implied probability
        if odds > 0:
            market_prob = 100 / (odds + 100)
        else:
            market_prob = abs(odds) / (abs(odds) + 100)

        # Calculate edge
        edge = true_probability - market_prob

        # Calculate CE%
        ce_pct = self.calculate_ce(**ce_inputs)

        # Adjust CE% if verification failed
        if not verification_passed:
            ce_pct = min(ce_pct, 50)  # Cap at C grade if verification fails

        # Get grade
        grade = self.get_grade(ce_pct)

        # Calculate Kelly
        kelly = self.calculate_kelly(true_probability, odds)

        # Get position size
        position_size = self.get_position_size(grade, kelly * 100)

        # Determine recommendation
        if edge < self.min_edge_threshold:
            recommendation = "PASS"
            rationale = f"Edge ({edge*100:.1f}%) below minimum threshold (5%)"
        elif not verification_passed:
            recommendation = "PASS"
            rationale = "Verification failed - data quality concerns"
        elif grade in [BetGrade.C, BetGrade.PASS]:
            recommendation = "PASS"
            rationale = f"CE% ({ce_pct}%) too low for bet"
        else:
            recommendation = "BET"
            rationale = f"Edge: {edge*100:.1f}% | CE: {ce_pct}% | Grade: {grade.value}"

        # Generate education
        education = self._generate_education(edge, market_prob, true_probability, odds)

        # Risk factors
        risk_factors = self._identify_risks(ce_inputs, edge, verification_passed)

        return BetRecommendation(
            selection=selection,
            market_type=market_type,
            odds=odds,
            true_probability=round(true_probability, 3),
            market_probability=round(market_prob, 3),
            edge_pct=round(edge * 100, 2),
            ce_pct=ce_pct,
            grade=grade,
            position_size_pct=position_size * 100,
            kelly_pct=round(kelly * 100, 2),
            recommendation=recommendation,
            rationale=rationale,
            education=education,
            risk_factors=risk_factors,
            timestamp=timestamp,
        )

    def _generate_education(
        self,
        edge: float,
        market_prob: float,
        true_prob: float,
        odds: int
    ) -> str:
        """Generate educational explanation of why this bet has/lacks value."""
        if edge <= 0:
            return (
                f"The market implies {market_prob*100:.1f}% probability at {odds} odds. "
                f"Our analysis suggests {true_prob*100:.1f}% - NO EDGE exists. "
                f"Betting here means paying more than fair value."
            )

        ev_per_unit = (true_prob * (100/abs(odds) if odds < 0 else odds/100)) - (1 - true_prob)

        return (
            f"WHY THIS BET HAS VALUE:\n"
            f"• Market implies {market_prob*100:.1f}% probability\n"
            f"• Our analysis: {true_prob*100:.1f}% true probability\n"
            f"• Edge: {edge*100:.1f}% (we're getting a {edge*100:.1f}% discount)\n"
            f"• Expected Value: +{ev_per_unit*100:.1f}% per unit bet\n\n"
            f"Over 100 bets with this edge, we expect to profit even if we lose some."
        )

    def _identify_risks(
        self,
        ce_inputs: Dict,
        edge: float,
        verification_passed: bool
    ) -> List[str]:
        """Identify risk factors for the bet."""
        risks = []

        if not verification_passed:
            risks.append("CRITICAL: Verification checks failed")

        if edge > 0.15:
            risks.append("High edge (>15%) - markets rarely this inefficient, verify extensively")

        if ce_inputs.get("freshness", 1.0) < 0.7:
            risks.append("Data freshness concern - may be working with stale information")

        if ce_inputs.get("liquidity", 1.0) < 0.5:
            risks.append("Low liquidity - may have trouble getting desired size")

        if ce_inputs.get("volatility", 0) > 0.5:
            risks.append("High volatility market - outcome highly uncertain")

        if ce_inputs.get("source_agreement", 1.0) < 0.5:
            risks.append("Source conflict - different sources disagree")

        return risks


class PositionManager:
    """
    Manages position sizing and bankroll protection.

    Iron Laws:
    - Maximum 5% single position (10% only for pure arb)
    - Stop trading after 2% daily loss
    - Reserve 50% bankroll for new opportunities
    """

    def __init__(self, bankroll: float):
        self.bankroll = bankroll
        self.daily_pnl = 0.0
        self.positions = []
        self.max_single_position = 0.05  # 5%
        self.daily_loss_limit = 0.02  # 2%
        self.reserve_ratio = 0.50  # 50%

    def can_bet(self) -> bool:
        """Check if more betting is allowed today."""
        if self.daily_pnl < -self.daily_loss_limit * self.bankroll:
            return False
        return True

    def available_bankroll(self) -> float:
        """Calculate available bankroll (after reserve)."""
        return self.bankroll * (1 - self.reserve_ratio)

    def validate_bet_size(self, amount: float) -> Dict:
        """Validate proposed bet size against rules."""
        max_allowed = self.bankroll * self.max_single_position

        if amount > max_allowed:
            return {
                "valid": False,
                "reason": f"Exceeds max single position ({self.max_single_position*100}%)",
                "suggested": max_allowed,
            }

        if not self.can_bet():
            return {
                "valid": False,
                "reason": "Daily loss limit reached - stop trading",
                "suggested": 0,
            }

        return {"valid": True, "amount": amount}
