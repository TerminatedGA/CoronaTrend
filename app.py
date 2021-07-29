#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import plotly.express as px
from plotly.subplots import make_subplots
import natsort
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd

lineagedict = dict(zip(['All Sequences', 'B.1.1.7','B.1.1.63', 'B.1.36', 'B.1.351', 'B.1.427', 'B.1.525', 'B.1.526', 'B.1.620', 'B.1.621', 'B.1.617.1', 'B.1.617.2', 'C.37', 'P.1', 'P.2'],
                       ['All', 'B117','B1163', 'B136', 'B1351', 'B1427', 'B1525', 'B1526', 'B1620', 'B1621', 'B16171', 'B16172', 'C37', 'P1', 'P2']))

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

app.layout = html.Div([
    html.Datalist(id='mut-suggestion', 
                  children=[html.Option(value=word) for word in []]),
    html.Div(dcc.Loading(
        id='loading',
        children=[
            dcc.Graph(id='mutation-chart', style={'height': '100vh'})]), style={'width': '78vw', 'display': 'inline-block', 'vertical-align': 'top'}),
    html.Div([
        html.Div('Filters', 
        style={'color': 'black', 'fontSize': 20, 'font-weight': 'bold'}),
        html.Div('Filter by lineage using dropdown:', 
        style={'color': 'black', 'fontSize': 15}),
        dcc.Dropdown(
        id='lineage-dropdown',
        options=[{'label': list(lineagedict.keys())[x], 'value': list(lineagedict.values())[x]} for x in range(len(lineagedict))],
        value="All",
        clearable=False),
        html.Hr(style={'borderColor': '#828282'}),
        dcc.Input(id="mut-input", 
                  type="text", 
                  placeholder="Search for mutation", 
                  list='mut-suggestion'),
        dcc.RadioItems(id='change-mut',
                   options=[{'label': 'AA Mutations', 'value': 'aamut'},
                            {'label': 'Nucleotide Mutations', 'value': 'nuclmut'}],
                   value='aamut',
                   style={'fontSize': 13}),
        html.Hr(style={'borderColor': '#828282'}),
        html.Div('Filter by gene using dropdown:', 
        style={'color': 'black', 'fontSize': 15}),
    dcc.Dropdown(
        id='gene-dropdown',
        options=[{'label': x, 'value': x} for x in ["placeholder_text"]],
        value="All",
        clearable=False),
    html.Hr(style={'borderColor': '#828282'}),
    html.Div(id='change-slider-container'),
    dcc.RadioItems(id='change-radio',
                   options=[{'label': '(Final - Initial)', 'value': 'fin'},
                            {'label': 'All-time', 'value': 'all'}],
                   value='fin',
                   style={'fontSize': 13}),
    html.Div([dcc.Slider(id='change-slider',
           min=0,
           max=100,
           value=10,
           step=0.5)],
           style={'padding-bottom': 0.5}),
    html.Hr(style={'borderColor': '#828282'}),
    html.Div(id='init-slider-container-min'),
    html.Div(id='init-slider-container-max'),
    html.Div([dcc.RangeSlider(id='init-slider',
               min=0,
               max=100,
               value=[0, 100],
               step=0.5)])], 
    style={'width': '18vw', 'display': 'inline-block', 'vertical-align': 'top', 'borderLeftStyle': 'solid', 'padding-left': 10, 'borderColor': '#828282'})])

@app.callback(
    Output('change-slider-container', 'children'),
    [Input('change-slider', 'value')])
def update_output(value):
    return 'Minimum change in prevalence: {}%'.format(value)

@app.callback(
    [Output('init-slider-container-min', 'children'), Output('init-slider-container-max', 'children')],
    [Input('init-slider', 'value')])
def update_output(value):
    return 'Minimum inital prevalence: {}%'.format(value[0]), 'Maximum inital prevalence: {}%'.format(value[1])

@app.callback(
    [Output('mutation-chart', 'figure'), Output('mut-suggestion', 'children'), Output('gene-dropdown', 'options')],
    [Input('change-slider', 'value'), Input('change-radio', 'value'), Input('init-slider', 'value'), Input('gene-dropdown', 'value'), Input('mut-input', 'value'), Input('change-mut', 'value'), Input('lineage-dropdown', 'value')])
def multiple_output(selected_change_slider, selected_change_radio, selected_init, selected_gene, search_mut, mut_radio, selected_lineage):
    #Update figure with user selection
    
    
    url1 = 'https://media.githubusercontent.com/media/TerminatedGA/GISAID-Dataframes/master/' + selected_lineage + '_1.csv'
    url2 = 'https://media.githubusercontent.com/media/TerminatedGA/GISAID-Dataframes/master/' + selected_lineage + '_2.csv'
    pxdf1 = pd.read_table(url1, sep = ',', index_col=0)
    pxdf2 = pd.read_table(url2, sep = ',', index_col=0)
    
    percentagelistlist1 = [[float(b) for b in a] for a in [[i.strip() for i in a[1:-1].replace('"',"").split(',')] for a in pxdf1['Percentage by period']]]
    pxdf1['Percentage by period'] = percentagelistlist1

    periodlist1repeats = len(pxdf1['Mutations'])
    genelistfinal = natsort.natsorted(set(pxdf1['Gene']))
    genelistfinal.insert(0, "All")
    pxdf1 = pxdf1.explode('Percentage by period')
    pxdf1['Periods'] = list(pxdf2['Periods']) * periodlist1repeats
    
    if search_mut is not None:
        search_mut = search_mut.upper()
    if selected_gene == "All":
        if selected_change_radio == 'all':
            changecolumn = 'Change in prevalence (All)(%)'
        else:
            changecolumn = 'Change in prevalence (Fin - Start)(%)'
        if mut_radio == 'nuclmut':
            mutcolumn = 'Mutations'
        else:
            mutcolumn = 'AA Mutations'
        if search_mut is None or search_mut == '':
            searchmut = (pxdf1[mutcolumn] != None)
        else: 
            searchmut = (pxdf1[mutcolumn].str.contains(search_mut)) 
        filtered_pxdf1 = pxdf1[(pxdf1[changecolumn] >= selected_change_slider) & 
                               (pxdf1['Initial prevalence'] >= selected_init[0]) & 
                               (pxdf1['Initial prevalence'] <= selected_init[1]) & 
                               searchmut]
    else:
        if selected_change_radio == 'all':
            changecolumn = 'Change in prevalence (All)(%)'
        else:
            changecolumn = 'Change in prevalence (Fin - Start)(%)'
        if mut_radio == 'nuclmut':
            mutcolumn = 'Mutations'
        else:
            mutcolumn = 'AA Mutations'
        if search_mut is None or search_mut == '':
            searchmut = (pxdf1[mutcolumn] != None)
        else: 
            searchmut = (pxdf1[mutcolumn].str.contains(search_mut))
        filtered_pxdf1 = pxdf1[(pxdf1[changecolumn] >= selected_change_slider) & 
                               (pxdf1['Initial prevalence'] >= selected_init[0]) & 
                               (pxdf1['Initial prevalence'] <= selected_init[1]) &
                               (pxdf1['Gene'] == selected_gene) &
                               searchmut]
        
    #Create new mutation suggestion list
    if mut_radio == 'nuclmut':
        mutsuggestlist = natsort.natsorted(set(filtered_pxdf1['Mutations']))
    else:
        mutsuggestlist = natsort.natsorted(set(filtered_pxdf1['AA Mutations']))
    
    #Create figures from dataframes, then combine both together
    fig1 = px.line(filtered_pxdf1,
                x = 'Periods',
                y = 'Percentage by period', 
                color = 'Labels',
                custom_data = [filtered_pxdf1['Labels']])
    fig1.update_traces(hovertemplate='<b>%{customdata[0]}</b><br><br>Week: %{x}<br>Prevalence: %{y}'+'%'+'<extra></extra>')
    
    fig2 = px.line(pxdf2, 
                x = 'Periods',
                y = 'Totals',
                color = 'Label', 
                hover_name = 'Label',
                hover_data = {'Periods': True, 'Totals': True, 'Label': False},
                labels = {'Periods' : 'Week',  'Totals': 'Count'})

    fig2.update_traces(yaxis="y2", line = {'color': '#456987', 'dash': "dot", 'width': 4})

    pxfig = make_subplots(specs=[[{"secondary_y": True}]])

    pxfig.add_traces(fig2.data + fig1.data)

    pxfig.layout.xaxis.title = "Time"
    pxfig.layout.yaxis.title = "Mutation Prevalence (%)"
    #pxfig.layout.yaxis1.type="log"
    pxfig.layout.yaxis2.title = "Total Number of Sequences"
    pxfig.layout.update(title={
                            'text' : 'Mutation prevalence over time',
                            'x':0.5,
                            'xanchor': 'center'}, 
                        template = 'plotly_white')

    fig1.update_layout(transition_duration=1000)
    return pxfig, [html.Option(value=word) for word in mutsuggestlist], [{'label': x, 'value': x} for x in genelistfinal]

if __name__ == '__main__':
    app.run_server()

