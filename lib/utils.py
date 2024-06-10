import pickle
import os
import shutil

class Property:
    label: str
    prop_iri: str

    def __init__(self, label, prop_iri):
        self.label = label
        self.prop_iri = prop_iri


class ClassMetaData:
    label: str
    properties: list[Property]
    folder_path: str

    def __init__(self, label):
        self.label = label
        self.properties = list()


class ObjectPropertyMetaData:
    label: str
    domain_iri: str
    domain_label: str
    range_iri: str
    range_label: str
    folder_path: str

    def __init__(self, label, domain_iri, domain_label, range_iri, range_label):
        self.label = label
        self.domain_iri = domain_iri
        self.domain_label = domain_label
        self.range_iri = range_iri
        self.range_label = range_label


def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
    percent = ("{0:." + str(decimals) + "f}").format(100 *
                                                     (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)

    if iteration == total:
        print()


def dump_metadata_to_file(classesMetaData: dict[str, ClassMetaData], objectPropertiesMetaData: dict[str, ObjectPropertyMetaData]):
    new_directory_path = os.path.join(os.getcwd() + '/metadata')

    if os.path.exists(new_directory_path):
        shutil.rmtree(new_directory_path)

    os.makedirs(new_directory_path, exist_ok=True)

    with open(f"{new_directory_path}/Classes", "wb") as file:
        pickle.dump(classesMetaData, file, pickle.HIGHEST_PROTOCOL)

    with open(f"{new_directory_path}/Object Properties", "wb") as file:
        pickle.dump(objectPropertiesMetaData, file, pickle.HIGHEST_PROTOCOL)


def get_last_part(url: str):
    return url.removeprefix('http://dbpedia.org/resource/')

def sanitize_node_name(node_name: str):
    return f"`{node_name}`"

def sanitize_edge_name(edge_name: str):
    return edge_name.upper().replace(' ','_')
