from boto.kinesis.exceptions import ProvisionedThroughputExceededException
import sqlalchemy as db
from sqlalchemy import select, insert, MetaData, Table, Column, String, Float, Integer, exc as sa_exc
import datetime
import boto3
import time
import sys
import json


class Consumer:
    def __init__(self, consumer_id):

        self.kinesis=boto3.client('kinesis')
        self.consumer_id=str(consumer_id)
        self.poland_bbox = (49.0273953314, 54.8515359564, 14.0745211117,24.0299857927)
        
        self.database_credentials_path = "database_credentials.json"
        self.database_credentials = json.load(open(self.database_credentials_path, "r"))
        self.user = self.database_credentials["database"]["user"]
        self.password = self.database_credentials["database"]["password"]
        self.host = self.database_credentials["database"]["host"]
        self.port = self.database_credentials["database"]["port"]
        self.database = self.database_credentials["database"]["database"]
        
        self.engine = db.create_engine('postgresql://'+self.user+':'+self.password+'@'+self.host+':'+self.port+'/'+self.database)
        self.meta = MetaData()
        if not db.inspect(self.engine).has_table("airplanes"):
            print("Baza danych nie istnieje. Zostanie utworzona.")
            airplanes = Table("airplanes", self.meta,
            Column("airplane_id", Integer, primary_key=True),
            Column("ICAO",String(10)),
            Column("Timestamp", Float),
            Column("Latitude", Float),
            Column("Longitude", Float),
            Column("On_Ground", String(5)),
            Column("Velocity", Float))
            
            airplanes.create(self.engine)
            self.table = Table("airplanes", self.meta, autoload_with= self.engine)
        else:
            self.table = Table("airplanes", self.meta, autoload_with= self.engine)
            stmt = (
                self.table.delete()
            )	
            with self.engine.begin() as conn:
                conn.execute(stmt)
        
        self.update()

        
        
    def update_database(self, data):
        stmt = select(self.table.c.ICAO).where(self.table.c.ICAO == data[0])
        with self.engine.begin() as conn:	
            res = conn.execute(stmt)
                
            if(len(res.fetchall())>0):
                if(float(data[2])>=self.poland_bbox[0] and float(data[2])<=self.poland_bbox[1] and float(data[3]) >= self.poland_bbox[2] and float(data[3])<=self.poland_bbox[3]):
                
                    stmt = (
                        self.table.update().where(self.table.c.ICAO==data[0]).values(Timestamp = data[1], Latitude = data[2], Longitude = data[3], On_Ground = data[4], Velocity = data[5] )
                    )
                    with self.engine.begin() as conn:
                        conn.execute(stmt)        
                else:
                    stmt = (
                        self.table.delete().where(self.table.c.ICAO == data[0])
                    )	
                    with self.engine.begin() as conn:
                        conn.execute(stmt)
            else:
                if(float(data[2])>=self.poland_bbox[0] and float(data[2])<=self.poland_bbox[1] and float(data[3]) >= self.poland_bbox[2] and float(data[3])<=self.poland_bbox[3]):
                    stmt =	(
                        self.table.insert().
                        values(ICAO=data[0],Timestamp = data[1], Latitude= data[2], Longitude=data[3],
                        On_Ground= data[4], Velocity=data[5])
                    )
                    with self.engine.begin() as conn:
                        conn.execute(stmt)                
                   

    def update(self):
        response = self.kinesis.get_shard_iterator(StreamName="stream_0",ShardId="shardId-000000000000", ShardIteratorType="LATEST")
        next_iterator = response['ShardIterator']
        while True:
            try:
                response = self.kinesis.get_records(ShardIterator=next_iterator, Limit=1000)
                records = response['Records']
                if records:
                    for record in records:      
                        if record['PartitionKey']==self.consumer_id:
                            self.update_database([i for i in record['Data'].decode("utf-8").split(";")])
                    print()

                next_iterator = response['NextShardIterator']
                time.sleep(0.5)
            except ProvisionedThroughputExceededException:
                time.sleep(1)
                

if(len(sys.argv)>1):
    Consumer(sys.argv[1])
