from flask import Flask, render_template, redirect, request, url_for
import datetime
import json
import MySQLdb as mdb
from queries import *
import decimal

app = Flask(__name__)

## dd/mm/yyyy format
def getCurrentDate():
	return datetime.datetime.today()

start_of_billboard100_date = datetime.datetime(1955, 1, 1)
con = mdb.connect(host='mysqlsrv.cs.tau.ac.il', db='DbMysql08', user='DbMysql08', passwd='DbMysql08')

# class for parsing Decimal for json format
# from https://stackoverflow.com/questions/1960516/python-json-serialize-a-decimal-object
class DecimalEncoder(json.JSONEncoder):
	def default(self, o):
		if isinstance(o, decimal.Decimal):
			return float(o)
		return super(DecimalEncoder, self).default(o)


#get result of MySQL query and convert it to json format.
def from_query_result_to_json(cur, isDecimal):
	row_headers=[x[0] for x in cur.description] # this will extract row headers
	rows = cur.fetchall()
	json_data=[]
	for row in rows:
		json_data.append(row)
	if isDecimal:
		return json.dumps(json_data, cls = DecimalEncoder)
	else:
		return json.dumps(json_data)


def query_best(json_query_parameters):
	artist_name = json_query_parameters['artistName']
	source_country = json_query_parameters['country']
	start_date = json_query_parameters['start_date']
	if start_date == '':
		start_date = start_of_billboard100_date
	end_date = json_query_parameters['end_date']
	if end_date == '':
		end_date = getCurrentDate()
	cur = con.cursor(mdb.cursors.DictCursor)
	# add option to select whether we want songs or artists or bonus queries
	return query_best_artists(cur, artist_name, source_country, start_date, end_date)


def query_best_artists(cur, artist_name, source_country, start_date, end_date):
	if source_country != '':
		cur.execute(queryTopArtistsOfCountryInTimeRange, {'start_date': start_date, 'end_date': start_date})
	else:
		cur.execute(queryTopArtistsInTimeRange, {'start_date': start_date, 'end_date': start_date})
	return from_query_result_to_json(cur, False)


def query_best_songs(cur, artist_name, source_country, start_date, end_date):
	if source_country != '':
		cur.execute(queryTopSongsOfCountryInTimeRange, {'start_date': start_date, 'end_date': start_date})
	else:
		if artist_name != '':
			cur.execute(queryTopOfArtist, {'start_date': start_date, 'end_date': start_date})
		else:
			cur.execute(queryTopSongsInTimeRange, {'start_date': start_date, 'end_date': start_date})
	return from_query_result_to_json(cur, False)


'''def query_best2():
	if request.method == 'GET':
		return render_template('welcome.html')
	elif request.method == 'POST':
		cur = con.cursor(mdb.cursors.DictCursor)
		artist_name = request.form['name']
		source_country = request.form['country']
		start_date = request.form['fromDate']
		end_date = request.form['untilDate']
		if source_country != '':
			if start_date == '':
				query = queryTopArtistsOfCountryAllTime
			else:
				query = queryTopArtistsOfCountryInTimeRange
			cur.execute(query)
			json_query_result = from_query_result_to_json(cur)
			return redirect(url_for('best-artists', country=source_country))'''


def HearMeRoar():
	cur = con.cursor(mdb.cursors.DictCursor)
	cur.execute(querySongsOnMe, {'artist_name': 'Shakira'})
	json_query_result = from_query_result_to_json(cur, False)
	print json_query_result


def GrowingStrong():
	cur = con.cursor(mdb.cursors.DictCursor)
	cur.execute(queryGrowingStrong, {'current_year': getCurrentDate().year})
	json_query_result = from_query_result_to_json(cur, True)
	print json_query_result


#simple query for sanity check
def test():
	cur = con.cursor(mdb.cursors.DictCursor)
	cur.execute('SELECT Artist.artist_name FROM Artist LIMIT 50;')
	json_query_result = from_query_result_to_json(cur, False)
	print json_query_result


@app.route('/template')
def use_query_best_template():
	return render_template('web_no_style.html')\


@app.route('/')
def hello_world():
	return "In the game of music you either sing or you disappear!"


if __name__ == '__main__':
	#print query_best({"artistName" : '', "country" : '', "start_date" : datetime.datetime(2000, 1, 1), "end_date" : ''})
	print GrowingStrong()
	app.run(port=8888, host="0.0.0.0", debug=True)