"""
Copyright: Brian Etheridge 2023
Author: Brian Etheridge
"""
import c4d
from c4d import documents

import r_functions

config = r_functions.get_config_values()
debug = bool(int(config.get(r_functions.CONFIG_SECTION, 'debug')))
verbose = bool(int(config.get(r_functions.CONFIG_SECTION, 'verbose')))

# ===================================================================
def handle_render_queue(customFrameRanges, startRenderQueue):
# ===================================================================
    # Submits a render request for one or more frames to the BatchRender queue
    # ........................................................................

    try:
        print("*** In handle_render_queue")

        doc = c4d.documents.GetActiveDocument()
        docFullPath = r_functions.get_projectFullPath()

        # Retrieve the batch render instance
        br = c4d.documents.GetBatchRender()
        if br is None:
            raise RuntimeError("Failed to retrieve the batch render instance.")

        frameRanges = customFrameRanges.split(',')
        for range in frameRanges:
            rangeLimits = range.split('-')

            frameFrom = int(rangeLimits[0])
            frameTo = int(rangeLimits[1])

            print("Adding entry for range limit from: ", frameFrom, " to ", frameTo)

            # Set the chunk frame range in this instance of the project
            renderData = doc.GetActiveRenderData()

            print("*** Render data: ", renderData[c4d.RDATA_FRAMEFROM], " and to ", renderData[c4d.RDATA_FRAMETO])

            renderData[c4d.RDATA_FRAMEFROM] = c4d.BaseTime(frameFrom, renderData[c4d.RDATA_FRAMERATE])
            renderData[c4d.RDATA_FRAMETO] = c4d.BaseTime(frameTo, renderData[c4d.RDATA_FRAMERATE])
            # Update the project with the new details
            doc.SetActiveRenderData(renderData)

            # Add the project to the end of the queue
            br.AddFile(docFullPath, br.GetElementCount())

        if True == startRenderQueue:
            print("*** Start render queue requested")

            br.SetRendering(c4d.BR_START)
            if True == debug:
                print("*** Render queue started")

        else:
            print("*** Start render queue not requested")

        return True

    except Exception as e:
        message = "Error trying to render. Error message: " + str(e)
        print(message)
        print(e.args)

        return False
