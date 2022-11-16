import os
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

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['GET'])

def get_drinks():

    drinks = Drink.query.all()

    if len(drinks)==0:

        abort(404)

    drinks_short = [drink.short() for drink in drinks]

    response = {'success': True,
        'drinks': drinks_short,}

    return jsonify(response) , 200

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

def get_drink_detail(payload):

    drinks = Drink.query.all()

    if len(drinks) == 0 :

        abort(404)

    drinks_long = [drink.long() for drink in drinks]

    response = {'success': True,
        'drinks': drinks_long}

    return jsonify(response), 200

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
def post_drinks(jwt):
    drinks = request.get_json()
    new_title = drinks.get('title')
    new_recipe = drinks.get('recipe')
    recepe = json.dumps(new_recipe)

    responses = Drink(title=new_title, recipe=recepe)

    responses.insert()

    return jsonify({'success': True,
        'drinks': [drinking.long() for drinking in Drink.query.all()]})

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

@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):

    form = request.get_json()
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if not drink:
        abort(404)
    try:
        title = form.get('title')
        recipe = form.get('recipe')

        if title:
            drink.title = title
        if recipe:
            drink.recipe = json.dumps(form['recipe'])

        drink.update()
    except BaseException:
        abort(400)
    response = {'success': True,
                'drinks': [drink.long()]}

    return jsonify(response), 200

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
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
  
###drink = Drink.query.filter (Drink.id === id).one_none()
    drink = Drink.query.filter_by(id=id)

    if not drink:
        abort(404)
    try:
        drink.delete()
    except BaseException:
        abort(400)
    response = {'success': True,
            'delete': id}

    return jsonify(response), 200

# Error Handling
'''
Example error handling for unprocessable entity
'''

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({"success": False,
        "error": 422,
        "message": "unprocessable"}), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404
'''
@app.errorhandler(404)
def not_found(error):
    response = {"success": False,
        "error": 404,
        "message": "resource not found"}
    return jsonify(response), 404

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def auth_error(error):
    response ={
        "success": False,
        "error": error.status_code,
        "message": error.error['description']}
    return jsonify(response), error.status_code

@app.errorhandler(401)
def unauthorized(error):
    response = {"success": False,
        "error": 401,
        "message": 'Unathorized'}
    return jsonify(response),401

@app.errorhandler(500)
def internal_server_error(error):
    response = {"success": False,
        "error": 500,
        "message": 'Internal Server Error'}
    return jsonify(response),500


@app.errorhandler(400)
def bad_request(error):
    response = {"success": False,
        "error": 400,
        "message": 'Bad Request'}
    return jsonify(response), 400


@app.errorhandler(405)
def method_not_allowed(error):
    response = {"success": False,
        "error": 405,
        "message": 'Method Not Allowed'}
    return jsonify(response), 405
