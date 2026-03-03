#!/usr/bin/env python3
import os
import pandas as pd
import plotly.express as px

PROC_DIR = os.path.join("data", "processed")


def build_figure():
    path = os.path.join(PROC_DIR, "top20_monthly.csv")
    df = pd.read_csv(path, parse_dates=["year_month"])
    df["label"] = df["label"].fillna(df["asset_id"])

    fig = px.bar(
        df,
        x="market_cap",
        y="label",
        color="label",
        orientation="h",
        animation_frame="year_month",
        animation_group="label",
        range_x=[0, df["market_cap"].max() * 1.1],
        title="Top 20 Assets by Market Cap Over Time",
        labels={"market_cap": "Market Cap (approx)", "label": "Asset"},
    )
    fig.update_layout(template="plotly_dark", height=700)
    return fig


if __name__ == "__main__":
    fig = build_figure()
    fig.show()
