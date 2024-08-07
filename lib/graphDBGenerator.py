import pickle
import time
from lib.utils import *
import os
import json


class GraphDBGenerator:
    """
    A Python class for creating Neo4j cypher files from JSON data.

    ...

    Attributes
    ----------
    dbPedia_uri : str
        The prefix URI of instances in DBPedia. We ignore those instances that their IRI has not this prefix.

    Methods
    -------
    start() -> None:
        Starts the script-generation process.

    create_script_for_classes() -> None:
        Creates cypher files for nodes from extracted JSON data.

    create_script_for_object_properties() -> None:
        Creates cypher files for edges from extracted JSON data.
    """

    dbPedia_uri = 'http://dbpedia.org/resource'

    def __init__(self) -> None:
        """
        Here we populate self.classes and self.object_properties dictionries, from "metadata/Classes" and 
        "metadata/Object Properties" files, respectively. We also delete the "cypher" folder, if it already exists.

        Parameters
        ----------
        None
        """
        self.classes: dict[str, ClassMetaData] = dict()
        self.object_properties: list[ObjectPropertyMetaData] = []
        currrent_director = os.getcwd()
        directory_path = os.path.join(currrent_director + '/metadata')
        with open(f"{directory_path}/Classes", "rb") as file:
            self.classes = pickle.load(file)
        with open(f"{directory_path}/Object Properties", "rb") as file:
            self.object_properties = pickle.load(file)
        if os.path.exists(os.path.join(currrent_director + '/cypher')):
            shutil.rmtree(os.path.join(currrent_director + '/cypher'))

    def start(self) -> None:
        """
        Starts the cypher-file-generation process. We read the JSON data from "data" folder and create corresponding 
        neo4j cypher files into separate folders. We also create a "All.cypher" file which contains all the scripts, combined.

        Parameters
        ----------
        None
        """
        print('Step 3, Creating Scripts '.ljust(129, '#'))
        self.create_script_for_classes()
        self.create_script_for_object_properties()

    def create_script_for_classes(self) -> None:
        """
        We read JSON data that are in "data/Classes" folder for each class, and then generate the script for nodes.
        Each class record corresponds to one node in the final cypher file. 
        At the end, each offset file in the "data/Classes" is mapped to one cypher file, named with its offset.
        
        Parameters
        ----------
        None
        """
        class_directory_path = os.path.join(os.getcwd() + '/cypher')
        os.makedirs(f"{class_directory_path}/Classes/", exist_ok=True)
        all_scripts_file = open(f"{class_directory_path}/All.cypher", "a+")
        for _, cls_metadata in self.classes.items():
            if len(cls_metadata.parentClass) > 0:
                continue
            nodes_set = set()
            progress_prefix = f'Node: {cls_metadata.label}'.ljust(60)
            folder_path = cls_metadata.folder_path
            total_count = len(os.listdir(folder_path))
            os.makedirs(
                f"{class_directory_path}/Classes/{cls_metadata.label}", exist_ok=True)
            for index, file_name in enumerate(os.listdir(folder_path)):
                with open(f"{class_directory_path}/Classes/{cls_metadata.label}/{file_name}.cypher", "w+") as cypher:
                    file_path = os.path.join(folder_path, file_name)
                    with open(file_path, "r") as file:
                        script = ''
                        data = json.load(file)
                        variables = data['head']['vars']
                        bindings = data['results']['bindings']
                        for record in bindings:
                            vars_script = ''
                            record_iri = ''
                            class_name = ''
                            node_name = ''
                            extended_classes = ' '
                            for variable in variables:
                                if variable not in record:
                                    continue
                                if variable.lower() == cls_metadata.label.lower():
                                    record_iri = record[f"{variable}"]['value']
                                    node_name = sanitize_node_name(
                                        get_last_part(record_iri))
                                    class_name = variable.upper()
                                    vars_script += f"IRI" + ":\"" + record_iri + "\","
                                elif 'Is_' in variable:
                                    if record[f"{variable}"]['value'] == '1':
                                        extended_classes += ':' + \
                                            variable.removeprefix(
                                                'Is_').upper() + ' '
                                else:
                                    vars_script += f"{variable}" + ":\"" + \
                                        record[f"{variable}"]['value'].replace(
                                            '"', ('\'')).replace('\\', ('\'')) + "\","
                            if node_name not in nodes_set:
                                script += f"CREATE ({node_name}:{class_name}{extended_classes} {{{vars_script[:-1]}}})\n"
                                nodes_set.add(node_name)
                            else:
                                continue
                        cypher.write(script)
                        cypher.flush()
                        all_scripts_file.write(script)
                        all_scripts_file.flush()
                        time.sleep(0.1)
                        printProgressBar(
                            index + 1, total_count, prefix=progress_prefix, suffix='Complete', length=50)
                    cypher.write(';')
                    cypher.close()
                    all_scripts_file.write('\n')
        all_scripts_file.close()

    def create_script_for_object_properties(self) -> None:
        """
        We read JSON data that are in "data/Object Properties" folder for each relation, and then generate the script for edges.
        Each object property record corresponds to one edge in the final cypher file. 
        At the end, each offset file in the "data/Properties" is mapped to one cypher file, named with its offset.

        Parameters
        ----------
        None
        """
        object_properties_directory_path = os.path.join(
            os.getcwd() + '/cypher')
        os.makedirs(
            f"{object_properties_directory_path}/Object Properties/", exist_ok=True)
        all_scripts_file = open(
            f"{object_properties_directory_path}/All.cypher", "a+")
        for object_prop_metadata in self.object_properties:
            os.makedirs(
                f"{object_properties_directory_path}/Object Properties/{object_prop_metadata.label}", exist_ok=True)
            progress_prefix = f'Edge: {object_prop_metadata.label}'.ljust(60)
            script = ''
            edge_name = sanitize_node_name(object_prop_metadata.label)
            folder_path = object_prop_metadata.folder_path
            for index, file_name in enumerate(os.listdir(folder_path)):
                with open(f"{object_properties_directory_path}/Object Properties/{object_prop_metadata.label}/{file_name}.cypher", "w+") as cypher:
                    total_count = len(os.listdir(folder_path))
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
                        all_scripts_file.write(script)
                        all_scripts_file.flush()
                        time.sleep(0.1)
                        printProgressBar(
                            index + 1, total_count, prefix=progress_prefix, suffix='Complete', length=50)
                        script = ''
                    cypher.write(';')
                    all_scripts_file.write('\n')
                    cypher.close()
        all_scripts_file.close()
