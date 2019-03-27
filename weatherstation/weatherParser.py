import time
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import pywws
from pywws import livelog
import datetime
import pprint

#Checking if the database exists#

con = psycopg2.connect(dbname='postgres')
con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cur = con.cursor()
cur.execute("SELECT COUNT(*) = 0 FROM pg_catalog.pg_database WHERE datname = 'weather'")
not_exists_row = cur.fetchone()
not_exists = not_exists_row[0]
if not_exists:
    cur.execute('CREATE DATABASE weather')

cur.close()
con.commit()
con.close()

#################################

command = (''' CREATE TABLE IF NOT EXISTS data (
                                 abs_pressure REAL,
                                 delay REAL,
                                 hum_in REAL,
                                 hum_out REAL,
                                 idx TEXT,
                                 rain REAL,
                                 temp_in REAL,
                                 temp_out REAL,
                                 wind_ave REAL,
                                 wind_dir REAL,
                                 wind_gust REAL)''')


con = psycopg2.connect('dbname = weather')
con.autocommit = True
cur = con.cursor()
cur.execute(command)
cur.close()
con.commit()
if con is not None:
    con.close()



class Forecast():
    def addData(self,tagged_data) :
        con = psycopg2.connect('dbname = weather')
        con.autocommit = True
        cur = con.cursor()
        command = ('''INSERT INTO data(abs_pressure, 
                                       delay,
                                       hum_in,
                                       hum_out,
                                       idx,
                                       rain,
                                       temp_in,
                                       temp_out,
                                       wind_ave,
                                       wind_dir,
                                       wind_gust) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''')
        
        
        cur.execute(command,(tagged_data['abs_pressure'], 
                             tagged_data['delay'],
                             tagged_data['hum_in'], 
                             tagged_data['hum_out'],
                             datetime.datetime.now().strftime('%s'),
                             tagged_data['rain'],
                             tagged_data['temp_in'],
                             tagged_data['temp_out'],
                             tagged_data['wind_ave'],
                             tagged_data['wind_dir'],
                             tagged_data['wind_gust']))
        con.commit()
        cur.close()
        con.close()
        
        m_time = datetime.datetime.now().strftime('%s')
        print( m_time)
        print(time.ctime(int(m_time)))
        print(tagged_data['idx'])

        
    
    def main(self):

        ws = pywws.weatherstation.WeatherStation()
        for data, ptr ,logged in ws.live_data() :
            print(data)
            self.addData(data)
    
if __name__ == '__main__':
    a = Forecast()
    a.main()




