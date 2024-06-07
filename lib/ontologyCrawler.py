from typing import Dict
from lib.utils import ClassMetaData, Property
from lxml import etree
import requests
import json


class OntologyCrawler:

    classesMetaData: Dict[str, ClassMetaData] = dict()

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
            dtProperty_range = dtProperty.xpath(
                "rdfs:range/@rdf:resource", namespaces=namespaces)[0]

            if dtProperty_domain in self.classesMetaData:
                self.classesMetaData[dtProperty_domain].properties.append(Property(dtProperty_label,dtProperty_iri))

        objProperties = xml_tree.xpath(
            '//owl:ObjectProperty', namespaces=namespaces) 

        for objProperty in objProperties:
            objProperty_iri = dtProperty.xpath(
                '@rdf:about', namespaces=namespaces)[0]
            objProperty_label = dtProperty.xpath(
                "rdfs:label", namespaces=namespaces)[0].text
            objProperty_domain = dtProperty.xpath(
                "rdfs:domain/@rdf:resource", namespaces=namespaces)[0]
            objProperty_range = dtProperty.xpath(
                "rdfs:range/@rdf:resource", namespaces=namespaces)[0]  

        return self.classesMetaData        