import json
from SPARQLWrapper import SPARQLWrapper, JSON

# dictionary: ontology class -> [precision score, closest valid parent class]
# (an ontology class is valid if its frequency is superior to a defined threshold)
with open('onto_classes_system.json', encoding="utf8") as f:
    onto_classes_system = json.load(f)

def dbpedia_query(query_string, resource = False):
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setQuery(query_string)
    sparql.setReturnFormat(JSON)
    
    if resource:    # we query dbpedia about a resource/entity (subject or object of a triple)
        try:
            results = sparql.query().convert()
            onto_classes = [x["x"]["value"][28:] for x in results["results"]["bindings"] if x["x"]["value"].startswith("http://dbpedia.org/ontology/")]   # we only consider the dbpedia:ontology results
            
            bestPrecision = 0
            mostPreciseType = "THING"
            for type in onto_classes:
                if type in onto_classes_system:
                    if onto_classes_system[type][0] > bestPrecision:
                        mostPreciseType = type
                        bestPrecision = onto_classes_system[type][0]
            return onto_classes_system[mostPreciseType][1].upper() # the ontology class returned is the closest valid parent of the most precise class
            
        except Exception:
            return "THING"
    
    else:   # we query dbpedia about an ontology (property of a triple)
        try:
            results = sparql.query().convert()
            if len(results["results"]["bindings"]) == 0:
                return "*"
            else:
                return results["results"]["bindings"][0]["x"]["value"][28:].upper() # there should be exactly one result
            
        except Exception:
            return "*"

def get_property_range(property):
    query_string = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?x
        WHERE { <http://dbpedia.org/ontology/""" + property + """> rdfs:range ?x .}
    """
    
    return dbpedia_query(query_string)

def get_property_domain(property):
    query_string = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?x
        WHERE { <http://dbpedia.org/ontology/""" + property + """> rdfs:domain ?x .}
    """
    
    return dbpedia_query(query_string)

def get_resource_type(resource):
    query_string = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT ?x
        WHERE { <http://dbpedia.org/resource/""" + resource + """> rdf:type ?x .}
    """
    
    return dbpedia_query(query_string, resource = True)