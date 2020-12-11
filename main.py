from flask import Flask, json, request
from pymongo import MongoClient


USER = "grupo35"
PASS = "grupo35"
DATABASE = "grupo35"

URL = f"mongodb://{USER}:{PASS}@gray.ing.puc.cl/{DATABASE}?authSource=admin"
client = MongoClient(URL)

MESSAGE_KEYS = ['message', 'sender', 'receptant', 'lat', 'long', 'date']

TEXT_SEARCH_KEYS = ['desired', 'required', 'forbidden', 'userId']


# Base de datos del grupo
db = client["grupo35"]

# Seleccionamos la collección de usuarios y mensajes
usuarios = db.usuarios
mensajes = db.mensajes

#Iniciamos la aplicación de flask
app = Flask(__name__)

@app.route("/")
def home():
    '''
    Inicio
    '''
    return "<h1>Probando pagina</h1>"

#Esta consulta incluye la consulta 1 y 5
@app.route("/messages", methods =['GET'])
def get_conversation():
    '''
    Obtiene todos los mensajes entre id1 e id2 (en ambos sentidos)
    '''
    id1 = int(request.args.get('id1',False))
    id2 = int(request.args.get('id2',False))
    if id1 + id2 > 0:
        conv = list(db.mensajes.find({ "$or": [{"$and":[{"sender":id1},{"receptant":id2}]},{"$and":[{"sender":id2},{"receptant":id1}]}]},{"_id":0}))
    else:
        conv = list(mensajes.find({}, {"_id": 0}))
    
    if conv != []:
        return json.jsonify(conv)
    
    else:
        return json.jsonify({"Error:": "No hay mensajes entre el usuario ID: %s y el usuario ID: %s" % (id1, id2)})


#Supuesto: solo se probaran :id del tipo INT (en caso contrario se cae la página)
@app.route("/messages/<int:mid>")
def get_message(mid):
    '''
    Obtiene el mensaje de id entregada
    '''
    msje = list(mensajes.find({"mid":mid}, {"_id": 0}))

    if msje != []:
        return json.jsonify(msje)

    else:
        return json.jsonify({"Error": "El mensaje con id: %s no existe" % mid})

@app.route("/users")
def get_users():
    '''
    Obtiene todos los usuarios
    '''
    users = list(usuarios.find({}, {"_id": 0}))

    return json.jsonify(users)

@app.route("/users/<int:uid>")
def get_user(uid):
    us = list(usuarios.find({"uid":uid}, {"_id": 0}))

    me = list(mensajes.find({"sender":uid}, {"_id": 0}))

    for u in us:
        u["mensajes"] = me

    if us != []:
        return json.jsonify(us)

    else:
        return json.jsonify({"Error:": "El usuario con ID: %s no existe" % uid})



#Metodo POST
@app.route("/messages", methods=['POST'])
def create_message():

    dic_data = request.json
    keys = dic_data.keys()
    falta = []
    for k in MESSAGE_KEYS:
        if not k in keys:
            falta.append(k)
    
    if falta == []:
        mid_list = []
        ms = list(mensajes.find({}, {"_id": 0}))
        for m in ms:
            mid_list.append(m["mid"])
        mid_list.sort()
        mid_n = mid_list[-1] + 1
        data = {key: request.json[key] for key in MESSAGE_KEYS}
        data["mid"] = mid_n
        result = mensajes.insert_one(data)
        return json.jsonify({"success": True})

    else:
        return json.jsonify({"Error": "Falta(n) la(s) llave(s): %s  " % (falta)})


#Metodo DELETE
@app.route("/message/<int:mid>", methods=['DELETE'])
def delete_message(mid):
    '''
    Elimina el usuario de id entregada
    '''
    msje = list(mensajes.find({"mid":mid}, {"_id": 0}))
    if msje != []:
        mensajes.remove({"mid": mid})
        return json.jsonify({"success": True})

    else:
        return json.jsonify({"Error": "El mensaje con id: %s no existe" % mid})


#TEXT SEARCH
@app.route("/text-search", methods=['GET'])
# VER CASO INPUT VACIO VS RESULTADO CONSULTA VACIO
def busqueda_texto():
    no_dicc = True
    if request.data:
        # mensajes.create_Index({ "message" : "text" },{ "default_language": "none" })
        l_ms = []
        no_dicc = False
        data = request.json
        if "desired" in data: 
            desired = data["desired"] 
            
            if len(desired) == 0:
                #ds = list(mensajes.find({},{"_id":0}))
                ds = []
            else:    
                desired = " ".join(desired)
                ds = list(mensajes.find({"$text": {"$search": desired}}, {"_id": 0,  "score": { "$meta": "textScore" } }).sort([("score", { "$meta": "textScore" })]))            

            
            
            l_ms = ds

        if "required" in data:
            required = data['required']

            if len(required) == 0:
                #ts = list(mensajes.find({},{"_id":0}))
                ts = []
            else:
                texto = ""
                for element in required:
                    elemento = f'\"{element}\"'
                    texto = texto + elemento
                ts  = list(mensajes.find({"$text": {"$search": texto}},{"_id":0}))

            
            l_ms.extend(ts)


            # l_ms = set(l_ms)


        if "forbidden" in data:
            forbidden = data['forbidden']
            
            # asumo que si forbidden esta vacio no se eliminan palabras
            if len(forbidden) == 0:
                #l_ms = list(mensajes.find({},{"_id":0}))
                pass
            elif len(l_ms) == 0:
                forbidden = " ".join(forbidden)
                l_ms = list(mensajes.find({},{"_id":0}))
                # busca los mensajes que no queremos y los almacena en la lista "l_ms_malos"
                l_dic_malos= list(mensajes.find({"$text": {"$search": forbidden}},{"_id":0}))
                l_ms_malos = []
                for dic_ms in l_dic_malos:
                    l_ms_malos.append(dic_ms["message"])
                
                l_ms_buenos = []
                # seleciona los mensajes buenos
                for ms in l_ms:
                    if ms["message"] not in l_ms_malos:
                        l_ms_buenos.append(ms)

                l_ms = l_ms_buenos
        

            elif len(l_ms) > 0:

                forbidden = " ".join(forbidden)

                # busca los mensajes que no queremos y los almacena en la lista "l_ms_malos"
                l_dic_malos= list(mensajes.find({"$text": {"$search": forbidden}},{"_id":0}))
                l_ms_malos = []
                for dic_ms in l_dic_malos:
                    l_ms_malos.append(dic_ms["message"])
                
                if "desired" not in data and "required" not in data:
                    l_ms = mensajes.find({},{"_id":0})

                l_ms_buenos = []
                # seleciona los mensajes buenos
                for ms in l_ms:
                    if ms["message"] not in l_ms_malos:
                        l_ms_buenos.append(ms)

                l_ms = l_ms_buenos

        
        if "userId" in data:
            userId = data['userId']
            
            #if len(userId)==0:
            #    ts = list(mensajes.find({},{"_id":0}))
            #else:
            ts = list(mensajes.find({"sender":userId},{"_id": 0}))

            if "desired" not in data and "required" not in data and "forbidden"not in data:
                l_ms = mensajes.find({},{"_id":0})

            l_ms_user = []
            for dic_user in ts:
                if dic_user in l_ms:
                    l_ms_user.append(dic_user)
            
            l_ms = l_ms_user
        
        if l_ms == []:
            l_ms= list(mensajes.find({}, {"_id": 0}))
        if "desired" not in data and "required" not in data and "forbidden" not in data and "userId" not in data:

            ## DICCIONARIO VACIO, POR LO QUE NO HAY RESTRICCIONES Y SE RETORNAN TODOS LOS MENSAJES
            l_ms= list(mensajes.find({}, {"_id": 0}))


        return json.jsonify(l_ms)

    elif no_dicc == True:
        ## NO HAY DICCIONARIO, POR LO QUE SE RETORNA TODOS LOS MENSAJES 
        msjs = list(mensajes.find({}, {"_id": 0}))
        return json.jsonify(msjs)
if __name__ == "__main__":
    app.run(debug=True)