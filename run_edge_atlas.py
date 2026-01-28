#!/usr/bin/env python3
"""
EDGE ATLAS V5.0 APEX - MASTER EDITION
Runner Script

Usage:
    python run_edge_atlas.py [--scan] [--live] [--sport SPORT]

Examples:
    python run_edge_atlas.py                    # Interactive mode
    python run_edge_atlas.py --scan             # Scan all markets
    python run_edge_atlas.py --live             # Get live suggestions
    python run_edge_atlas.py --sport nba        # Scan NBA only
    python run_edge_atlas.py --scoreboard nfl   # NFL scoreboard
"""

import argparse
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from edge_atlas import EdgeAtlasAgent


def main():
    parser = argparse.ArgumentParser(
        description="EDGE ATLAS V5.0 APEX - Sports Betting Edge Detection"
    )
    parser.add_argument(
        "--scan", action="store_true",
        help="Scan all markets for edge opportunities"
    )
    parser.add_argument(
        "--live", action="store_true",
        help="Get live in-game suggestions"
    )
    parser.add_argument(
        "--sport", type=str,
        help="Scan specific sport (nfl, nba, cfb, cbb, nhl)"
    )
    parser.add_argument(
        "--scoreboard", type=str,
        help="Show scoreboard for sport"
    )
    parser.add_argument(
        "--learn", type=str,
        help="Learn about a topic (dvoa, epa, kenpom, corsi, clv, kelly)"
    )
    parser.add_argument(
        "--odds-api-key", type=str,
        help="API key for The Odds API (optional)"
    )
    parser.add_argument(
        "--bankroll", type=float, default=10000,
        help="Starting bankroll (default: 10000)"
    )

    args = parser.parse_args()

    # Initialize agent
    agent = EdgeAtlasAgent(
        odds_api_key=args.odds_api_key,
        bankroll=args.bankroll
    )

    # Handle command-line modes
    if args.scan:
        print(agent.activate())
        print("\n🔍 Scanning all markets for edges...")
        print(agent.scan_all_markets())
        return

    if args.live:
        print(agent.activate())
        print("\n🔴 Getting live suggestions...")
        sport = args.sport if args.sport else None
        print(agent.get_live_suggestions(sport))
        return

    if args.sport:
        print(agent.activate())
        print(f"\n🔍 Scanning {args.sport.upper()}...")
        print(agent.scan_sport(args.sport))
        return

    if args.scoreboard:
        print(agent.activate())
        print(agent.get_scoreboard(args.scoreboard))
        return

    if args.learn:
        print(agent.activate())
        print(agent.learn(args.learn))
        return

    # Default: Interactive mode
    agent.run_interactive()


if __name__ == "__main__":
    main()
