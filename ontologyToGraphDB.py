"""
    This the main Python file for OntologyToGraphDB project.
    In this file, we read data from config.json file which is located in the root folder.
    There are two keys in this file. OntologyFile and OntologyUrl:
        - ontologyFile: Points to the file located in the "ontologies" folder
        - ontologyUrl: Points to the url of the ontology
    Ontologies should be based on OWL ontology and follow the structure of DBPedia.

    There are 3 main steps to convert an ontology to Neo4j GraphDB structure.
        - OntologyExtractor: Extracts metadat from the ontology file. It saves the metadata into binary files.
        - DBPediaCrawler: Crawls the DBPedia by running SPARQL queries, based on the metadata that were extracted
                          in the previous step. It saves these data with JSON format into "data" folder.
        - GraphDBGenerator: Creats Neo4j scripts from extracted data. It saves the output into "cypher" folder               
"""

import json
from lib.dbPediaCrawler import DBPediaCrawler
from lib.graphDBGenerator import GraphDBGenerator
from lib.ontologyExtractor import OntologyExtractor


def main():
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
        ontology_file = config["OntologyFile"]
        ontology_url = config["OntologyUrl"]
    
    ontologyExtractor = OntologyExtractor(ontology_file, ontology_url)
    ontologyExtractor.start()
    
    dbPediaCrawler = DBPediaCrawler()
    dbPediaCrawler.start()
    
    graphDBGenerator = GraphDBGenerator()
    graphDBGenerator.start()


if __name__ == "__main__":
    main()
