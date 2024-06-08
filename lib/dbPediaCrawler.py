import pickle
import shutil
import time
from SPARQLWrapper import SPARQLWrapper, JSON
from lib.utils import ClassMetaData, ObjectPropertyMetaData, printProgressBar, dump_metadata_to_file
import os
import json
import math


class DBPediaCrawler:
    namespace = """ 
                PREFIX dbo: <http://dbpedia.org/ontology/>
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    """

    def __init__(self):
        self.classes: dict[str, ClassMetaData] = dict()
        self.object_properties: dict[str, ObjectPropertyMetaData] = dict()
        self.wrapper = SPARQLWrapper("https://dbpedia.org/sparql")
        currrent_director = os.getcwd()
        directory_path = os.path.join(currrent_director + '/metadata')
        with open(f"{directory_path}/Classes", "rb") as file:
            self.classes = pickle.load(file)
        with open(f"{directory_path}/Object Properties", "rb") as file:
            self.object_properties = pickle.load(file)
        if os.path.exists(os.path.join(currrent_director + '/data')):    
            shutil.rmtree(os.path.join(currrent_director + '/data'))
    
    def start(self):
        for cls_iri, cls_metadata in self.classes.items():
            self.query_class(cls_iri, cls_metadata)
        for obj_prop_iri, obj_prop_metadata in self.object_properties.items():
            self.query_object_properties(obj_prop_iri, obj_prop_metadata)
        dump_metadata_to_file(self.classes, self.object_properties)

    def query_class(self, cls_iri: str, cls_metadata: ClassMetaData):
        cls_var_label = cls_metadata.label.replace(' ', '_').lower()
        select_str = '?' + cls_var_label + ' '
        for prop in cls_metadata.properties:
            prop_label = prop.label.replace(' ', '_').lower()
            select_str += f" (SAMPLE(?{prop_label}) AS ?{prop_label}) " 
        where_str = '?' + cls_var_label + ' a ' + '<' + cls_iri + '> .' + '\n'
        for prop in cls_metadata.properties:
            where_str += 'OPTIONAL {' + '?' + \
                cls_var_label + ' <' + \
                prop.prop_iri + '>' + ' ?' + \
                prop.label.replace(' ', '_').lower() + ' }\n'
        obj_prop_iri_list = []
        for obj_prop_iri, obj_prop_metadata in self.object_properties.items():
            if obj_prop_metadata.range_iri == cls_iri:
                obj_prop_iri_list.append(obj_prop_iri)
        where_str += ' UNION '.join(
            [f'{{ ?a <{item}> ?{cls_var_label}}}' for item in obj_prop_iri_list])
        offset_count = self.get_offset_class_count(cls_var_label, where_str)
        directory_path = os.path.join(
            os.getcwd() + '/data/Classes', cls_metadata.label)
        os.makedirs(directory_path, exist_ok=True)
        self.classes[cls_iri].folder_path = directory_path
        progress_prefix = f'Fetching Class ({cls_metadata.label}):'
        for i in range(offset_count):
            query = """
                %s
                SELECT DISTINCT %s  
                WHERE { %s }
                GROUP BY ?%s
                LIMIT 10000
                OFFSET  %s0000 """ % (self.namespace, select_str, where_str, cls_var_label ,str(i))
            self.wrapper.setQuery(query)
            self.wrapper.setReturnFormat(JSON)
            results = self.wrapper.query().convert()
            with open(f"{directory_path}/{i}", "w", encoding='utf8') as f:
                json.dump(results, f, indent=4, ensure_ascii=False)
            time.sleep(0.1)
            printProgressBar(
                i + 1, offset_count, prefix=progress_prefix, suffix='Complete', length=50)

    def query_object_properties(self, obj_prop_iri: str, obj_prop_metadata: ObjectPropertyMetaData):
        offset_count = self.get_offset_objects_count(obj_prop_iri)
        domain_label_var_label = obj_prop_metadata.domain_label.replace(
            ' ', '_').lower()
        range_label_var_label = obj_prop_metadata.range_label.replace(
            ' ', '_').lower()
        select_str = '?' + domain_label_var_label + ' ,?' + range_label_var_label
        where_str = '?' + domain_label_var_label + '<' + \
            obj_prop_iri + '> ' + ' ?' + range_label_var_label
        folder_name = f"{obj_prop_metadata.domain_label}_{obj_prop_metadata.label}­_{obj_prop_metadata.range_label}"
        directory_path = os.path.join(
            os.getcwd() + '/data/Object Properties', folder_name)
        os.makedirs(directory_path, exist_ok=True)
        self.object_properties[obj_prop_iri].folder_path = directory_path
        progress_prefix = f'Fetching Object Property ({folder_name}):'
        printProgressBar(0, offset_count, prefix=progress_prefix,
                         suffix='Complete', length=50)
        for i in range(offset_count):
            query = """
                  %s
                  SELECT DISTINCT %s  
                  WHERE { %s }
                  LIMIT 10000
                  OFFSET  %s0000 """ % (self.namespace, select_str, where_str, str(i))
            self.wrapper.setQuery(query)
            self.wrapper.setReturnFormat(JSON)
            results = self.wrapper.query().convert()
            with open(f"{directory_path}/{i}", "w", encoding='utf8') as f:
                json.dump(results, f, indent=4, ensure_ascii=False)
            time.sleep(0.1)
            printProgressBar(
                i + 1, offset_count, prefix=progress_prefix, suffix='Complete', length=50)

    def get_offset_class_count(self, cls_var_label: str, where_str: str) -> int:
        query = """
            SELECT COUNT (DISTINCT ?%s)  
            WHERE { %s } """ % (cls_var_label, where_str)
        self.wrapper.setQuery(query)
        self.wrapper.setReturnFormat(JSON)
        results = self.wrapper.query().convert()
        return math.ceil(int(results["results"]["bindings"][0]["callret-0"]["value"]) / 10000) + 1

    def get_offset_objects_count(self, iri: str) -> int:
        query = """
            SELECT count (DISTINCT ?a)  
            WHERE {?a <%s> ?b} """ % iri
        self.wrapper.setQuery(query)
        self.wrapper.setReturnFormat(JSON)
        results = self.wrapper.query().convert()
        return math.ceil(int(results["results"]["bindings"][0]["callret-0"]["value"]) / 10000) + 1
