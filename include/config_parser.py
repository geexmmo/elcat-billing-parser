import configparser, logging

def Config_parser(filename, uniqoption):
    config = configparser.ConfigParser(strict=False)
    config.sections()
    config.read(filename)
    section = config.sections()
    dataexport = {}
    for i in section:
        testvalue = config.get(i, uniqoption, fallback=None)
        if testvalue != None:
            dataexport[i] = [config.get(i,'username'),config.get(i,'secret')]
    return dataexport