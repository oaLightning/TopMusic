from flask import Flask, render_template, redirect, request, url_for
import json
import datetime
from queries import *
import decimal

app = Flask(__name__)

## dd/mm/yyyy format
def getCurrentDate():
	return datetime.datetime.today()

start_of_billboard100_date = datetime.datetime(1955, 1, 1)

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


@app.route('/queryBest', methods=['POST', 'GET'])
def query_best():
	artist_name = request.form['artistName']
	source_country = request.form['country']
	start_date = request.form['start_date']
	if start_date == '':
		start_date = start_of_billboard100_date
	end_date = request.form['end_date']
	if end_date == '':
		end_date = getCurrentDate()
	result = \
		[
			{"song" : "Overprotected", "artist": "Britney Spears" },
			{"song" : "Waka waka", "artist": "Shakira" },
			{"song" : "Come Together", "artist": "The Beatles" },
			{"song" : "Woman", "artist": "John Lennon" },
			{"song" : "Imagine", "artist": "John Lennon" }
		]
	return render_template('web_no_style_results.html', col1_name='song', col2_name='artist', list_result=result)

@app.route('/')
@app.route('/web_no_style_template')
def use_best_template():
	return render_template('web_no_style_main.html')



if __name__ == '__main__':
	#print query_best({"artistName" : '', "country" : '', "start_date" : datetime.datetime(2000, 1, 1), "end_date" : ''})
	# print GrowingStrong()
	app.run(port=8888, host="localhost", debug=True)