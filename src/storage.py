#!/usr/bin/env python3

import os
import json

def create(project, settings):
    """
    data = {
        "metadata": {
            "name": "data",
            "description": "",
            "ownwer": "",
        },
        "settings": {
            "project": {
                "path": "./projects/",
                "filename": "data.json"
            },
            "open_refine": {
                "fast_service_check": True,
                "minimum_query_length": 8
            },
            "refindit": {
                "limit_results_per_db": True,
                "num_results_per_db": 5,
                "num_results_per_db_for_slow_check": 0,
                "limit_by_dbs": True,
                "dbs": ["crossref", "datacite"],
                "timeout": 20,
                "repeat": 3
            },
            "reconciliation": {
                "match_threshold": 90,
                "only_dois": True
            }
        },
        "status": {
            "service_checked": False,
            "redo-reconcile": False
        },
        "summary": {
            "num_of_queries": 0,
            "refindit": {
                "total_number_of_results": 0,
		        "number_of_results_per_query": {},
		        "average_time_per_query": 0
                },
            "zenodo": {
                #"figures": {"q1": [], "q2": []},
		        "total_num_figures": 0,
		        "average_num_figures_per_query": 0,
		        #"treatments" {"q1": [], "q2": []},
		        "total_num_treatments": 0,
		        "average_num_treatments_per_query": 0
            }
        },
        "data": {}
    }
    """

    with open(settings, "r") as settings2:
        data = json.load(settings2)

    print(data)

    with open(project, "w", encoding="utf8") as data_file:
        json.dump(data, data_file)


def read(project, settings):
    if os.path.isfile(project):
        with open(project, "r", encoding="utf8") as data_file:
            data = json.load(data_file)
    else:
        create(project, settings)
        with open(project, "r", encoding="utf8") as data_file:
            data = json.load(data_file)

    return data


def update(data, parameters, new_data):

    #data = read(project)
    #path = data["parameters"]["project"]["path"]
    #file_name = data["parameters"]["project"]["name"]
    project = os.path.join(data["settings"]["project"]["path"], data["settings"]["project"]["filename"])
    settings = os.path.join(data["settings"]["path"], data["settings"]["filename"])
    data = read(project, settings)
    #print("PARAMETROS", parameters)
    #print("QUANTIDADE DE PARAMETROS", len(parameters))
    #print(new_data)

    if len(parameters) == 3:
        #print(data[parameters[0]])
        data[parameters[0]][parameters[1]][parameters[2]].update(new_data)
    elif len(parameters) == 2:
        data[parameters[0]][parameters[1]].update(new_data)
    elif len(parameters) == 1:
        print(parameters[0])
        print(new_data)
        data[parameters[0]].update(new_data)
        print(data[parameters[0]])

    #print("MY DATA IS HERE", data["data"])

    with open(project, "w", encoding="utf8") as data_file:
        json.dump(data, data_file)


def renew(data):
    #data = read(data)
    #path = data["parameters"]["project"]["path"]
    #file_name = data["parameters"]["project"]["name"]
    project = os.path.join(data["settings"]["project"]["path"], data["settings"]["project"]["filename"])
    settings = os.path.join(data["settings"]["path"], data["settings"]["filename"])
    #os.remove(project)
    summary = read(settings, settings)

    #create(project)
    data["status"]["num_of_queries"] = 0
    data["status"]["redo-reconcile"] = False
    data["data"] = {}
    data["summary"] = summary["summary"]

    with open(project, "w", encoding="utf8") as data_file:
        json.dump(data, data_file)
    
    data = read(project, settings)

    return data