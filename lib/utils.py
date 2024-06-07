import pickle
import os
import shutil
from urllib.parse import urlparse

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
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
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

def get_last_part(url):
    parsed_url = urlparse(url)
    return parsed_url.path.split('/')[-1]      

def sanitize_node_name(node_name):
    if node_name[0].isdigit():
        node_name = '_' + node_name
    translation_table = str.maketrans(",()%'–&-!.’+:", "_____________")
    return node_name.translate(translation_table)  
