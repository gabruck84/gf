import snscrape.modules.twitter as sntwitter
import pandas as pd
from jupyter_dash import JupyterDash
import re
from dash import Dash, dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import numpy as np
from pyvis.network import Network
import networkx as nx
import matplotlib.pyplot as plt
import time 

app = JupyterDash(__name__,  external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server


card1 = dbc.Card(
    [
        dbc.CardImg(src="https://i.ibb.co/m0rXh59/icone-perfil.png",  style={"width": "20vh", 'margin':'15px'}, top=True),
        dbc.CardBody(
            [
                html.H4("Redes Sociais", className="card-title"),
                html.P(
                    "Análise do Twitter.",
                    className="card-text",
                ),
                
                html.Div(
    [dbc.Label("O que você procura?"),dbc.Input(placeholder="Palavra Chave", type="text", id='input-on-submit')]),
                 html.Div(
    [dbc.Label("Quantidade de tweets?"),dbc.Input(placeholder="Número de tweets", type="text", id='input-on-submit2')]),
                dbc.Button('Pesquisar', id='submit-val',
            n_clicks=0,style={'margin':'10px'},),
                
                
                
        dbc.Spinner(html.Div(id="loading-output")),
                
            ]
        ),
    ], style={'height':'100vh'}
   
)





card2 = dbc.Card(
    dbc.CardBody(
        [
            html.H4("Tabela de dados", className="card-title"),
            html.H6(["Usuários únicos: ",html.Div(id='userunico')]),
            html.H6(["Reply: ",html.Div(id='reply')]),
            html.H6(["Original: ",html.Div(id='original')]),
            html.H6(["Retweet: ",html.Div(id='retweet')]),
              html.H6(["Progresso: ",html.Div(id='aguarde')]),
         

           
            html.P(dash_table.DataTable(
        id='computed-table', page_size=5, style_table={'height': 'auto', 'overflowY': 'auto'}, style_data={
        
        'height': 'auto'
        
    }
       )),
            
      
        
    
    
            
             dbc.Button('Download Excel',  id='btn_csv', n_clicks=0,style={'margin':'10px'}),  dcc.Download(id="download-dataframe-csv"), 
             dbc.Button('Download Rede', id='rede', n_clicks=0),  dcc.Download(id="redegephi")
            
            
        ], style={'height':'100vh'}
    ),  
)







row = html.Div( dbc.Row(
            [
                dbc.Col(html.Div(card1),width=4),
        
                dbc.Col(html.Div((card2)
       ),width=8),
            ]
        ),
    
)



    
app.layout = html.Div(row)






@app.callback(
    Output("loading-output", "children"),
    Output('computed-table', 'data'),
    Output('computed-table', 'columns'),
    Output('reply', 'children'),
     Output('original', 'children'),
    Output('retweet', 'children'),
     Output('userunico', 'children'),
    Input('submit-val', 'n_clicks'),
    [State('input-on-submit', 'value'),State('input-on-submit2', 'value')],
     prevent_initial_call=True

    
)
def update_output(n_clicks,a,b):
    
    query = a
    if b is not None:
        limit = int(b)
    elif b is None:
        limit=100
    tweets = []
 
    try: 
        print('Start crawling')
        for tweet in sntwitter.TwitterSearchScraper(query=query).get_items():
            if len(tweets) == limit:
                break
            else:
                if tweet.inReplyToUser is not None:
                    tweet_type = 'reply'
                    tweet_reply = re.findall(r'[/]\w+', str(tweet.inReplyToUser))[-1].replace('/','')
                elif tweet.quotedTweet is not None:
                    tweet_type = 'retweet'
                    tweet_reply = None
                else:
                    tweet_type = 'original'
                    tweet_reply = None
                tweets.append([
                           tweet.inReplyToUser,
                            tweet.quotedTweet,
                           tweet.renderedContent,
                           tweet_type,
                           tweet.user.username])
                
    except Exception as e:
        print(e)
        
    print('Finished')
    print('-----')
    
    df = pd.DataFrame(data=tweets, columns=[
                                        'inReplyToUser',
                                        'quoted',
                                
                                        'description',
                                        'tweet_type',
                                    
                                        'username'])
  
    df=df.astype(str)
    lista=[]
    for i in df['inReplyToUser']:
        lista.append(re.sub('https://twitter.com/',' ', i))
    
    df['inReplyToUser']= lista
  
    d=df.to_dict('records')
    c0=len(df['username'].unique())
    c1=len(df.loc[df['tweet_type'] == 'reply'])
    c2=len(df.loc[df['tweet_type'] == 'original'])
    c3=len(df.loc[df['tweet_type'] == 'retweet'])
    
   
    return  "Pronto", d, [{"name": i, "id": i} for i in df.columns],c1,c2,c3,c0
    
    
    
@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn_csv", "n_clicks"),
    State('computed-table', 'data'),
    prevent_initial_call=True
    
)
def func(n_clicks,data):
    V = pd.DataFrame(data)
    return dcc.send_data_frame(V.to_excel, "arquivo.xlsx")


@app.callback(
    Output("redegephi", "data"),
    Input("rede", "n_clicks"),
    State('computed-table', 'data'),
    prevent_initial_call=True)

def rede(n_clicks,data):
   
   
    if data is None:
        return data
    else:
       
        H = pd.DataFrame(data)
        
        df_reply = H[['inReplyToUser','username']][H['tweet_type'] == 'reply']
        
        
        relationship_df = pd.DataFrame(np.sort(df_reply.values, axis = 1), columns = ['from','to'])
        relationship_df['value'] = 1
        relationship_df.groupby(["from","to"], sort=False, as_index=False).sum()
        
       
        
        G = nx.from_pandas_edgelist(relationship_df, 
                            source = "from", 
                            target = "to", 
                            edge_attr = "value", 
                            create_using = nx.Graph())

        plt.figure(figsize=(10,10))
        pos = nx.kamada_kawai_layout(G)
        nx.draw(G, with_labels=True, node_color='skyblue', edge_cmap=plt.cm.Blues, pos = pos)
        plt.show()
        
        net = Network(notebook=True, width='1000px', height='700px', bgcolor='#222222', font_color='white')

        node_degree = dict(G.degree)
        nx.set_node_attributes(G, node_degree, 'size')

        net.from_nx(G)
       
        net.show('rede.html')
        
       
        
        
        
        
        return dcc.send_file('rede.html')
           




if __name__ == '__main__':
    app.run_server(mode='external', port=1230)

