import pickle
import time
from lib.utils import *
import os
import json


class GraphDBGenerator:
    dbPedia_uri = 'http://dbpedia.org/resource'

    def __init__(self):
        self.classes: dict[str, ClassMetaData] = dict()
        self.object_properties: dict[str, ObjectPropertyMetaData] = dict()
        directory_path = os.path.join(os.getcwd() + '/metadata')
        with open(f"{directory_path}/Classes", "rb") as file:
            self.classes = pickle.load(file)
        with open(f"{directory_path}/Object Properties", "rb") as file:
            self.object_properties = pickle.load(file)

    def start(self):
        self.create_script_for_classes()
        self.create_script_for_object_properties()

    def create_script_for_classes(self):
        class_directory_path = os.path.join(os.getcwd() + '/cypher')
        os.makedirs(f"{class_directory_path}/Classes/", exist_ok=True)
        for _, cls_metadata in self.classes.items():
            progress_prefix = f'Creating script for Class ({cls_metadata.label}):'
            script = ''
            with open(f"{class_directory_path}/Classes/{cls_metadata.label}.cypher", "w+") as cypher:
                folder_path = cls_metadata.folder_path
                total_count = len(os.listdir(folder_path))
                for index, file_name in enumerate(os.listdir(folder_path)):
                    file_path = os.path.join(folder_path, file_name)
                    with open(file_path, "r") as file:
                        data = json.load(file)
                        variables = data['head']['vars']
                        bindings = data['results']['bindings']
                        for record in bindings:
                            vars_script = ''
                            record_iri = ''
                            class_name = ''
                            node_name = ''
                            for variable in variables:
                                if variable not in record:
                                    continue
                                if variable.lower() == cls_metadata.label.lower():
                                    record_iri = record[f"{variable}"]['value']
                                    node_name = sanitize_node_name(
                                        get_last_part(record_iri))
                                    class_name = variable.upper()
                                    vars_script += f"IRI" + ":\"" + record_iri + "\","
                                else:
                                    if record[f"{variable}"]['type'] == "typed-literal":
                                        vars_script += f"{variable}" + ":" + \
                                            record[f"{variable}"]['value'] + ","
                                    else:
                                        vars_script += f"{variable}" + ":\"" + \
                                            record[f"{variable}"]['value'] + "\","
                            script += f"CREATE ({node_name}:{class_name} {{{vars_script[:-1]}}})\n"
                        cypher.write(script)
                        cypher.flush()
                        time.sleep(0.1)
                        printProgressBar(
                            index + 1, total_count, prefix=progress_prefix, suffix='Complete', length=50)
                        script = ''
                cypher.close()

    def create_script_for_object_properties(self):
        object_properties_directory_path = os.path.join(
            os.getcwd() + '/cypher')
        os.makedirs(
            f"{object_properties_directory_path}/Object Properties/", exist_ok=True)
        for _, object_prop_metadata in self.object_properties.items():
            progress_prefix = f'Creating script for Object Properties ({object_prop_metadata.label}):'
            script = ''
            edge_name = sanitize_node_name(object_prop_metadata.label)
            with open(f"{object_properties_directory_path}/Object Properties/{object_prop_metadata.label}.cypher", "w+") as cypher:
                folder_path = object_prop_metadata.folder_path
                total_count = len(os.listdir(folder_path))
                for index, file_name in enumerate(os.listdir(folder_path)):
                    file_path = os.path.join(folder_path, file_name)
                    with open(file_path, "r") as file:
                        data = json.load(file)
                        bindings = data['results']['bindings']
                        subject = data['head']['vars'][0]
                        object = data['head']['vars'][1]
                        for record in bindings:
                            subject_uri = record[f"{subject}"]['value']
                            object_uri = record[f"{object}"]['value']
                            if self.dbPedia_uri not in subject_uri or self.dbPedia_uri not in object_uri:
                                continue
                            subject_node = sanitize_node_name(
                                get_last_part(subject_uri))
                            object_node = sanitize_node_name(
                                get_last_part(object_uri))
                            script += f"CREATE ({subject_node})-[:{edge_name}]->({object_node})\n"
                        cypher.write(script)
                        cypher.flush()
                        time.sleep(0.1)
                        printProgressBar(
                            index + 1, total_count, prefix=progress_prefix, suffix='Complete', length=50)
                        script = ''
                cypher.close()
