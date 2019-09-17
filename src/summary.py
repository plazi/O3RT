#!/usr/bin/env python3

import os
from src import storage

def calculate(data):


    project = os.path.join(data["settings"]["project"]["path"], data["settings"]["project"]["filename"])
    settings = os.path.join(data["settings"]["path"], data["settings"]["filename"])
    data = storage.read(project, settings)

    # Calculate the total number of results
    results = data["summary"]["refindit"]["num_of_results_per_query"]
    total_results = 0
    
    if len(results) > 0:
        for query in results:
            total_results += results[query]

        parameters = ["summary", "refindit"]
        new_data = {"total_num_of_results": total_results}
        storage.update(data, parameters, new_data)

        # Calculate the average number of results
        parameters = ["summary", "refindit"]
        new_data = {
            "avg_num_of_results_per_query": total_results/len(results)
            }
        storage.update(data, parameters, new_data)

    # Calculate the average time per query, and the average time per all
    # queries
    time_per_query = data["summary"]["refindit"]["time_per_query"]

    total_time = 0
    counter = 0

    if len(time_per_query) > 0:
        for query in time_per_query:
            total_per_query = 0

            for time_spam in time_per_query[query]:
                total_per_query += time_spam
                total_time += time_spam
                counter += 1

            avg_time_per_query = total_per_query/len(time_per_query[query])
            parameters = ["summary", "refindit", "avg_time_per_query"]
            new_data = {
                query: avg_time_per_query
                }
            storage.update(data, parameters, new_data)

        parameters = ["summary", "refindit"]
        avg_time = total_time/counter
        new_data = {
            "avg_time": avg_time
        }
        storage.update(data, parameters, new_data)

    # Calculate the total number of selected results
    selected_results = data["summary"]["reconcile"]["num_of_selected_results_per_query"]

    total_selected_results = 0

    if len(selected_results) > 0:
        for query in selected_results:
            total_selected_results += selected_results[query]

        parameters = ["summary", "reconcile"]
        new_data = {
            "total_num_of_selected_results": total_selected_results
        }
        storage.update(data, parameters, new_data)


    # Calculate Zenodo total number of figures and treatments
    zenodo_figures = 0
    zenodo_treatments = 0

    queries_with_figures = 0
    queries_with_treatments = 0

    num_of_queries = data["summary"]["num_of_queries"]
    print("olhe aqui", len(data["data"]))

    if len(data["data"]) > 0:
        print("CHEGAMOS AQUI")
        for query in data["data"]:
            zenodo_figures += len(data["data"][query]["zenodo"]["figures"])
            zenodo_treatments += len(data["data"][query]["zenodo"]["treatments"])

            if len(data["data"][query]["zenodo"]["figures"]) > 0:
                queries_with_figures += 1

            if len(data["data"][query]["zenodo"]["treatments"]) > 0:
                queries_with_treatments += 1

        parameters = ["summary", "zenodo"]
        new_data = {
            "total_num_figures": zenodo_figures
        }
        storage.update(data, parameters, new_data)

        new_data = {
            "number_of_queries_with_figures": queries_with_figures
        }
        storage.update(data, parameters, new_data)

        new_data = {
            "avg_num_figures_per_query": zenodo_figures/num_of_queries
        }
        storage.update(data, parameters, new_data)

        new_data = {
            "total_num_treatments": zenodo_treatments
        }
        storage.update(data, parameters, new_data)

        new_data = {
            "number_of_queries_with_treatments": queries_with_treatments
        }
        storage.update(data, parameters, new_data)

        new_data = {
            "avg_num_treatments_per_query": zenodo_treatments/num_of_queries
        }
        storage.update(data, parameters, new_data)