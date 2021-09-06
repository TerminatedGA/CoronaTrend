import plotly.express as px
from plotly.subplots import make_subplots
import natsort
import dash
from dash import dcc
import dash_bootstrap_components as dbc
from dash import html
from dash.dependencies import Input, Output, State
import pandas as pd
from collections import Counter
first = True

lineagedict = dict(zip(['All Sequences', 'B.1.1.7', 'B.1.1.63', 'B.1.36', 'B.1.351', 'B.1.427', 'B.1.525', 'B.1.526', 'B.1.620', 'B.1.621', 'B.1.617.1', 'B.1.617.2', 'C.37', 'P.1', 'P.2'],
                       ['All', 'B117', 'B1163', 'B136', 'B1351', 'B1427', 'B1525', 'B1526', 'B1620', 'B1621', 'B16171', 'B16172', 'C37', 'P1', 'P2']))

hrstyledict = dict(zip(['borderColor', 'margin', 'marginLeft', 'width'], ['#828282', 15, '-4%', '104%']))

index_html = open('assets/index.html', 'r')

external_stylesheets = [dbc.themes.FLATLY, dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, update_title='CoronaTrend - Loading')

app.index_string = index_html.read()

index_html.close()

server = app.server

navbar = dbc.Navbar(
    id='navbar',
    children=[
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Col(html.A(html.Img(src=app.get_asset_url('images/CoronaTrend Logo.png'), height="100px", width = 100),
                                   href="https://coronatrend.live",
                                style={'text-decoration': 'none'})),
                    dbc.Col([html.A(html.Div('CoronaTrend',
                                              style={'color': 'black', 'fontSize': 27, 'font-weight': 'bold'}),
                             href="https://coronatrend.live",
                             style={'text-decoration': 'none'}),
                                 html.Div(children=[html.Div('Enabled by data from', 
                                                              style={'color': 'black', 'fontSize': 14, 'marginRight': 5, 'display': 'inline'}),
                                 html.A(href="https://www.gisaid.org/",
                                        target='_blank',
                                        children=[html.Img(src=app.get_asset_url('images/GISAID.png'),
                                                           style={'width': 70, 'verticalAlign': 'center'})])])],
                           width=150),
                ],
                align="center",
                no_gutters=True,
            ),
        dbc.NavbarToggler(id="navbar-toggler", n_clicks=0)
    ],
    color="#F5F7C3",
    dark=False,
    style={'height': 100}
)

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "float": "right",
    "left": "80%",
    "width": "20%",
    "height": "110vh",
    "z-index": 1,
    "transition": "all 0.5s",
    "padding": "1rem 1rem",
    "background-color": "light",
    "overflow-y": "scroll",
    'borderLeftStyle': 'solid',
    'borderColor': '#828282'
}

SIDEBAR_HIDDEN = {
    "float": "right",
    "left": "105%",
    "width": 0,
    "height": 0,
    "z-index": 1,
    "transition": "all 0.5s",
    "background-color": "light",
    "overflow": "hidden"
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "float": "left",
    "transition": "all 0.5s",
    "width": "80%",
    "height": "100%",
    "padding": "1rem 1rem",
    "background-color": "light",
    'position': 'relative'
}

CONTENT_STYLE1 = {
    "float": "left",
    "transition": "all 0.5s",
    "width": "100%",
    "height": "100%",
    "padding": "1rem 1rem",
    "background-color": "light",
    'position': 'relative'
}

content=html.Div(id='page-content',
                 children=[dcc.Tabs([
            #Graph 1: Mutation graph
            dcc.Tab(label='Mutation graph', 
                    children=[dcc.Loading(
                                id='loading-mutation-chart',
                                children=[dcc.Graph(id='mutation-chart', 
                                                    style={'height': '90vh'},
                                                    config={"displaylogo": False})]),
                      html.Div(["NOTES:", 
                               html.Br(), 
                               "1. The time mentioned above refers to the collection date of each sequence.", 
                               html.Br(), 
                               "2. Only deletion and substitution mutations are shown. Insertion mutations cannot be shown.", 
                               html.Br(), 
                               "3. Sequenced regions with ambiguous bases (such as N) are treated as having no mutations."])]),
            #Graph 2: Gene Pie Chart
            dcc.Tab(label='Gene Pie Chart',
                    children=[dcc.Loading(
                                id='loading-pie-chart',
                                children=[dcc.Graph(id='pie-chart', 
                                                    style={'height': '90vh'},
                                                    config={"displaylogo": False})])])],
            style={'height': 60}),
                          dbc.Button('>',
                                     id='btn_sidebar',
                                     style={'width': '0.5rem',
                                            'height': '2rem',
                                            'top': '20vh',
                                            'right': '0vw',
                                            'fontSize': 12,
                                            'border-top-left-radius': '0.5rem',
                                            'border-bottom-left-radius': '0.5rem',
                                            'border-top-right-radius': '0rem',
                                            'border-bottom-right-radius': '0rem',
                                            'position': 'absolute',
                                            'display': 'flex',
                                            'align-items': 'center',
                                            'justify-content': 'center',
                                            'background-color': '#828282',
                                            'border': 'none'})])

sidebar = html.Div(id='filter-sidebar',
             children=[    
        html.Div('Viewing Options', 
        style={'color': 'black', 'fontSize': 20, 'font-weight': 'bold'}),
        dcc.RadioItems(id='y-scale',
                   options=[{'label': 'Linear Primary Y-axis', 'value': "linear"},
                            {'label': 'Log Primary Y-axis', 'value': "log"}],
                   value="linear",
                   style={'fontSize': 13},
                   labelStyle={'display': 'block'}),
        html.Div('Filters', 
                 style={'color': 'black', 'fontSize': 20, 'font-weight': 'bold'}),
        html.Div('Lineage:', 
                 style={'color': 'black', 'fontSize': 15}),
        dcc.Dropdown(id='lineage-dropdown',
                     options=[{'label': list(lineagedict.keys())[x], 'value': list(lineagedict.values())[x]} for x in range(len(lineagedict))],
                     value="B1351",
                     clearable=False),
        html.Hr(style=hrstyledict),
        html.Div('Country:', 
                 style={'color': 'black', 'fontSize': 15}),
        dcc.Input(id='country-input',
                  type='text',
                  value='',
                  list="country-suggestion"),
        html.Div(id='country-error-container',
                 children='', 
                 style={'color': 'red', 'fontSize': 10}),
        html.Hr(style=hrstyledict),
        dcc.Input(id="mut-input", 
                  type="text", 
                  placeholder="Search for mutation", 
                  list='mut-suggestion'),
        html.Div(id='mut-error-container',
                 children='', 
                 style={'color': 'red', 'fontSize': 10}),
        dcc.RadioItems(id='change-mut',
                   options=[{'label': 'AA Mutations', 'value': 'aamut'},
                            {'label': 'Nucleotide Mutations', 'value': 'nuclmut'}],
                   value='aamut',
                   style={'fontSize': 13},
                   labelStyle={'display': 'block'}),
        html.Hr(style=hrstyledict),
        dcc.Checklist(id='remove-syn-checkbox',
                      options=[{'label': 'Hide Synonymous Mutations', 'value': 'drop'}],
                      value = ['drop']),
        html.Hr(style=hrstyledict),
        html.Div('Gene:', 
                 style={'color': 'black', 'fontSize': 15}),
        dcc.Dropdown(
            id='gene-dropdown',
            options=[{'label': 'Loading...', 'value':"placeholder"}],
            value="All",
            clearable=False),
        html.Hr(style=hrstyledict),
        html.Div('Minimum total number of sequences per time period:', 
                 style={'color': 'black', 'fontSize': 15}),
        dcc.Input(
            id="total-input",
            type="number",
            value=10),
        html.Hr(style=hrstyledict),
        html.Div(id='change-slider-container'),
        dcc.RadioItems(id='change-radio',
                       options=[{'label': '(Final - Initial)', 'value': 'fin'},
                                {'label': 'All-time', 'value': 'all'}],
                       value='fin',
                       style={'fontSize': 13},
                       labelStyle={'display': 'block'}),
        html.Div([dcc.Slider(id='change-slider',
               min=-100,
               max=100,
               value=10,
               step=0.5)]),
        html.Hr(style=hrstyledict),
        html.Div(id='init-slider-container-min'),
        html.Div(id='init-slider-container-max'),
        html.Div([dcc.RangeSlider(id='init-slider',
                   min=0,
                   max=100,
                   value=[0, 100],
                   step=0.5)])])

footer = html.Div(id='footer',
                  children=[dbc.Navbar(children=[html.Div(children=[
                          html.Button("Acknowledgements",
                                      id="acknowledgement-open-button",
                                      style={'display': 'inline-block', 
                                             'border': 'None', 
                                             'outline': 'None',
                                             'background': 'None',
                                             'paddingRight': '50px'},
                                      n_clicks=0),
                          html.Div(children=["GISAID data provided on this website are subject to GISAID’s ", 
                                             dcc.Link("Terms and Conditions",
                                                      target='_blank',
                                                      href="https://www.gisaid.org/registration/terms-of-use/")],
                                   style={'display': 'inline-block'})],
                               style={"fontSize": 13,
                                      "textAlign": "center"})],
                               style={"borderTop": "1px grey solid", 
                                      "textAlign": "center",
                                      "paddingTop": "20px", 
                                      "paddingBottom": "20px",
                                      "width": "98vw",
                                      'display': 'flex',
                                      'justify-content': 'center'}),
 #Acknowledgement modal window
html.Div([
    html.Div([
        html.Div([html.Div('CoronaTrend',
                 style={'color': 'black', 
                        'fontSize': 26, 
                        'display':'inline', 
                        'font-weight': 'bold'}),
                 html.Button('✕', 
                            id='acknowledgement-close-button',
                            style={'float': 'right', 
                                   'border': 'None', 
                                   'outline': 'None',
                                   'background': 'None'})],
                 style={'paddingBottom': 20}),
        html.Div(children=["CoronaTrend aims to be a public resource from the The University of Hong Kong, detailing the prevalence of different mutations across different lineages as time passes. ", 
                           html.Br(),
                           html.Br(),
                           "Developers: Mr. Chan Tze To, Mr. Jonathan Ip, Dr. Kelvin To"],
                 style={'paddingBottom': 30}),
        html.Div(children='GISAID Initiative',
                 style={'color': 'black', 
                        'fontSize': 26, 
                        'font-weight': 'bold', 
                        'paddingBottom': 20}),
        html.Div(children=["We gratefully acknowledge all data contributors, i.e. the Authors and their Originating laboratories responsible for obtaining the specimens, and their Submitting laboratories for generating the genetic sequence and metadata and sharing via the GISAID Initiative (1), on which this research is based.",
                           html.Br(),
                           html.Br(),
                           html.Div([html.Div("1) Elbe, S., and Buckland-Merrett, G. (2017) Data, disease and diplomacy: GISAID’s innovative contribution to global health. Global Challenges, 1:33-46. DOI: ",
                                               style={'display': 'inline'}),
                                      dcc.Link("10.1002/gch2.1018",
                                                target='_blank',
                                                href="https://dx.doi.org/10.1002/gch2.1018",
                                                style={'display': 'inline'}),
                                      html.Div(" PMCID: ",
                                               style={'display': 'inline'}),
                                      dcc.Link("31565258",
                                                target='_blank',
                                                href="https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6607375/")])])],
        className='modal-content')],
                id='acknowledgement-modal',
     className='modal',
     style={"display": "none"})])

app.layout = html.Div([
    html.Datalist(id='mut-suggestion', 
                  children=[html.Option(value=word) for word in []]),
    html.Datalist(id='country-suggestion', 
                  children=[html.Option(value=word) for word in []]),
    html.Div([html.Div(id='graph-error-container',
                 children='', 
                 style={'color': 'red', 'fontSize': 10})]),
    dcc.Store(id='side_click'),
    dcc.Location(id="url"),       
    navbar,
    html.Div(children=[content, sidebar],
             style={'width': '98.72vw'}),
    footer])

@app.callback(Output('acknowledgement-modal', 'style'),
              [Input('acknowledgement-open-button', 'n_clicks'),
               Input('acknowledgement-close-button', 'n_clicks')])
def close_modal(selected_open, selected_close):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'acknowledgement-open-button' in changed_id:
        return {"display": "block"}
    if 'acknowledgement-close-button' in changed_id:
        return {"display": "none"}

@app.callback(
    [
        Output("filter-sidebar", "style"),
        Output("page-content", "style"),
        Output("side_click", "data"),
        Output("btn_sidebar", "children"),
    ],

    [Input("btn_sidebar", "n_clicks")],
    [
        State("side_click", "data"),
    ]
)
def toggle_sidebar(n, nclick):
    if n:
        if nclick == "SHOW":
            sidebar_style = SIDEBAR_HIDDEN
            content_style = CONTENT_STYLE1
            cur_nclick = "HIDDEN"
            button_text = "<"
        else:
            sidebar_style = SIDEBAR_STYLE
            content_style = CONTENT_STYLE
            cur_nclick = "SHOW"
            button_text = ">"
    else:
        sidebar_style = SIDEBAR_STYLE
        content_style = CONTENT_STYLE
        cur_nclick = 'SHOW'
        button_text = ">"
        
    navbar_style = content_style.copy()
    navbar_style["background-color"] = "#F5F7C3"
    navbar_style["height"] = 100

    return sidebar_style, content_style, cur_nclick, button_text

@app.callback(
    Output('change-slider-container', 'children'),
    [Input('change-slider', 'value')])
def update_output(value):
    return 'Minimum increaase in prevalence: {}%'.format(value)

@app.callback(
    [Output('init-slider-container-min', 'children'), 
     Output('init-slider-container-max', 'children')],
    [Input('init-slider', 'value')])
def update_output(value):
    return 'Minimum inital prevalence: {}%'.format(value[0]), 'Maximum inital prevalence: {}%'.format(value[1])

@app.callback(
    [Output('mutation-chart', 'figure'), 
     Output('pie-chart', 'figure'), 
     Output('mut-suggestion', 'children'), 
     Output('gene-dropdown', 'options'),
     Output('country-suggestion', 'children'),
     Output('country-error-container', 'children'),
     Output('graph-error-container', 'children'),
     Output('mut-error-container', 'children')],
    [Input('change-slider', 'value'), 
     Input('change-radio', 'value'), 
     Input('init-slider', 'value'), 
     Input('gene-dropdown', 'value'), 
     Input('mut-input', 'value'), 
     Input('change-mut', 'value'), 
     Input('lineage-dropdown', 'value'), 
     Input('y-scale', 'value'),
     Input('remove-syn-checkbox', 'value'),
     Input('country-input', 'value'),
     Input('total-input', 'value')])
def multiple_output(selected_change_slider, 
                    selected_change_radio, 
                    selected_init, 
                    selected_gene, 
                    search_mut, 
                    mut_radio, 
                    selected_lineage, 
                    selected_y_scale,
                    remove_syn,
                    search_country,
                    input_total):
#Update figure with user selection
    #Check if graph has error
    grapherror = False
    
    #Defaults
    if search_country == "":
        search_country = 'All'
    if input_total is None:
        input_total = 0

    #Updates country search bar results
    global first
    if first == True:
        global prevcountry
        global prevcountry1
        global countrylist
        global prevlineage
        global prevlineage1
        global prevtotal1
        url3 = 'https://github.com/TerminatedGA/GISAID-Dataframes/blob/master/{}/{}_metadata.pickle?raw=true'.format(selected_lineage, selected_lineage)
        prevlineage = selected_lineage
        prevtotal1 = input_total
        metadata = pd.read_pickle(url3, compression = "gzip")
        countrylist = metadata[0]
        prevcountry = "All"
        prevcountry1 = search_country
        prevlineage1 = selected_lineage
        countryerror = ""
    else:
        if selected_lineage != prevlineage:
            url3 = 'https://github.com/TerminatedGA/GISAID-Dataframes/blob/master/{}/{}_metadata.pickle?raw=true'.format(selected_lineage, selected_lineage)
            prevlineage = selected_lineage
            metadata = pd.read_pickle(url3, compression = "gzip")
            countrylist = metadata[0]
        #Prevents graph update until a valid country is input
        if search_country not in countrylist and search_country != "All":
            countryerror = "Error: {} is not a valid option!".format(search_country)
            grapherror = True
            search_country = prevcountry
            if search_country not in countrylist and search_country != "All":
                selected_lineage = prevlineage1
        else:
            countryerror = ""
        prevcountry = search_country
    
    search_country.replace(" ", "_")
    
    #Fetch dataframes from GitHub and generate required lists
    if first == True:
        global url1
        global pxdf1original
        global pxdf2original
        global pxdf1
        global pxdf2
        global piedf1
        global filtered_pxdf2
        global genelistfinal
        global prevtotallist
        global totallist
        global periodlist1repeats
        global search_mutoriginal
        
        search_mutoriginal = None
    
    #Fetches new dataframe upon new user selection and generates required lists
    if first == True or prevtotal1 != input_total or prevlineage1 != selected_lineage or prevcountry1 != search_country:
        url1 = 'https://github.com/TerminatedGA/GISAID-Dataframes/blob/master/{}/{}_{}_1.feather?raw=true'.format(selected_lineage, selected_lineage, search_country)
        url2 = 'https://github.com/TerminatedGA/GISAID-Dataframes/blob/master/{}/{}_{}_2.feather?raw=true'.format(selected_lineage, selected_lineage, search_country)
        pxdf1original = pd.read_feather(url1)
        pxdf2original = pd.read_feather(url2)
        
        pxdf1 = pxdf1original.copy()
        pxdf2 = pxdf2original.copy()
        piedf1 = pxdf1.copy()

        totallist = list(pxdf2original["Totals"])
        periodlist1repeats = len(pxdf1original['Mutations'])
        genelistfinal = natsort.natsorted(set(pxdf1original['Gene']))
        genelistfinal.insert(0, "All")
        deletedlist = []
        for x in range(len(totallist)):
            if totallist[x] < input_total:
                deletedlist.append(x)

        filtered_pxdf2 = pxdf2.drop(deletedlist)

        pxdf1["Percentage by period"] = [[a[b] for b in range(len(a)) if b not in deletedlist] for a in pxdf1original["Percentage by period"]]
        pxdf1 = pxdf1.explode('Percentage by period')
        if len(filtered_pxdf2['Periods']) == 0:
            pxdf1['Periods'] = None
            pxdf1['Labels'] = ""
            grapherror = True
        else:
            pxdf1['Periods'] = list(filtered_pxdf2['Periods']) * periodlist1repeats
        
        if first == True:
            first = False
        else:
            prevtotal1 = input_total
            prevlineage1 = selected_lineage
            prevcountry1 = search_country
    
    if search_mut is not None:
        search_mutoriginal = search_mut
        search_mut = search_mut.upper()
        
    
    if selected_change_radio == 'all':
        changecolumn = 'Change in prevalence (All)(%)'
    else:
        changecolumn = 'Change in prevalence (Fin - Start)(%)'
    if mut_radio == 'nuclmut':
        mutcolumn = 'Mutations'
    else:
        mutcolumn = 'AA Label'
    if search_mut is None or search_mut == '':
        searchmutline = (pxdf1[mutcolumn] != None)
        searchmutpie = (piedf1[mutcolumn] != None)
    else: 
        searchmutline = (pxdf1[mutcolumn].str.contains(search_mut, case=False)) 
        searchmutpie = (piedf1[mutcolumn].str.contains(search_mut, case=False)) 
    if selected_gene == "All":
        selectedgeneline = (pxdf1['Gene'] != None)
        selectedgenepie = (piedf1['Gene'] != None)
    else:
        selectedgeneline = (pxdf1['Gene'] == selected_gene)
        selectedgenepie = (piedf1['Gene'] == selected_gene)
    if remove_syn == ['drop']:
        removesynline = (pxdf1['Synonymous'] == 'No')
        removesynpie = (piedf1['Synonymous'] == 'No')
    else:
        removesynline = (pxdf1['Synonymous'] != None)
        removesynpie = (piedf1['Synonymous'] != None)
        
        
 #Filters dataframe based on user selection       
    def filter_df(df, selectedgene, searchmut, removesyn):
        return df[(df[changecolumn] >= selected_change_slider) & 
                           (df['Initial prevalence'] >= selected_init[0]) & 
                           (df['Initial prevalence'] <= selected_init[1]) &
                           selectedgene &
                           searchmut &
                           removesyn]
    
    filtered_pxdf1 = filter_df(pxdf1, selectedgeneline, searchmutline, removesynline)
    
    filtered_piedf1 =  filter_df(piedf1, selectedgenepie, searchmutpie, removesynpie)

#Count the genes for each amino acid mutation
    piedict = Counter(filtered_piedf1['Gene'])

    #Create new mutation suggestion list for search bar
    if mut_radio == 'nuclmut':
        mutsuggestlist = natsort.natsorted(set(filtered_pxdf1['Mutations']))
    else:
        mutsuggestlist = natsort.natsorted(set(filtered_pxdf1['AA Label']))
    
    #Returns error if searched mutation is invalid
    if int(len(filtered_pxdf1)) == 0 and search_mutoriginal is not None:
        muterror = "Error: {} is not a valid option!".format(search_mutoriginal)
    else:
        muterror = ""
    
    #Create mutation chart from dataframe 1
    fig1 = px.line(filtered_pxdf1,
                x = 'Periods',
                y = 'Percentage by period', 
                color = 'Labels',
                custom_data = [filtered_pxdf1['Labels']])
    fig1.update_traces(hovertemplate='<b>%{customdata[0]}</b><br><br>Week: %{x}<br>Prevalence: %{y}'+'%'+'<extra></extra>')
    
    #Create chart showing sample size of sequence in each time point 
    fig2 = px.line(filtered_pxdf2, 
                x = 'Periods',
                y = 'Totals',
                color = 'Label', 
                hover_name = 'Label',
                hover_data = {'Periods': True, 'Totals': True, 'Label': False},
                labels = {'Periods' : 'Week',  'Totals': 'Count'})

    fig2.update_traces(yaxis="y2", line = {'color': '#456987', 'dash': "dot", 'width': 4})

    #Combine both graphs together
    pxfig1 = make_subplots(specs=[[{"secondary_y": True}]])

    pxfig1.add_traces(fig2.data + fig1.data)

    pxfig1.layout.xaxis.title = "Time"
    pxfig1.layout.yaxis.title = "Mutation Prevalence (%)"
    pxfig1.layout.yaxis1.type = selected_y_scale
    pxfig1.layout.yaxis2.title = "Total Number of Sequences"
    pxfig1.layout.update(title={
                            'text' : 'Mutation prevalence over time',
                            'x':0.5,
                            'xanchor': 'center'}, 
                        template = 'plotly_white')
    
    piefig1 = px.pie(filtered_piedf1, 
                    names=piedict.keys(),
                    values=piedict.values())
    
    piefig1.update_traces(hovertemplate='<b>Gene: %{label}</b><br>Percentage: %{percent}<br>Count: %{value}',
                          textfont_size=20)
    piefig1.layout.update(title={
                            'text' : 'Mutations Grouped by Genes',
                            'x':0.5,
                            'xanchor': 'center'}, 
                        template = 'plotly_white')

    #Returns error to user if no sequences are available
    if grapherror is True:
        grapherrortext = "Graph error: No sequences available!"
    else:
        grapherrortext = ""
        
    return pxfig1, piefig1, [html.Option(value=word) for word in mutsuggestlist], [{'label': x, 'value': x} for x in genelistfinal], [html.Option(value=word) for word in countrylist], countryerror, grapherrortext, muterror

if __name__ == '__main__':
    app.run_server()