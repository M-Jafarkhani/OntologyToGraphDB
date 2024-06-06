class Property:
    label: str
    prop_type: str

    def __init__(self, label, prop_type):
        self.label = label
        self.prop_type = prop_type


class ClassMetaData:
    label: str
    properties: list[Property]

    def __init__(self, label):
        self.label = label
        self.properties = list()


class DataTypePropertyMetaData:
    label: str
