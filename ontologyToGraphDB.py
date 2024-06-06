import json
from lib.ontologyCrawler import OntologyCrawler


def main():
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
        ontology_file = config["OntologyFile"]
        ontology_url = config["OntologyUrl"]

    crawler = OntologyCrawler(ontology_file, ontology_url, 'propertyMappings.json')
    crawler.start()


if __name__ == "__main__":
    main()
