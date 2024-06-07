from typing import Dict
from lib.utils import ClassMetaData, DataEncoder, ObjectPropertyMetaData, Property
from lxml import etree
import requests
from urllib.parse import urlparse
import os
import json


class OntologyCrawler:

    classesMetaData: Dict[str, ClassMetaData] = dict()
    objectPropertiesMetaData: Dict[str, ObjectPropertyMetaData] = dict()

    def __init__(self, file, url):
        self.file = file
        self.url = url

    def start(self) -> (Dict[str, ClassMetaData]):
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
            self.classesMetaData[class_iri] = ClassMetaData(label=class_label)

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

            objProperty_domain_label = self.get_last_part(objProperty_domain)
            objProperty_range_label = self.get_last_part(objProperty_range)

            if objProperty_domain in self.classesMetaData:
                objProperty_domain_label = self.classesMetaData[objProperty_domain].label

            if objProperty_range in self.classesMetaData:
                objProperty_range_label = self.classesMetaData[objProperty_range].label

            self.objectPropertiesMetaData[objProperty_iri] = ObjectPropertyMetaData(
                objProperty_label, objProperty_domain, objProperty_domain_label, objProperty_range, objProperty_range_label)

            self.dump_metadata_to_file(
                self.classesMetaData, self.objectPropertiesMetaData)

    def dump_metadata_to_file(self, classesMetaData: Dict[str, ClassMetaData], objectPropertiesMetaData: Dict[str, ObjectPropertyMetaData]):
        new_directory_path = os.path.join(os.getcwd() + '/metadata')

        os.makedirs(new_directory_path, exist_ok=True)

        with open(f"{new_directory_path}/Classes.json", "w", encoding='utf8') as f:
            json.dump(classesMetaData, f, indent=4,
                      ensure_ascii=False, cls=DataEncoder)

        with open(f"{new_directory_path}/Object Properties.json", "w", encoding='utf8') as f:
            json.dump(objectPropertiesMetaData, f,
                      indent=4, ensure_ascii=False, cls=DataEncoder)

    def get_last_part(self, url):
        parsed_url = urlparse(url)
        return parsed_url.path.split('/')[-1]
