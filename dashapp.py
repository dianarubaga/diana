import dash
from dash import html,dcc
from dash.dependencies import Input, Output
import pandas as pd
from sqlalchemy import create_engine

# Connect to the Sakila database
engine = create_engine('mysql://root:Forzaforza3@localhost/sakila')

# Create the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    html.H1("Sakila Rental Data Over Time"),
    
    # Dropdown to select a category
    dcc.Dropdown(
        id='category-dropdown',
        options=[
            {'label': 'Category 1', 'value': 1},
            {'label': 'Category 2', 'value': 2},
            # Add more options based on your data
        ],
        value=1  # Default selected option
    ),
    
    # Line chart to display data over time
    dcc.Graph(id='line-chart'),
        
    dcc.Graph(id='plot-chart'),
    dcc.Graph(id='clo-chart'),
    dcc.Graph(id='alexa-chart'),
    dcc.Graph(id='diana-chart'),

])
@app.callback(
    Output('diana-chart', 'figure'),
    [Input('category-dropdown', 'value')]
)
def update_diana_chart(selected_category):
    # SQL query to retrieve data for actors with at least 16 film appearances
    query = """
    SELECT a.actor_id, a.first_name, a.last_name, COUNT(fa.film_id) AS film_count
    FROM actor a
    JOIN film_actor fa ON a.actor_id = fa.actor_id
    GROUP BY a.actor_id, a.first_name, a.last_name
    HAVING COUNT(fa.film_id) >= 16
    ORDER BY film_count DESC
    LIMIT 5;
    """

    actor_data = pd.read_sql(query, engine)

    # Create the bar chart
    fig = {
        'data': [
            {
                'x': actor_data['first_name'] + ' ' + actor_data['last_name'],
                'y': actor_data['film_count'],
                'type': 'bar',
                'marker': {'color': 'blue'}
            }
        ],
        'layout': {
            'title': f'Top 5 Actors with Most Film Appearances (at least 16 films)',
            'xaxis': {'title': 'Actor Name'},
            'yaxis': {'title': 'Film Count'}
        }
    }

    return fig

@app.callback(
    Output('alexa-chart', 'figure'),
    [Input('category-dropdown', 'value')]
)
def update_alexa_chart(selected_category):
    # SQL query to retrieve data for the top 5 movies with the highest total revenue
    query = f"""
    SELECT
        f.title AS movie_title,
        SUM(p.amount) AS revenue
    FROM
        film f
    JOIN
        inventory i ON f.film_id = i.film_id
    JOIN
        rental r ON i.inventory_id = r.inventory_id
    JOIN
        payment p ON r.rental_id = p.rental_id
    JOIN
        film_category fc ON f.film_id = fc.film_id
    JOIN
        category cat ON fc.category_id = cat.category_id
    WHERE
        cat.name = 'Family'
    GROUP BY
        f.title
    ORDER BY
        revenue DESC
    LIMIT 5;
    """

    movie_data = pd.read_sql(query, engine)

    # Create the bar chart
    fig = {
        'data': [
            {
                'x': movie_data['movie_title'],
                'y': movie_data['revenue'],
                'type': 'bar',
                'marker': {'color': 'blue'}
            }
        ],
        'layout': {
            'title': f'Top 5 Movies with Highest Revenue in Category {selected_category}',
            'xaxis': {'title': 'Movie Title'},
            'yaxis': {'title': 'Total Revenue'}
        }
    }

    return fig

@app.callback(
    Output('clo-chart', 'figure'),
    [Input('category-dropdown', 'value')]
)
def update_clo_chart(selected_category):
    # SQL query to retrieve data for customers in the "Family" category
    query = f"""
    SELECT
        c.first_name,
        c.last_name
    FROM
        customer c
    JOIN
        rental r ON c.customer_id = r.customer_id
    JOIN
        inventory i ON r.inventory_id = i.inventory_id
    JOIN
        film f ON i.film_id = f.film_id
    JOIN
        film_category fc ON f.film_id = fc.film_id
    JOIN
        category cat ON fc.category_id = cat.category_id
    WHERE
        cat.name = 'Family';
    """

    rental_data = pd.read_sql(query, engine)

    # Create the line chart
    fig = {
        'data': [
            {
                'x': rental_data['first_name'] + ' ' + rental_data['last_name'],
                'y': [1] * len(rental_data),  # A constant value (e.g., 1) for each customer
                'type': 'bar',
                'marker': {'color': 'blue'}
            }
        ],
        'layout': {
            'title': f'Rental Count for Category {selected_category}',
            'xaxis': {'title': 'Customer Name'},
            'yaxis': {'title': 'Rental Count'}
        }
    }

    return fig
# Define callback to update the line chart based on the selected category
@app.callback(
    Output('line-chart', 'figure'),
    [Input('category-dropdown', 'value')]
)
def update_line_chart(selected_category):
    # SQL query to retrieve data for the selected category over time
    query = f"""
    SELECT DATE(rental_date) AS rental_day, COUNT(rental_id) AS rental_count
    FROM rental, inventory, film, film_category
    WHERE rental.inventory_id = inventory.inventory_id AND
    inventory.film_id = film.film_id AND
    film.film_id = film_category.film_id AND
    category_id = {selected_category}
    GROUP BY rental_day;
    """

    rental_data = pd.read_sql(query, engine)

    # Create the line chart
    fig = {
        'data': [
            {
                'x': rental_data['rental_day'],
                'y': rental_data['rental_count'],
                'type': 'bar',
                'marker': {'color': 'blue'}
            }
        ],
        'layout': {
            'title': f'Rental Count for Category {selected_category}',
            'xaxis': {'title': 'Rental Day'},
            'yaxis': {'title': 'Rental Count'}
        }
    }

    return fig


@app.callback(
    Output('plot-chart', 'figure'),
    [Input('category-dropdown', 'value')]
)
def update_plot_chart(selected_category):
    # SQL query to retrieve data for the selected category over time
    query = f"""
    SELECT f.title, SUM(p.amount) AS total_revenue
    FROM film f
    JOIN inventory i ON f.film_id = i.film_id
    JOIN rental r ON i.inventory_id = r.inventory_id
    JOIN payment p ON r.rental_id = p.rental_id
    GROUP BY f.title
    ORDER BY total_revenue DESC
    LIMIT 5;
    """

    rental_data = pd.read_sql(query, engine)

    # Create the bar chart
    fig = {
        'data': [
            {
                'x': rental_data['title'],
                'y': rental_data['total_revenue'],
                'type': 'bar',
                'marker': {'color': 'blue'}
            }
        ],
        'layout': {
            'title': f'Total Revenue by Film for Category {selected_category}',
            'xaxis': {'title': 'Film Title'},
            'yaxis': {'title': 'Total Revenue'}
        }
    }

    return fig

if __name__ == '__main__':
    app.run_server(debug=True) 
