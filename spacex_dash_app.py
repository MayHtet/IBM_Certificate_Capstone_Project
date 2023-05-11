import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Load the dataset
spacex_df = pd.read_csv('spacex_launch_dash.csv')

# Create a dropdown list of launch sites
sites = spacex_df['Launch Site'].unique().tolist()
sites.insert(0, 'ALL')

# Create a dropdown list of booster versions
boosters = spacex_df['Booster Version'].unique().tolist()
boosters.insert(0, 'ALL')

app = dash.Dash(__name__)

# Define the layout of the dashboard
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Dashboard', style={'textAlign': 'center', 'color': '#503D36',
                                              'font-size': '40px', 'font-family': 'sans-serif'}),
    dcc.Dropdown(id='site-dropdown', options=[{'label': x, 'value': x} for x in sites],
                 value='ALL', placeholder='Select a Launch Site here', searchable=True),
    dcc.Graph(id='success-pie-chart'),
    html.Br(),
    html.Div(dcc.RangeSlider(id='payload-slider', min=0, max=10000, step=1000,
                              value=[spacex_df['Payload Mass (kg)'].min(), spacex_df['Payload Mass (kg)'].max()])),
    html.Br(),
    
    dcc.Graph(id='success-payload-scatter-chart'),
])

# Define a callback function to update the success-pie-chart based on selected site dropdown
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def update_pie_chart(site_dropdown_value):
    if site_dropdown_value == 'ALL':
        data = spacex_df[spacex_df['class'] == 1]
        data = data.groupby('Launch Site').size().reset_index(name='counts')
        
        fig = px.pie(data, values='counts', names='Launch Site', title='Total Success Launches By Site')
        return fig
    else:
        site_df = spacex_df[spacex_df['Launch Site'] == site_dropdown_value]
        data = site_df.groupby('class').size().reset_index(name='counts')
        fig = px.pie(data, values='counts', names='class', title=f"Success Launches for {site_dropdown_value}")
        return fig

# Define a callback function to update the success-payload-scatter-chart based on selected site and payload slider
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'),
               Input(component_id='payload-slider', component_property='value'),
               ])
def update_payload_scatter_chart(site_dropdown, payload_range):
    if site_dropdown == 'ALL':
        filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) & (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
        scatter_chart = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version Category', title='Correlation between Payload and Success for all Sites')
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == site_dropdown]
        filtered_df = filtered_df[(filtered_df['Payload Mass (kg)'] >= payload_range[0]) & (filtered_df['Payload Mass (kg)'] <= payload_range[1])]
        scatter_chart = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version Category', title='Correlation between Payload and Success for '+site_dropdown)
    scatter_chart.update_layout(transition_duration=500)
    return scatter_chart

# Run the app
if __name__ == '__main__':
    app.run_server()