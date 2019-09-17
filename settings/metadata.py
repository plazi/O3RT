#!/usr/bin/env python3

# Basic service metadata. There are a number of other documented options
# but this is all we need for a simple service.
metadata = {
    "name": "Refindit Reconciliation Service",
    "owner": {
        "name": "Plazi",
        "site": "http://www.plazi.org"
    },
    "author": {
        "name": "Marcus Guidoti",
        "other": {
            "email": "marcus.guidoti@gmail.com",
            "linkedin": "http://www.linkedin.com/in/mguidoti",
            "twitter": "http://www.twitter.com/marcusguidoti"
        }
    },
    "defaultTypes": [{
        "id": "Refindit", "name": "journal-article"
        }],
    "extend": {
        "propose_properties": {
            "service_url": "http://localhost:8000",
            "service_path": "/extend"
        }
    }
}


properties = {
        "properties": [
                    {"id": "RR01", "name": "Id", "Refindit": None},
                    {"id": "RR02", "name": "Source", "Refindit": "source"},
                    {"id": "RR03", "name": "Title", "Refindit": "title"},
                    {"id": "RR04", "name": "Author(s) Name(s)", "Refindit": "authors"},
                    {"id": "RR05", "name": "Year", "Refindit": "year"},
                    {"id": "RR06", "name": "Published in", "Refindit": "publishedIn"},
                    {"id": "RR07", "name": "Volume", "Refindit": "id", "Refindit": "volume"},
                    {"id": "RR08", "name": "Issue", "Refindit": "issue"},
                    {"id": "RR09", "name": "Initial Page", "Refindit": "spage"},
                    {"id": "RR10", "name": "Last Page", "Refindit": "epage"},
                    {"id": "RR11", "name": "Type of Publication", "Refindit": "type"},
                    {"id": "RR12", "name": "DOI", "Refindit": "doi"},
                    {"id": "RR13", "name": "Link", "Refindit": "href"},
                    {"id": "RR14", "name": "Zenodo (Figures DOIs)", "Refindit": "related"},
                    {"id": "RR15", "name": "Zenodo (Treatments DOIs)", "Refindit": "related"},
                    {"id": "RR16", "name": "Reconciliation Score", "Refindit": None}
                ],
        "type": "publication",
        "limit": 17
    }