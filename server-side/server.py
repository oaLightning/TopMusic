from flask import Flask, render_template
import datetime
import json
import MySQLClient as mdb

con = mdb.connect('mysqlsrv.tau.ac.il', 'DbMysql08', 'DbMysql08', 'DbMysql08')
app = Flask(__name__)

@app.route('/')
def hello_world():
	return "Hello Music!"

# get result of MySQL query and convert it to json format.
def fromQueryResultToJson(cur)
	row_headers=[x[0] for x in cur.description] #this will extract row headers
	rows = cur.fetchall()
	json_data=[]
	for row in rows:
        json_data.append(dict(zip(row_headers,row)))
    return json.dumps(json_data)

@app.route('/beastie', methods=['POST', 'GET'])
def queryBeasties():
    if request.method == 'GET':
        return render_template('login.html')

    elif request.method == 'POST':
		cur = con.cursor(mdb.cursors.DictCursor)
        artistName = request.form['name']
        country = request.form['country']
		start_date = request.form['fromDate']
		end_date = request.form['untilDate']
        if artistName != '':
			if start_date == '':
				query = queryTopArtistsOfCountryAllTime
			else:
				query = queryTopArtistsOfCountryInTimeRange
			
			cur.execute(query)
			jsonQueryResult = fromQueryResultToJson(cur)
			# return something else
            return redirect(url_for('post_login', name=user))
        else:
			# return something else
            return redirect(url_for('post_login', name='fail'))

# also not sure about that			
if __name__ == '__main__':
	app.run(port=8888, host="0.0.0.0", debug=True)

# not sure what to do with those lines
# singer_name = raw_input(“Optional: Enter a singer name”)
# start_date = raw_input("Enter start date")
# end_date = raw_input("Enter end date")
	



