"""
EDGE ATLAS V5.0 - Web Application
Real-time sports betting edge detection via web interface
"""

import os
from datetime import datetime
from dash import Dash, Input, Output, State, dcc, html, callback

# Import Edge Atlas components
from edge_atlas.api.espn import ESPNClient
from edge_atlas.engine.real_data_analyzer import RealDataAnalyzer
from edge_atlas.engine.smart_evaluator import SmartEvaluator, format_smart_pick
from edge_atlas.config import LeagueData

# Initialize components
espn = ESPNClient()
real_analyzer = RealDataAnalyzer()
smart_evaluator = SmartEvaluator()

# Dash app setup
app = Dash(
    __name__,
    suppress_callback_exceptions=True,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
        {"name": "theme-color", "content": "#1a1a2e"},
    ],
)
app.title = "EDGE ATLAS V5.0"
server = app.server

# Custom CSS
CUSTOM_CSS = """
body {
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    color: #e8e8e8;
    margin: 0;
    min-height: 100vh;
}
.container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 20px;
}
.header {
    text-align: center;
    padding: 30px 0;
    border-bottom: 2px solid #e94560;
    margin-bottom: 30px;
}
.header h1 {
    font-size: 2.5em;
    margin: 0;
    background: linear-gradient(90deg, #e94560, #ff6b6b);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.header p {
    color: #888;
    margin-top: 10px;
}
.controls {
    display: flex;
    gap: 15px;
    flex-wrap: wrap;
    margin-bottom: 30px;
    justify-content: center;
}
.btn {
    padding: 12px 24px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 600;
    font-size: 14px;
    transition: all 0.3s;
}
.btn-primary {
    background: linear-gradient(135deg, #e94560, #ff6b6b);
    color: white;
}
.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 20px rgba(233, 69, 96, 0.4);
}
.btn-secondary {
    background: #2d2d44;
    color: #e8e8e8;
    border: 1px solid #444;
}
.btn-secondary:hover {
    background: #3d3d54;
}
.card {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}
.card-header {
    font-size: 1.2em;
    font-weight: 600;
    margin-bottom: 15px;
    color: #e94560;
    display: flex;
    align-items: center;
    gap: 10px;
}
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
    margin-bottom: 30px;
}
.stat-card {
    background: rgba(233, 69, 96, 0.1);
    border-radius: 10px;
    padding: 20px;
    text-align: center;
    border: 1px solid rgba(233, 69, 96, 0.3);
}
.stat-value {
    font-size: 2em;
    font-weight: 700;
    color: #e94560;
}
.stat-label {
    color: #888;
    font-size: 0.9em;
    margin-top: 5px;
}
.results-container {
    background: rgba(0, 0, 0, 0.3);
    border-radius: 12px;
    padding: 20px;
    font-family: 'Monaco', 'Consolas', monospace;
    font-size: 13px;
    line-height: 1.6;
    white-space: pre-wrap;
    max-height: 600px;
    overflow-y: auto;
    border: 1px solid #333;
}
.edge-card {
    background: rgba(46, 204, 113, 0.1);
    border: 1px solid rgba(46, 204, 113, 0.3);
    border-radius: 10px;
    padding: 15px;
    margin-bottom: 15px;
}
.edge-card.high-confidence {
    background: rgba(233, 69, 96, 0.15);
    border-color: rgba(233, 69, 96, 0.4);
}
.edge-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}
.edge-game {
    font-weight: 600;
    font-size: 1.1em;
}
.edge-badge {
    background: #2ecc71;
    color: white;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.8em;
    font-weight: 600;
}
.edge-badge.grade-a { background: #e94560; }
.edge-badge.grade-b { background: #f39c12; }
.edge-badge.grade-c { background: #3498db; }
.loading {
    text-align: center;
    padding: 40px;
    color: #888;
}
.sport-tabs {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
    flex-wrap: wrap;
}
.sport-tab {
    padding: 10px 20px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s;
}
.sport-tab:hover, .sport-tab.active {
    background: rgba(233, 69, 96, 0.2);
    border-color: #e94560;
}
.data-status {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 10px;
}
.status-item {
    background: rgba(255, 255, 255, 0.05);
    padding: 15px;
    border-radius: 8px;
    text-align: center;
}
.status-fresh { border-left: 3px solid #2ecc71; }
.status-current { border-left: 3px solid #f39c12; }
.status-stale { border-left: 3px solid #e74c3c; }
.footer {
    text-align: center;
    padding: 30px;
    color: #666;
    font-size: 0.9em;
    border-top: 1px solid #333;
    margin-top: 40px;
}
"""

# Layout
app.layout = html.Div(
    className="container",
    style={"fontFamily": "'Segoe UI', system-ui, sans-serif", "background": "linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)", "color": "#e8e8e8", "minHeight": "100vh", "padding": "20px"},
    children=[
        # Header
        html.Div(
            className="header",
            children=[
                html.H1("EDGE ATLAS V5.0"),
                html.P("APEX MASTER EDITION - Real-Time Sports Betting Edge Detection"),
                html.P(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Data Source: ESPN Live API",
                       style={"fontSize": "0.8em", "color": "#666"}),
            ]
        ),

        # Control buttons
        html.Div(
            className="controls",
            children=[
                html.Button("Scan All Markets", id="btn-scan-all", className="btn btn-primary"),
                html.Button("Live Games", id="btn-live", className="btn btn-secondary"),
                html.Button("Data Status", id="btn-data-status", className="btn btn-secondary"),
                dcc.Dropdown(
                    id="sport-selector",
                    options=[
                        {"label": "NFL Football", "value": "nfl"},
                        {"label": "NBA Basketball", "value": "nba"},
                        {"label": "College Football", "value": "cfb"},
                        {"label": "College Basketball", "value": "cbb"},
                        {"label": "NHL Hockey", "value": "nhl"},
                    ],
                    placeholder="Select Sport for Deep Dive",
                    style={"width": "250px", "color": "#333"},
                ),
                html.Button("Scan Sport", id="btn-scan-sport", className="btn btn-secondary"),
            ]
        ),

        # Results area - FIRST so users see it immediately
        dcc.Loading(
            id="loading",
            type="circle",
            color="#e94560",
            children=[
                html.Div(
                    className="card",
                    style={"marginBottom": "20px"},
                    children=[
                        html.Div(className="card-header", children=["Results"]),
                        html.Div(
                            id="results-container",
                            className="results-container",
                            style={"minHeight": "200px", "maxHeight": "400px"},
                            children="Tap 'Scan All Markets' to find edges..."
                        ),
                    ]
                ),
            ]
        ),

        # Data status section
        html.Div(
            className="card",
            id="data-status-card",
            style={"display": "none"},
            children=[
                html.Div(className="card-header", children=["Data Freshness Status"]),
                html.Div(id="data-status-content"),
            ]
        ),

        # Stats overview - moved below results
        html.Div(
            className="stats-grid",
            id="stats-grid",
            style={"marginTop": "20px"},
            children=[
                html.Div(className="stat-card", children=[
                    html.Div("--", className="stat-value", id="stat-edges"),
                    html.Div("Edges Found", className="stat-label"),
                ]),
                html.Div(className="stat-card", children=[
                    html.Div("--", className="stat-value", id="stat-live"),
                    html.Div("Live Games", className="stat-label"),
                ]),
                html.Div(className="stat-card", children=[
                    html.Div("--", className="stat-value", id="stat-sports"),
                    html.Div("Sports Active", className="stat-label"),
                ]),
                html.Div(className="stat-card", children=[
                    html.Div("--", className="stat-value", id="stat-confidence"),
                    html.Div("Avg Confidence", className="stat-label"),
                ]),
            ]
        ),

        # Footer
        html.Div(
            className="footer",
            children=[
                html.P("EDGE ATLAS V5.0 APEX MASTER EDITION"),
                html.P("Education-First | Real-Time Verified | No Simulated Data"),
                html.P("NFL | NBA | College Football | College Basketball | NHL"),
            ]
        ),

        # Store for results
        dcc.Store(id="scan-results-store"),
        dcc.Interval(id="auto-refresh", interval=60000, n_intervals=0, disabled=True),
    ]
)


def scan_all_markets():
    """Scan all sports for edge opportunities."""
    output_lines = []
    output_lines.append("=" * 70)
    output_lines.append("EDGE ATLAS V5.0 - SMART MARKET SCAN")
    output_lines.append("Real Data | Human-Like Evaluation | No Simulations")
    output_lines.append("=" * 70)
    output_lines.append(f"Scan Time: {datetime.now().isoformat()}")
    output_lines.append("Data Source: ESPN Live API")
    output_lines.append("=" * 70)

    all_picks = []
    sports_with_games = 0

    supported_sports = {
        "nfl": "NFL Football",
        "nba": "NBA Basketball",
        "cfb": "College Football",
        "cbb": "College Basketball",
        "nhl": "NHL Hockey",
    }

    for sport, sport_name in supported_sports.items():
        output_lines.append(f"\nScanning {sport_name}...")

        try:
            games = real_analyzer.get_real_scoreboard(sport)
            upcoming = [g for g in games if g.get("status", {}).get("state") == "pre"]

            if not upcoming:
                output_lines.append(f"  No upcoming {sport.upper()} games found")
                continue

            sports_with_games += 1
            output_lines.append(f"  Found {len(upcoming)} upcoming games")

            for game in upcoming[:5]:
                pick = smart_evaluator.evaluate_game(sport, game)
                if pick.confidence_level != "PASS":
                    all_picks.append(pick)

        except Exception as e:
            output_lines.append(f"  Error scanning {sport}: {str(e)}")

    output_lines.append("\n" + "=" * 70)

    if all_picks:
        all_picks.sort(key=lambda x: x.edge_pct, reverse=True)
        output_lines.append(f"\nFOUND {len(all_picks)} EDGE OPPORTUNITIES:")
        output_lines.append("=" * 70)

        for pick in all_picks[:10]:
            output_lines.append(format_smart_pick(pick))
    else:
        output_lines.append("\nNO EDGES FOUND MEETING CRITERIA")
        output_lines.append("\nThis is NORMAL - sharp markets don't offer easy edges.")
        output_lines.append("Most games are fairly priced. Be patient.")
        output_lines.append("\nRemember: One excellent bet beats ten mediocre ones.")

    return "\n".join(output_lines), len(all_picks), sports_with_games


def get_live_games():
    """Get all live games across sports."""
    output_lines = []
    output_lines.append("=" * 70)
    output_lines.append("EDGE ATLAS V5.0 - LIVE GAME ANALYSIS")
    output_lines.append("Real-Time Data | In-Progress Games Only")
    output_lines.append("=" * 70)
    output_lines.append(f"Scan Time: {datetime.now().isoformat()}")
    output_lines.append("=" * 70)

    total_live = 0

    for sport in ["nfl", "nba", "cfb", "cbb", "nhl"]:
        try:
            live_games = real_analyzer.get_live_games_real(sport)

            if live_games:
                total_live += len(live_games)
                output_lines.append(f"\n{sport.upper()}: {len(live_games)} live game(s)")

                for game in live_games:
                    analysis = real_analyzer.analyze_live_game_real(sport, game)
                    output_lines.append(f"\n  LIVE: {analysis['game_name']}")
                    output_lines.append(f"  Score: {analysis['teams']['away']} {analysis['score']['away']} - "
                                       f"{analysis['score']['home']} {analysis['teams']['home']}")
                    output_lines.append(f"  {analysis['status'].get('detail', '')}")

                    if analysis['live_odds'].get('spread'):
                        output_lines.append(f"  Live Spread: {analysis['live_odds']['spread']}")
                    if analysis['live_odds'].get('total'):
                        output_lines.append(f"  Live Total: {analysis['live_odds']['total']}")

        except Exception as e:
            output_lines.append(f"\n{sport.upper()}: Error - {str(e)}")

    if total_live == 0:
        output_lines.append("\nNo live games currently in progress.")
        output_lines.append("Check back when games are being played.")

    output_lines.append("\n" + "=" * 70)
    return "\n".join(output_lines), total_live


def get_data_status():
    """Get data freshness status."""
    status = LeagueData.get_freshness_status()

    content = []

    # Overall status
    status_class = "status-fresh" if status["status"] == "FRESH" else \
                   "status-current" if status["status"] == "CURRENT" else "status-stale"

    content.append(html.Div([
        html.H3(f"Status: {status['status']}", style={"color": "#2ecc71" if status["status"] == "FRESH" else "#f39c12" if status["status"] == "CURRENT" else "#e74c3c"}),
        html.P(f"Last Updated: {status['last_updated']}"),
        html.P(f"Season: {status['season']}"),
        html.P(f"Data Age: {status['age_days']} days"),
    ]))

    # By sport
    content.append(html.H4("By Sport:", style={"marginTop": "20px"}))

    sport_items = []
    for sport, updated in status['sports'].items():
        sport_data = getattr(LeagueData, sport.upper(), {})
        season = sport_data.get("season", "N/A")
        sport_items.append(
            html.Div(
                className=f"status-item {status_class}",
                children=[
                    html.Strong(sport.upper()),
                    html.Div(f"Season: {season}"),
                    html.Div(f"Updated: {updated}", style={"fontSize": "0.8em", "color": "#888"}),
                ]
            )
        )

    content.append(html.Div(className="data-status", children=sport_items))

    return content


def scan_sport(sport):
    """Scan a specific sport."""
    output_lines = []
    sport_names = {
        "nfl": "NFL Football",
        "nba": "NBA Basketball",
        "cfb": "College Football",
        "cbb": "College Basketball",
        "nhl": "NHL Hockey",
    }

    output_lines.append("=" * 70)
    output_lines.append(f"EDGE ATLAS V5.0 - {sport_names.get(sport, sport.upper())} DEEP DIVE")
    output_lines.append("=" * 70)
    output_lines.append(f"Scan Time: {datetime.now().isoformat()}")
    output_lines.append("=" * 70)

    try:
        games = real_analyzer.get_real_scoreboard(sport)

        # Upcoming games
        upcoming = [g for g in games if g.get("status", {}).get("state") == "pre"]
        live = [g for g in games if g.get("status", {}).get("state") == "in"]

        output_lines.append(f"\nFound {len(upcoming)} upcoming games, {len(live)} live")

        all_picks = []
        for game in upcoming[:10]:
            pick = smart_evaluator.evaluate_game(sport, game)
            if pick.confidence_level != "PASS":
                all_picks.append(pick)

        if all_picks:
            all_picks.sort(key=lambda x: x.edge_pct, reverse=True)
            output_lines.append(f"\n{len(all_picks)} EDGE OPPORTUNITIES:")
            output_lines.append("-" * 70)

            for pick in all_picks:
                output_lines.append(format_smart_pick(pick))
        else:
            output_lines.append("\nNo edges found for this sport currently.")
            output_lines.append("Markets appear efficiently priced.")

    except Exception as e:
        output_lines.append(f"\nError: {str(e)}")

    output_lines.append("\n" + "=" * 70)
    return "\n".join(output_lines)


# Callbacks
@callback(
    Output("results-container", "children"),
    Output("stat-edges", "children"),
    Output("stat-sports", "children"),
    Output("data-status-card", "style"),
    Input("btn-scan-all", "n_clicks"),
    prevent_initial_call=True,
)
def handle_scan_all(n_clicks):
    results, edges, sports = scan_all_markets()
    return results, str(edges), str(sports), {"display": "none"}


@callback(
    Output("results-container", "children", allow_duplicate=True),
    Output("stat-live", "children"),
    Output("data-status-card", "style", allow_duplicate=True),
    Input("btn-live", "n_clicks"),
    prevent_initial_call=True,
)
def handle_live(n_clicks):
    results, live_count = get_live_games()
    return results, str(live_count), {"display": "none"}


@callback(
    Output("data-status-card", "style", allow_duplicate=True),
    Output("data-status-content", "children"),
    Output("results-container", "children", allow_duplicate=True),
    Input("btn-data-status", "n_clicks"),
    prevent_initial_call=True,
)
def handle_data_status(n_clicks):
    content = get_data_status()
    return {"display": "block"}, content, "Data status displayed above."


@callback(
    Output("results-container", "children", allow_duplicate=True),
    Output("data-status-card", "style", allow_duplicate=True),
    Input("btn-scan-sport", "n_clicks"),
    State("sport-selector", "value"),
    prevent_initial_call=True,
)
def handle_scan_sport(n_clicks, sport):
    if not sport:
        return "Please select a sport from the dropdown first.", {"display": "none"}
    results = scan_sport(sport)
    return results, {"display": "none"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
