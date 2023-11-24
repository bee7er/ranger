"""
Copyright: Brian Etheridge 2023
Author: Brian Etheridge

Description:
    A Cinema 4D plugin to assist with rendering individual or ranges of frames.
"""

import os, sys

__root__ = os.path.dirname(__file__)
if os.path.join(__root__, 'modules') not in sys.path: sys.path.insert(0, os.path.join(__root__, 'modules'))

import c4d
from c4d import gui, bitmaps, utils
from c4d import documents

# Ranger modules for various shared functions
import r_functions, r_handle_render_queue

__res__ = c4d.plugins.GeResource()
__res__.Init(__root__)

# TODO Unique ID can be obtained from www.plugincafe.com
PLUGIN_ID = 1052323
GROUP_ID = 100000

FRAME_RANGES_TEXT = 100015
EDIT_FRAME_RANGES_TEXT = 100016
START_QUEUE_CHECKBOX_TEXT = 100017
START_QUEUE_CHECKBOX = 100018

config = r_functions.get_config_values()
debug = bool(int(config.get(r_functions.CONFIG_SECTION, 'debug')))
verbose = bool(int(config.get(r_functions.CONFIG_SECTION, 'verbose')))

# ===================================================================
class RangerDlg(c4d.gui.GeDialog):
# ===================================================================

    customFrameRanges = config.get(r_functions.CONFIG_RANGER_SECTION, 'customFrameRanges')
    startRenderQueue = r_functions.str_to_bool(config.get(r_functions.CONFIG_RANGER_SECTION, 'startRenderQueue'))
    rangeFrom = 0
    rangeTo = 0

    # ===================================================================
    def CreateLayout(self):
    # ===================================================================
        """ Called when Cinema 4D creates the dialog """

        renderData = r_functions.get_render_settings()
        self.rangeFrom = renderData[r_functions.RANGE_FROM]
        self.rangeTo = renderData[r_functions.RANGE_TO]

        self.SetTitle("Submit Range Details")

        self.GroupBegin(id=GROUP_ID, flags=c4d.BFH_SCALEFIT, cols=2, rows=5)
        """ Custom ranges field """
        self.AddStaticText(id=FRAME_RANGES_TEXT, flags=c4d.BFV_MASK, initw=145, name="Custom frame ranges: ", borderstyle=c4d.BORDER_NONE)
        self.AddEditText(EDIT_FRAME_RANGES_TEXT, c4d.BFV_MASK, initw=240, inith=16, editflags=0)
        self.SetString(EDIT_FRAME_RANGES_TEXT, self.customFrameRanges)
        """ Start rendering field """
        self.AddStaticText(id=START_QUEUE_CHECKBOX_TEXT, flags=c4d.BFV_MASK, initw=145, name="Start rendering: ", borderstyle=c4d.BORDER_NONE)
        self.AddCheckbox(START_QUEUE_CHECKBOX, flags=c4d.BFH_LEFT, initw=160, inith=22, name="Check to start on OK")
        self.SetBool(START_QUEUE_CHECKBOX, self.startRenderQueue)

        self.AddDlgGroup(c4d.DLG_OK | c4d.DLG_CANCEL)
        self.GroupEnd()

        return True

    # ===================================================================
    def Command(self, messageId, bc):
    # ===================================================================
        """ Called when the user clicks on the dialog, clicks button, etc, or when a menu item selected.

        Args:
            messageId (int): The ID of the resource that triggered the event.
            bc (c4d.BaseContainer): The original message container.

        Returns:
            bool: False on error else True.
        """

        # User click on Ok button
        if messageId == c4d.DLG_OK:

            if '' == r_functions.get_projectFullPath():
                gui.MessageDialog("Please open your project file")
                return True

            self.customFrameRanges = self.GetString(EDIT_FRAME_RANGES_TEXT)
            self.startRenderQueue = self.GetBool(START_QUEUE_CHECKBOX)

            # Analyse the custom frange ranges
            self.customFrameRanges = r_functions.analyse_frame_ranges(self.customFrameRanges)
            if '' == self.customFrameRanges:
                gui.MessageDialog("Please enter at least one valid range, in the format 'm - m, n - n, etc'")
                return False

            # Save changes to the config file
            r_functions.update_config_values(r_functions.CONFIG_RANGER_SECTION, [
                ('customFrameRanges', self.customFrameRanges),
                ('startRenderQueue', self.startRenderQueue)
                ])

            # Create entries in the render queue for the frame ranges entered
            if True == self.submitRangeDetails():
                # Reset the range for the next submission
                self.rangeFrom = 0
                self.rangeTo = 0

                # Close the Dialog
                self.Close()

            else:
                print("Submission of render request cancelled")
                return False

            return True

        # User click on Cancel button
        elif messageId == c4d.DLG_CANCEL:
            if True == verbose:
                print("User clicked Cancel")

            # Close the Dialog
            self.Close()
            return True

        return True

    # ===================================================================
    def submitRangeDetails(self):
    # ===================================================================
        """
        Submit the render request to the master node
        """
        # Get the user to confirm the submission
        yesNo = gui.QuestionDialog(
            "Submitting frames: \n" + self.customFrameRanges + "\n\n" +
            "Click Yes to submit the render request.\n\n"
            )
        if False == yesNo:
            if True == debug:
                print("*** User cancelled the request")
            return False

        if True == r_handle_render_queue.handle_render_queue(self.customFrameRanges, self.startRenderQueue):
            print("*** Custom frame ranges submitted")

        else:
            print("*** Unexpected result from custom frame ranges submission")
            return False

        return True

# ===================================================================
class RangerDlgCommand(c4d.plugins.CommandData):
# ===================================================================
    """Command Data class that holds the RenderDlg instance."""
    dialog = None

    # ===================================================================
    def Execute(self, doc):
    # ===================================================================
        """Called when the user executes a command via either CallCommand() or a click on the Command from the extension menu.

        Args:
            doc (c4d.documents.BaseDocument): The current active document.

        Returns:
            bool: True if the command success.
        """
        # Creates the dialog if it does not already exists
        if self.dialog is None:
            self.dialog = RangerDlg()

        # Opens the dialog
        return self.dialog.Open(dlgtype=c4d.DLG_TYPE_ASYNC, pluginid=PLUGIN_ID, defaultw=400, defaulth=32)

    # ===================================================================
    def RestoreLayout(self, sec_ref):
    # ===================================================================
        """Used to restore an asynchronous dialog that has been placed in the users layout.

        Args:
            sec_ref (PyCObject): The data that needs to be passed to the dialog.

        Returns:
            bool: True if the restore success
        """
        # Creates the dialog if its not already exists
        if self.dialog is None:
            self.dialog = RangerDlg()

        # Restores the layout
        return self.dialog.Restore(pluginid=PLUGIN_ID, secret=sec_ref)

# ===================================================================
# main entry function
# ===================================================================
if __name__ == "__main__":
    if True == verbose:
        print("Setting up Ranger Plugin")

    # Retrieves the icon path
    directory, _ = os.path.split(__file__)
    fn = os.path.join(directory, "res", "icon_ranger.tif")

    # Creates a BaseBitmap
    bbmp = c4d.bitmaps.BaseBitmap()
    if bbmp is None:
        raise MemoryError("Failed to create a BaseBitmap.")

    # Init the BaseBitmap with the icon
    if bbmp.InitWith(fn)[0] != c4d.IMAGERESULT_OK:
        raise MemoryError("Failed to initialise the BaseBitmap.")

    # Registers the plugin
    c4d.plugins.RegisterCommandPlugin(id=PLUGIN_ID,
                                      str="Submit Ranger Details",
                                      info=0,
                                      help="Submit ranger details",
                                      dat=RangerDlgCommand(),
                                      icon=bbmp)

    if True == verbose:
        print("Ranger Details Plugin set up ok")
