class Property:
    label: str
    prop_iri: str

    def __init__(self, label, prop_iri):
        self.label = label
        self.prop_iri = prop_iri


class ClassMetaData:
    label: str
    properties: list[Property]

    def __init__(self, label):
        self.label = label
        self.properties = list()


class DataTypePropertyMetaData:
    label: str
