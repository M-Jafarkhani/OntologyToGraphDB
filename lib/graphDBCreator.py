import time
from typing import Dict
from lib.utils import ClassMetaData, ObjectPropertyMetaData, printProgressBar
import os
import json
import math


class GraphDBCreator:

    def __init__(self, classes: Dict[str, ClassMetaData], object_properties: Dict[str, ObjectPropertyMetaData]):
        self.classes = classes
        self.object_properties = object_properties

    def start(self):
        pass

    
