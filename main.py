import flask
import postgresql
import json
import re

app = flask.Flask(__name__)


def db_connection():
    return postgresql.open("pq://postgres:postgres@localhost:5432/birds_db")


def to_json(data):
    return json.dumps(data)


def response(code, data):
    return flask.Response(
        status=code,
        mimetype="application/json",
        response=to_json(data)
    )


def check_limit_offset_params():
    limit = flask.request.args.get('limit')
    offset = flask.request.args.get('offset')

    errors = []
    params = ''

    if (limit is None or limit == '') or (offset is None or offset == ''):
        errors.append("Param limit/offset is missing")
    else:
        incorrect_limit_param = re.sub(r'\d+', '', limit)
        if incorrect_limit_param:
            errors.append("Param limit should be positive number")
        else:
            incorrect_offset_param = re.sub(r'\d+', '', offset)
            if incorrect_offset_param:
                errors.append("Param offset should be positive number")
            else:
                params = params + " LIMIT " + limit + " OFFSET " + offset

    return params, errors


def params_validate():
    attribute = flask.request.args.get('attribute')
    order = flask.request.args.get('order')

    error = []
    errors_attr_order_params = []
    params = ''

    if (attribute is None or attribute == '') or (order is None or order == ''):
        errors_attr_order_params.append("Param attribute/order is missing")
    else:
        incorrect_attr_param = re.sub(r'species|name|color|body_length|wingspan', '', attribute)
        if incorrect_attr_param:
            errors_attr_order_params.append("Param attribute not found")
        else:
            order = str(order).upper()
            incorrect_order_param = re.sub(r'ASC|DESC', '', order)
            if incorrect_order_param:
                errors_attr_order_params.append("Param order should be ASC or DESC")
            else:
                params = "ORDER BY " + str(attribute) + " " + order

    (limit_offset_params, errors_limit_offset_params) = check_limit_offset_params()

    if errors_attr_order_params:
        if errors_limit_offset_params:
            error.append(errors_attr_order_params[0] + " OR " + errors_limit_offset_params[0])
        else:
            params = params + limit_offset_params
    else:
        if not errors_limit_offset_params:
            params = params + limit_offset_params

    return params, error


def bird_validate():
    errors = []
    json_obj = flask.request.get_json()
    if json_obj is None:
        errors.append(
            "Incorrect JSON")
        return None, errors

    for field_name in ['species', 'name', 'color']:
        if type(json_obj.get(field_name)) is not str:
            errors.append(
                "Field '{}' is missing or is not a string".format(field_name))

    for field_name in ['body_length', 'wingspan']:
        if type(json_obj.get(field_name)) is not int:
            errors.append(
                "Field '{}' is missing or is not a int ".format(field_name))

        if json_obj.get(field_name) <= 0:
            errors.append(
                "Value of field '{}' should be more than 0 ".format(field_name))

    return json_obj, errors


@app.route('/')
def root():
    return flask.redirect('/birds')


@app.route('/version', methods=['GET'])
def get_version():
    return "Birds Service. Version 0.1"


@app.route('/birds', methods=['GET'])
def get_birds():
    query = "SELECT species, name, color, body_length, wingspan FROM birds "
    params = ''
    if len(flask.request.args) != 0:
        (params, errors) = params_validate()
        if errors:
            return response(400, {"errors": errors})

    query = query + params

    with db_connection() as db:
        tuples = db.query(query)
        birds = []
        for (species, name, color, body_length, wingspan) in tuples:
            birds.append({
                "species": species,
                "name": name,
                "color": color,
                "body_length": body_length,
                "wingspan": wingspan
            })

        resp = birds
        if len(flask.request.args) != 0:
            resp = {"query": query, "results": resp}

        return response(200, resp)


@app.route('/birds', methods=['POST'])
def add_bird():
    (json_obj, errors) = bird_validate()
    if errors:
        return response(400, {"errors": errors})

    with db_connection() as db:
        try:
            insert = db.prepare(
                "INSERT INTO birds (species, name, color, body_length, wingspan) VALUES ($1, $2, $3, $4, $5) " +
                "RETURNING name")
            [(name,)] = insert(
                json_obj['species'],
                json_obj['name'],
                json_obj['color'],
                json_obj['body_length'],
                json_obj['wingspan'])
            return response(200, {"bird_name": name})
        except Exception:
            errors.append("This entry cannot be added to the base")
            return response(400, {"errors": errors})


if __name__ == "__main__":
    app.run(port=8080, debug=True)
