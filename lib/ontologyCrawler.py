from typing import Dict
from lib.utils import ClassMetaData, Property
from lxml import etree
import requests
import json


class OntologyCrawler:

    classesMetaData: Dict[str, ClassMetaData] = dict()

    def __init__(self, file, url, propertyMappingsFile):
        self.file = file
        self.url = url
        self.propertyMappingsFile = propertyMappingsFile

    def start(self):
        if self.file:
            xml_content = open(self.file, 'r').read()
        elif self.url:
            response = requests.get(self.url)
            xml_content = response.content
        else:
            exit()

        with open(self.propertyMappingsFile, 'r') as file:
            property_mapping = json.load(file)

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

            if dtProperty_range in property_mapping and dtProperty_domain in self.classesMetaData:
                self.classesMetaData[dtProperty_domain].properties.append(
                    Property(dtProperty_label, property_mapping[dtProperty_range]))

        for cls_label, cls in self.classesMetaData.items():
            print(f'------')
            print(f'{cls_label}')
            for prop in cls.properties:
                print(f'{prop.label}-{prop.prop_type}')
            print(f'------')

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