"""
Copyright: Etheridge Family Nov 2022
Author: Brian Etheridge
"""
import os, platform, c4d

try:
    # R2023
    import configparser as configurator
    print("*** Ranger plugin started")
except:
    # Prior to R2023
    import ConfigParser as configurator
    print("** Ranger plugin started")

__root__ = os.path.dirname(os.path.dirname(__file__))

RANGE_FROM = "RANGE_FROM"
RANGE_TO = "RANGE_TO"
RANGE_STEP = "RANGE_STEP"
FRAME_RATE = "FRAME_RATE"

CONFIG_SECTION = 'CONFIG'
CONFIG_RANGER_SECTION = 'RANGER'

CONFIG_FILE = __root__ + '/config/properties.ini'

# ===================================================================
def get_config_values():
# ===================================================================
    # Returns entries in the config file
    # .....................................................
    config = configurator.ConfigParser()
    # Replace the translate function with 'str', which will stop ini field names from being lower cased
    config.optionxform = str
    config.read(CONFIG_FILE)
      
    return config

# ===================================================================
def get_plugin_directory(dir):
# ===================================================================
    # Returns the full path to a plugin directory
    pluginDir, _ = os.path.split(os.path.dirname(__file__))
    return os.path.join(pluginDir, dir)

# ===================================================================
def update_config_values(section, configFields):
# ===================================================================
    # Updates a list of tuples of config field name and values
    # .....................................................

    config = get_config_values()
    verbose = config.get(CONFIG_SECTION, 'verbose')
    
    # configfields is a list of tuples:
    #    [('field name', 'field value'), ('field name', 'field value'), ...]
    #
    for field in configFields:
        if True == verbose:
            print("Config out: ", field[0], field[1])
        config.set(section, field[0], field[1])

    with open(CONFIG_FILE, 'w') as configFile:
        config.write(configFile)
        
    return config 

# ===================================================================
def analyse_frame_ranges(frameRangeStr):
# ===================================================================
    # Analyses a string of frame ranges, validates them and returns a list of them
    # .....................................................

    config = get_config_values()
    verbose = config.get(CONFIG_SECTION, 'verbose')

    # Remove all spaces
    frameRangeLst = frameRangeStr.replace(' ', '').split(',')
    rangeArray = []

    for entry in frameRangeLst:
        # Range should be number-number
        rangelet = entry.split('-')
        if 1 == len(rangelet):
            # Build a rangelet from what we've been given, e.g. 12 -> 12-12
            rangelet = [rangelet[0], rangelet[0]]
        if True == verbose:
            print("Adjusted rangelet: ", rangelet)
        # Check what we've got
        if 2 < len(rangelet):
            if True == verbose:
                print("Error: Ignoring invalid rangelet: ", str(rangelet))
            continue
        elif True != str(rangelet[0]).isdigit() or True != str(rangelet[1]).isdigit():
            if True == verbose:
                print("Error: Ignoring non-integer rangelet: ", str(rangelet))
            continue
        elif int(rangelet[1]) < int(rangelet[0]):
            el = rangelet[0]
            rangelet[0] = rangelet[1]
            rangelet[1] = el
            
        rangeArray.append(rangelet)

    return normalise_frame_ranges(rangeArray)

# ===================================================================
def sortNumeric(val):
# ===================================================================
    # We sort on the first element of the array, but make sure it is
    # a numeric comparison so that 7 is before 15 (ie '7' > '15')
    return int(val[0])

# ===================================================================
def normalise_frame_ranges(rangeArray):
# ===================================================================
    # Check that the set of rangelets make sense
    # .....................................................
    # If we have one or no ranges specified then nothing to do here
    if 1 >= len(rangeArray):
        return []

    # Do a numeric sort into ascending order
    rangeArray.sort(key=sortNumeric)
    outArray = []
    for elem in rangeArray:
        outArrayLen = len(outArray)
        if 0 >= outArrayLen:
            outArray.append(elem)
            continue

        # If start of range is less than or equal to end of range plus 1
        # E.g. 1-1, 2-6, combine them
        if int(elem[0]) <= int(outArray[outArrayLen - 1][1]) + 1:
            if int(elem[1]) >= int(outArray[outArrayLen - 1][1]):
                outArray[outArrayLen - 1][1] = elem[1]
            # We have adjusted the out array and do not need the element
            continue

        # Just add this new rangelet to out array
        outArray.append(elem)

    returnStr = sep = ''
    for elem in outArray:
        returnStr += sep + str(elem[0]) + '-' + str(elem[1])
        sep = ','

    return returnStr

# ===================================================================
def get_render_settings():
# ===================================================================
    # Gets render settings from the current active set
    # .....................................................

    activeDocument = c4d.documents.GetActiveDocument()
    renderData = activeDocument.GetActiveRenderData()

    return {
        RANGE_FROM: int(renderData[c4d.RDATA_FRAMEFROM].Get() * renderData[c4d.RDATA_FRAMERATE]),
        RANGE_TO: int(renderData[c4d.RDATA_FRAMETO].Get() * renderData[c4d.RDATA_FRAMERATE]),
        RANGE_STEP: renderData[c4d.RDATA_FRAMESTEP],
        FRAME_RATE: int(renderData[c4d.RDATA_FRAMERATE])
    }

# ===================================================================
def get_projectFullPath():
# ===================================================================
    # Gets project full path and name from the currently loaded project
    # .................................................................

    md = c4d.documents.GetActiveDocument()
    path = c4d.documents.BaseDocument.GetDocumentPath(md)
    name = c4d.documents.BaseDocument.GetDocumentName(md)

    print("NB Project path is: ", path)
    print("NB Project name is: ", name)

    c4dProjectFullPath = ''
    if '' == path:
        print("*** A project has not yet been opened for full path")
    else:
        c4dProjectFullPath = os.path.join(path, c4d.documents.BaseDocument.GetDocumentName(md))
        print("NB Project opened is: ", c4dProjectFullPath)

    return c4dProjectFullPath

# ===================================================================
def get_projectPath():
# ===================================================================
    # Gets project path from the currently loaded project
    # ...................................................

    md = c4d.documents.GetActiveDocument()
    path = c4d.documents.BaseDocument.GetDocumentPath(md)
    if '' == path:
        print("*** A project has not yet been opened for path")

    return path

# ===================================================================
def get_projectName():
# ===================================================================
    # Gets project name from the currently loaded project
    # ...................................................

    md = c4d.documents.GetActiveDocument()
    if '' == md:
        print("*** A project has not yet been opened for name")
        return ''

    projectName = c4d.documents.BaseDocument.GetDocumentName(md)
    print("*** Project name is ", projectName)

    return projectName

# ===================================================================
def str_to_bool(str):
# ===================================================================
    if str == 'True':
         return True

    # Anything else
    return False
