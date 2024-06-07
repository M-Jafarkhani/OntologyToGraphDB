from SPARQLWrapper import SPARQLWrapper, JSON
from lib.utils import ClassMetaData, Property
import os
import json
import math

class DBPediaCrawler:
    namespace = """ 
                PREFIX dbo: <http://dbpedia.org/ontology/>
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    """

    def __init__(self, classes):
        self.classes = classes
        self.wrapper = SPARQLWrapper("https://dbpedia.org/sparql")

    def start(self):
        for cls_iri, cls_metadata in self.classes.items():
            self.query_class(cls_iri, cls_metadata)

    def query_class(self, cls_iri: str, cls_metadata: ClassMetaData):
        offset_count = self.get_offset_count(cls_iri)

        cls_var_label = cls_metadata.label.replace(' ', '_').lower()

        select_str = '?' + cls_var_label + ',?' + ',?'.join(prop.label.replace(' ', '_').lower()
                                                            for prop in cls_metadata.properties)

        where_str = '?' + cls_var_label + ' a ' + '<' + cls_iri + '> .' + '\n'

        for prop in cls_metadata.properties:
            where_str += 'OPTIONAL {' + '?' + \
                cls_var_label + ' <' + \
                prop.prop_iri + '>' + ' ?' + \
                prop.label.replace(' ', '_').lower() + ' }\n'

        new_directory_path = os.path.join(
            os.getcwd() + '/data', cls_metadata.label)
        os.makedirs(new_directory_path, exist_ok=True)

        for i in range(offset_count):
            query = """
                  %s
                  SELECT %s  
                  WHERE { %s }
                  LIMIT 10000
                  OFFSET  %s0000 """ % (self.namespace, select_str, where_str, str(i))

            self.wrapper.setQuery(query)
            self.wrapper.setReturnFormat(JSON)
            results = self.wrapper.query().convert()

            with open(f"{new_directory_path}/{i}", "w", encoding='utf8') as f:
                json.dump(results, f, indent=4, ensure_ascii=False)

    def get_offset_count(self, iri: str) -> int:
        query = """
              PREFIX dbo: <http://dbpedia.org/ontology/>
              PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
              PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

              SELECT count (?a)  
              WHERE {?a a <%s> } """ % iri
        self.wrapper.setQuery(query)
        self.wrapper.setReturnFormat(JSON)
        results = self.wrapper.query().convert()
        return math.ceil(int(results["results"]["bindings"][0]["callret-0"]["value"]) / 10000)
