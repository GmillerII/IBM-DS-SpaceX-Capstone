# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import requests
from io import StringIO
#####
    #Load Data
#####
URL = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv"

try:
    # Fetch the data
    response = requests.get(URL, timeout=120)  # Timeout to prevent hanging
    response.raise_for_status()  # Raise an error for HTTP issues

    # Check content type for CSV validation
    if 'text/csv' in response.headers.get('Content-Type', ''):
        # Use StringIO to preprocess the raw data if needed
        raw_data = StringIO(response.text)
        
        # Example: Cleaning or transforming the raw data
        # Uncomment and modify the section below for custom preprocessing
        # cleaned_data = ""
        # for line in raw_data:
        #     # Example: Strip extra whitespace and remove empty lines
        #     line = line.strip()
        #     if line:
        #         cleaned_data += line + '\n'
        # # Replace raw_data with cleaned_data for further processing
        # raw_data = StringIO(cleaned_data)

        # Load into DataFrame
        spacex_df = pd.read_csv(raw_data)
        print(spacex_df.head(5))
        #print(spacex_df.unique("launch Site"))
    else:
        raise ValueError("The URL does not point to a valid CSV file.")

except requests.exceptions.RequestException as e:
    print(f"HTTP request error: {e}")

except ValueError as e:
    print(f"Data validation error: {e}")

except Exception as e:
    print(f"Unexpected error: {e}")

if spacex_df.empty:
    raise RuntimeError("Failed to load SpaceX data. Please check the URL or connection.")

max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1(
        'SpaceX Launch Records Dashboard',
        style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}
    ),
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
        ],
        value='ALL',
        placeholder="Select Launch Site",
        searchable=True
    ),
    html.Br(),
    html.Div(dcc.Graph(id = 'success-pie-chart')),
    html.Br(),
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        value=[min_payload, max_payload]
    ),
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(
    Output(component_id = 'success-pie-chart', component_property = 'figure'),
    Input(component_id = 'site-dropdown', component_property = 'value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        fig = px.pie(spacex_df, 
            values='class', 
            names='Launch Site', 
            title='Total Sucessful Launches for All Sites'
        )
        return fig
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        fig = px.pie(spacex_df, values='class', 
        names='class', 
        title=f"Total Sucessful Launches for {entered_site}")
        return fig
        # return the outcomes piechart for a selected site
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id = 'success-payload-scatter-chart', component_property = 'figure'),
    [Input(component_id = 'site-dropdown', component_property = 'value'), 
    Input(component_id = "payload-slider", component_property = "value")]
)
def get_scatter_chart(entered_site, payload_range):
    # Initialize filtered_df with the full dataframe
    filtered_df = spacex_df

    # Filter by entered site if it's not 'ALL'
    if entered_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]

    # Further filter by payload range
    filtered_df = filtered_df[
        (filtered_df['Payload Mass (kg)'] >= payload_range[0]) & 
        (filtered_df['Payload Mass (kg)'] <= payload_range[1])
    ]

    # Create the scatter plot
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color="Booster Version Category",
        title=f"Correlation between Payload and Success for {entered_site}"
    )

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)