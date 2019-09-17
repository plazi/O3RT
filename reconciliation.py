#!/usr/bin/env python3

import re
import sys
import json
from src import process, storage, summary
from settings import metadata as meta
from flask import Flask, request, jsonify

app = Flask(__name__)

project = "./projects/data.json"
settings = "./settings/default.json"

def jsonpify(obj):
    """
    Like jsonify but wraps result in a JSONP callback if a 'callback'
    query param is supplied.
    """
    try:
        callback = request.args['callback']
        response = app.make_response("%s(%s)" % (callback, json.dumps(obj)))
        response.mimetype = "text/javascript"
        return response
    except KeyError:
        return jsonify(obj)


@app.route("/reconcile", methods=['POST', 'GET'])
def reconcile():
    """
    # If a single 'query' is provided do a straightforward search.
    query = request.form.get('query')
    if query:
        #print("Query:", query)
        # If the 'query' param starts with a "{" then it is a JSON object
        # with the search string as the 'query' member. Otherwise,
        # the 'query' param is the search string itself.
        if query.startswith("{"):
            full_title = json.loads(query)['query']
        results = process.complete(data, full_title, limit=1)
        return jsonpify({"result": results})
    """
    # If a 'queries' parameter is supplied then it is a dictionary
    # of (key, query) pairs representing a batch of queries. We
    # should return a dictionary of (key, results) pairs.
    queries = request.form.get('queries')
    if queries:
        print("Queries:", queries)

        queries = json.loads(queries)
        results = {}

        data = storage.read(project, settings)
        count = data["summary"]["num_of_queries"]

        """
        limit = ""


        if data["settings"]["refindit"]["limit_results_per_db"] == True:
            limit = str(data["settings"]["refindit"]["num_results_per_db"])
        """

        if queries["q0"].get("type") == None:
            if data["summary"]["num_of_queries"] > 0:
                parameters = ["status"]
                new_data = {"redo-reconcile": True}
                #storage.update(project, "status", "redo-reconcile", True)
                #storage.update(project, parameters, new_data)
                storage.update(data, parameters, new_data)

            if data["status"]["service_checked"] == False:
                if data["settings"]["open_refine"]["fast_service_check"] == True:
                    results = {"q0": {"result": process.fast(data)}}
                else:
                    data["settings"]["refindit"]["num_results_per_db_for_slow_check"] = queries["q0"]["limit"]
                    print("Worked, limit set to:", data["settings"]["refindit"]["num_results_per_db_for_slow_check"])
                    for (key, query) in queries.items():
                        print("Worked, limit set to:", data["settings"]["refindit"]["num_results_per_db_for_slow_check"])
                        results[key] = {"result": process.complete(data, query={"title": query['query']})}


                parameters = ["status"]
                new_data = {"service_checked": True}
                #storage.update(project, "status", "service_checked", True)
                #storage.update(project, parameters, new_data)
                storage.update(data, parameters, new_data)
            else:
                results = {"q0": {"result": process.fast(data)}}

        else:
            if data["status"]["redo-reconcile"] == True:
                #parameters = ["status"]
                #new_data = {"redo-reconcile": False}
                #storage.update(project, parameters, new_data)
                #storage.update(data, parameters, new_data)
                data = storage.renew(data)
                count = 0

            for (key, query) in queries.items():

                if data["settings"]["open_refine"]["minimum_query_length"] > len(query['query'].split()):
                    results[key] = {"result": []}
                    print(count, query['query'])
                    print("----------")

                elif query.get('properties') != None:
                    resultinhos = process.complete(data, query={"title": query['query'], "properties": query["properties"]}, id=count)
                    results[key] = {"result": resultinhos}
                    print(count, query['query'])
                    print(count, len(resultinhos))
                    print("----------")

                else:
                    resultinhos = process.complete(data, query={"title": query['query']}, id=count)
                    results[key] = {"result": resultinhos}
                    print(count, query['query'])
                    print(count, len(resultinhos))
                    print("----------")

                count += 1

            print("OK chegamos aqui para oq eu der e vier")
            #storage.update(project, "status", "redo-reconcile", True)
            parameters = ["summary"]
            new_data = {"num_of_queries": count}
            #storage.update(project, "summary", "num_of_queries", count)
            #storage.update(project, parameters, new_data)
            data = storage.read(project, settings)
            print(data["summary"]["num_of_queries"])
            storage.update(data, parameters, new_data)
            print(data["summary"]["num_of_queries"])
            print("HERE IS WHAT IT IS", new_data)
            print(data["status"]["redo-reconcile"])

        #print(results)
        summary.calculate(data)
        return jsonpify(results)

    if request.form.get("extend"):

        extend = json.loads(request.form.get("extend"))

        data = storage.read(project, settings)

        ids = {}
        properties_value = {}
        properties_name = []

        for each_id in extend["ids"]:
            print(each_id)

            properties_value = {}
            for each_clicked_property in extend["properties"]:
                for each_property in meta.properties["properties"]:
                    if each_property["id"] == each_clicked_property["id"]:
                        #properties_value.update({each_clicked_property["id"]: [{"str": str(data["data"][each_id][each_clicked_property["id"]])}]})
                        #each_id[:each_id.find('r')]
                        #print(each_id[:each_id.find('r')])
                        #print(each_id)
                        #print(each_clicked_property["id"])
                        if each_clicked_property["id"] == "RR14":
                            properties_value.update({each_clicked_property["id"]: [{"str": re.sub("[\][']", '', str(data["data"][each_id[:each_id.find('r')]]["zenodo"]["figures"]))}]})
                        elif each_clicked_property["id"] == "RR15":
                            properties_value.update({each_clicked_property["id"]: [{"str": re.sub("[\][']", '', str(data["data"][each_id[:each_id.find('r')]]["zenodo"]["treatments"]))}]})
                        else:
                            properties_value.update({each_clicked_property["id"]: [{"str": str(data["data"][each_id[:each_id.find('r')]]["results"][each_id][each_clicked_property["id"]])}]})

                        ids.update({each_id: properties_value})
                        break

        for each_clicked_property in properties_value:
            for each_property in meta.properties["properties"]:
                if each_clicked_property == each_property["id"]:
                    properties_name.append({"id": each_clicked_property, "name": each_property["name"]})

        extension = {
            "rows": ids,
            "meta": properties_name
        }

        return jsonpify(extension)

    # If neither a 'query' nor 'queries' parameter is supplied then
    # we should return the service metadata.
    return jsonpify(meta.metadata)


@app.route("/extend", methods=['POST', 'GET'])
def extend():

    return jsonpify(meta.properties)


if __name__ == '__main__':
    app.run(port=8000, debug=True)