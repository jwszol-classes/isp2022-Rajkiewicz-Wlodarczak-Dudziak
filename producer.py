import time
import datetime
from datetime import timezone
import threading
import boto3
from opensky_api import OpenSkyApi
import json
import requests

class Producer(threading.Thread):
    def __init__(self):
        self.counter=0
        self.shards_number=3

        self.boto3 = boto3
        self.kinesis = self.boto3.client('kinesis')

        self.opensky_credentials_path = "opensky_credentials.json"
        self.opensky_credentials = json.load(open(self.opensky_credentials_path, "r"))
        self.username = self.opensky_credentials["opensky"]["username"]
        self.password = self.opensky_credentials["opensky"]["password"]

        self.buffer_poland_bbox = (48.0273953314, 55.8515359564, 13.0745211117,25.0299857927)

        super().__init__()
        self.update()
            
            
    def get_airplanes_data(self):
        opensky_api = OpenSkyApi(self.username, self.password)
        run = True
        while run:
            try:
                states =  opensky_api.get_states(bbox=self.buffer_poland_bbox)
            except requests.exceptions.ReadTimeout:
                print("Timeout. Repeat!")
            else:
                run = False

        return states
            
            
    def update(self):
        while True:
            airplane_data=self.get_airplanes_data()   

            if airplane_data is not None:   
                for s in airplane_data.states:
                    timestamp=datetime.datetime.now().timestamp()
                    data =f"{s.icao24};{timestamp};{s.latitude};{s.longitude};{s.on_ground};{s.velocity}"
                    self.kinesis.put_record(StreamName = "stream_0", Data = data, PartitionKey = str(self.counter%self.shards_number) )
                    self.counter += 1
                print()
            time.sleep(5)


if __name__ == "__main__":
    Producer = Producer()
