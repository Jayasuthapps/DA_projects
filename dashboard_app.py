import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Load Data
df = pd.read_csv("retail_plotly_dataset.csv")
df["Order_Date"] = pd.to_datetime(df["Order_Date"])

app = dash.Dash(__name__)
app.title = "Retail Analytics Pro"

# ================= DARK STYLE =================
app.layout = html.Div(style={
    "backgroundColor": "#111111",
    "color": "white",
    "padding": "20px"
}, children=[

    html.H1("📊 Retail Sales Analytics Dashboard",
            style={"textAlign":"center"}),

    # ================= FILTERS =================
    html.Div([
        dcc.Dropdown(
            id="region_filter",
            options=[{"label": i, "value": i} for i in df["Region"].unique()],
            multi=True,
            placeholder="Select Region"
        ),

        dcc.Dropdown(
            id="segment_filter",
            options=[{"label": i, "value": i} for i in df["Customer_Segment"].unique()],
            multi=True,
            placeholder="Select Segment"
        ),

        dcc.DatePickerRange(
            id="date_filter",
            start_date=df["Order_Date"].min(),
            end_date=df["Order_Date"].max()
        )

    ], style={
        "display": "flex",
        "gap": "20px",
        "flexWrap": "wrap"
    }),

    html.Br(),

    html.Div(id="kpi_cards", style={
        "display":"flex",
        "justifyContent":"space-around",
        "flexWrap":"wrap"
    }),

    html.Br(),

    html.Div([
        dcc.Graph(id="line_chart", style={"width":"48%"}),
        dcc.Graph(id="bar_chart", style={"width":"48%"})
    ], style={"display":"flex","flexWrap":"wrap","justifyContent":"space-between"}),

    html.Div([
        dcc.Graph(id="scatter_chart", style={"width":"48%"}),
        dcc.Graph(id="treemap_chart", style={"width":"48%"})
    ], style={"display":"flex","flexWrap":"wrap","justifyContent":"space-between"}),

    html.Br(),

    html.H3("📈 Animated Monthly Sales"),
    dcc.Graph(id="animated_chart")

])

# ================= CALLBACK =================
@app.callback(
    [
        Output("kpi_cards", "children"),
        Output("line_chart", "figure"),
        Output("bar_chart", "figure"),
        Output("scatter_chart", "figure"),
        Output("treemap_chart", "figure"),
        Output("animated_chart", "figure")
    ],
    [
        Input("region_filter", "value"),
        Input("segment_filter", "value"),
        Input("date_filter", "start_date"),
        Input("date_filter", "end_date")
    ]
)
def update_dashboard(region, segment, start_date, end_date):

    filtered = df.copy()

    if region:
        filtered = filtered[filtered["Region"].isin(region)]

    if segment:
        filtered = filtered[filtered["Customer_Segment"].isin(segment)]

    filtered = filtered[
        (filtered["Order_Date"] >= start_date) &
        (filtered["Order_Date"] <= end_date)
    ]

    # KPIs
    kpis = [
        html.Div(f"Total Sales: {filtered['Sales'].sum()}",
                 style={"padding":"20px","backgroundColor":"#222","margin":"10px"}),
        html.Div(f"Total Profit: {filtered['Profit'].sum()}",
                 style={"padding":"20px","backgroundColor":"#222","margin":"10px"}),
        html.Div(f"Total Orders: {len(filtered)}",
                 style={"padding":"20px","backgroundColor":"#222","margin":"10px"}),
    ]

    monthly = filtered.groupby("Month")["Sales"].sum().reset_index()

    line_fig = px.line(monthly, x="Month", y="Sales",
                       template="plotly_dark")

    bar_data = filtered.groupby("Customer_Segment")["Sales"].sum().reset_index()
    bar_fig = px.bar(bar_data, x="Customer_Segment", y="Sales",
                     template="plotly_dark")

    scatter_fig = px.scatter(filtered,
                             x="Sales",
                             y="Profit",
                             color="Region",
                             template="plotly_dark")

    tree_fig = px.treemap(filtered,
                          path=["Product_Category","Product_SubCategory"],
                          values="Sales",
                          template="plotly_dark")

    animated_fig = px.line(filtered,
                           x="Month",
                           y="Sales",
                           animation_frame="Month",
                           template="plotly_dark")

    return kpis, line_fig, bar_fig, scatter_fig, tree_fig, animated_fig


if __name__ == "__main__":
    app.run(debug=True)