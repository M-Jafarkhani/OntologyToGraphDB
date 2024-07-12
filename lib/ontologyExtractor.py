from lib.utils import *
from lxml import etree
import requests


class OntologyExtractor:
    """
    A Python class for extracting metadata from an OWL-based RDF/XML ontology, and saving them into binary files.

    ...

    Attributes
    ----------
    classesMetaData: dict[str, ClassMetaData]
        A dictionary for storing metadata of classes, with class IRI as the key and their metadata as values.

    objectPropertiesMetaData: list[ObjectPropertyMetaData]
        A list for storing metadata of object properties.

    Methods
    -------
    start() -> None:
        Starts the metadata-extraction process.

    """

    classesMetaData: dict[str, ClassMetaData] = dict()
    objectPropertiesMetaData: list[ObjectPropertyMetaData] = []

    def __init__(self, file: str, url: str) -> None:
        """
        Initilaizes the self.file and self.url properties

        Parameters
        ----------
        file: str
            relative file path to the ontology. 

        url: str
            URL of the ontology.
        """
        self.file = file
        self.url = url

    def start(self) -> None:
        """
        Starts the metadata-extraction process from the specified ontology. Note that ontologies should
        be given in RDF/XML format and match the structure of DBPedia. TO get started, some sample ontologies
        are already given in 'ontologies' folder. If the file path is specified, we read from file, otherwise 
        we read from URL. We extract these metadata using XPATH and save thethe objects into 'metadata' folder.

        We extract the following information from the ontology using XPATH:
            
            - owl:class: Corresponds to a class. We extract :
                -- @rdf:about: Class IRI.
                -- rdfs:label: Label of the class.
                -- rdfs:subClassOf/@rdf:resource: Parent class IRI, if it is a subclass.
            
            - owl:DatatypeProperty: Corresponds to class attributes.  We extract :
                -- @rdf:about: IRI of the attribute.
                -- rdfs:label: Label of the attribute.
                -- rdfs:domain/@rdf:resource: Refers to its class IRI.

            - owl:ObjectProperty: Corresponds to relationships between classes.  We extract : 
                -- @rdf:about: Relation IRI.
                -- rdfs:label: Label of the relation. 
                -- rdfs:domain/@rdf:resource: Domain of the relation, which is a class IRI. 
                -- rdfs:range/@rdf:resource: Range of the relation, , which is a class IRI.
        Parameters
        ----------
        None
        """

        print('Step 1, Crawling Ontology '.ljust(129, '#'))
        if self.file:
            xml_content = open(self.file, 'r').read()
        elif self.url:
            response = requests.get(self.url)
            xml_content = response.content
        else:
            exit()

        xml_tree = etree.fromstring(xml_content)

        namespaces = {
            'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
            'owl': 'http://www.w3.org/2002/07/owl#'
        }

        classes = xml_tree.xpath('//owl:Class', namespaces=namespaces)

        for cls in classes:
            class_iri = cls.xpath('@rdf:about', namespaces=namespaces)[0]
            class_label = cls.xpath(
                "rdfs:label", namespaces=namespaces)[0].text
            subClassOf_element = cls.xpath(
                "rdfs:subClassOf/@rdf:resource", namespaces=namespaces)
            parentClass = ''
            if (len(subClassOf_element) > 0):
                parentClass = str(subClassOf_element[0])
            self.classesMetaData[class_iri] = ClassMetaData(
                label=class_label, parentClass=parentClass)

        dtProperties = xml_tree.xpath(
            '//owl:DatatypeProperty', namespaces=namespaces)

        for dtProperty in dtProperties:
            dtProperty_iri = dtProperty.xpath(
                '@rdf:about', namespaces=namespaces)[0]
            dtProperty_label = dtProperty.xpath(
                "rdfs:label", namespaces=namespaces)[0].text
            dtProperty_domain = dtProperty.xpath(
                "rdfs:domain/@rdf:resource", namespaces=namespaces)[0]

            if dtProperty_domain in self.classesMetaData:
                self.classesMetaData[dtProperty_domain].properties.append(
                    Property(dtProperty_label, dtProperty_iri))

        objProperties = xml_tree.xpath(
            '//owl:ObjectProperty', namespaces=namespaces)

        for objProperty in objProperties:
            objProperty_iri = objProperty.xpath(
                '@rdf:about', namespaces=namespaces)[0]
            objProperty_label = objProperty.xpath(
                "rdfs:label", namespaces=namespaces)[0].text
            objProperty_domain = objProperty.xpath(
                "rdfs:domain/@rdf:resource", namespaces=namespaces)[0]
            objProperty_range = objProperty.xpath(
                "rdfs:range/@rdf:resource", namespaces=namespaces)[0]

            objProperty_domain_label = get_last_part(objProperty_domain)
            objProperty_range_label = get_last_part(objProperty_range)

            if objProperty_domain in self.classesMetaData:
                objProperty_domain_label = self.classesMetaData[objProperty_domain].label

            if objProperty_range in self.classesMetaData:
                objProperty_range_label = self.classesMetaData[objProperty_range].label

            self.objectPropertiesMetaData.append(ObjectPropertyMetaData(
                objProperty_iri, objProperty_label, objProperty_domain, objProperty_domain_label, objProperty_range, objProperty_range_label))

        for _, cls_metadata in self.classesMetaData.items():
            if len(cls_metadata.parentClass) > 0:
                self.classesMetaData[cls_metadata.parentClass].properties.extend(
                    cls_metadata.properties)

        dump_metadata_to_file(self.classesMetaData,
                              self.objectPropertiesMetaData)
