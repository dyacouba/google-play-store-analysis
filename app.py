# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.plotly as py
import plotly.graph_objs as go
import pandas as pd
import numpy as np

"""
import mysql.connector

mydb = mysql.connector.connect(
    host= "db4free.net",
    user= "dyacouba",
    passwd= "Yacouba5!"
)

mycursor = mydb.cursor()
mycursor.execute("CREATE DATABASE Foogle")

"""

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server  # the Flask app


app.scripts.config.serve_locally = True
app.css.config.serve_locally = True

# Reading the Google Play Store Apps data from a csv files
df = pd.read_csv("googleplaystore.csv", sep=",")
# print(df.loc[df['Type'] == "0"])
print(df.loc[1])
print("\n\n")

#### Number of app by categories (Top n against average)
def get_categories_count(nb_showed_cat):
    # Group by
    categories_count = df.groupby(["Category"]).size().reset_index(name="count")
    categories_nb_mean = categories_count[
        "count"
    ].mean()  # Mean number of app per category

    # Sorting by app count
    categories_count = categories_count.sort_values(by=["count"], ascending=False)
    # print(categories_count)
    categories_count_labels = categories_count["Category"].iloc[0:nb_showed_cat,]
    categories_count_values = categories_count["count"].iloc[0:nb_showed_cat,]

    # Reverse items order for better comprehension of bar chart
    categories_count_labels = categories_count_labels.iloc[::-1]
    categories_count_values = categories_count_values.iloc[::-1]

    return go.Figure(
        data=[
            go.Bar(
                x=categories_count_values,
                y=categories_count_labels,
                name="Number of app",
                orientation="h",
                marker=go.bar.Marker(
                    color="#1DABE6", line=dict(color="#0f658a", width=1.5)
                ),
                opacity=0.8,
            )
        ],
        layout=go.Layout(
            # yaxis=go.layout.YAxis(title='Categories'),
            xaxis=go.layout.XAxis(title="Number of app"),
            title="Number of app per categories",
            showlegend=False,
            legend=go.layout.Legend(x=0, y=1.0),
            margin=go.layout.Margin(l=170, r=10, t=74, b=42),
        ),
    )


#### Average rating by categories (Top n against average)
def get_categories_ratings_zoomed(nb_showed_cat):
    categories_rating = (
        df[["Category", "Rating"]].groupby(["Category"]).mean().reset_index()
    )
    categories_rating = categories_rating.sort_values(by=["Rating"], ascending=False)
    categories_rating_mean = round(
        categories_rating["Rating"].mean(), 3
    )  # Mean rating of the apps per category
    # Separating values in two arrays, one for value that are higher than average, and one for value that are lower than average
    higher_bins = np.array([])
    lower_bins = np.array([])
    category_rank = 1  # Used to limit the number of showed categories
    for index, category in categories_rating.iterrows():
        if float(category["Rating"]) > categories_rating_mean:
            higher_bins = np.append(higher_bins, round(category["Rating"], 3))
            lower_bins = np.append(lower_bins, np.NaN)
        else:
            higher_bins = np.append(higher_bins, np.NaN)
            lower_bins = np.append(lower_bins, round(category["Rating"], 3))
        if category_rank >= nb_showed_cat:
            break  # Stop if we reached the number of categories passed into parameter
        category_rank = category_rank + 1

    categories_labels = categories_rating["Category"].iloc[0:nb_showed_cat,]

    # For this visualization, we need to substract the average from each value
    higher_bins = higher_bins - categories_rating_mean
    lower_bins = lower_bins - categories_rating_mean

    # Reverse items order for better comprehension of bar chart
    categories_labels = categories_labels.iloc[::-1]
    higher_bins = higher_bins[::-1]
    lower_bins = lower_bins[::-1]

    return go.Figure(
        layout=go.Layout(
            # yaxis=go.layout.YAxis(title='Categories'),
            xaxis=go.layout.XAxis(
                range=[-0.3, 0.3],
                tickvals=[-0.3, -0.2, -0.1, 0, 0.1, 0.2, 0.3],
                ticktext=[
                    categories_rating_mean - 0.3,
                    categories_rating_mean - 0.2,
                    categories_rating_mean - 0.1,
                    categories_rating_mean,
                    categories_rating_mean + 0.1,
                    categories_rating_mean + 0.2,
                    categories_rating_mean + 0.3,
                ],
                title="Ratings",
            ),
            title="Average app rating per categories (centered on mean = "
            + str(categories_rating_mean)
            + ")",
            barmode="overlay",
            margin=go.layout.Margin(l=170, r=10, t=74, b=42),
        ),
        data=[
            go.Bar(
                y=categories_labels,
                x=higher_bins,
                orientation="h",
                name="> average",
                hoverinfo="text",
                text=higher_bins + categories_rating_mean,
                marker=dict(color="#1DABE6", line=dict(color="#0f658a", width=1.5)),
                opacity=0.8,
            ),
            go.Bar(
                y=categories_labels,
                x=lower_bins,
                orientation="h",
                name="< average",
                hoverinfo="text",
                text=lower_bins + categories_rating_mean,
                marker=dict(color="#FF0028", line=dict(color="#b3001b", width=1.5)),
                opacity=0.8,
            ),
        ],
    )


categories = df.groupby(["Category"]).size().reset_index(name="count")
categories = categories["Category"]
categories_options = np.array([])
for i in range(len(categories)):
    categories_options = np.append(
        categories_options,
        {"label": categories[i].replace("_", " "), "value": categories[i]},
    )


colors = ["#e6e6e6", "#1DABE6", "#AF060F", "#ffff00", "#E43034S", "#ff66cc"]
colors2 = ["#e6e6e6", "#ffff00"]

### Apps content rating distribution
def get_categories_content_ratings(category):
    # Group by content ratings
    content_rating_count = (
        df.loc[df["Category"] == category]
        .groupby(["Content Rating"])
        .size()
        .reset_index(name="count")
    )
    content_rating_count = content_rating_count.sort_values(
        by=["count"], ascending=False
    )

    content_rating_labels = content_rating_count["Content Rating"]
    content_rating_values = content_rating_count["count"]

    category_name = (
        category.replace("_", " ").lower()[0].upper()
        + category.replace("_", " ").lower()[1:]
    )
    return go.Figure(
        data=[
            go.Pie(
                labels=content_rating_labels,
                values=content_rating_values,
                hoverinfo="label+percent",
                textinfo="value",
                textfont=dict(size=20),
                marker=dict(colors=colors, line=dict(color="#000000", width=1)),
            )
        ],
        layout=go.Layout(
            title='Apps content rating distribution in "' + category_name + '" apps',
            showlegend=True,
            legend=go.layout.Legend(x=0, y=1.0),
            margin=go.layout.Margin(l=20, r=0, t=100, b=10),
        ),
    )


def get_categories_price_type(category):
    # Group by type
    type_count = (
        df.loc[df["Category"] == category]
        .groupby(["Type"])
        .size()
        .reset_index(name="count")
    )
    type_count = type_count.sort_values(by=["count"], ascending=False)

    type_labels = type_count["Type"]
    type_values = type_count["count"]

    category_name = (
        category.replace("_", " ").lower()[0].upper()
        + category.replace("_", " ").lower()[1:]
    )
    return go.Figure(
        data=[
            go.Pie(
                labels=type_labels,
                values=type_values,
                hoverinfo="label+percent",
                textinfo="value",
                textfont=dict(size=20),
                marker=dict(colors=colors2, line=dict(color="#000000", width=1)),
            )
        ],
        layout=go.Layout(
            title='Apps price type distribution in "' + category_name + '" apps',
            showlegend=True,
            legend=go.layout.Legend(x=0, y=1.0),
            margin=go.layout.Margin(l=20, r=0, t=100, b=10),
        ),
    )


app.layout = html.Div(
    children=[
        html.H1(children="Google Play Store's apps analysis using Dash"),
        html.Div(
            [
                html.Div(
                    [
                        dcc.Slider(
                            min=10,
                            max=33,
                            marks={i: "{}".format(i) for i in range(10, 34)},
                            value=20,
                            id="slider_category",
                        ),
                        html.Div(
                            id="slider-output-container", style={"margin-top": 30}
                        ),
                    ],
                    id="slider_container",
                    className="six columns",
                )
            ],
            className="row",
        ),
        
        html.Div(
            [
                html.Div(
                    [dcc.Graph(style={"height": 700}, id="nb_app_categories")],
                    id="nb_app_categories_container",
                    className="six columns",
                ),
                html.Div(
                    [dcc.Graph(style={"height": 700}, id="categories_ratings_zoomed")],
                    id="categories_ratings_zoomed_container",
                    className="six columns",
                ),
            ],
            className="row",
        ),
        
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            ["Choose the category (for pie charts)"],
                            id="installs_dropdown_label",
                        ),
                        dcc.Dropdown(
                            options=categories_options,
                            value="ART_AND_DESIGN",
                            id="category_dropdown",
                        ),
                    ],
                    id="category_dropdown_container",
                    className="six columns",
                )
            ],
            className="row",
        ),
        
        html.Div(
            [
                html.Div(
                    [dcc.Graph(style={"height": 300}, id="pie_categories_ratings")],
                    id="pie_categories_ratings_container",
                    className="six columns",
                ),
                html.Div(
                    [dcc.Graph(style={"height": 300}, id="pie_type_count")],
                    id="pie_type_count_container",
                    className="six columns",
                ),
            ],
            className="row",
        ),
        
        html.Div(
            [
                dcc.Graph(
                    figure=go.Figure(
                        data=[
                            go.Table(
                                header=dict(
                                    values=[
                                        "App",
                                        "Category",
                                        "Rating",
                                        "Size",
                                        "Price",
                                        "Content Rating",
                                        "Last Updated",
                                    ],
                                    fill=dict(color="#C2D4FF"),
                                    align=["left"] * 5,
                                ),
                                cells=dict(
                                    values=[
                                        df.App,
                                        df.Category,
                                        df.Rating,
                                        df.Size,
                                        df.Price,
                                        df["Content Rating"],
                                        df["Last Updated"],
                                    ],
                                    fill=dict(color="#F5F8FF"),
                                    align=["left"],
                                ),
                            )
                        ],
                        layout=go.Layout(
                            title="Full app list",
                            showlegend=True,
                            legend=go.layout.Legend(x=0, y=1.0),
                            margin=go.layout.Margin(l=100, r=50, t=40, b=100),
                        ),
                    ),
                    style={"height": 600},
                    id="app_list",
                )
            ],
            id="app_list_container",
            className="twelve columns",
        ),
    ]
)


@app.callback(
    dash.dependencies.Output("slider-output-container", "children"),
    [dash.dependencies.Input("slider_category", "value")],
)
def update_output(value):
    return (
        "showing the " + format(value) + " first categories (in horizontal bar charts)"
    )


@app.callback(
    dash.dependencies.Output("nb_app_categories", "figure"),
    [dash.dependencies.Input("slider_category", "value")],
)
def update_output(value):
    return get_categories_count(value)


@app.callback(
    dash.dependencies.Output("categories_ratings_zoomed", "figure"),
    [dash.dependencies.Input("slider_category", "value")],
)
def update_output(value):
    return get_categories_ratings_zoomed(value)


@app.callback(
    dash.dependencies.Output("pie_categories_ratings", "figure"),
    [dash.dependencies.Input("category_dropdown", "value")],
)
def update_output(value):
    return get_categories_content_ratings(value)


@app.callback(
    dash.dependencies.Output("pie_type_count", "figure"),
    [dash.dependencies.Input("category_dropdown", "value")],
)
def update_output(value):
    return get_categories_price_type(value)


if __name__ == "__main__":
    app.run_server(debug=True)
