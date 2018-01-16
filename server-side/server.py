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
def from_query_result_to_json(cur, row_headers, isDecimal):
        rows = cur.fetchall()
        json_data=[]
        print "\n"
        for row in rows:
                print row
                json_data.append(dict(zip(row_headers,row)))
        print "\n"
        if isDecimal:
                return json.dumps(json_data, cls = DecimalEncoder)
        else:
                return json.dumps(json_data)


@app.route('/queryOnCountry', methods=['POST', 'GET'])
def query_on_country():
	source_country = request.form['country']
	start_date = request.form['start_date'][:10]
	if start_date == '':
		start_date = start_of_billboard100_date
	end_date = request.form['end_date'][:10]
	if end_date == '':
		end_date = getCurrentDate()
	query_option = request.form['select_bar']
	if source_country == '':
		return render_template('web_no_style_error.html',
                                       msg='You need to enter a country name before pressing submit')
	cur = con.cursor(mdb.cursors.DictCursor)
	if query_option == 'Top Songs':
                col2 = 'Song'
		cur.execute(queryTopSongsOfCountryInTimeRange,
                            {'country':source_country, 'start_date': start_date, 'end_date': start_date})
	elif query_option == 'Top Singers':
                col2 = 'Artist'
		cur.execute(queryTopArtistsOfCountryInTimeRange,
                            {'country': source_country, 'start_date': start_date, 'end_date': start_date})
	else:
		# query_option == 'Patriotic Songs'
		col2 = 'Song'
		cur.execute(querySongsOnCountry,
                            {'country': source_country, 'start_date': start_date, 'end_date': start_date})
	row_headers=[x[0] for x in cur.description] # this will extract row headers
	# result = from_query_result_to_json(cur, row_headers, False)
	result = cur.fetchall()
	rows = cur.rowcount
	print "rows = " + str(rows) + " col1 = 'country" + " col2 = " + col2 + "\n" + "\n" + "\n"
        return render_template('web_no_style_results.html', num_of_rows=rows,
                               col1_name='country', col2_name=col2, list_result=result)


@app.route('/queryOnArtist', methods=['POST', 'GET'])
def query_on_artist():
	artist_name = request.form['artistName']
	print "artistName = " + artist_name +"\n\n\\n"
	start_date = request.form['start_date'][:10]
	if start_date == '':
		start_date = start_of_billboard100_date
	end_date = request.form['end_date'][:10]
	if end_date == '':
		end_date = getCurrentDate()
	query_option = request.form['select_bar']
	if artist_name == '':
		return render_template('web_no_style_error.html',
                                       msg='You need to enter an artist name before pressing submit')
	cur = con.cursor(mdb.cursors.DictCursor)
	if query_option == 'Top Songs':
                col2 = 'Song'
                #cur.execute(queryTopOfArtistTest)
                cur.execute(queryTopOfArtist, {'artist_name':'Shakira', 'start_date': '1980-01-01', 'end_date': '2018-01-01'})
		#cur.execute(queryTopOfArtist,
                #            {'artist_name':artist_name, 'start_date': start_date, 'end_date': start_date})
	elif query_option == 'Best Year':
                col2 = 'Year'
		cur.execute(queryBestYears,
                            {'artist_name': artist_name, 'start_date': start_date, 'end_date': start_date})
	else:
		# query_option == 'Self adored Songs'
		col2 = 'Song'
		cur.execute(querySongsOnMe, {'artist_name': artist_name, 'start_date': start_date, 'end_date': start_date})
	row_headers=[x[0] for x in cur.description] # this will extract row headers
	#result = from_query_result_to_json(cur, row_headers, False)
	result = cur.fetchall()
	rows = cur.rowcount
	print "rows = " + str(rows) + " col1 = Artist" + " col2 = " + col2 + "\n" + "\n" + "\n"
        return render_template('web_no_style_results.html', num_of_rows=rows,
                               col1_name='Artist', col2_name=col2, list_result=result)


@app.route('/queryTop100', methods=['POST', 'GET'])
def query_top_100():
	start_date = request.form['start_date'][:10]
	if start_date == '':
		start_date = start_of_billboard100_date
	end_date = request.form['end_date'][:10]
	if end_date == '':
		end_date = getCurrentDate()
	query_option = request.form['select_bar']
	cur = con.cursor(mdb.cursors.DictCursor)
	if query_option == 'Songs':
		cur.execute(queryTopSongsInTimeRange, {'start_date': start_date, 'end_date': start_date})
		col2 = 'Song'
	else:
		# query_option == 'Singers'
		cur.execute(queryTopArtistsInTimeRange, {'start_date': start_date, 'end_date': start_date})
		col1 = 'Srtist'
	row_headers=[x[0] for x in cur.description] # this will extract row headers
	#result = from_query_result_to_json(cur, row_headers, False)
	result = cur.fetchall()
	rows = cur.rowcount
	print "rows = " + str(rows) + " col1 = " + col1 + " col2 = Score" + "\n" + "\n" + "\n"
	return render_template('web_no_style_results.html', num_of_rows=rows,
                               col1_name=col1, col2_name='Score', list_result=result)


@app.route('/queryTopOfTheWorld', methods=['POST', 'GET'])
def query_top_of_the_world():
	year = request.form['year']
	if year == '':
		year = getCurrentDate().year
	cur = con.cursor(mdb.cursors.DictCursor)
	cur.execute(queryAtTheTopOfTheGame, {'year':year})
	row_headers=[x[0] for x in cur.description] # this will extract row headers
        # result = from_query_result_to_json(cur, row_headers, False)
	result = cur.fetchall()
	rows = cur.rowcount
	return render_template('web_no_style_results.html', num_of_rows=rows,
                               col1_name=row_headers[0], col2_name=row_headers[1], list_result=result)


#simple query for sanity check
def test():
	cur = con.cursor(mdb.cursors.DictCursor)
	cur.execute('SELECT Artist.artist_name Artist.source_country FROM Artist LIMIT 50;')
	row_headers=[x[0] for x in cur.description] # this will extract row headers
        #result = from_query_result_to_json(cur, row_headers, False)
	result = cur.fetchall()
	rows = cur.rowcount
	return render_template('web_no_style_results.html', num_of_rows=rows, col1_name='artist', col2_name='source_country_id', list_result=result)

@app.route('/country_search', methods=['POST', 'GET'])
def use_country_search_template():
	return render_template('country_search.html')

@app.route('/artist_search', methods=['POST', 'GET'])
def use_artist_search_template():
	return render_template('artist_search.html')

@app.route('/top_100', methods=['POST', 'GET'])
def use_top_100_template():
	return render_template('top_100.html')

@app.route('/', methods=['POST', 'GET'])
@app.route('/main_page', methods=['POST', 'GET'])
def use_best_template():
	return render_template('main_page.html')\

@app.route('/error', methods=['POST', 'GET'])
def use_error_template():
	return render_template('web_no_style_error.html', msg='blah')\


if __name__ == '__main__':
	app.run(port=8888, host="localhost", debug=True)
