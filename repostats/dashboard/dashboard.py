import plotly.express as px
from dash import Dash, Input, Output, dcc, html

from repostats.dashboard.callbacks import apply_callbacks, callback
from repostats.dashboard.provider import Provider


class Dashboard:
    def __init__(self) -> None:
        self.app = Dash(__name__, suppress_callback_exceptions=True)
        apply_callbacks(self)

        self.provider = Provider.from_json("data/metrics.json")

        repos = list(set(metric.repo for metric in self.provider.metrics))
        self.app.layout = html.Div(
            [
                html.Div(children="Github Repository Metrics"),
                html.Hr(),
                dcc.Checklist(options=repos, value=repos, id="dropdown"),
                dcc.Graph(figure={}, id="graph"),
            ]
        )

    @callback(Output("graph", "figure"), Input("dropdown", "value"))
    def update_graph(self, value):
        value = value or []
        value = value if not isinstance(value, str) else [value]
        data = self.provider.get_files_changed(value)
        fig = px.box(
            data,
            orientation="h",
            x="changed_files",
            y="repo",
        )
        fig.update_layout(hovermode=False)
        return fig


if __name__ == "__main__":
    dashboard = Dashboard()
    dashboard.app.run(debug=True)
