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


class ObjectPropertyMetaData:
    label: str
    domain_iri: str
    domain_label: str
    range_iri: str
    range_label: str

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
    # Print New Line on Complete
    if iteration == total:
        print()
