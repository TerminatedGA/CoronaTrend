import plotly.express as px
from plotly.subplots import make_subplots
import natsort
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
from collections import Counter
from github import Github

first = True

hrstyledict = dict(zip(['borderColor', 'margin', 'marginLeft', 'width'], ['#828282', 15, '-4%', '104%']))

index_html = open('assets/index.html', 'r')

repo = Github().get_repo("TerminatedGA/CoronaTrend")
commits = repo.get_commits(path='GISAID-Dataframes')
lastupdated = commits[0].commit.committer.date

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
                #className="g-0",
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
                 children=[html.Div(id='graph-error-container',
                                    children='', 
                                    style={'color': 'red', 'fontSize': 10}),
                           html.Div(id='last-updated',
                                    children='Last updated: ' + str(lastupdated) + ' (UTC +0)',
                                    style={'textAlign': 'left'}),
                           html.Div(id='total-sequences',
                                    children='Total sequences (after filtering): ' + "{:,}".format(pd.read_pickle('GISAID-Dataframes/metadata.pickle', compression = "gzip")[1]),
                                    style={'textAlign': 'left'}),
                           dcc.Interval(id='last-updated-interval',
                                        interval=10*60*1000, # in milliseconds
                                        n_intervals=0),
                           dcc.Tabs([
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
                               "2. Sequenced regions with ambiguous bases (such as N) are treated as having no mutations."])]),
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
                                            'top': '0vh',
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
                     options=[{'label': x, 'value': x} for x in pd.read_pickle('GISAID-Dataframes/metadata.pickle', compression = "gzip")[0]],
                     value="BA.4",
                     clearable=False),
        dcc.Interval(id='lineage-dropdown-interval',
                     interval=10*60*1000, # in milliseconds
                     n_intervals=0),
        html.Hr(style=hrstyledict),
        html.Div('Country  / Region:', 
                 style={'color': 'black', 'fontSize': 15}),
        dcc.Input(id='country-input',
                  type='text',
                  value='',
                  list="country-suggestion"),
        html.Div(id='country-error-container',
                 children='', 
                 style={'color': 'red', 'fontSize': 10}),
        html.Hr(style=hrstyledict),
        html.Div('Amino Acid Mutation:', 
                 style={'color': 'black', 'fontSize': 15}),
        dcc.Input(id="mut-input", 
                  type="text", 
                  list='mut-suggestion'),
        html.Div(id='mut-error-container',
                 children='', 
                 style={'color': 'red', 'fontSize': 10}),
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
        dcc.Dropdown(
            id='total-dropdown',
            options=[{'label': x, 'value': x} for x in [0, 10, 100, 1000]],
            value=100,
            clearable=False),
        html.Hr(style=hrstyledict),
        html.Div([html.Div(children='Minimum increase in prevalence: (%)',
                           id='change-slider-container',
                 style={'display': 'inline'}),
        dcc.Input(id='change-input',
                  type='number',
                  value=10,
                  style={'display': 'inline'})]),
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
        html.Div(children='Minimum inital prevalence:',
                 id='init-slider-container-min'),
        dcc.Input(id='init-input-min',
                  type='number',
                  value=0),
        html.Div(children='Maximum inital prevalence:',
                 id='init-slider-container-max'),
        dcc.Input(id='init-input-max',
                  type='number',
                  value=100),
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
                          html.Button("Contact",
                                      id="contact-open-button",
                                      style={'display': 'inline-block', 
                                             'border': 'None', 
                                             'outline': 'None',
                                             'background': 'None',
                                             'paddingRight': '50px'},
                                      n_clicks=0),
                          html.A(html.Button('GitHub',
                                             id="github-link-button",
                                             style={'display': 'inline-block', 
                                                    'border': 'None', 
                                                    'outline': 'None',
                                                    'background': 'None',
                                                    'paddingRight': '50px'},
                                             n_clicks=0),
                                 href='https://github.com/TerminatedGA/CoronaTrend',
                                 target='_blank'),
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
        html.Div(children=["CoronaTrend aims to be a public resource from the Department of Microbiology, Li Ka Shing Faculty of Medicine, The University of Hong Kong, detailing the prevalence of different mutations across different lineages as time passes. ", 
                           html.Br(),
                           html.Br(),
                           "Developers: Miss Chan Tze To (Lea), Mr. Jonathan Ip, Dr. Kelvin To"],
                 style={'paddingBottom': 30}),
        html.Div(children='GISAID Initiative',
                 style={'color': 'black', 
                        'fontSize': 26, 
                        'font-weight': 'bold', 
                        'paddingBottom': 20}),
        html.Div(children=["We gratefully acknowledge all data contributors, i.e. the Authors and their Originating laboratories responsible for obtaining the specimens, and their Submitting laboratories for generating the genetic sequence and metadata and sharing via the GISAID Initiative",
        				   html.Sup("1"),
        				   ", on which this research is based.",
                           html.Br(),
                           html.Br(),
                           html.Div([html.Div("1) Elbe, S., and Buckland-Merrett, G. (2017) Data, disease and diplomacy: GISAID’s innovative contribution to global health. Global Challenges, 1:33-46. DOI: ",
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
     style={"display": "none"}),
                           html.Div([
    html.Div([
        html.Div([html.Div('Contact',
                 style={'color': 'black', 
                        'fontSize': 26, 
                        'display':'inline', 
                        'font-weight': 'bold'}),
                 html.Button('✕', 
                            id='contact-close-button',
                            style={'float': 'right', 
                                   'border': 'None', 
                                   'outline': 'None',
                                   'background': 'None'})],
                 style={'paddingBottom': 20}),
        html.Div(children=["For enquiries on CoronaTrend, please email ",
                           dcc.Link("contact@coronatrend.live",
                                                target='_blank',
                                                href="mailto:contact@coronatrend.live"), 
                           ". We will get to you as soon as possible."],
                 style={'paddingBottom': 30})],
        className='modal-content')],
                id='contact-modal',
     className='modal',
     style={"display": "none"})])

app.layout = html.Div([
    html.Datalist(id='mut-suggestion', 
                  children=[html.Option(value=word) for word in []]),
    html.Datalist(id='country-suggestion', 
                  children=[html.Option(value=word) for word in []]),
    dcc.Store(id='side_click'),
    dcc.Location(id="url"),       
    navbar,
    html.Div(children=[content, sidebar],
             style={'width': '98.72vw'}),
    footer])

@app.callback(Output('last-updated', 'children'),
              [Input('last-updated-interval', 'n_intervals')])
def update_date(n):
    return 'Last updated: ' + str(lastupdated) + ' (UTC +0)'
    
@app.callback(Output('lineage-dropdown', 'options'),
              [Input('lineage-dropdown-interval', 'n_intervals')])
def update_date(n):
    return [{'label': x, 'value': x} for x in pd.read_pickle('GISAID-Dataframes/metadata.pickle', compression = "gzip")[0]]
    
@app.callback(Output('acknowledgement-modal', 'style'),
              [Input('acknowledgement-open-button', 'n_clicks'),
               Input('acknowledgement-close-button', 'n_clicks')])
def close_acknowledgement_modal(selected_open, selected_close):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'acknowledgement-open-button' in changed_id:
        return {"display": "block"}
    if 'acknowledgement-close-button' in changed_id:
        return {"display": "none"}
    
@app.callback(Output('contact-modal', 'style'),
              [Input('contact-open-button', 'n_clicks'),
               Input('contact-close-button', 'n_clicks')])
def close_contact_modal(selected_open, selected_close):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'contact-open-button' in changed_id:
        return {"display": "block"}
    if 'contact-close-button' in changed_id:
        return {"display": "none"}

@app.callback(
    [
        Output("filter-sidebar", "style"),
        Output("page-content", "style"),
        Output("side_click", "data"),
        Output("btn_sidebar", "children"),
    ],

    [Input("btn_sidebar", "n_clicks")],
    [State("side_click", "data")]
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
    [dash.dependencies.Output('change-input', 'value'),
     dash.dependencies.Output('change-slider', 'value')],
    [dash.dependencies.Input('change-input', 'value'),
     dash.dependencies.Input('change-slider', 'value')]
)
def sync_change_value(input_value, slider_value):
    input_value_update = False
    if input_value is None:
        input_value = 10
        input_value_update = True
    
    if input_value_update is True:
        input_value_output = input_value
    else:
        input_value_output = dash.no_update
    
    if input_value == slider_value:
        return input_value_output, dash.no_update

    if dash.callback_context.triggered[0]['prop_id'] == 'change-input.value':
        return input_value_output, input_value
    else:
        return slider_value, dash.no_update

@app.callback(
    [dash.dependencies.Output('init-input-min', 'value'),
     dash.dependencies.Output('init-input-max', 'value'),
     dash.dependencies.Output('init-slider', 'value')],
    [dash.dependencies.Input('init-input-min', 'value'),
     dash.dependencies.Input('init-input-max', 'value'),
     dash.dependencies.Input('init-slider', 'value')]
)
def sync_init_value(input_value_min, input_value_max, slider_value):
    input_value_min_update = False
    input_value_max_update = False
        #Returns default value is input is None
    if input_value_min is None:
        input_value_min = 0
        input_value_min_update = True
    if input_value_max is None:
        input_value_max = 100
        input_value_max_update = True

    #Swap min and max value if min value is larger than max value
    if input_value_max < input_value_min:
        temp = input_value_min
        input_value_min = input_value_max
        input_value_max = temp
        input_value_min_update = True
        input_value_max_update = True
        
    if input_value_min_update is True:
        input_value_min_output = input_value_min
    else:
        input_value_min_output = dash.no_update
        
    if input_value_max_update is True:
        input_value_max_output = input_value_max
    else:
        input_value_max_output = dash.no_update
    
    if [input_value_min, input_value_max] == slider_value:
        return input_value_min_output, input_value_max_output, dash.no_update

    if dash.callback_context.triggered[0]['prop_id'] in ['init-input-min.value', 'init-input-max.value']:
        return input_value_min_output, input_value_max_output, [input_value_min, input_value_max]
    else:
        return slider_value[0], slider_value[1], dash.no_update

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
     Input('lineage-dropdown', 'value'), 
     Input('y-scale', 'value'),
     Input('country-input', 'value'),
     Input('total-dropdown', 'value')])
def multiple_output(selected_change_slider, 
                    selected_change_radio, 
                    selected_init, 
                    selected_gene, 
                    search_mut, 
                    selected_lineage, 
                    selected_y_scale,
                    search_country,
                    selected_total):
#Update figure with user selection
    #Check if graph has error
    grapherror = False
    
    #Defaults
    if search_country == "":
        search_country = 'All'

    #Updates country search bar results
    global first
    if first == True:
        global prevcountry
        global prevcountry1
        global countrylist
        global prevlineage
        global prevlineage1
        global prevtotal1
        url3 = 'GISAID-Dataframes/{}/{}/{}_metadata_Mintotal{}.pickle'.format(selected_lineage, selected_total, selected_lineage, selected_total)
        prevlineage = selected_lineage
        prevtotal1 = selected_total
        metadata = pd.read_pickle(url3, compression = "gzip")
        countrylist = metadata[0]
        if len(countrylist) == 0:
            grapherror = True
            print("oops")
        prevcountry = "All"
        prevcountry1 = search_country
        prevlineage1 = selected_lineage
        countryerror = ""
    else:
        if selected_lineage != prevlineage or selected_total != prevtotal1:
            url3 = 'GISAID-Dataframes/{}/{}/{}_metadata_Mintotal{}.pickle'.format(selected_lineage, selected_total, selected_lineage, selected_total)
            prevlineage = selected_lineage
            metadata = pd.read_pickle(url3, compression = "gzip")
            countrylist = metadata[0]
            if len(countrylist) == 0:
                grapherror = True
                print("oops")
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
    if [first == True or prevtotal1 != selected_total or prevlineage1 != selected_lineage or prevcountry1 != search_country] and grapherror == False:
        url1 = 'GISAID-Dataframes/{}/{}/{}_{}_1_Mintotal{}.feather'.format(selected_lineage, selected_total, selected_lineage, search_country.replace(" ", "_"), selected_total)
        url2 = 'GISAID-Dataframes/{}/{}/{}_{}_2_Mintotal{}.feather'.format(selected_lineage, selected_total, selected_lineage, search_country.replace(" ", "_"), selected_total)
        pxdf1original = pd.read_feather(url1)
        pxdf2original = pd.read_feather(url2)
        
        pxdf1 = pxdf1original.copy()
        pxdf2 = pxdf2original.copy()
        piedf1 = pxdf1.copy()

        totallist = list(pxdf2original["Totals"])
        periodlist1repeats = len(pxdf1original['AA Label'])
        genelistfinal = natsort.natsorted(set(pxdf1original['Gene']))
        genelistfinal.insert(0, "All")

        filtered_pxdf2 = pxdf2

        pxdf1["Percentage by period"] = pxdf1original["Percentage by period"]
        pxdf1 = pxdf1.explode('Percentage by period')
        if len(filtered_pxdf2['Periods']) == 0:
            pxdf1['Periods'] = None
            grapherror = True
        else:
            pxdf1['Periods'] = list(filtered_pxdf2['Periods']) * periodlist1repeats
        
        if first == True:
            first = False
        else:
            prevtotal1 = selected_total
            prevlineage1 = selected_lineage
            prevcountry1 = search_country
    
    if search_mut is not None:
        search_mutoriginal = search_mut
        search_mut = search_mut.upper()
        
    
    if selected_change_radio == 'all':
        changecolumn = 'Change in prevalence (All)(%)'
    else:
        changecolumn = 'Change in prevalence (Fin - Start)(%)'
    if search_mut is None or search_mut == '':
        searchmutline = (pxdf1['AA Label'] != None)
        searchmutpie = (piedf1['AA Label'] != None)
    else: 
        searchmutline = (pxdf1['AA Label'].str.contains(search_mut, case=False)) 
        searchmutpie = (piedf1['AA Label'].str.contains(search_mut, case=False)) 
    if selected_gene == "All":
        selectedgeneline = (pxdf1['Gene'] != None)
        selectedgenepie = (piedf1['Gene'] != None)
    else:
        selectedgeneline = (pxdf1['Gene'] == selected_gene)
        selectedgenepie = (piedf1['Gene'] == selected_gene)
        
        
 #Filters dataframe based on user selection       
    def filter_df(df, selectedgene, searchmut):
        return df[(df[changecolumn] >= selected_change_slider) & 
                           (df['Initial prevalence'] >= selected_init[0]) & 
                           (df['Initial prevalence'] <= selected_init[1]) &
                           selectedgene &
                           searchmut]
    
    filtered_pxdf1 = filter_df(pxdf1, selectedgeneline, searchmutline)
    
    filtered_piedf1 =  filter_df(piedf1, selectedgenepie, searchmutpie)

#Count the genes for each amino acid mutation
    piedict = Counter(filtered_piedf1['Gene'])

    #Create new mutation suggestion list for search bar
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
                color = 'AA Label',
                custom_data = [filtered_pxdf1['AA Label']])
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
