#!/usr/bin/env python3

import requests
import json
import timeit
import re
from src import storage


def get_settings(data):

    if data["settings"]["open_refine"]["fast_service_check"] == False and data["status"]["service_checked"] == False:
        dbs = False
    elif data["settings"]["refindit"]["limit_by_dbs"] == False:
        dbs = []
    else:
        dbs = data["settings"]["refindit"]["dbs"]

    if data["settings"]["open_refine"]["fast_service_check"] == False and data["status"]["service_checked"] == False:
        limit = str(data["settings"]["refindit"]["num_results_per_db_for_slow_check"])
    elif data["settings"]["refindit"]["limit_results_per_db"] == False:
        limit = 0
    else:
        limit = str(data["settings"]["refindit"]["num_results_per_db"])

    repeat = data["settings"]["refindit"]["repeat"]

    timeout = data["settings"]["refindit"]["timeout"]

    settings = {
        "db": dbs,
        "limit": limit,
        "timeout": timeout,
        "repeat": repeat
    }

    return settings


def set_parameters(query, settings):

    if query.get("properties") != None:
        print("Ok, the search will be advanced.")

        author = ""
        year = ""
        published_in = ""

        for each_parameter in query["properties"]:
            if each_parameter["pid"] == "author":
                author = each_parameter["v"]

            if each_parameter["pid"] == "year":
                year = each_parameter["v"]

            if each_parameter["pid"] == "origin":
                published_in = each_parameter["v"]

        params = {
        'search': 'advanced',
        'title': query.get("title"),
        'author': author,
        'year': year,
        'origin': published_in,
        'db': settings["db"],
        'limit': settings["limit"]
        }

    else:
        print("Ok, the search will be simple.")
        params = {
        'search': 'simple',
        'text': query.get("title"),
        'db': settings["db"],
        'limit': settings["limit"]
        }

    for parameter in params:
        if parameter == None:
            params.pop(parameter, None)

    if settings["db"] == False or len(settings["db"]) == 0:
        params.pop('db', None)
        print("Funcionou!")

    if settings["limit"] == 0:
        params.pop('limit', None)

    return params

def search(data, query, id_prefix):

    """
    dbs = data["parameters"]["refindit"]["dbs"]

    if data["parameters"]["refindit"]["limit_by_dbs"] == False:
        dbs = []
    else:
        dbs = data["parameters"]["refindit"]["dbs"]

    if data["parameters"]["refindit"]["limit_results_per_db"] == True:
        limit = data["parameters"]["refindit"]["num_results_per_db"]

    repeat = data["parameters"]["reconciliation"]["repeat"]
    """

    settings = get_settings(data)
    params = set_parameters(query, settings)

    """
    params = {
        'search': 'simple',
        'text': full_title,
        'db': settings["db"],
        'limit': settings["limit"]
        }
    """
    #print("Limit:", limit)
    """
    if settings["limit"] == 0:
        params.pop('limit', None)

    if len(settings["db"]) == 0:
        params.pop('db', None)
    """
    counter = 0
    time_spam = []
    failed = 0
    results_all = []

    while counter < settings["repeat"] and results_all == []:
        try:
            start = timeit.default_timer()
            r = requests.get('https://www.refindit.org/find', params=params, timeout=settings["timeout"])
            print(r.url)
            # There is a current bug with refindit API responses, that hampers
            # requests json() and json package to work properly. Thus, I replace the
            # problem with the appropriate character before jsonify the response.
            end = timeit.default_timer()
            results_fix = r.text.replace("][", ",")
            time_spam.append(end-start)
            print("Timer Success:", (end-start))
            results_all = json.loads(results_fix)
        except requests.exceptions.Timeout as error:
            print("Timeout. Error:")
            print(error)
            end = timeit.default_timer()
            time_spam.append(end-start)
            failed += 1
            print("Timer Failure:", (end-start))

        counter += 1

    if results_all == []:
        print("No results were found.")

    parameters = ["summary", "refindit", "time_per_query"]
    new_data = {id_prefix: time_spam}
    storage.update(data, parameters, new_data)

    parameters = ["summary", "refindit", "timeouts_per_query"]
    new_data = {id_prefix: failed}
    storage.update(data, parameters, new_data)

    print("Total Results:", len(results_all))
    return results_all


def results(data, query, id_prefix):

    results_all = search(data, query, id_prefix)

    results_processed = []

    for result in results_all:

        authors = []
        author = ""

        for each_author in result.get("authors"):
            if len(each_author) == 2 and each_author[0] != None and each_author[1] != None:
                author = each_author[1].title() + ", " + each_author[0].title()
            elif len(each_author) == 1 and each_author[0]:
                author = each_author[0].title()
            authors.append(author)
            #print(author)

        doi = result.get("doi")
        zenodo_figure = ""
        zenodo_treatment = ""

        if type(doi) == str and "zenodo" in doi.lower():

            for each in result.get("related"):
                if each["relation"] == "IsPartOf" and each["idType"] == "DOI":
                    doi = each["value"]
                    #print(doi)
                    break

            if result.get("type") == "Figure":
                zenodo_figure = result.get("doi")
                #print("Iuhu")

            elif result.get("type") == "Treatment":
                zenodo_treatment = result.get("doi")

        #print(result.get("title"))
        if result.get("title") != None or result.get("title") != "":
            title = re.sub("<.*?>", '', str(result.get("title")))
            #title = "bugauga"
        else:
            title = ""

        """
        if result.get("doi") != None:

            results_processed.append({
                "RR01": "",
                "RR02": result.get("source"),
                "RR03": result.get("title"),
                "RR04": "; ".join(authors),
                "RR05": result.get("year"),
                "RR06": result.get("publishedIn"),
                "RR07": result.get("volume"),
                "RR08": result.get("issue"),
                "RR09": result.get("spage"),
                "RR10": result.get("epage"),
                "RR11": result.get("type"),
                "RR12": result.get("doi"),
                "RR13": result.get("href"),
                "RR14": zenodo_figure,
                "RR15": zenodo_treatment,
                "RR16": ""
            })
        """
        results_processed.append({
                "RR01": "",
                "RR02": result.get("source"),
                "RR03": title,
                "RR04": "; ".join(authors),
                "RR05": result.get("year"),
                "RR06": result.get("publishedIn"),
                "RR07": result.get("volume"),
                "RR08": result.get("issue"),
                "RR09": result.get("spage"),
                "RR10": result.get("epage"),
                "RR11": result.get("type"),
                "RR12": doi,
                "RR13": result.get("href"),
                "RR14": zenodo_figure,
                "RR15": zenodo_treatment,
                "RR16": ""
            })

    #print(results_processed)
    return results_processed