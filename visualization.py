from flask import Flask, render_template, request
import sqlalchemy as db
from sqlalchemy import select, insert, MetaData, Table, Column, String, Float, Integer, exc as sa_exc
import json
app=Flask(__name__)

database_credentials_path = "database_credentials.json"
database_credentials = json.load(open(database_credentials_path, "r"))
user = database_credentials["database"]["user"]
password = database_credentials["database"]["password"]
host = database_credentials["database"]["host"]
port = database_credentials["database"]["port"]
database = database_credentials["database"]["database"]

engine = db.create_engine('postgresql://'+user+':'+password+'@'+host+':'+port+'/'+database)
meta = MetaData()

table = Table("airplanes", meta, autoload_with= engine)

@app.route('/')
def root():
    return render_template('index.html')

@app.get("/update")
def update():

    markers = []
    
    stmt = select(table)
    with engine.begin() as conn:	
        res = conn.execute(stmt)
        for airplane in(res.fetchall()):
            marker = [airplane[3], airplane[4],f'ICAO = {airplane[1]}, lat = {airplane[3]}, lon = {airplane[4]}, On Ground = {airplane[5]}, Velocity = {airplane[6]}']
            markers.append(marker)
    
    return markers

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
