import sys
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# Implement CORS headers
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Function for returning all drinks from the `drink` table with the long format representation. 
def get_long_drinks():
    return [drink.long() for drink in Drink.query.all()]

# Function to check if a record exists in a table. 
def check_if_records_exists(model):
    if len(model) == 0:
        abort(404)

# Function to check if a drink exist on the `drink` table. 
def check_if_drink_exists(drink):
    if drink is None:
        abort(404)

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def drinks():
    drinks = Drink.query.order_by(Drink.id).all()
    check_if_records_exists(drinks)

    return jsonify({
        'success': True,
        'drinks': [drink.short() for drink in drinks]
    }), 200

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def show_drink(payload):
    drinks = get_long_drinks()
    check_if_records_exists(drinks)

    return jsonify({
        'success': True,
        'drinks': drinks
    }), 200

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    body = request.get_json()

    if 'title' and 'recipe' not in body:
        abort(422)

    try:
        drink = Drink(title=body.get("title", None),
                      recipe=json.dumps(body.get("recipe", None)))
        drink.insert()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })
    except:
        drink.rollback()
        print(sys.exc_info())
        abort(422)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_existing_drink(token, drink_id):

    try:

        existing_drink = Drink.query.filter(Drink.id==drink_id).one_or_none()

        if existing_drink is None:
            abort(404)

        body = request.get_json()

        drink_title = body.get("title", None)

        drink_recipe = json.dumps(body.get("recipe", None))

        existing_drink.title = drink_title

        existing_drink.recipe = drink_recipe

        existing_drink.update()

        drink_created = Drink.query.filter(Drink.title==drink_title).all()
        drink = [drinks.long() for drinks in drink_created]

        return jsonify({
            'success': True,
            'drinks': drink,            
        })

    except:
        abort(405)

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):
    drink = Drink.query.get(drink_id)
    check_if_drink_exists(drink)

    try:
        drink.delete()

        return jsonify({
            'success': True,
            'delete': drink.id
        })
    except:
        abort(422)

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''

@app.errorhandler(AuthError)
def forbidden(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "forbidden"
    }), 403
    
if __name__ == "__main__":
    app.debug = True
    app.run()