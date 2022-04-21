from dash import Dash, html, dash_table, dcc
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
from modules.crop_specific_affected import date_of_conflict_map, CropSpecificAffected, crops, years, oblast_names, data_path
import geopandas as gpd
from dash.dash_table.Format import Format
from dash.dependencies import Input, Output



app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

csa = CropSpecificAffected(data_path)

df_2021 = dash_table.DataTable(
    id = 'impact-table-2021',
    data = [{'Crop' : c, 'Impact' : csa.perc_impacted(2021, c)} for c in crops],
    columns = [
        {'name' : 'Crop', 'id' : 'Crop'},
        {'name' : 'Impact', 'id' : 'Impact', 'type' : 'numeric', 'format' : Format(precision=3)}
    ],
    fill_width=False
)

df_2020 = dash_table.DataTable(
    id = 'impact-table-2020',
    data = [{'Crop' : c, 'Impact' : csa.perc_impacted(2020, c)} for c in crops],
    columns = [
        {'name' : 'Crop', 'id' : 'Crop'},
        {'name' : 'Impact', 'id' : 'Impact', 'type' : 'numeric', 'format' : Format(precision=3)}
    ],
    fill_width=False

)

oblast_table = dash_table.DataTable(
    id='oblast-input',
    data = csa.oblast_conflict_df.reset_index().to_dict('records'),
    columns = [{'name' : 'Oblast', 'id' : 'Oblast'},
    {'name' : 'Under Conflict', 'id' : 'Under Conflict'}],
    page_size=5,
    fill_width=False,
    editable=True
)

@app.callback(
    Output('impact-table-2020', 'data'),
    Output('impact-table-2021', 'data'),
    Input('oblast-input', 'data')
)
def update_impacts(data):

    data_2021 = [{'Crop' : c, 'Impact' : csa.perc_impacted(2021, c, pd.DataFrame(data).set_index('Oblast').astype(float))} for c in crops]
    data_2020 = [{'Crop' : c, 'Impact' : csa.perc_impacted(2020, c, pd.DataFrame(data).set_index('Oblast').astype(float))} for c in crops]


    return data_2020, data_2021

@app.callback(
    Output('oblast-input', 'data'),
    Input('reset-button', 'n_clicks')
)
def reset_oblast_conflict(n):

    if n is None or n>0:
        data = csa.oblast_conflict_df.reset_index().to_dict('records')
        return data



app.layout = html.Div(children=[
    html.H1(children='Ukraine Conflict Dashboard'),
    html.Div(children=f'''
        An application with user input that allows you to simulate affected crops in Ukraine based on 
        a conflict map. 

        Conflict map last updated: {date_of_conflict_map}
    '''),
    html.Br(),
    dbc.Row([
        dbc.Col(html.Iframe(srcDoc=open("maps/conflict_map.html", 'r').read(), width=2000, height=1000)),
        dbc.Col([
            html.H2("Oblast Percentage Affected"),
            dcc.Markdown('''
            This tables gives percentage affected numbers for each oblast, change them to simulate other scenarios,
            by changing the number in the data cell and hitting <Enter>.
            '''),
            dbc.Container(oblast_table),
            dbc.Button("Reset", color='primary', className='me-1', id='reset-button'),
            dcc.Markdown('---'),
            html.H2("Estimated Impact Share (2021 Baseline)"),
            dbc.Container(df_2021),
            html.H2("Estimated Impact Share (2020 Baseline)"),
            dbc.Container(df_2020)
        ])
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True)