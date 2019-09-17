#!/usr/bin/env python3

import re
import os
from src import refindit
from src import storage
from settings import metadata as meta
from fuzzywuzzy import process as fw_process
from fuzzywuzzy import fuzz


def fast(data, empty=False):

        #data = storage.read(project)

        result = []

        checker = data["data"].get("q0")

        if checker != None and empty == False:
                result.append({
                        "id": checker["results"]["q0r1"].get("RR01"),
                        "name": checker["results"]["q0r1"].get("RR03"),
                        "score": checker["results"]["q0r1"].get("RR15"),
                        "match": True,
                        "type": [
                                {"id": "Refindit",
                                "name": checker["results"]["q0r1"].get("RR11")}
                                ]
                        })

        else:
                result.append({
                        "id": "",
                        "name": "",
                        "score": 0,
                        "match": False,
                        "type": [{
                                "id": meta.metadata["defaultTypes"][0]["id"],
                                "name": meta.metadata["defaultTypes"][0]["name"]
                                }]
                        })

        return result


def complete(data, query, id=1):

    #data = storage.read(project)

    id_prefix = "q" + str(id)

    refindit_results = refindit.results(data, query, id_prefix)

    # Matching threshold.
    if data["settings"]["open_refine"]["fast_service_check"] == False and data["status"]["service_checked"] == False:
        match_threshold = 0
        print("Worked.")
    else:
        match_threshold = data["settings"]["reconciliation"]["match_threshold"]

    # Initialize matches.
    matches = []

    zenodo_figures = []
    zenodo_treatments = []

    counter = 1

    # Search person records for matches.
    for each_result in refindit_results:
        score = fuzz.token_set_ratio(query["title"], each_result['RR03'])


        new_id = id_prefix + "r" + str(counter)

        if each_result["RR11"] == None:
                each_result["RR11"] = "None"

        if score > match_threshold:

                project = os.path.join(data["settings"]["project"]["path"], data["settings"]["project"]["filename"])
                settings = os.path.join(data["settings"]["path"], data["settings"]["filename"])
                data = storage.read(project, settings)

                if data["settings"]["reconciliation"]["only_dois"] == True:
                        if each_result["RR12"] == None:
                                print("THERE IS NO DOI")
                                continue



                matches.append({
                        "id": new_id,
                        "name": each_result["RR03"],
                        "score": score,
                        "match": query["title"] == each_result["RR03"],
                        "type": [{
                                "id": "Refindit",
                                "name": each_result["RR11"]
                                }]
                        })

                each_result["RR01"] = new_id
                each_result["RR16"] = score

                if data["status"]["service_checked"] == True:
                        #print(data["data"][id_prefix])
                        if data["data"].get(id_prefix) == None:
                                print("ESTAMOS AQUI")
                                selected_results = {
                                        id_prefix: {
                                                "results": {
                                                        new_id: each_result
                                                },
                                                "zenodo": {
                                                        "figures": [],
                                                        "treatments": []
                                                }
                                        }
                                }
                                parameters = ["data"]
                                #storage.add(project, selected_results)
                                #storage.update(project, parameters, selected_results)
                                storage.update(data, parameters, selected_results)
                        else:
                                print("chegou aqui")

                                selected_results = {
                                        new_id: each_result
                                }
                                parameters = ["data", id_prefix, "results"]
                                #storage.update(project, parameters, selected_results)
                                storage.update(data, parameters, selected_results)
                        
                        if each_result["RR14"] != "":
                                if each_result["RR03"] in zenodo_figures:
                                        print("repeated zenodo entry")
                                else:
                                        zenodo_figures.append(each_result["RR03"])
                                        parameters = ["data", id_prefix, "zenodo"]
                                        if data["data"].get(id_prefix) != None:
                                                old_data = data["data"][id_prefix]["zenodo"]["figures"]
                                                old_data.append(each_result["RR14"])
                                        else:
                                                old_data = [each_result["RR14"]]
                                        new_data = {"figures": old_data}
                                        storage.update(data, parameters, new_data)

                        if each_result["RR15"] != "":
                                if each_result["RR03"] in zenodo_treatments:
                                        print("repeated zenodo entry")
                                else:
                                        zenodo_treatments.append(each_result["RR03"])
                                        parameters = ["data", id_prefix, "zenodo"]
                                        old_data = data["data"][id_prefix]["zenodo"]["treatments"]
                                        old_data.append(each_result["RR14"])
                                        new_data = {"treatments": old_data}
                                        storage.update(data, parameters, new_data)
                
                """
                print(type(data["data"][id_prefix]["zenodo"]["figure"]))
                print(len(data["data"][id_prefix]["zenodo"]["figure"]))
                print(data["data"][id_prefix]["zenodo"]["figure"])
                """
                counter += 1

    
    """
    parameters = ["summary", "refindit"]
    old_data = data["summary"]["refindit"]["total_num_of_results"]
    print("OLD DATA:", old_data)
    print("NEW DATA:", len(refindit_results))
    final_data = (old_data + len(refindit_results))
    print("FINAL:", final_data)
    new_data = {"total_num_of_results": final_data}
    storage.update(data, parameters, new_data)
    """


    parameters = ["summary", "refindit", "num_of_results_per_query"]
    new_data = {id_prefix: len(refindit_results)}
    storage.update(data, parameters, new_data)

    parameters = ["summary", "reconcile", "num_of_selected_results_per_query"]
    new_data = {id_prefix: len(matches)}
    storage.update(data, parameters, new_data)

    print("Accepted results:", len(matches))
    return matches