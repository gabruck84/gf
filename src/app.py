#!/usr/bin/env python
# coding: utf-8

# In[1]:


import snscrape.modules.twitter as sntwitter
import pandas as pd
from jupyter_dash import JupyterDash
from dash import Dash, dcc, html, Input, Output, State, dash_table



app = JupyterDash(__name__)
server = app.server



    
app.layout = html.Div([

    
    
    html.Div(dcc.Input(id='input-on-submit', type='text',placeholder='Palavra Chave')),
    html.Div(dcc.Input(id='input-on-submit2', type='text',placeholder='Número de Tweets')),
    html.Button('Pesquisar', id='submit-val', n_clicks=0),
    html.Div(id='container-button-basic'),
    dash_table.DataTable(
        id='computed-table', fixed_rows={'headers': True}, page_size=10,style_data={
        'width': '50px',
        'maxWidth': '50px',
        'minWidth': '50px',
    }
       ),
    html.Button("Download CSV", id="btn_csv",n_clicks=0),
    dcc.Download(id="download-dataframe-csv")
   
    
       
])

[]

@app.callback(
    Output('computed-table', 'data'),
    Output('computed-table', 'columns'),
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
                           tweet.renderedContent])
                           
                
    except Exception as e:
        print(e)
        
    print('Finished')
    print('-----')
    
  
    df = pd.DataFrame(data=tweets, columns=['Texto'])
    c=df
    d=df.to_dict('records')
 
    if c is None:
        return [{}], []
    elif c is not None:
        return d, [{"name": i, "id": i} for i in df.columns]
    
    
@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn_csv", "n_clicks"),
    State('computed-table', 'data'),
    prevent_initial_call=True
    
)
def func(n_clicks,data):
    V = pd.DataFrame(data)
    return dcc.send_data_frame(V.to_csv, "{}.csv".format('arquivo'))


if __name__ == '__main__':
    app.run_server(mode='external', port=800)

    


# In[ ]:




