
import base64
import hashlib
import binascii
from typing import List

from fetchai.ledger.api import TokenApi, TransactionApi
from fetchai.ledger.crypto import Identity
from oef.messages import PROPOSE_TYPES


from oef.agents import OEFAgent
from oef.schema import DataModel, AttributeSchema
from oef.query import Query, Constraint, Eq , NotEq ,Range,And


import weather_station_dataModel

import json
import datetime

import time


class ClientAgent(OEFAgent):
    """
    The class that defines the behaviour of the echo client agent.
    """
    def __init__(self, public_key: str, oef_addr: str, oef_port: int = 3333):
        super().__init__(public_key, oef_addr, oef_port)
        self.identity = Identity()
        self.txs = TransactionApi("ledger.economicagents.com" , 80)
        self.tokens = TokenApi("ledger.economicagents.com" , 80)
        print('Submitting wealth creation...')
        self.wait_for_tx(self.txs, self.tokens.wealth(self.identity.private_key_bytes, 1000))
        self.cost = 0
        self.pending_cfp = 0
        self.received_proposals = []
        self.received_declines = 0
    
    def wait_for_tx(self, txs: TransactionApi, tx: str):
        while True:
            if txs.status(tx) == "Executed":
                break
        time.sleep(1)  



    def on_message(self, msg_id: int, dialogue_id: int, origin: str, content: bytes):
        #print("Received message: origin={}, dialogue_id={}, content={}".format(origin, dialogue_id, content))
        data = json.loads(content.decode())
        #print(data)
        if "Public_Key" in data.keys():
            self.make_the_payment(data, origin, dialogue_id)
        if "Command" in data.keys() :
            if data['Command'] == "success" :
                for items in data['fetched_data'] :
                    #print(items)
                    pass
                #print(data['fetched_data'])
                self.stop()

            if "fail" in data.keys() :
                pass
                self.stop()
                

    def make_the_payment(self, data, origin,dialogue_id) :
        print("sending the correct amount")
        self.wait_for_tx(self.txs, self.tokens.transfer(self.identity.private_key_bytes,
                                               binascii.unhexlify(data['Public_Key'].encode()),
                                               self.cost))

        print("Sending executed command")
                
        command = {}
        command['Command'] = "Executed"

        print(self.tokens.balance(self.identity.public_key))
        msg = json.dumps(command)
        self.send_message(0,dialogue_id,origin,msg.encode())
       

    def on_search_result(self, search_id: int, agents: List[str]):
        """For every agent returned in the service search, send a CFP to obtain resources from them."""
        if len(agents) == 0:
            print("[{}]: No agent found. Stopping...".format(self.public_key))
            self.stop()
            return

        print("[{0}]: Agent found: {1}".format(self.public_key, agents))

        for agent in agents:
            
            print("[{0}]: Sending to agent {1}".format(self.public_key, agent))
            # we send a 'None' query, meaning "give me all the resources you can propose."
            query = Query([Constraint("Date", Range( ("20/3/2019","21/3/2019") ))])
            self.pending_cfp += 1
            self.send_cfp(1, 0, agent, 0, query)

    def on_propose(self, msg_id: int, dialogue_id: int, origin: str, target: int, proposals: PROPOSE_TYPES):
        """When we receive a Propose message, answer with an Accept."""
        print("[{0}]: Received propose from agent {1}".format(self.public_key, origin))
       #print(dialogue_id)
       
        for i,p in enumerate(proposals):
            self.received_proposals.append({"agent" : origin, 
                                            "proposal":p.values})
        received_cfp = len(self.received_proposals) + self.received_declines 
        print(received_cfp)
        print(received_cfp == self.pending_cfp)
        print(self.pending_cfp)


        if received_cfp == self.pending_cfp :
            print("I am here")
            if len( self.received_proposals) >= 1 :
                self.received_proposals = sorted(self.received_proposals, key= lambda i : int(i['proposal']['Price']))
            
                
                for i in range(1 , len(self.received_proposals)) :
                    print("Sending decline !")
                    self.send_decline(msg_id,dialogue_id, self.received_proposals[i]['agent'],msg_id + 1)
               
                self.cost = int(self.received_proposals[0]['proposal']['Price'])    
                self.send_accept(msg_id,dialogue_id,self.received_proposals[0]['agent'],msg_id + 1)
            else : 
                print("They don't have data")
                self.stop()

    def on_decline(self, msg_id: int, dialogue_id: int, origin: str, target: int) :
        print("Received a decline!")
        self.received_declines += 1

if __name__ == '__main__':

    # define an OEF Agent
    client_agent = ClientAgent("agent_client", oef_addr="oef.economicagents.com", oef_port=3333)

    # connect it to the OEF Node
    client_agent.connect()

    # query OEF for DataService providers
    echo_query = Query([Constraint("country", Eq("UK"))],
                        weather_station_dataModel.WEATHER_STATION_DATAMODEL())

    print("Make search to the OEF")
    client_agent.search_services(0, echo_query)

    # wait for events
    client_agent.run()
