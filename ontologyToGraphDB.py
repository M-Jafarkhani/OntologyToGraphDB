import json
from lib.dbPediaCrawler import DBPediaCrawler
from lib.ontologyCrawler import OntologyCrawler


def main():
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
        ontology_file = config["OntologyFile"]
        ontology_url = config["OntologyUrl"]

    ontologyCrawler = OntologyCrawler(ontology_file, ontology_url)
    (classes, object_properties) = ontologyCrawler.start()

    dbPediaCrawler = DBPediaCrawler(classes, object_properties)
    dbPediaCrawler.start()


if __name__ == "__main__":
    main()
