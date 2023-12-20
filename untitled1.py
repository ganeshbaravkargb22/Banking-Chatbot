# Import required libraries
import dash
from dash import html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import mysql.connector
import pandas as pd
import pathlib
import textwrap
import google.generativeai as genai
import sqlalchemy
import pandas as pd

genai.configure(api_key='AIzaSyBMgiKtSBvpe9A5BnQB3akhKMDWqmeiOeQ')
model = genai.GenerativeModel('gemini-pro')

mydb = mysql.connector.connect( host="bankdb.mysql.database.azure.com", user="ganeshgb22", password="India.@22", database="bank")
db=mydb.cursor()

# engine = sqlalchemy.create_engine("mysql+pymysql://ganeshgb22:India.@22/@bankdb.mysql.database.azure.com/bank")

login_page=[
    dbc.NavbarSimple(
        brand="MAGICBUS  BANK  CHATBOT",
        color="primary",
        dark=True,
    ),
    dbc.Container(
        [
            html.H3("Login"),
            dbc.FormGroup(
                [
                    dbc.Label("Customer ID:", className="mt-3"),
                    dbc.Input(type="text", id="username", placeholder="Enter Customer ID", style={"width":"300px"}),
                    dbc.Label("Password:", className="mt-3"),
                    dbc.Input(type="password", id="password", placeholder="Enter Password",style={"width":"300px"}),
                    dbc.Button("Login", id='login-submit',n_clicks=0, color="primary", className="mt-3")
                ]
            )
        ], 
        className="p-5"
    )
]

global chattext
chattext=[html.Div([html.P('Hi, How can I help you?',style={'background':'#333333',"border-radius": "15px",'float':'left','margin-left':'7px','margin-top':'7px','padding':'10px'})],style={'width':'100%','display':'block'})]
# query='''SELECT DISTINCT Cit
# FROM customer
# WHERE CustomerID = 1'''
# db.execute(query)
# filtered_df=pd.DataFrame(db.fetchall())
# filtered_df = pd.read_sql_query(query, engine)
# T=html.Table(
#     # Header
#     [html.Tr([html.Th(col) for col in filtered_df.columns])]
#     +
#     # Body
#     [html.Tr([html.Td(filtered_df.iloc[i][col]) for col in filtered_df.columns]) for i in range(len(filtered_df))],
# style={'border': '1px solid black',  'textAlign': 'center'}
# )
# chattext.append(html.Div(html.Div([T],style={'background':'#999999',"border-radius": "5px",'float':'left','margin-left':'7px','margin-top':'7px','padding':'10px'}),style={'clear': 'both'}))




chat_page=[
  dbc.NavbarSimple(
    brand="MAGICBUS BANK CHATBOT",
    color="primary",
    dark=True,
  ),
  dbc.Container(
    [
      html.Div(id="textarea", children=chattext, style={"width": "100%", "height": "400px",'background':'#111111',"border-radius": "15px",'overflow-y': 'scroll'}),
      dbc.Input(type="text", id="query", placeholder="Enter Your Query",style={"width": "100%", "height": "50px","border-radius": "15px",'display':'inline-block'}),
      dbc.Button("Submit", id="chat-submit", color="primary",style={'margin-top':'5px','display':'inline-block',"border-radius": "15px"}),
    ], 
    className="p-4"
  )
]

# chattext=[html.Div(html.P('Hi, How can I help you?'),style={'background':'#999999',"border-radius": "5px",'float':'left'})]
# Create a Dash application instance
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

# Define the layout of the web application
global flag
flag='login'
app.layout = html.Div(id='UI',children=login_page)


@app.callback(
  Output('UI', 'children'),
  [Input('login-submit', 'n_clicks')],
  [dash.dependencies.State('username', 'value'),dash.dependencies.State('password', 'value')]
)
def validate_login(n_clicks, userid,passwd):
  global flag
  if flag=='login':
    global customer_id, password, firstname, lastname
    customer_id=userid
    password=passwd
    db.execute(f'''select * from Auth where customer_id={customer_id} and password='{password}' ''')
    u=db.fetchall()
    if len(u)==1:
      firstname=u[0][1]
      lastname=u[0][2]
      flag='chat'
      return chat_page
    else:
      # Display an error message if login fails
      return dbc.Alert("Invalid credentials. Please try again.", color="danger", style={"position": "absolute", "top": "20%", "left": "50%", "transform": "translate(-50%, -50%)"}), *login_page
  else:
    # Return the chat page if the login-submit button has been clicked
    return chat_page



@app.callback(
    [Output("textarea", "children"),Output("query", "value")],
    [Input("chat-submit", "n_clicks")],
    [State("query", "value"), State("textarea", "value")],
)
def update_textarea(n_clicks, question, text):
    global chattext
    if n_clicks is not None:
        try:
            greeting='''CONTEXT:The client who is asking the query has customer_id={} and its name is '{} {}'. The client has asked the query as '{}' 
                        INSTRUCTION: check if this is a query for customer care. answer in just "Yes" or "No" where "Yes" means he is asking for customer care number. No means he is not asking for customer care number'''
            
            response = model.generate_content(greeting.format(customer_id, firstname, lastname, question))
            if response.text=="Yes":
                response='+91-7666941195'
                chattext.append(html.Div([html.P(question,style={'background':'#1B4242',"border-radius": "15px",'float':'right','margin-right':'7px','margin-top':'7px','padding':'10px'})], style={'clear': 'both'}))
                chattext.append(html.Div([html.P(str(response),style={'background':'#333333',"border-radius": "15px",'float':'left','margin-left':'7px','margin-top':'7px','padding':'10px'})], style={'clear': 'both'}))
                return(chattext,'')
            else:
                greeting='''CONTEXT:The client who is asking the query has customer_id={} and its name is '{} {}'. The client has asked the query as '{}' 
                            INSTRUCTION: check if this is a greeting. answer in just "Yes" or "No" where "Yes" means he is greeting. No means he is not greeting, rather asking something'''
                
                response = model.generate_content(greeting.format(customer_id, firstname, lastname, question))
                if response.text=="Yes":
                    greeting='''The client whose name is '{}' has greeted you as {}. greet him back appropriately as client has greeted you directly and ask client how you can help him.
                                you response must have 1 greet only.
                                You response must have geeting only. must not have any supporing sentences like "Here are some ways you could greet the client back:"  '''
                    response = model.generate_content(greeting.format(firstname, question))
                    print(response.text)
                    chattext.append(html.Div([html.P(question,style={'background':'#1B4242',"border-radius": "15px",'float':'right','margin-right':'7px','margin-top':'7px','padding':'10px'})], style={'clear': 'both'}))
                    chattext.append(html.Div([html.P(str(response.text),style={'background':'#333333',"border-radius": "15px",'float':'left','margin-left':'7px','margin-top':'7px','padding':'10px'})], style={'clear': 'both'}))
                    return(chattext,'')
                else: 
                    verification='''The client who is asking the query has customer_id={} and its name is '{} {}'. The client has asked the query as '{}'
                     so does client is asking the query about its owns data or of someone else's data. answer in just "Yes" or "No" where "Yes" means he is asking query of self. No means he is asking for the data of some else persons details '''
                    response = model.generate_content(verification.format(customer_id, firstname, lastname, question))
                    if response.text=="Yes":
                        verification='''The client has account in the bank. The query asked by the custumer should be in regard to banking and his finances. The client has asked the query as '{}'
                                        so does client is asking the query regrds to his financial/bank account details. answer in just "Yes" or "No" where "Yes" means he is asking query about finances. "No" means he is asking non financial queries '''
                        response = model.generate_content(verification.format(question))
                        if response.text=="Yes":
                            prompt='''
                            CONTEXT: I have a database named "bank". This database has only one table named "customer".
                            Customer table has following columns. The descriptions of the columns are mentioned along with the name of the column in the format as <column name>:<description of the column> 
                                CustomerID: Customer id,
                                FirstName : First name of the customer,
                                LastName : Last name of the customer,
                                Phone_no : Phone number of the customer,
                                City : City in which customer resides,
                                Investment_type : Type of investment the customer has made in that bank. ex: FD, Mutual-funds etc
                                Investment_id : ID of the investment,
                                Start_date : Date when the investment was made,
                                End_date : maturity date of the investment,
                                Amount: investment amount by the customer,
                                kyc_status : status of kyc for customer successfully completed or painding,
                                IFSC_CODE : IFSC_CODE is the code of the bank in which customer has his account,
                                atmcard_expiryDate : Date when the atmcard of customer will be expired
                            QUESTION:{}. The data has to be figured out from customers table only for customer_id={}
                            '''
                            response = model.generate_content(prompt.format(question,customer_id))
                            query=str(response.text).split('sql')[-1].split(';')[0]
                            print(query)
                            # results = pd.read_sql_query(query, engine)
                            # print(results)
                            db.execute(query)
                            # results=db.fetchall()
                            chattext.append(html.Div([html.P(question,style={'background':'#1B4242',"border-radius": "15px",'float':'right','margin-right':'7px','margin-top':'7px','padding':'10px'})], style={'clear': 'both'}))
                            filtered_df=pd.DataFrame(db.fetchall())
                            # filtered_df = pd.read_sql_query(query, engine)
                            cols=list(filtered_df.columns)
                            filtered_df['SR.No']=range(1,1+len(filtered_df))
                            filtered_df=filtered_df[['SR.No']+cols]
                            T=html.Table(
                                # Header
                                [html.Tr([html.Th(col) for col in filtered_df.columns])]
                                +
                                # Body
                                [html.Tr([html.Td(filtered_df.iloc[i][col]) for col in filtered_df.columns]) for i in range(len(filtered_df))]
                            ,style={'textAlign': 'center'}
                            )
                            chattext.append(html.Div(html.Div([T],style={'background':'#333333',"border-radius": "15px",'float':'left','margin-left':'7px','margin-top':'7px','padding':'10px'}),style={'clear': 'both'}))
        
                            
                            
                            # chattext.append(html.Div([html.Table(pd.DataFrame(results),style={'background':'#999999',"border-radius": "5px",'float':'left','margin-left':'7px','margin-top':'7px','padding':'10px'})], style={'clear': 'both'}))
                            # chattext.append(html.Div([html.Table(dangerously_allow_html=True,style={'border': '1px solid black','margin-top': '10px','columns': [{'width': '100px'} ]},children=pd.DataFrame(results).to_html())]))
                            # chattext.append(html.Div([html.Table(pd.DataFrame(results).to_html(),style={'background':'#999999',"border-radius": "5px",'float':'left','margin-left':'7px','margin-top':'7px','padding':'10px'})], style={'clear': 'both'}))
                            # chattext.append(html.Div([html.P(question,style={'background':'#999900',"border-radius": "5px",'float':'right','margin-right':'7px','margin-top':'7px','padding':'10px'})],style={'width':'100%','display':'block'}))
                            # chattext.append(html.Div([html.P(str(pd.DataFrame(results)),style={'background':'#999999',"border-radius": "5px",'float':'left','margin-left':'7px','margin-top':'7px','padding':'10px'})],style={'width':'100%','display':'block'}))
        
                            # textarea_value='\n\nQuestion: \n'+question+'\n\nAnswer: \n'+str(pd.DataFrame(results))
                            return(chattext,'')
                        else:
                            chattext.append(html.Div([html.P(question,style={'background':'#1B4242',"border-radius": "15px",'float':'right','margin-right':'7px','margin-top':'7px','padding':'10px'})], style={'clear': 'both'}))
                            chattext.append(html.Div([html.P('Please ask banking related questions',style={'background':'#333333',"border-radius": "15px",'float':'left','margin-left':'7px','margin-top':'7px','padding':'10px'})], style={'clear': 'both'}))
                            return(chattext,'')
        
                    else:
                        chattext.append(html.Div([html.P(question,style={'background':'#1B4242',"border-radius": "15px",'float':'right','margin-right':'7px','margin-top':'7px','padding':'10px'})], style={'clear': 'both'}))
                        chattext.append(html.Div([html.P('Please ask questions of your accounts',style={'background':'#333333',"border-radius": "15px",'float':'left','margin-left':'7px','margin-top':'7px','padding':'10px'})], style={'clear': 'both'}))
                        return(chattext,'')
    
        except:
            pass
    else:
        # Return the current value of the dbc.Textarea component
        return (chattext,'')


# Run the Dash app
if __name__ == '__main__':
    app.run_server()
