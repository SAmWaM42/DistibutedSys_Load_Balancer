import os
import flask as fl
app=fl.Flask(__name__)
server_id=os.getenv("SERVER_ID")
@app.route("/home",methods=['GET'])
def hello_world():
    response=fl.jsonify({
        "message":f"Hello from server [{server_id}]",
        "status":"successful" })
    return response,200
@app.route("/heartbeat",methods=['GET'])
def check_status():
    response=[]
    return fl.jsonify({"message":response}),200

if __name__=='__main__':
    app.run(host="0.0.0.0",port=5000,debug=True)