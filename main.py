from bottle import post, request, run, response
import bottle
from bottle_cors_plugin import cors_plugin
from db import connection
import json


class EnableCors(object):
    name = "enable_cors"
    api = 2

    def apply(self, fn, context):
        def _enable_cors(*args, **kwargs):
            # set CORS headers
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, OPTIONS"
            response.headers[
                "Access-Control-Allow-Headers"] = "Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token"

            if bottle.request.method != "OPTIONS":
                # actual request; reply with the actual response
                return fn(*args, **kwargs)

        return _enable_cors


def get_contracts(collection_uuid):
    return connection.select(
        '''
            SELECT *
            FROM contracts
            WHERE collection = %s;
        ''',
        (collection_uuid,)
    )


def get_floor_price(chain_id, contract_address):
    return "0x001"


def get_volume(chain_id, contract_address):
    return "0x0141"


@post("/getCollections")
def get_collections():
    collections = connection.select(
        '''
            SELECT *
            FROM collections;
        ''',
        ()
    )
    for collection in collections:
        collection["contracts"] = get_contracts(collection["uuid"])
        for contract in collection["contracts"]:
            chain_id = contract["chain_id"]
            address = contract["address"]
            contract["floor"] = get_floor_price(chain_id, address)
            contract["volume"] = get_volume(chain_id, address)

    return json.dumps(collections)


@post("/getTokens")
def get_tokens():
    return json.dumps(
        connection.select(
            '''
                SELECT *
                FROM tokens
                WHERE owner = %s;
            ''',
            (request.json["address"],)
        )
    )


#@post("/getListedTokens")
#def get_listed_tokens():
#    return json.dumps(
#        connection.select(
#            '''
#                SELECT *
#                FROM orders
#                WHERE owner = %s;
#            ''',
#            (request.json["collectionUuid"],)
#        )
#    )


if __name__ == "__main__":
    application = bottle.default_app()
    #application.install(cors_plugin("*"))
    application.install(EnableCors())
    run(application, host="0.0.0.0", port=8004)
