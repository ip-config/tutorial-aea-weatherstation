import base64
import hashlib
import binascii


from fetchai.ledger.api import TokenApi, TransactionApi
from fetchai.ledger.crypto import Identity

from oef.agents import OEFAgent
from typing import List
import os, sys

from codecs import encode

import json
import time
import struct
from struct import * 

from oef.proxy import  OEFProxy, PROPOSE_TYPES
from oef.query import Eq, Range, Constraint, Query, AttributeSchema, Distance 
from oef.schema import DataModel, Description , Location
from oef.messages import CFP_TYPES


import weather_station_dataModel
from weather_station_dataModel import WEATHER_STATION_DATAMODEL

import db_communication
from db_communication import Db_communication

import json
import datetime
 
class WeatherAgent(OEFAgent):
    
    def __init__(self, public_key: str, oef_addr: str, db_source : str, oef_port: int = 3333):
        super().__init__(public_key, oef_addr, oef_port)

        self.scheme = {}
        self.scheme['country'] = None
        self.scheme['city'] = None
        self.description = None
        self.db = db_communication.Db_communication(db_source)
        self.identity = Identity()
        self.tokens = TokenApi("ledger.economicagents.com", 80)
        self.balance = self.tokens.balance(self.identity.public_key)
        self.fetched_data = None
        self.price_per_row = 0.02
        self.totalPrice = 0

    def on_cfp(self, msg_id: int, dialogue_id: int, origin: str, target: int, query: CFP_TYPES):
        """Send a simple Propose to the sender of the CFP."""
        print("[{0}]: Received CFP from {1}".format(self.public_key, origin))

        print(query.constraints[0].constraint.values)

        self.fetched_data  = self.db.specific_dates(query.constraints[0].constraint.values[0], 
                                                    query.constraints[0].constraint.values[1])
        if len(self.fetched_data) >= 1 : 
            print(len(self.fetched_data))
            self.totalPrice = self.price_per_row * len(self.fetched_data)
            proposal = Description({"Rows" : len(self.fetched_data),
                                    "Price" : self.totalPrice })
            print("[{}]: Sending propose at price: {}".format(self.public_key, self.totalPrice))
            self.send_propose(msg_id + 1, dialogue_id, origin, target + 1, [proposal])
        else :
            #self.send_propose(msg_id + 1, dialogue_id, origin, target + 1, [])
            self.send_decline(msg_id + 1, dialogue_id, origin, target + 1)

    def on_accept(self, msg_id: int, dialogue_id: int, origin: str, target: int):
        """Once we received an Accept, send the requested data."""
        print("[{0}]: Received accept from {1}."
              .format(self.public_key, origin))

        command = {}
        command['Public_Key'] = binascii.hexlify(self.identity.public_key_bytes).decode()
        msg = json.dumps(command)
        self.send_message(0,dialogue_id, origin, msg.encode())

 
    def on_decline(self, msg_id: int, dialogue_id: int, origin: str, target: int):
        print("declined")
        

    def on_message(self, msg_id: int, dialogue_id: int, origin: str, content: bytes):
        data = json.loads(content.decode())

        if data['Command'] == "Executed" :
            correct_balance = self.balance + int(self.totalPrice)

            if correct_balance == self.tokens.balance(self.identity.public_key) :
                print("Success")
                self.balance = correct_balance
                print(self.balance)
                command = {}
                command['Command'] = "success"
                command['fetched_data'] = [] 
                
                for items in self.fetched_data :
                    dict_of_data = {}
                    dict_of_data['abs_pressure'] = items[0]
                    dict_of_data['delay'] = items[1]
                    dict_of_data['hum_in'] = items[2]
                    dict_of_data['hum_out'] = items[3]
                    dict_of_data['idx'] = time.ctime(int(items[4]))
                    dict_of_data['rain'] = items[5]
                    dict_of_data['temp_in'] = items[6]
                    dict_of_data['temp_out'] = items[7]
                    dict_of_data['wind_ave'] = items[8]
                    dict_of_data['wind_dir'] = items[9]
                    dict_of_data['wind_gust'] = items[10]
                    command['fetched_data'].append(dict_of_data)
                

                msg = json.dumps(command)
                print("Sending Data")
                self.send_message(0,dialogue_id,origin,msg.encode())
            else : 
                print("Fail")
                command = {}
                command['Command'] = "fail"
                msg = json.dumps(command)
                self.send_message(0,dialogue_id,origin,msg.encode())

 
if __name__ == '__main__':

    # sys arg fake or actual

    if len(sys.argv) < 3:
        sys.exit("Incorrect args - example : python3 weatherAgent.py 27 fake")

    else:
 
        # create agent and connect it to OEF
        server_agent = WeatherAgent("weather_station_{}".format(sys.argv[1]), oef_addr="oef.economicagents.com", db_source="fake", oef_port=3333)
        
        server_agent.scheme['country'] = "UK"
        server_agent.scheme['city'] = "Cambridge"

        server_agent.connect()
     
        # register a service on the OEF
        server_agent.description = Description(server_agent.scheme, weather_station_dataModel.WEATHER_STATION_DATAMODEL())
     
        server_agent.register_service(0,server_agent.description)
     
        # run the agent
        server_agent.run()
