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
                json_data.append(dict(zip(row_headers,row)))
        if isDecimal:
                return json.dumps(json_data, cls = DecimalEncoder)
        else:
                return json.dumps(json_data)


@app.route('/queryOnCountry', methods=['POST', 'GET'])
def query_on_country():
	source_country = request.form['country']
	start_date = request.form['start_date']
	if start_date == '':
		start_date = start_of_billboard100_date
	end_date = request.form['end_date']
	if end_date == '':
		end_date = getCurrentDate()
	query_option = request.form['query_option']
	cur = con.cursor(mdb.cursors.DictCursor)
	if query_option == 'topSongs':
		if source_country != '':
			cur.execute(queryTopSongsOfCountryInTimeRange, {'country':source_country, 'start_date': start_date, 'end_date': start_date})
		else:
			cur.execute(queryTopSongsInTimeRange, {'start_date': start_date, 'end_date': start_date})
	elif query_option == 'topArtists':
		if source_country != '':
			cur.execute(queryTopArtistsOfCountryInTimeRange, {'country': source_country, 'start_date': start_date, 'end_date': start_date})
		else:
			cur.execute(queryTopArtistsInTimeRange, {'start_date': start_date, 'end_date': start_date})
	else:
		# query_option == 'patrioticSongs'
		if source_country != '':
			cur.execute(querySongsOnMe, {'country': source_country, 'start_date': start_date, 'end_date': start_date})
		else:
			#error
			return render_template('web_no_style_error.html', msg='You must enter a country name before querying')
	result = from_query_result_to_json(cur, False)
	rows = cur.rowcount
	return render_template('web_no_style_results.html', num_of_rows=rows, col1_name='song', col2_name='artist', list_result=result)

@app.route('/queryOnArtist', methods=['POST', 'GET'])
def query_on_artist():
	artist_name = request.form['artistName']
	start_date = request.form['start_date']
	if start_date == '':
		start_date = start_of_billboard100_date
	end_date = request.form['end_date']
	if end_date == '':
		end_date = getCurrentDate()
	query_option = request.form['query_option']
	cur = con.cursor(mdb.cursors.DictCursor)
	if query_option == 'topSongs':
		if artist_name != '':
			cur.execute(queryTopOfArtist, {'artistName':artist_name, 'start_date': start_date, 'end_date': start_date})
		else:
			cur.execute(queryTopSongsInTimeRange, {'start_date': start_date, 'end_date': start_date})
	elif query_option == 'bestYear':
		if artist_name != '':
			cur.execute(queryGrowingStrong, {'artistName': artist_name, 'year': getCurrentDate().year})
		else:
			cur.execute(queryTopArtistsInTimeRange, {'start_date': start_date, 'end_date': start_date})
	else:
		# query_option == 'narcissisticSongs'
		if artist_name != '':
			cur.execute(querySongsOnMe, {'artistName': artist_name, 'start_date': start_date, 'end_date': start_date})
		else:
			#error
			return render_template('web_no_style_error.html', msg='You must enter an artist name before querying')
	result = from_query_result_to_json(cur, False)
	rows = cur.rowcount
	return render_template('web_no_style_results.html', num_of_rows=rows, col1_name='song', col2_name='artist', list_result=result)


@app.route('/queryTopOfTheWorld', methods=['POST', 'GET'])
def query_top_of_the_world():
	year = request.form['year']
	if year == '':
		year = getCurrentDate().year
	cur = con.cursor(mdb.cursors.DictCursor)
	cur.execute(queryAtTheTopOfTheGame, {'year':year})
	result = from_query_result_to_json(cur, False)
	rows = cur.rowcount
	return render_template('web_no_style_results.html', num_of_rows=rows, col1_name='artist', col2_name='year', list_result=result)


#simple query for sanity check
def test():
	cur = con.cursor(mdb.cursors.DictCursor)
	cur.execute('SELECT Artist.artist_name Artist.source_country FROM Artist LIMIT 50;')
	result = from_query_result_to_json(cur, False)
	rows = cur.rowcount
	return render_template('web_no_style_results.html', num_of_rows=rows, col1_name='artist', col2_name='source_country_id', list_result=result)


@app.route('/', methods=['POST', 'GET'])
@app.route('/web_no_style_main', methods=['POST', 'GET'])
def use_best_template():
	return render_template('web_no_style_main.html')\


if __name__ == '__main__':
	app.run(port=8883, host="localhost", debug=True)
