import psycopg2
import datetime
import time


class Db_communication():

	source = None
	def __init__(self, source):
		self.source = source

	def db_connection(self):
		con = None
		print (self.source)
		if self.source is "fake":
			con = psycopg2.connect('dbname =  weather_fake')
		else:
			con = psycopg2.connect('dbname =  weather')

		con.autocommit = True
		return con


	def specific_dates (self, start, end) :

		con = self.db_connection()
		cur = con.cursor()
		
		if type(start) is str :
			start = datetime.datetime.strptime(start,'%d/%m/%Y')
			start = start.strftime('%s')
		if type(end) is str :
			end = datetime.datetime.strptime(end,'%d/%m/%Y')
			end = end.strftime('%s')
		command = "SELECT * FROM data WHERE idx BETWEEN %s::Text AND %s::Text"
		cur.execute(command, (float(start),float(end),))
		data = cur.fetchall()

		cur.close()
		con.close()
		return data


if __name__ == '__main__':
	a = Db_communication()
	date1 = "10/12/2018"
	date2 = "9/12/2018"
	test = a.specific_dates(date2, date1)