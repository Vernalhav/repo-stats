import plotly.express as px
from dash import Dash, Input, Output, dcc, html

from repostats.dashboard.callbacks import apply_callbacks, callback
from repostats.dashboard.provider import Provider


class Dashboard:
    def __init__(self, provider: Provider) -> None:
        if len(provider.metrics) == 0:
            raise ValueError("No PRs found!")

        self.app = Dash(__name__, suppress_callback_exceptions=True)
        self.provider = provider
        self._init_layout()

        apply_callbacks(self)

    @callback(Output("files-graph", "figure"), Input("files-dropdown", "value"))
    def update_files_graph(self, repos):
        repos = repos or []
        repos = repos if not isinstance(repos, str) else [repos]
        data = self.provider.get_files_changed(repos)
        fig = px.bar(
            data.groupby("repo").mean().reset_index(),
            orientation="h",
            x="changed_files",
            y="repo",
        )
        fig.update_xaxes(fixedrange=True, title="Avg files changed per PR")
        fig.update_yaxes(
            fixedrange=True, title="Repo", ticksuffix=" " * 3, type="category"
        )
        return fig

    @callback(
        [Output("hotfix-graph", "figure"), Output("avg-hotfixes", "children")],
        Input("hotfix-dropdown", "value"),
    )
    def update_hotfix_graph(self, repo):
        data = self.provider.get_hotfixes_per_release(repo)
        fig = px.bar(
            data.loc[:, ("release", "hotfixes")],
            x="release",
            y="hotfixes",
        )
        yticks = (
            list(range(0, int(data.hotfixes.max() + 1))) if len(data.hotfixes) else [0]
        )
        fig.update_xaxes(fixedrange=True, type="category", showgrid=False)
        fig.update_yaxes(
            fixedrange=True,
            tickvals=yticks,
        )
        avg = data.hotfixes.mean() if len(data.hotfixes) else 0
        return fig, round(avg, 1)

    def _init_layout(self):
        repos = list(set(metric.repo for metric in self.provider.metrics))
        self.app.layout = html.Div(
            className="container",
            children=[
                html.H3("Github Repository Metrics"),
                html.Hr(),
                dcc.Checklist(options=repos, value=repos, id="files-dropdown"),
                dcc.Graph(
                    id="files-graph",
                    config={
                        "displayModeBar": False,
                        "scrollZoom": False,
                    },
                ),
                html.Hr(),
                dcc.Dropdown(
                    options=repos,
                    value=repos[0],
                    id="hotfix-dropdown",
                    clearable=False,
                ),
                html.Div(
                    className="columns centered",
                    children=[
                        html.Div(
                            className="two columns centered",
                            children=html.Div(
                                children=[
                                    html.H1(
                                        0,
                                        id="avg-hotfixes",
                                        style={"margin": 0, "text-align": "center"},
                                    ),
                                    html.H6(
                                        "hotfixes",
                                        style={"margin": 0, "text-align": "center"},
                                    ),
                                    html.P(
                                        "per release",
                                        style={"margin": -10, "text-align": "center"},
                                    ),
                                ]
                            ),
                        ),
                        dcc.Graph(
                            className="ten columns",
                            id="hotfix-graph",
                            config={
                                "displayModeBar": False,
                                "scrollZoom": False,
                            },
                        ),
                    ],
                ),
            ],
        )
