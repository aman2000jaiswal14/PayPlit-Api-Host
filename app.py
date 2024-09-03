import firebase_admin
from firebase_admin import credentials, firestore, db
from flask import Flask, request, jsonify
import os

config_path = os.path.join(os.path.dirname(__file__), 'config')
cred = credentials.Certificate(os.path.join(config_path, 'C:\\Users\\aman2\\Desktop\\F\\git_test\\config\\firebase.json'))
firebase_admin.initialize_app(cred,{"databaseURL": "https://kotlinfirebase-95de4-default-rtdb.firebaseio.com/"})

app = Flask(__name__)

'''
groups =>
{
    groupId : String
    groupName : String
    groupMembers : List<String> 
        :memberId : String
    groupItems : List<String> 
            :itemId : String
}

items =>
{
    itemId : String
    itemName : String
    itemGroupId : String
    itemDateUpdate: String
    itemTimeUpdate: String
    itemTotalAmount: String
    itemPayer : List<String>
        :memberId: String
    itemSpliter : List<String>
        :memberId : String
    itemSpliterValue : List<String>
        :itemValue: String
}

'''


@app.route("/",methods=["GET"])
def checkConnectivity():
    return "api running ok ",200

@app.route("/items",methods=["GET"])
def get_items():
    ref = db.reference("items")
    item_data = ref.get()
    items = []
    if(item_data != None):
        for item_id,item_info in item_data.items():
            item_dict = {'itemId' : item_info['itemId'],
                         'itemName' : item_info['itemName'],
                         'itemDateUpdate' : item_info['itemDateUpdate'],
                         'itemTimeUpdate' : item_info['itemTimeUpdate'],
                         'itemTotalAmount' : item_info['itemTotalAmount'],
                         'itemPayer' : item_info['itemPayer'],
                         'itemSpliter': item_info['itemSpliter'],
                         'itemSpliterValue' : item_info['itemSpliterValue'],
                         'itemGroupId' : item_info['itemGroupId']}
            items.append(item_dict)
    return jsonify(items),200

@app.route("/items/create",methods=["POST"])
def create_item():
    data = request.get_json()
    doc_ref = db.reference("items")
    item_dict = dict(data)
    if('itemName' in item_dict and
       'itemDateUpdate' in item_dict and
       'itemTimeUpdate' in item_dict and
       'itemTotalAmount' in item_dict and
       'itemPayer' in item_dict and
       'itemSpliter' in item_dict and
       'itemSpliterValue' in item_dict and
       'itemGroupId' in item_dict):
        new_doc_ref = doc_ref.push()
        data["itemId"] = new_doc_ref.key
        new_doc_ref.set(data)
        return "item created",201
    else:
        return "item key wrong",404

@app.route("/items/<item_id>",methods = ["GET"])
def get_item_by_id(item_id):
    try:
        return jsonify(db.reference(f"items").get()[item_id]),200
    except Exception as e:
        return f"Item Error : {e}",404

@app.route("/items/update-item",methods = ["PUT"])
def update_item():
    data = request.get_json()
    if("itemId" not in data):
        return "itemId Error",404
    itemId = data["itemId"]
    doc_ref = db.reference("items")
    item_data = doc_ref.get()
    try:
        if(itemId in item_data):
            if("itemName" in data):
                item_data[itemId]['itemName'] = data["itemName"]
            if("itemPayer" in data):
                item_data[itemId]['itemPayer'] = data["itemPayer"]
            if("itemTotalAmount" in data):
                item_data[itemId]['itemTotalAmount'] = data["itemTotalAmount"]
            if("itemSpliter" in data and "itemSpliter" in data and "itemSpliterValue" in data ):
                item_data[itemId]['itemSpliter'] = data["itemSpliter"]
                item_data[itemId]['itemSpliter'] = data["itemSpliter"]
                item_data[itemId]['itemSpliterValue'] = data["itemSpliterValue"]
                
            doc_ref.set(item_data)
            return "item updated",200
        else:
            return "item not found",404
    except Exception as e:
        return f"item update add error : {e}",404



@app.route("/items",methods=["DELETE"])
def delete_item():
    data = request.get_json()
    itemId = data['itemId']
    item_ref = db.reference(f'items/{itemId}')
    if(item_ref.get() is not None):
        item_ref.delete()
        return "deleted item succ",200
    else:
        return "item not found",404      
    

@app.route("/groups",methods=["GET"])
def get_groups():
    ref = db.reference("groups")
    groups_data = ref.get()
    groups = []
    if(groups_data != None):
        for group_id,group_info in groups_data.items():
            group_dict = {'groupId':group_id,'groupName': group_info['groupName']}
            if('groupMembers' in group_info):
                group_dict['groupMembers'] = group_info['groupMembers']
            else:
                group_dict['groupMembers'] = []
            
            if('groupItems' in group_info):
                group_dict['groupItems'] = group_info['groupItems']
            else:
                group_dict['groupItems'] = []
            
            groups.append(group_dict)
    
    return jsonify(groups),200


@app.route("/groups/<group_id>",methods=["GET","POST"])
def get_group(group_id):
    try:
        return jsonify(db.reference(f"groups").get()[group_id]),200
    except Exception as e:
        return f"Group Error : {e}",404
    
@app.route("/groups/members/<group_id>",methods=["GET","POST"])
def get_group_members(group_id):
    try:
        return jsonify(db.reference(f"groups").get()[group_id]['groupMembers']),200
    except Exception as e:
        return f"Group Error : {e}",404

@app.route("/groups/create",methods = ["POST"])
def create_group():
    data = request.get_json()
    doc_ref = db.reference("groups")
    new_doc_ref = doc_ref.push()
    data["groupId"] = new_doc_ref.key
    new_doc_ref.set(data)
    return "group created",201

@app.route("/groups/addMember/<group_id>",methods = ["PUT"])
def add_member_to_group(group_id):
    data = request.get_json()
    doc_ref = db.reference("groups")
    group_data = doc_ref.get()
    try:
        if(group_id in group_data):
            if('groupMembers' not in group_data[group_id]):
                group_data[group_id]['groupMembers'] = []
                
            group_data[group_id]['groupMembers'].append(data['memberId'])
            doc_ref.set(group_data)
            return "Member added",200
        else:
            return "group not found",404
    except Exception as e:
        return f"Memeber add error : {e}",404
    
@app.route("/groups/addItem/<group_id>",methods = ["PUT"])
def add_item_to_group(group_id):
    data = request.get_json()
    doc_ref = db.reference("groups")
    group_data = doc_ref.get()
    try:
        if(group_id in group_data):
            if('itemId' not in group_data[group_id]):
                group_data[group_id]['itemId'] = []
                
            group_data[group_id]['itemId'].append(data['itemId'])
            doc_ref.set(group_data)
            return "item added",200
    except Exception as e:
        return f"item add error : {e}",404
    
@app.route("/groups",methods=["DELETE"])
def delete_group():
    data = request.get_json()
    groupId = data['groupId']
    group_ref = db.reference(f'groups/{groupId}')
    if(group_ref.get() is not None):
        group_ref.delete()
        return "deleted group succ",200
    else:
        return "group not found",404       


@app.route("/users")
def get_users():
    ref = db.reference("users")
    users_data = ref.get()
    users = []
    if(users_data != None):
        for user_id, user_info in users_data.items():
            users.append({'user_id': user_id, 'user_name': user_info["user_name"],'user_email': user_info["user_email"]})

    return jsonify(users)
    
    
@app.route("/users/<user_id>",methods=["GET","POST"])
def get_user(user_id):
    user_data = db.reference('users').get()
    try:
        return jsonify(user_data[user_id]),200
    except Exception as e:
                
        print(f"the erorr is {e}")
        return f"the erorr is {e}",404
    

@app.route("/users/create",methods=["POST"])
def create_user():
    data = request.get_json()
    doc_ref =  db.reference('users')
    new_doc_ref = doc_ref.push()
    data["user_id"] = new_doc_ref.key
    new_doc_ref.set(data)
    return "user created",201

@app.route("/users",methods=["DELETE"])
def delete_user():
    data = request.get_json()
    user_id = data['user_id']
    user_ref = db.reference(f'users/{user_id}')
    if(user_ref.get() is not None):
        user_ref.delete()
        return "deleted succ",200
    else:
        return "not found",404
    try:
        if(user_ref.get() is not None):
            user_ref.delete()
        return "deleted succ",200
    except Exception as e:
                
        print(f"the erorr is {e}")
        return f"the erorr is {e}",404
    
if __name__ == "__main__":
    print(__name__)
    app.run("192.168.29.141",debug=True,port=7000)