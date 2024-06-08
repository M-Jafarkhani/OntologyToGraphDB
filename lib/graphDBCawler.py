import pickle
from lib.utils import ClassMetaData, ObjectPropertyMetaData, get_last_part, sanitize_node_name
import os
import json


class GraphDBCawler:

    def __init__(self):
        self.classes: dict[str, ClassMetaData] = dict()
        self.object_properties: dict[str, ObjectPropertyMetaData] = dict()

        directory_path = os.path.join(os.getcwd() + '/metadata')

        with open(f"{directory_path}/Classes", "rb") as file:
            self.classes = pickle.load(file)

        with open(f"{directory_path}/Object Properties", "rb") as file:
            self.object_properties = pickle.load(file)

    def start(self):
        directory_path = os.path.join(os.getcwd() + '/cypher')
        os.makedirs(f"{directory_path}/Classes/", exist_ok=True)

        for _, cls_metadata in self.classes.items():
            script = ''
            with open(f"{directory_path}/Classes/{cls_metadata.label}.cypher", "w+") as cypher:
                folder_path = cls_metadata.folder_path
                for file_name in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, file_name)
                    with open(file_path, "r") as file:
                        print(file.name)
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
                        script = ''
                print('Closing  file')    
                cypher.close()            

        