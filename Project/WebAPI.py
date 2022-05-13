from crypt import methods
import json
from flask import Flask,Response, jsonify, request
import werkzeug.exceptions
import MySQLdb

app = Flask(__name__)

@app.route('/',methods=["GET"])
def hello_world():
    user = request.args.get("user")
    print(user)
    return jsonify({'message':'Hello world'})
@app.route('/company',methods=["GET"])
def fetch_company():
    secCode = request.args.get("code")
    try:
        conn:MySQLdb.connections.Connection = MySQLdb.connect(
            user = 'root',
            host = '127.0.0.1',
            port = 3306,
            db='companydb'
        )
        query = "SELECT * FROM company WHERE secCode = %s LIMIT 0:10"
        args = (secCode,)
        cursor:MySQLdb.cursors.Cursor = conn.cursor()
        cursor.execute(query=query,args=args)
        result = cursor.fetchone()
        cursor.close()
        conn.close()
    except:
        pass



@app.errorhandler(404)
def page_not_found(error:werkzeug.exceptions.HTTPException):
    return Response(response=json.dumps({'status':error.code,'message':error.description}),status=error.code,content_type="application/json;charset=utf-8")

if __name__ == "__main__":
    app.run(host='127.0.0.1',port=8888,debug=True)

    