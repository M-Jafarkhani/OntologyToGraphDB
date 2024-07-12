import pickle
import os
import shutil


class Property:
    """
    A Python class for storing class properties.

    ...

    Attributes
    ----------
    label: str
        Property label.

    prop_iri: str
        Property IRI.
    """
    label: str
    prop_iri: str

    def __init__(self, label, prop_iri) -> None:
        """
        We set self.label and self.prop_iri attributes.

        Parameters
        ----------
        label: str
            Property label.

        prop_iri: str
            Property IRI.
        """

        self.label = label
        self.prop_iri = prop_iri


class ClassMetaData:
    """
    A Python class for storing class metadata.

    ...

    Attributes
    ----------
    label: str
        Class label.

    parentClass: str
        Parent class IRI, if it is a subclass.

    properties: list[Property]
        List of class properties.

    folder_path: str
        Relative folder path that corresponds to its JSON data location.
    """

    label: str
    parentClass: str
    properties: list[Property]
    folder_path: str

    def __init__(self, label, parentClass) -> None:
        """
        We set self.label and self.parentClass attributes, and init the self.properties to empty list

        Parameters
        ----------
        label: str
            Property label

        prop_iri: str
            Property IRI
        """

        self.label = label
        self.parentClass = parentClass
        self.properties = list()


class ObjectPropertyMetaData:
    """
    A Python class for storing object properties metadata.

    ...

    Attributes
    ----------
    iri: str
        Object property IRI.

    label: str
        Object property label.

    domain_iri: str
        IRI of its domain, which points to a class IRI

    domain_label: str
        Label of its domain, which is a class label

    range_iri: str
        IRI of its range, which points to a class IRI

    range_label: str
        Label of its range, which is a class label

    folder_path: str
        Relative folder path that corresponds to its JSON data location.      
    """

    iri: str
    label: str
    domain_iri: str
    domain_label: str
    range_iri: str
    range_label: str
    folder_path: str

    def __init__(self, iri: str, label: str, domain_iri: str, domain_label: str, range_iri: str, range_label: str) -> None:
        """
        We set self.iri, self.label, self.domain_iri, self.domain_label, self.range_iri and self.range_label of an object property

        Parameters
        ----------
        iri: str
            Object property IRI.

        label: str 
            Object property label.

        domain_iri: str
            IRI of its domain, which points to a class IRI

        domain_label: str
            Label of its domain, which is a class label

        range_iri: str
            IRI of its range, which points to a class IRI

        range_label: str
            Label of its range, which is a class label
        """

        self.iri = iri
        self.label = label
        self.domain_iri = domain_iri
        self.domain_label = domain_label
        self.range_iri = range_iri
        self.range_label = range_label


def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r") -> None:
    """
    This code is copied from Stackoverflow, which helps to print progress bar in the terminal. Available at:
    https://stackoverflow.com/questions/3173320/text-progress-bar-in-terminal-with-block-characters

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


def dump_metadata_to_file(classesMetaData: dict[str, ClassMetaData], objectPropertiesMetaData: list[ObjectPropertyMetaData]) -> None:
    """
    Saves two objects, classesMetaData and objectPropertiesMetaData into a binary file in 'data' folder   

    Parameters
    ----------
    classesMetaData: dict[str, ClassMetaData]
        An dictionary which contains metadata about classes

    objectPropertiesMetaData: list[ObjectPropertyMetaData]
        A list which contains metadata about object properties

    """
    new_directory_path = os.path.join(os.getcwd() + '/metadata')

    if os.path.exists(new_directory_path):
        shutil.rmtree(new_directory_path)

    os.makedirs(new_directory_path, exist_ok=True)

    with open(f"{new_directory_path}/Classes", "wb") as file:
        pickle.dump(classesMetaData, file, pickle.HIGHEST_PROTOCOL)

    with open(f"{new_directory_path}/Object Properties", "wb") as file:
        pickle.dump(objectPropertiesMetaData, file, pickle.HIGHEST_PROTOCOL)


def get_last_part(url: str) -> str:
    """
    Removes the 'http://dbpedia.org/resource/' prefix from an IRI

    Parameters
    ----------
    url: str
        URL or IRI of the class or object property

    objectPropertiesMetaData: list[ObjectPropertyMetaData]
        A list which contains metadata about object properties

    Returns
    -------
    str
        String with the prefix removed.
    """
    return url.removeprefix('http://dbpedia.org/resource/')


def sanitize_node_name(node_name: str) -> str:
    """
    Node name sanitization mechanism, to create node label of neo4j cypher file.
    Simply puts the node_name between two ` characters.

    Parameters
    ----------
    node_name: str
        The node name before sanitaziation

    Returns
    -------
    str
        Node name between two ` characters.
    """
    return f"`{node_name}`"


def sanitize_edge_name(edge_name: str) -> str:
    """
    Edge name sanitization mechanism, to create edge label of neo4j cypher file.
    Simply upper cases all the chararters and replace the spaces with _ character.

    Parameters
    ----------
    edge_name: str
        The edge name before sanitaziation.

    Returns
    -------
    str
        Edge name converted into uppper case with spaces being replaced with _ character.
    """
    return edge_name.upper().replace(' ', '_')
