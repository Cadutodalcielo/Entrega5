# Entrega 4: Desarrollo de una Web API utilizando MongoDB y Flask

## Integrantes:
* Felipe Aceituno
* Maximiliano Aguirre
* Christian La Regla

### Instrucciones para ejecución

Para el correcto uso, primero en la terminal debe (ubicado en la carpeta):

- correr 'pipenv shell'
- correr 'pipenv install'
- correr 'python main.py'

En ese momento se podrá realizar consultas a la API y esta funcionará.

Si hubiese algún error lo básico que se utilizó fue:

- Python 3.7
- flask
- pymongo


### Implementaciones

TODOS LOS ERRORES SON NOTIFICADOS AL USUARIO MEDIANTE UN JSON

* **Ruta GET**:
    * **Ruta /messages**: Esta ruta implementa las consultas 1 y 5. En primer lugar utilizando la función "request.args.get" permite obtener los mensajes entre 2 usuarios utilizando la ruta con la disposición: /messages?id1=57&id2=35. Esta misma ruta al incluir unicamente /messages, muestra todos los mensajes y sus atributos.

    * **Ruta /messages/:id**: Acepta unicamente id del tipo INT y devuelve el mensaje con mid = id señalado. En caso de no existir mensaje con tal id, se retorna un mensaje señalado que el mensaje no existe.

    * **Ruta /users**: Devuelve todos los usuarios de la base de datos en formato JSON.

    * **Ruta /users/:id**: Acepta unicamente id del tipo INT y devuelve el usuario con uid = id señalado. Además se agrega al diccionario del usuario una llave "mensajes" cuyo valor es una lista de todos los mensajes enviados por el usuario. En caso de no existir usuario con tal id, se retorna un mensaje señalado que el usuario no existe.

    
* **Ruta GET: text-search**: Cumple con los recorridos a partir de los criterios puestos en el body del request: desired, required, forbidden y userID. 


* **Ruta POST**: 
    * **Ruta /messages**: Se recibe un mensaje mediante un JSON en el body de la request. Primero se analiza si los parametros ingresados son validos, comparandolos con los parametros señalados en MESSAGE_KEYS.
                          En caso de incluir todos los parametros, se genera un mid nuevo a partir del mid más alto registrado siendo el nuevo mid = mid_mas_alto + 1. Luego se inserta este nuevo mensaje en los mensajes.
                          En caso de no incluir todos los parametros, se retorna un mensaje señalando los parametros faltantes.


* **Ruta DELETE**: 
    * **Ruta /message/:id**: Esta ruta solo acepta id del type INT. En caso de existir un mensaje con el mid señalado, se elimina de la base de datos. En caso contrario se retorna el mensaje: ""El mensaje con id: (id indicada) no existe".
    
