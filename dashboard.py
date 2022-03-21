import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

df = pd.read_csv("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv", index_col=0)
for i in range(len(df)):
    if df.loc[i,'class'] == 0:
        df.loc[i,'result'] = 'Failure'
    else:
        df.loc[i,'result'] = 'Success'
max_payload = df['Payload Mass (kg)'].max()
min_payload = df['Payload Mass (kg)'].min()
launch_sites = [i for i in df['Launch Site'].value_counts().index]

app = dash.Dash(__name__)

app.layout = html.Div(children=[
                                html.H1(
                                        'SpaceX Launch Records Dashboard',
                                            style={
                                                    'textAlign' : 'center',
                                                    'color' : '#503D36',
                                                    'font-size' : 40
                                                    }
                                        ),
                                dcc.Dropdown(
                                            id = 'dropdown',
                                            options = [{
                                                        'label' : 'All launch sites',
                                                        'value' : 'ALL'
                                                        }]+
                                                        [{
                                                        'label' : i,
                                                        'value' : i
                                                        } for i in launch_sites],
                                            value = 'ALL',
                                            placeholder = 'Launch Site Selection',
                                            searchable = True
                                            ),
                                html.Br(),
                                html.Div(dcc.Graph(id='pie-chart')),
                                html.Br(),
                                html.P("Payload range (Kg):"),
                                dcc.RangeSlider(
                                                id='slider',
                                                value=[min_payload, max_payload],
                                                min=0, max=10000, step=1000,
                                                ),
                                html.Div(dcc.Graph(id='scatter-chart')),
                                ])
@app.callback(
    Output('pie-chart','figure'),
    Input('dropdown','value'))
def get_pie(site):
    dfr = df
    if site == 'ALL':
        dfr = dfr[dfr['result'] == 'Success']
        dfr = dfr.groupby('Launch Site').size().reset_index(name='count')
        fig = px.pie(dfr,names='Launch Site', values='count' , title='Success Rate of All Launch Sites')
    else:
        dfr = dfr[dfr['Launch Site'] == str(site)]
        dfr = dfr.groupby(['Launch Site','result']).size().reset_index(name='count')
        fig = px.pie(dfr, values='count', names='result', title=f'Success Rate of Launch Site {str(site)}')
    return fig

@app.callback(
    Output('scatter-chart','figure'),
    Input('dropdown','value'),
    Input('slider','value'))
def get_scatter(downer,slider):
    if downer == 'ALL':
        dfr = df[df['Payload Mass (kg)'].between(slider[0],slider[-1])]
        fig = px.scatter(dfr, x='Payload Mass (kg)',y='result',color='Booster Version Category',
            title='Correlation between Payload and Success for all Sites')
    else:
        dfr = df[df['Payload Mass (kg)'].between(slider[0],slider[-1])]
        dfr = dfr[dfr['Launch Site'] == str(downer)]
        fig = px.scatter(dfr, x='Payload Mass (kg)',y='result',color='Booster Version Category',
            title=f'Correlation between Payload and Success for {downer}')
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
