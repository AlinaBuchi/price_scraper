from database import MongoConnector
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta


connector = MongoConnector()
product_list_db = connector.list('products')

app_dash = Dash(__name__, routes_pathname_prefix='/dash/') #, external_stylesheets=[dbc.themes.BOOTSTRAP])

products = []
price_history = {}
images = {}

# Prepare data from db
for item in product_list_db:
    product_name = item["product_name"]
    products.append(product_name)
    price_history[product_name] = item["price_history"]
    images[product_name] = item["image"]

# Define the layout
app_dash.layout = html.Div(
    style={'margin-left': '100px', 'margin-right': '100px'},
    children=[
        html.H1("Product Price Evolution",
                style={'textAlign': 'center', 'color': '#6495ED'}
                ),
        # html.Div(style={'margin-bottom': '40px'}),  # Blank line
        dcc.Dropdown(
            id="product-dropdown",
            options=[{"label": product, "value": product} for product in products],
            value=[products[0]],  # default value
            multi=True, # for multiple choices
            style={'color': 'black'}
        ),
        html.Div(style={'margin-bottom': '40px'}),  # Blank line
        html.Div(id="image-container"),
        dcc.Graph(id="price-evolution-graph"),
        # html.H3("Price Evolution", style={'textAlign': 'left', 'margin-left': '20px'})
             ])

# @app.callback(
#     Output("product-dropdown", "style"),
#     [Input("product-dropdown", "value")]
# )
# def update_dropdown_style(selected_products):
#     return {
#         'color': 'black',
#         'fontWeight': 'bold' if selected_products else 'normal'
#     }


# callback for getting output after user interaction
@app_dash.callback(
    Output("price-evolution-graph", "figure"),
    Output("image-container", "children"),
    Input("product-dropdown", "value")
)
def update_price_evolution_graph(selected_products):
    fig = go.Figure()
    images_html = []

    for product in selected_products:
        product_price_history = price_history[product]
        dates = [entry["date"].date() for entry in product_price_history]
        prices = [entry["price"] for entry in product_price_history]

        today = datetime.now().date()

        if today not in dates:
            # Use the last available price as the price for today
            last_price = prices[-1]
            dates.append(today)
            prices.append(last_price)
        # Add the dates and prices to the chart
        fig.add_trace(go.Scatter(x=dates, y=prices, mode='lines', name=product))

        # Create an image element for the selected product
        image_url = images[product]
        image_element = html.Img(src=image_url, style={'width': 'auto', 'max-width': '300px', 'object-fit': 'contain'})
        images_html.append(image_element)

        # Linear regression for future price estimation
        x = np.array([(date - dates[0]).days for date in dates]).reshape(-1, 1)
        y = np.array(prices)
        model = LinearRegression()
        # Train the model with data
        model.fit(x, y)

        # Predict future prices for the next 7 days
        future_dates = [dates[-1] + timedelta(days=i) for i in range(1, 8)]
        future_x = np.array([(date - dates[0]).days for date in future_dates]).reshape(-1, 1)
        future_prices = model.predict(future_x)

        # Mark today's price on the graph with a diamond symbol and dots for predicted prices
        # today = datetime.now().date()
        today_price = prices[-1]
        fig.add_trace(go.Scatter(x=[today], y=[today_price], mode='markers', name="Today's Price", marker=dict(size=8, symbol='diamond')))

        fig.add_trace(go.Scatter(x=future_dates, y=future_prices, mode='markers', name="Estimated Future Prices"))

    fig.update_layout(
        xaxis_tickformat='%Y-%m-%d',
        yaxis_tickformat=".2f",
        xaxis=dict(title="Date"),
        yaxis=dict(title="Price"),)
    return fig, images_html


if __name__ == '__main__':
    app_dash.run(debug=True)

