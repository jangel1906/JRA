from __future__ import annotations

import datetime
import os
import textwrap
import uuid
from typing import Any, Dict, List

import requests

from dash import Dash, Input, Output, State, dcc, html, callback

# Starting set of goals provided by the user
COLOR_PALETTE = [
    ("#91f2c1", "#0f3a2d"),
    ("#9dc7ff", "#102b5c"),
    ("#ffdea8", "#5a3b0d"),
    ("#f7b0dc", "#4e1035"),
    ("#8ad8f2", "#0f3242"),
    ("#d7c6ff", "#2d1c5c"),
    ("#b1f0ff", "#0f324f"),
]


def seeded_color_index(seed: str) -> int:
    return sum(ord(ch) for ch in seed) % len(COLOR_PALETTE)


INITIAL_GOALS: List[Dict[str, Any]] = [
    {
        "id": str(uuid.uuid4()),
        "title": textwrap.shorten(
            "Establish and lead a structured backlog grooming process for the operational squad by March 31, 2026. "
            "Implement bi-weekly sessions (30–45 minutes) with key stakeholders to refine and prioritize backlog items, "
            "ensuring they are well-prepared for sprint planning. The objective is to enable clarity during sprint planning "
            "by having at least 80% of stories meet the Definition of Ready (DoR).",
            width=220,
            placeholder="...",
        ),
        "category": "Work",
        "horizon": "Short-Term",
        "focus": "Agile Ops",
        "status": "Fresh goal",
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Earn the Scrum Alliance microcredential ‘AI for Product Owners’ and apply AI-driven practices to product initiatives.",
        "category": "Work",
        "horizon": "Short-Term",
        "focus": "Learning",
        "status": "Fresh goal",
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Introduce and institutionalize the Sprint Planning ceremony for the operational squad with clear priorities and team capacity.",
        "category": "Work",
        "horizon": "Short-Term",
        "focus": "Agile Ops",
        "status": "Fresh goal",
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Optimize my learning for my apps and explore new technical concepts.",
        "category": "Work",
        "horizon": "Ongoing",
        "focus": "Learning",
        "status": "Fresh goal",
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Gain deeper understanding of APIs, integrations, and system architecture for products like AIRCOM and Cyberjet.",
        "category": "Work",
        "horizon": "Ongoing",
        "focus": "Architecture",
        "status": "Fresh goal",
    },
    {
        "id": str(uuid.uuid4()),
        "title": textwrap.shorten(
            "Introduce outcome-based delivery practices by embedding measurable success metrics into backlog items, including hypotheses and targets.",
            width=160,
            placeholder="...",
        ),
        "category": "Work",
        "horizon": "Ongoing",
        "focus": "Outcomes",
        "status": "Fresh goal",
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Volunteer at least twice no matter where you are.",
        "category": "Community",
        "horizon": "Short-Term",
        "focus": "Giving Back",
        "status": "Fresh goal",
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Participate in an AG and attend events or try something new.",
        "category": "Community",
        "horizon": "Ongoing",
        "focus": "Social",
        "status": "Fresh goal",
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Start my day with prayer, exercise, and be on the road no later than 6 AM (M-F).",
        "category": "Health & Routine",
        "horizon": "Habit",
        "focus": "Discipline",
        "status": "Fresh goal",
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Improve my AI capabilities to understand and accomplish anything.",
        "category": "Learning",
        "horizon": "Long-Term",
        "focus": "AI",
        "status": "Fresh goal",
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Find out what I need to become active again for the Bruhs!",
        "category": "Community",
        "horizon": "Short-Term",
        "focus": "Fraternity",
        "status": "Fresh goal",
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Read one book every 60 days.",
        "category": "Learning",
        "horizon": "Habit",
        "focus": "Reading",
        "status": "Fresh goal",
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Watch one documentary per week.",
        "category": "Learning",
        "horizon": "Habit",
        "focus": "Media",
        "status": "Fresh goal",
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Find a couple of AI conferences to attend to separate myself from the fold.",
        "category": "Learning",
        "horizon": "Short-Term",
        "focus": "AI",
        "status": "Fresh goal",
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Check on one person weekly just to have a conversation.",
        "category": "Family & Friends",
        "horizon": "Habit",
        "focus": "Relationships",
        "status": "Fresh goal",
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Take a trip to visit friends or family—no huddling in this year.",
        "category": "Travel & Experiences",
        "horizon": "Short-Term",
        "focus": "Connection",
        "status": "Fresh goal",
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Cook new meals I haven’t made before.",
        "category": "Personal Growth",
        "horizon": "Ongoing",
        "focus": "Creativity",
        "status": "Fresh goal",
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Bring flowers or something special to Shawn once a month.",
        "category": "Family & Friends",
        "horizon": "Habit",
        "focus": "Relationships",
        "status": "Fresh goal",
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Pray hard—continue daily wakeup prayer and focus on reading the Bible.",
        "category": "Faith",
        "horizon": "Habit",
        "focus": "Spirituality",
        "status": "Fresh goal",
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Lose 40 pounds prior to the Tokyo trip.",
        "category": "Health & Routine",
        "horizon": "Short-Term",
        "focus": "Fitness",
        "status": "Fresh goal",
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Remove myself from social media for four months annually.",
        "category": "Health & Routine",
        "horizon": "Habit",
        "focus": "Digital Detox",
        "status": "Fresh goal",
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Take a trip to Tokyo and build a plan behind it.",
        "category": "Travel & Experiences",
        "horizon": "Short-Term",
        "focus": "Adventure",
        "status": "Fresh goal",
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Buy a designer bag of my choice.",
        "category": "Personal",
        "horizon": "Short-Term",
        "focus": "Treat Yourself",
        "status": "Fresh goal",
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Decide on a fun 50th birthday activity.",
        "category": "Personal",
        "horizon": "Short-Term",
        "focus": "Milestone",
        "status": "Fresh goal",
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Get certified in AI capabilities.",
        "category": "Learning",
        "horizon": "Long-Term",
        "focus": "AI",
        "status": "Fresh goal",
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Find a way to push through anything regardless of what people say.",
        "category": "Personal Growth",
        "horizon": "Mindset",
        "focus": "Resilience",
        "status": "Fresh goal",
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Improve emotional intelligence and personal business skills beyond AI.",
        "category": "Personal Growth",
        "horizon": "Ongoing",
        "focus": "EQ",
        "status": "Fresh goal",
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Call one of my daughters every other day.",
        "category": "Family & Friends",
        "horizon": "Habit",
        "focus": "Family",
        "status": "Fresh goal",
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Create a will for myself and Shawn.",
        "category": "Financial & Legal",
        "horizon": "Short-Term",
        "focus": "Estate",
        "status": "Fresh goal",
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Create a bucket list to start this year.",
        "category": "Personal",
        "horizon": "Short-Term",
        "focus": "Vision",
        "status": "Fresh goal",
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Set up meetings for the Bruhs Costa Rica trip.",
        "category": "Community",
        "horizon": "Short-Term",
        "focus": "Travel Planning",
        "status": "Fresh goal",
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Visit my mom in the Dominican Republic.",
        "category": "Family & Friends",
        "horizon": "Short-Term",
        "focus": "Family",
        "status": "Fresh goal",
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Plan a family trip for brothers and sisters.",
        "category": "Family & Friends",
        "horizon": "Short-Term",
        "focus": "Family",
        "status": "Fresh goal",
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Possibly attend the Vegas Summer League.",
        "category": "Travel & Experiences",
        "horizon": "Short-Term",
        "focus": "Sports",
        "status": "Fresh goal",
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Make $50,000 in personal money.",
        "category": "Financial & Legal",
        "horizon": "Long-Term",
        "focus": "Income",
        "status": "Fresh goal",
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Optimize 401K to reach $2M.",
        "category": "Financial & Legal",
        "horizon": "Long-Term",
        "focus": "Retirement",
        "status": "Fresh goal",
    },
]

for goal in INITIAL_GOALS:
    goal["color_index"] = seeded_color_index(goal["id"])


DEFAULT_FIREBASE_URL = os.getenv("FIREBASE_URL", "")
DEFAULT_FIREBASE_TOKEN = os.getenv("FIREBASE_AUTH_TOKEN", "")


app = Dash(__name__)
app.title = "Goal Bubbles"
server = app.server


def bubble_style(goal: Dict[str, Any]) -> Dict[str, Any]:
    # Size bubbles loosely based on goal length for visual variety
    base_size = 170
    scaled = min(260, base_size + len(goal["title"]) // 4)
    colors = COLOR_PALETTE[goal.get("color_index", 0)]
    return {
        "width": f"{scaled}px",
        "height": f"{scaled}px",
        "background": f"radial-gradient(circle at 30% 30%, {colors[0]} 0%, {colors[0]} 35%, {colors[1]} 100%)",
        "boxShadow": "0 16px 32px rgba(0,0,0,0.45), inset 0 0 0 1px rgba(255,255,255,0.25)",
    }


def render_goal(goal: Dict[str, Any]) -> html.Div:
    category_class = goal["category"].lower().replace(" & ", "-").replace(" ", "-")
    horizon = goal.get("horizon", "Ongoing")
    return html.Div(
        className=f"goal-bubble bubble-{category_class}",
        style=bubble_style(goal),
        children=[
            html.Div(className="bubble-focus", children=goal.get("focus", "")),
            html.Div(className="bubble-title", children=goal["title"]),
            html.Div(className="bubble-status", children=goal.get("status", "")),
            html.Div(className="bubble-meta", children=horizon),
        ],
    )


def filter_goals(goals: List[Dict[str, Any]], categories: List[str], horizons: List[str], term: str) -> List[Dict[str, Any]]:
    filtered = goals
    if categories:
        filtered = [g for g in filtered if g["category"] in categories]
    if horizons:
        filtered = [g for g in filtered if g.get("horizon", "") in horizons]
    if term:
        term_lower = term.lower()
        filtered = [g for g in filtered if term_lower in g["title"].lower() or term_lower in g.get("focus", "").lower()]
    return filtered


app.layout = html.Div(
    className="page",
    children=[
        html.Header(
            className="hero",
            children=[
                html.Div(
                    className="hero-text",
                    children=[
                        html.P("Personal + Work"),
                        html.H1("Goal Bubbles"),
                        html.P(
                            "Visualize the goals you shared as playful bubbles. Filter by category, horizon, or search keywords, "
                            "and add more as new ideas arrive."
                        ),
                        html.Div(
                            className="pill-row",
                            children=[
                                html.Span("Start now"),
                                html.Span("Invite accountability"),
                                html.Span("Track outcomes"),
                            ],
                        ),
                    ],
                ),
                html.Div(className="hero-accent", children="🎯"),
            ],
        ),
        dcc.Store(id="goal-store", data=INITIAL_GOALS),
        html.Section(
            className="controls",
            children=[
                html.Div(
                    className="control-block",
                    children=[
                        html.Label("Search goals"),
                        dcc.Input(id="search-filter", placeholder="keywords", type="text"),
                    ],
                ),
                html.Div(
                    className="control-block",
                    children=[
                        html.Label("Categories"),
                        dcc.Dropdown(
                            id="category-filter",
                            multi=True,
                            options=sorted({g["category"] for g in INITIAL_GOALS}),
                            placeholder="All",
                        ),
                    ],
                ),
                html.Div(
                    className="control-block",
                    children=[
                        html.Label("Horizon"),
                        dcc.Dropdown(
                            id="horizon-filter",
                            multi=True,
                            options=sorted({g["horizon"] for g in INITIAL_GOALS}),
                            placeholder="All",
                        ),
                    ],
                ),
                html.Div(
                    className="control-block add-form",
                    children=[
                        html.Label("Add a new goal"),
                        dcc.Textarea(
                            id="new-goal-text",
                            placeholder="Describe the goal…",
                            rows=3,
                        ),
                        html.Div(
                            className="inline-inputs",
                            children=[
                                dcc.Dropdown(
                                    id="new-goal-category",
                                    options=sorted({g["category"] for g in INITIAL_GOALS}),
                                    placeholder="Category",
                                    style={"minWidth": "200px"},
                                ),
                                dcc.Dropdown(
                                    id="new-goal-horizon",
                                    options=sorted({g["horizon"] for g in INITIAL_GOALS}),
                                    placeholder="Horizon",
                                    style={"minWidth": "180px"},
                                ),
                            ],
                        ),
                        html.Button("Add goal", id="add-goal-btn"),
                        html.Div(id="add-goal-feedback", className="feedback"),
                    ],
                ),
                html.Div(
                    className="control-block update-form",
                    children=[
                        html.Label("Update goal status & refresh its color"),
                        dcc.Dropdown(
                            id="status-goal-picker",
                            placeholder="Select a goal to update",
                            optionHeight=60,
                        ),
                        dcc.Textarea(
                            id="status-text",
                            placeholder="What changed? Capture latest status, progress, or next step.",
                            rows=3,
                        ),
                        html.Button("Update status", id="update-status-btn"),
                        html.Div(id="status-feedback", className="feedback"),
                    ],
                ),
            ],
        ),
        html.Section(
            className="status",
            children=[
                html.Div(id="goal-count", className="status-card"),
                html.Div(id="category-count", className="status-card"),
                html.Div(id="horizon-count", className="status-card"),
            ],
        ),
        html.Section(
            className="sync",
            children=[
                html.Div(
                    className="control-block sync-card",
                    children=[
                        html.Label("Push goals to Firebase (Realtime DB / Firestore REST)", className="sync-title"),
                        html.P(
                            "Provide a Firebase Realtime DB base URL (ending in .json) or a Firestore REST endpoint. "
                            "Include an auth token if your rules require it.",
                            className="sync-help",
                        ),
                        dcc.Input(
                            id="firebase-url",
                            placeholder="https://<project>.firebaseio.com/goals.json",
                            type="text",
                            value=DEFAULT_FIREBASE_URL,
                        ),
                        dcc.Input(
                            id="firebase-token",
                            placeholder="Optional auth token (kept client-side)",
                            type="password",
                            value=DEFAULT_FIREBASE_TOKEN,
                        ),
                        html.Div(
                            className="sync-buttons",
                            children=[
                                html.Button("Sync to Firebase", id="sync-btn"),
                                html.Button("Load from Firebase", id="load-btn", className="ghost"),
                            ],
                        ),
                        html.Div(id="sync-feedback", className="feedback"),
                    ],
                ),
            ],
        ),
        html.Section(id="bubble-grid", className="bubble-grid"),
    ],
)


@callback(
    Output("goal-store", "data"),
    Output("add-goal-feedback", "children"),
    Input("add-goal-btn", "n_clicks"),
    State("new-goal-text", "value"),
    State("new-goal-category", "value"),
    State("new-goal-horizon", "value"),
    State("goal-store", "data"),
    prevent_initial_call=True,
)
def add_goal(n_clicks: int, text: str, category: str, horizon: str, goals: List[Dict[str, Any]]):
    if not text or not category or not horizon:
        return goals, "Add details for the text, category, and horizon to create a bubble."

    new_goal = {
        "id": str(uuid.uuid4()),
        "title": text.strip(),
        "category": category,
        "horizon": horizon,
        "focus": "New",
        "status": "Fresh update",
        "color_index": 0,
    }
    updated = goals + [new_goal]
    return updated, "Added! The bubble is now in the grid."


@callback(
    Output("bubble-grid", "children"),
    Output("goal-count", "children"),
    Output("category-count", "children"),
    Output("horizon-count", "children"),
    Output("status-goal-picker", "options"),
    Input("goal-store", "data"),
    Input("category-filter", "value"),
    Input("horizon-filter", "value"),
    Input("search-filter", "value"),
)
def update_grid(goals: List[Dict[str, Any]], categories: List[str], horizons: List[str], term: str):
    categories = categories or []
    horizons = horizons or []
    filtered = filter_goals(goals, categories, horizons, term or "")

    bubbles = [render_goal(goal) for goal in filtered]
    if not bubbles:
        bubbles = [html.Div(className="empty", children="No goals match your filters yet.")]

    picker_options = [
        {"label": goal["title"], "value": goal["id"]}
        for goal in goals
    ]

    return (
        bubbles,
        f"Total goals: {len(goals)}",
        f"Selected categories: {len(categories) if categories else 'All'}",
        f"Selected horizons: {len(horizons) if horizons else 'All'}",
        picker_options,
    )


@callback(
    Output("goal-store", "data", allow_duplicate=True),
    Output("status-feedback", "children"),
    Input("update-status-btn", "n_clicks"),
    State("status-goal-picker", "value"),
    State("status-text", "value"),
    State("goal-store", "data"),
    prevent_initial_call=True,
)
def update_status(n_clicks: int, goal_id: str, status_text: str, goals: List[Dict[str, Any]]):
    if not goal_id or not status_text:
        return goals, "Pick a goal and add a status update to recolor the bubble."

    updated_goals = []
    timestamp = datetime.datetime.now().strftime("Updated %b %d, %H:%M")
    for goal in goals:
        if goal["id"] == goal_id:
            color_index = (goal.get("color_index", seeded_color_index(goal_id)) + 1) % len(COLOR_PALETTE)
            updated_goal = {
                **goal,
                "status": status_text.strip(),
                "color_index": color_index,
                "updated_at": timestamp,
            }
            updated_goals.append(updated_goal)
        else:
            updated_goals.append(goal)

    return updated_goals, "Status saved! Bubble refreshed with a new hue."


@callback(
    Output("sync-feedback", "children", allow_duplicate=True),
    Input("sync-btn", "n_clicks"),
    State("firebase-url", "value"),
    State("firebase-token", "value"),
    State("goal-store", "data"),
    prevent_initial_call=True,
)
def sync_to_firebase(n_clicks: int, url: str, token: str, goals: List[Dict[str, Any]]):
    if not url:
        return "Add your Firebase endpoint to sync the bubbles."

    params = {"auth": token} if token else None
    try:
        response = requests.put(url, json=goals, params=params, timeout=10)
        if response.ok:
            return "Synced! Your goals were pushed to Firebase."
        return f"Firebase responded with {response.status_code}: {response.text}"
    except Exception as exc:  # noqa: BLE001
        return f"Sync failed: {exc}"


@callback(
    Output("goal-store", "data", allow_duplicate=True),
    Output("sync-feedback", "children", allow_duplicate=True),
    Input("load-btn", "n_clicks"),
    State("firebase-url", "value"),
    State("firebase-token", "value"),
    State("goal-store", "data"),
    prevent_initial_call=True,
)
def load_from_firebase(n_clicks: int, url: str, token: str, goals: List[Dict[str, Any]]):
    if not url:
        return goals, "Add your Firebase endpoint to sync the bubbles."

    params = {"auth": token} if token else None
    try:
        response = requests.get(url, params=params, timeout=10)
        if not response.ok:
            return goals, f"Firebase responded with {response.status_code}: {response.text}"

        payload = response.json()
        if isinstance(payload, list):
            hydrated = []
            for goal in payload:
                if isinstance(goal, dict):
                    goal.setdefault("color_index", seeded_color_index(goal.get("id", str(uuid.uuid4()))))
                    hydrated.append(goal)
            if hydrated:
                return hydrated, "Loaded goals from Firebase."
            return goals, "Fetched data, but no valid goals were found to load."
        return goals, "Firebase data was not a list. Ensure you stored a list of goal objects."
    except Exception as exc:  # noqa: BLE001
        return goals, f"Load failed: {exc}"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run_server(host="0.0.0.0", port=port, debug=False)
