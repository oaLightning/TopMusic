# -*- coding: utf-8 -*-
from flask import Flask, render_template, redirect, request, url_for
import datetime
import json
import os
os.environ['PYTHON_EGG_CACHE'] = "./python_eggs"
import MySQLdb as mdb
from queries import *
import decimal
from filler import extract_billboard_charts

app = Flask(__name__)
app.debug = True
#app.config['SERVER_NAME'] = 'topmusic:40663'

## dd/mm/yyyy format
def getCurrentDate():
	return str(datetime.date.today())

date_1970_01_31 = str(datetime.date(1970, 12, 31))
con = mdb.connect(host='mysqlsrv.cs.tau.ac.il', db='DbMysql08', user='DbMysql08', passwd='DbMysql08')


@app.route('/queryOnCountry', methods=['POST', 'GET'])
def query_on_country():
	source_country = request.form['country']
	start_date = request.form['start_date'][:10]
	if start_date == '':
		start_date = date_1970_01_31
	end_date = request.form['end_date'][:10]
	if end_date == '':
		end_date = getCurrentDate()
	query_option = request.form['select_bar']
	if source_country == '':
		return render_template('error_or_empty_res.html',
							   msg='You need to enter a country name before pressing submit')
	# update count search for country
	cur = con.cursor(mdb.cursors.DictCursor)
	cur.execute(updateSearchCountCountry, {'country': source_country})
	# user query
	cur = con.cursor(mdb.cursors.DictCursor)
	if query_option == 'Top Songs':
		col2 = 'Song'
		cur.execute(queryTopSongsOfCountryInTimeRange,
                            {'country':source_country, 'start_date': start_date, 'end_date': end_date})
	elif query_option == 'Top Singers':
		col2 = 'Score'
		cur.execute(queryTopArtistsOfCountryInTimeRange,
                            {'country': source_country, 'start_date': start_date, 'end_date': end_date})
	else:
		# query_option == 'Patriotic Songs'
		col2 = 'Song'
		cur.execute(querySongsOnCountry,
                            {'country': source_country, 'start_date': start_date, 'end_date': end_date})
	result = cur.fetchall()
	rows = cur.rowcount
	if rows == 0:
		return render_template('error_or_empty_res.html',
							   msg='Couldn\'t find any results for country = ' + source_country + '. Please try again!')
	return render_template('web_table_result.html', num_of_rows=rows,
                               col1_name='Artist', col2_name=col2, list_result=result)


@app.route('/queryOnArtist', methods=['POST', 'GET'])
def query_on_artist():
	artist_name = request.form['artistName']
	start_date = request.form['start_date'][:10]
	if start_date == '':
		start_date = date_1970_01_31
	end_date = request.form['end_date'][:10]
	if end_date == '':
		end_date = getCurrentDate()
	query_option = request.form['select_bar']
	if artist_name == '':
		return render_template('error_or_empty_res.html',
                                       msg='You need to enter an artist name before pressing submit')
	# update count search for artist
	cur = con.cursor(mdb.cursors.DictCursor)
	cur.execute(updateSearchCountArtist, {'artist_name': artist_name})
	# user query
	# cur = con.cursor(mdb.cursors.DictCursor)
	if query_option == 'Top Songs':
		col2 = 'Song'
		cur.execute(queryTopOfArtist,
                            {'artist_name':artist_name, 'start_date': start_date, 'end_date': end_date})
	elif query_option == 'Best Year':
		col2 = 'Year'
		cur.execute(queryBestYears,
                            {'artist_name': artist_name, 'start_date': start_date, 'end_date': end_date})
	else:
		# query_option == 'Self adored Songs'
		col2 = 'Song'
		cur.execute(querySongsOnMe,
                            {'artist_name': artist_name, 'start_date': start_date, 'end_date': end_date})
	result = cur.fetchall()
	rows = cur.rowcount
	if rows == 0:
		return render_template('error_or_empty_res.html',
                                       msg='Couldn\'t find any results. for artist = ' + artist_name + '. Please try again!')
	return render_template('web_table_result.html', num_of_rows=rows,
						   col1_name='Artist', col2_name=col2, list_result=result)


@app.route('/queryTop100', methods=['POST', 'GET'])
def query_top_100():
	start_date = request.form['start_date'][:10]
	if start_date == '':
		start_date = date_1970_01_31
	end_date = request.form['end_date'][:10]
	if end_date == '':
		end_date = getCurrentDate()
	query_option = request.form['select_bar']
	print "start_date = " + start_date + ", end_date = " + end_date + "\n\n"
	cur = con.cursor(mdb.cursors.DictCursor)
	if query_option == 'Songs':
		cur.execute(queryTopSongsInTimeRange, {'start_date': start_date, 'end_date': end_date})
		col1 = 'Artist'
		col2 = 'Song'
	else:
		# query_option == 'Singers'
		cur.execute(queryTopArtistsInTimeRange, {'start_date': start_date, 'end_date': end_date})
		col1 = 'Artist'
		col2 = 'Score'
	result = cur.fetchall()
	rows = cur.rowcount
	if rows == 0:
		return render_template('error_or_empty_res.html',
                                       msg='Couldn\'t find any results. Please try again!')        
	print "rows = " + str(rows) + "\n"
	return render_template('web_table_result.html', num_of_rows=rows,
                               col1_name=col1, col2_name=col2, list_result=result)


@app.route('/queryTopOfTheWorld', methods=['POST', 'GET'])
def query_top_of_the_world():
	year = request.form['year']
	if year == '':
		year = getCurrentDate().year
	cur = con.cursor(mdb.cursors.DictCursor)
	cur.execute(queryAtTheTopOfTheGame, {'year':year})
	row_headers=[x[0] for x in cur.description] # this will extract row headers
	result = cur.fetchall()
	rows = cur.rowcount
	if rows == 0:
		return render_template('error_or_empty_res.html',
                                       msg='Couldn\'t find any results. Please try again!')        
	return render_template('web_table_result.html', num_of_rows=rows,
                               col1_name=row_headers[0], col2_name=row_headers[1], list_result=result)


@app.route('/update_vote', methods=['POST', 'GET'])
def update_vote():
	artist_name = request.form['artistName']
	user_score = request.form['select_bar']
	if artist_name == '':
		return render_template('error_or_empty_res.html',
							   msg='You need to enter an artist name before pressing Vote')
	cur = con.cursor(mdb.cursors.DictCursor)
	cur.execute(updatePopularityScore, {'artist_name' : artist_name, 'user_score' : vote})
	result = cur.fetchall()
	rows = cur.rowcount
	if rows == 0:
		return render_template('error_or_empty_res.html',
							   msg='Couldn\'t find any artist by the name ' + artist_name + ' . Please try again!')
	return render_template('error_or_empty_res.html',
                                       msg='Thank you for voting!')


@app.route('/show_statistics', methods=['POST', 'GET'])
def show_statistics():
	chosen_stats = request.form['select_bar']
	cur = con.cursor(mdb.cursors.DictCursor)
	if chosen_stats == "searches_of_artists":
		cur.execute(queryMostSearchedArtists)
	if chosen_stats == "searches_of_countries":
		cur.execute(queryMostSearchedCountries)
	if chosen_stats == "user_votes":
		cur.execute(queryMostPopularArtists)
	result = cur.fetchall()
	rows = cur.rowcount
	return render_template('statistics.html',
						   num_of_rows=rows, list_result=result)


@app.route('/', methods=['POST', 'GET'])
@app.route('/main_page', methods=['POST', 'GET'])
def use_best_template():
	return render_template('main_page.html')
               
@app.route('/country_search', methods=['POST', 'GET'])
def use_country_search_template():
	return render_template('country_search.html')

@app.route('/artist_search', methods=['POST', 'GET'])
def use_artist_search_template():
	return render_template('artist_search.html')

@app.route('/top_100', methods=['POST', 'GET'])
def use_top_100_template():
	return render_template('top_100.html')

@app.route('/error', methods=['POST', 'GET'])
def use_error_template():
	return render_template('error_or_empty_res.html', msg='blah')

@app.route('/get_latest_chart', methods=['POST', 'GET'])
def get_latest_chart():
	return render_template('get_latest_chart.html', msg='blah')

@app.route('/vote', methods=['POST', 'GET'])
def vote():
	return render_template('vote.html')

@app.route('/stats', methods=['POST', 'GET'])
def stats():
	return render_template('statistics_request.html')

if __name__ == '__main__':
	app.run(port=40663, host="0.0.0.0", debug=True)
