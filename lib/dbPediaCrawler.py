import pickle
import shutil
from SPARQLWrapper import SPARQLWrapper, JSON
from lib.utils import *
import os
import json
import math


class DBPediaCrawler:
    """
    A Python class for connection to DBPedia and extracting data using SPARQL endpint of DBPedia.

    ...

    Attributes
    ----------
    namespace : str
        List of namespaces required for SPARQL queries
    limit : str
        The limit-per-request specidifed by DBPedia for each SPARQL query, which is 10,000

    Methods
    -------
    start() -> None:
        Starts the query-and-retrieve process.

    query_class(cls_iri: str, cls_metadata: ClassMetaData) -> None:
        Creates SPARQL query for retrieving class data, then runs the queries and saves data into jSON format.

    query_object_properties(obj_prop_metadata: ObjectPropertyMetaData) -> None:
        Creates SPARQL query for retrieving object properties (or relations) between classes, 
        then runs the queries and saves data into JSON format.      
    
    get_offset_count(cls_var_label: str, where_str: str) -> tuple[int,int]:
        Counts the records per class or object property, which is required for pagination.
        It returns the count and the offset size.
    """

    namespace = """ 
                PREFIX dbo: <http://dbpedia.org/ontology/>
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    """
    limit = '10000'

    def __init__(self) -> None:
        """
        Here we populate self.classes and self.object_properties dictionries, from "metadata/Classes" and 
        "metadata/Object Properties" files, respectively. We also delete the "data" folder, if it already exists.

        Parameters
        ----------
        None
        """

        print('Step 2, Accessing DBPedia '.ljust(129, '#'))
        self.classes: dict[str, ClassMetaData] = dict()
        self.object_properties: list[ObjectPropertyMetaData] = []
        self.wrapper = SPARQLWrapper("https://dbpedia.org/sparql")
        currrent_director = os.getcwd()
        directory_path = os.path.join(currrent_director + '/metadata')
        with open(f"{directory_path}/Classes", "rb") as file:
            self.classes = pickle.load(file)
        with open(f"{directory_path}/Object Properties", "rb") as file:
            self.object_properties = pickle.load(file)
        if os.path.exists(os.path.join(currrent_director + '/data')):
            shutil.rmtree(os.path.join(currrent_director + '/data'))

    def start(self) -> None:
        """
        Starts the query-and-retrieve process. First we query the classes, then object properties, and save them into
        their corresponding folders.

        Parameters
        ----------
        None
        """
        for cls_iri, cls_metadata in self.classes.items():
            self.query_class(cls_iri, cls_metadata)
        for obj_prop_metadata in self.object_properties:
            self.query_object_properties(obj_prop_metadata)
        dump_metadata_to_file(self.classes, self.object_properties)

    def query_class(self, cls_iri: str, cls_metadata: ClassMetaData) -> None:
        """
        Creates SPARQL query for retrieving class data, and runs the queries.
        Finally it saves each class data into a folder with that class name, in the "data/Classes" folder.
        Each query batch is saved with its offset in the JSON format.

        Parameters
        ----------
        cls_iri: str
            IRI of the class, which is extracted from the given ontology.

        cls_metadata: ClassMetaData
            Metadata object of the class, which are extracted from the given ontology.
        """
        if len(cls_metadata.parentClass) > 0:
            return
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
        predicate_on_domain = []
        predicate_on_domain_target = []
        predicate_on_range = []
        predicate_on_range_subject = []
        for obj_prop_metadata in self.object_properties:
            if obj_prop_metadata.domain_iri == cls_iri:
                predicate_on_domain.append(obj_prop_metadata.iri)
                predicate_on_domain_target.append(obj_prop_metadata.range_iri)
            elif obj_prop_metadata.range_iri == cls_iri:
                predicate_on_range.append(obj_prop_metadata.iri)
                predicate_on_range_subject.append(obj_prop_metadata.domain_iri)
        where_str += ' UNION '.join(f'{{ ?{cls_var_label} <{predicate}> ?a. ?a a <{object}> }}\n' for predicate,
                                    object in zip(predicate_on_domain, predicate_on_domain_target))
        if (len(predicate_on_domain) > 0 and len(predicate_on_range) > 0):
            where_str += ' UNION '
        where_str += ' UNION '.join(f'{{ ?a <{predicate}> ?{cls_var_label}. ?a a <{subject}> }}\n' for subject,
                                    predicate in zip(predicate_on_range_subject, predicate_on_range))
        for subClass_iri, subClass_metadata in self.classes.items():
            if subClass_metadata.parentClass == cls_iri:
                appended_where_str = ''
                for obj_prop_meatdata in self.object_properties:
                    if obj_prop_meatdata.range_iri == subClass_iri:
                        src_label = self.classes[obj_prop_meatdata.domain_iri].label.replace(
                            ' ', '_').lower()
                        appended_where_str += f'?{src_label} a <{obj_prop_meatdata.domain_iri}>. ?{src_label} <{obj_prop_meatdata.iri}> ?{cls_var_label}.'
                where_str += 'UNION {' + '?' + cls_var_label + ' a ' + \
                    ' <' + subClass_iri + '>. ' + appended_where_str + ' }\n'
                select_str += f" (SAMPLE(?Is_{subClass_metadata.label}) AS ?Is_{subClass_metadata.label}) "
        for subClass_iri, subClass_metadata in self.classes.items():
            if subClass_metadata.parentClass == cls_iri:
                where_str += 'BIND(IF(EXISTS { ' + '?' + cls_var_label + \
                    ' a ' + ' <' + subClass_iri + '> }, 1, 0) AS ?Is_' + \
                    subClass_metadata.label + ' )\n'
        total_count, offset_count = self.get_offset_count(
            cls_var_label, where_str)
        directory_path = os.path.join(
            os.getcwd() + '/data/Classes', cls_metadata.label)
        os.makedirs(directory_path, exist_ok=True)
        self.classes[cls_iri].folder_path = directory_path
        progress_prefix = f'Node: {cls_metadata.label}, Total: {total_count:,}:'.ljust(
            60)
        for i in range(offset_count):
            query = """
                %s
                SELECT DISTINCT %s  
                WHERE { %s }
                GROUP BY ?%s
                LIMIT %s
                OFFSET  %s%s """ % (self.namespace, select_str, where_str, cls_var_label, self.limit, str(i), self.limit[1:])
            self.wrapper.setQuery(query)
            self.wrapper.setReturnFormat(JSON)
            results = self.wrapper.query().convert()
            with open(f"{directory_path}/{i}", "w", encoding='utf8') as f:
                json.dump(results, f, indent=4, ensure_ascii=False)
            printProgressBar(
                i + 1, offset_count, prefix=progress_prefix, suffix='Complete', length=50)

    def query_object_properties(self, obj_prop_metadata: ObjectPropertyMetaData) -> None:
        """
        Creates SPARQL query for retrieving object properties data, and runs the queries.
        Finally it saves each object properties data into a folder with that relation name, 
        in the "data/Object Properties" folder. Each query batch is saved with its offset in the JSON format.

        Parameters
        ----------
        obj_prop_metadata: ObjectPropertyMetaData
            Metadata object of the object property, which are extracted from the given ontology.
        """

        domain_label_var_label = obj_prop_metadata.domain_label.replace(
            ' ', '_').lower()
        range_label_var_label = obj_prop_metadata.range_label.replace(
            ' ', '_').lower()
        select_str = '?' + domain_label_var_label + ' ,?' + range_label_var_label
        where_str = """
            ?%s <%s> ?%s .
            ?%s a <%s> .
            ?%s a <%s>
        """ % (domain_label_var_label, obj_prop_metadata.iri, range_label_var_label, domain_label_var_label, obj_prop_metadata.domain_iri, range_label_var_label, obj_prop_metadata.range_iri)
        folder_name = f"{obj_prop_metadata.domain_label}_{obj_prop_metadata.label}_{obj_prop_metadata.range_label}"
        directory_path = os.path.join(
            os.getcwd() + '/data/Object Properties', folder_name)
        os.makedirs(directory_path, exist_ok=True)
        for index, item in enumerate(self.object_properties):
            if item.iri == obj_prop_metadata.iri and \
                    item.domain_iri == obj_prop_metadata.domain_iri and \
                        item.range_iri == obj_prop_metadata.range_iri:
                self.object_properties[index].folder_path = directory_path
                break
        total_count, offset_count = self.get_offset_count(
            domain_label_var_label, where_str)
        progress_prefix = f'Edge: {folder_name}, Total: {total_count:,}:'.ljust(
            60)
        for i in range(offset_count):
            query = """
                  %s
                  SELECT DISTINCT %s  
                  WHERE { %s }
                  LIMIT %s
                  OFFSET  %s%s """ % (self.namespace, select_str, where_str, self.limit, str(i), self.limit[1:])
            self.wrapper.setQuery(query)
            self.wrapper.setReturnFormat(JSON)
            results = self.wrapper.query().convert()
            with open(f"{directory_path}/{i}", "w", encoding='utf8') as f:
                json.dump(results, f, indent=4, ensure_ascii=False)
            printProgressBar(
                i + 1, offset_count, prefix=progress_prefix, suffix='Complete', length=50)

    def get_offset_count(self, var_label: str, where_str: str) -> tuple[int,int]:
        """
        Counts the records per class or object property, which is required for pagination. We create the COUNT query and then run it.
        The output is a tuple which specifies the total count and the offset count. 
        For example, if a class or object property has 25,325 records, with the limit specified as 10,000, the output is (25,325, 3).
        The offset is calculated with math.ceiling(25,325/10,000), which means that we have to access DBPedia 4 times 
        to get all the data.

        Parameters
        ----------
        var_label: str
            The class variable of the SPARQL query.

        where_str: str
            The WHERE expression specific for each class.

        Returns
        -------
        tuple[int,int]
            First item is total records counts and the second one is offset size.    
        """

        query = """
            SELECT COUNT (DISTINCT ?%s)  
            WHERE { %s } """ % (var_label, where_str)
        self.wrapper.setQuery(query)
        self.wrapper.setReturnFormat(JSON)
        results = self.wrapper.query().convert()
        total = int(results["results"]["bindings"][0]["callret-0"]["value"])
        return (total, math.ceil(total / int(self.limit)))
