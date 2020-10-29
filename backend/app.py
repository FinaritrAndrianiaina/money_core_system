from flask import Flask,jsonify,request
from flask_socketio import SocketIO
import threading,time
import money_core as m
import random_generator,pytz,datetime
from json import loads
app = Flask(__name__)

db = m.DatabaseEngine('mongodb://127.0.0.1:27017','MoneyEngineDB_0')
transaction = db.get_collection('transactions')
accounts = db.get_collection('accounts')

def push_transaction(_t):
    sender = m.Account.find_with_oid(db, _t['sender_token'])
    receiver = m.Account.find_with_oid(db, _t['receiver_token'])
    
    try:
        accounts.update_one({
            "_id":sender.object_id
        },{
            "$inc": {"balance":-_t['amount']}
        })
        accounts.update_one({
            "_id": receiver.object_id
        }, {
            "$inc": {"balance": _t['amount']}
        })
        status = "commited"
    except:
        status= "canceled"

    transaction.update_one({
        "_id": _t['_id']
    },
        {"$set": {"status": status, "timecommited": datetime.datetime.utcnow().replace(tzinfo=pytz.utc)}}
    )

def transaction_executor():
    _t = None
    while True:
        time.sleep(0.1)
        _t = transaction.find_one({'status':'initial'})
        if _t:
            transaction.update_one({
                "_id": _t['_id']
            },
                {"$set": {"status": "pending"}}
            )
            threading.Thread(target= lambda: push_transaction(_t),daemon=True).start()
            _t = None

@app.route('/',methods=['GET','POST'])
def home():
    if request.method == 'GET':
        return 'hello'

@app.route('/new/transaction',methods=['POST'])
def new_transaction():
    if request.method == 'POST':
        data = loads(request.data)
        ret = m.Transaction.do_transacion(
            db,
            sender_token =data['sender_token'],
            receiver_token = data['receiver_token'],
            hash = data['signature'],
            amount = data['amount']
        )
        return jsonify(ret)

@app.route('/new/account')
def new():
    acc, priv_key = m.Account.create_account(db,0)
    data = acc.to_dict()
    data['priv_key'] = priv_key
    return jsonify(data)

@app.route('/get/account')
def get():
    token = request.args.get('token')
    if token:
        try:
            account = m.Account.find_account(db, token)
            return jsonify(account.to_dict())
        except Exception as e:
            print(e)
    return jsonify({
        "message": "unable to reach this token"
    })

@app.route('/get_key/')
def random():
    token = request.args.get('token')
    if token:
        try:
            key = m.Account.key_to_hash(db,token) 
            return jsonify({
                "message": key
            })
        except:
            pass
    return jsonify({
        "message" : "errors"
    })

@app.route('/transactions/list')
def transaction_list():
    token = request.args.get('token')
    account = m.Account.find_account(db,token)
    if token:
        try:
            data = transaction.find({'sender_token':account.object_id}) 
            return jsonify({
                "message": data
            })
        except:
            pass
    return jsonify({
        "message" : "errors"
    })

if __name__ == "__main__":
    threading.Thread(name="transaction_executor",target=transaction_executor,daemon=True).start()
    #threading.Thread(target=random_generator.rebuild_signature,daemon=True).start()
    app.run(debug=True)
