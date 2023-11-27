"""
Copyright: Etheridge Family Nov 2022
Author: Brian Etheridge
"""
import c4d, time
from c4d import documents
from c4d import gui
import r_functions

SLEEP_LIMIT = 3

config = r_functions.get_config_values()
debug = bool(int(config.get(r_functions.CONFIG_SECTION, 'debug')))
verbose = bool(int(config.get(r_functions.CONFIG_SECTION, 'verbose')))

# ===================================================================
def handle_render_queue(customFrameRanges):
# ===================================================================
    # Submits a render request for one or more frames to the BatchRender queue
    # ........................................................................

    try:
        if True == debug:
            print("*** In handle_render_queue")

        doc = documents.GetActiveDocument()
        docPath = r_functions.get_projectPath()
        docFullPath = r_functions.get_projectFullPath()

        if True == debug:
            print("*** Saving to docPath: ", docPath)
            print("*** Doc full path: ", docFullPath)

        # Retrieve the batch render instance
        br = documents.GetBatchRender()
        if br is None:
            raise RuntimeError("Failed to retrieve the batch render instance.")

        rangesStillToDo = customFrameRanges
        frameRanges = customFrameRanges.split(',')
        sleepCount = 0
        for range in frameRanges:

            while True:
                if br.IsRendering():
                    if True == debug:
                        print("*** Sleeping: ", sleepCount)

                    sleepCount += 1
                    if SLEEP_LIMIT <= sleepCount:
                        raise RuntimeError("Render queue is too busy.  Unable to process: " + rangesStillToDo + " Please try again later.")

                    time.sleep(1)
                    continue

                else:
                    break

            sleepCount = 0
            # We can successfully render this range, remove it from set of ranges
            rangesStillToDo = rangesStillToDo.replace(range + ',', '')

            rangeLimits = range.split('-')
            frameFrom = int(rangeLimits[0])
            frameTo = int(rangeLimits[1])
            if True == debug:
                print("Adding entry for range limit from: ", frameFrom, " to ", frameTo)

            # Set the chunk frame range in this instance of the project
            renderData = doc.GetActiveRenderData()
            renderData[c4d.RDATA_FRAMEFROM] = c4d.BaseTime(frameFrom, renderData[c4d.RDATA_FRAMERATE])
            renderData[c4d.RDATA_FRAMETO] = c4d.BaseTime(frameTo, renderData[c4d.RDATA_FRAMERATE])
            # Update the project with the new details
            doc.SetActiveRenderData(renderData)

            missingAssets = []
            assets = []
            res = c4d.documents.SaveProject(doc, c4d.SAVEPROJECT_ASSETS | c4d.SAVEPROJECT_SCENEFILE | c4d.SAVEPROJECT_USEDOCUMENTNAMEASFILENAME, docPath, assets, missingAssets)
            if True == res:
                if True == debug:
                    print("*** Success saving project with assets")
            else:
                raise RuntimeError("*** Error saving project with assets")

            # What is the active doc full path now?
            docFullPath = r_functions.get_projectFullPath()
            if True == debug:
                print("*** Doc full path added to queue: ", docFullPath)

            # Add the project to the end of the queue
            br.AddFile(docFullPath, br.GetElementCount())

            # We have to render the frames immediately to get the right ones rendered, as c4d
            # does not save the render settings with the queue entry
            br.SetRendering(c4d.BR_START)
            if True == debug:
                print("*** Render queue started")

        return True

    except Exception as e:
        message = "Error trying to add render request to queue. Error message: " + str(e)
        print(message)
        gui.MessageDialog(message)

        return False
