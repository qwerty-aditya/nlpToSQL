from google.colab import auth as google_auth
google_auth.authenticate_user()
import vertexai
from vertexai.language_models import TextGenerationModel
from constants import parameters
import sqlite3
from sqlalchemy import text
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import Float
from sqlalchemy import String
from sqlalchemy import DateTime
from flask import Flask, session, request, jsonify
from flask_ngrok import run_with_ngrok

app = Flask(__name__)
run_with_ngrok(app)

#init vertex ai
vertexai.init(project="knowledge-minor", location="us-central1")
model = TextGenerationModel.from_pretrained("text-bison")

def nlp_to_query(query):
  response = model.predict(
      f"""You are an expert in writing SQL queries.
      Table Description:
      Table name = insights
      This table has the following columns
      \'id\': Identification number for the sales,
      \'State\': State of the deal,
      \'Territory\': Territory id of the dealer,
      \'Sales_District\': District where the sales happened,
      \'Tier\': Tier of the sales,
      \'Total_Pot\': Total pot,
      \'DCBL_Pot\': DCBL pot,
      \'UT_Pot\': UT pot,
      \'Ambuja_Pot\': Ambuja pot,
      \'ACC_Pot\': Acc pot,
      \'Shri_Pot\': Shri pot,
      \'Nuvoco_Pot\': Nuvoco pot,
      \'All_Oth_Pot\': other pot,
      \'L1_Plant\': Plant id L1,
      \'Dist_L1_Plant\': Distance of plant id L1 ,
      \'PTPK\',
      \'DD_Vol\',
      \'WSP_DCFT\',
      \'LYTD_Vol\': Last Year Volume,
      \'YTD_Vol\': This Year Volume,
      \'YTD_Deliveries\': Total delivery of the year
      Given the table description, your task is to only write correct sql queries for the input.

  Write sql query for: Which district has the highest growth?
  output: SELECT Sales_District FROM insights GROUP BY Sales_District ORDER BY (SUM(YTD_Vol)-SUM(LYTD_Vol)) DESC;

  Write sql query for: Which dealers out of the top 25% volume contributing dealers have grown since last year?
  output: SELECT State, Territory, Sales_District, SUM(YTD_Vol) AS Total_Volume FROM insights GROUP BY State, Territory, Sales_District HAVING (SUM(YTD_Vol)-SUM(LYTD_Vol))>0 ORDER BY Total_Volume DESC LIMIT 25;

  Write sql query for: Which dealers in tier 1 and 2 have degrown
  output: SELECT State, Territory, Sales_District, SUM(YTD_Vol) AS Total_Volume FROM insights WHERE Tier IN (1,2) GROUP BY State, Territory, Sales_District HAVING (SUM(YTD_Vol)-SUM(LYTD_Vol))<0 ORDER BY Total_Volume DESC;

  Write sql query for: {query}
  """,
      **parameters
  )
  colone_idx = response.text.find(';')
  fornmated_query_str = response.text[9:colone_idx+1]
  query = text(fornmated_query_str)
  output = []
  with engine.connect() as conn:
    results = conn.execute(query)
    output = pd.DataFrame(results.all())
  return fornmated_query_str, output


def create_sql_db():
    file_name = "DataForInsight.xlsx"
    output = 'output.xlsx'
    engine = create_engine('sqlite://', echo=False)
    df = pd.read_excel(file_name, sheet_name = 'Counters')
    list_ = df.columns
    list_r = []
    for i in list_:
        list_r.append(i.replace(' ','_'))
    df.columns = list_r
    list_dates_str = []
    for i in range(df.shape[0]):
    if type(df['OTD_[h:m:s]'].iloc[i]) == datetime.datetime:
        list_dates_str.append(df['OTD_[h:m:s]'].iloc[i].strftime("%H:%M:%S"))
    elif type(df['OTD_[h:m:s]'].iloc[i]) == datetime.time:
        list_dates_str.append(df['OTD_[h:m:s]'].iloc[i].strftime("%H:%M:%S"))
    else:
        list_dates_str.append(None)
    df['OTD_[h:m:s]'] = list_dates_str
    df['OTD_[h:m:s]'] = pd.to_datetime(df['OTD_[h:m:s]'])
    column_to_data_map = {}
    for i in df.columns:
    val = ""
    if df[i].dtype == 'O':
        val = String
    else:
        val = Float
    column_to_data_map[i] = val
    column_to_data_map['OTD_[h:m:s]'] = DateTime
    df.to_sql('insights', engine, if_exists='replace', index=False, dtype=column_to_data_map)

# API ENDPOINTS

@app.route("/")
def test():
    #create_sql_db()
    return "created the sql db"

@app.route("/")
def get_query():
    input_query = request.args.get("user_input")
    return input_query

if __name__ == '__main__':
    app.run()