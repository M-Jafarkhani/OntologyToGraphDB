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
