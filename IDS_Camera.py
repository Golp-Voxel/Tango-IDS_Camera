# -*- coding: utf-8 -*-
#
# This file is part of the IDS_Camera project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

"""
Zelux Thorlabs Camera

This class is to integrate a Zelux Thorlabs Camera.
After installing the Server on the jive/astor you will need to use the Wizard tool 
to difine the proparties of that particular device.
"""

# PROTECTED REGION ID(IDS_Camera.system_imports) ENABLED START #
# PROTECTED REGION END #    //  IDS_Camera.system_imports

# PyTango imports
import tango
from tango import DebugIt
from tango.server import run
from tango.server import Device
from tango.server import attribute, command
from tango.server import device_property
from tango import AttrQuality, DispLevel, DevState
from tango import AttrWriteType, PipeWriteType
# Additional import
# PROTECTED REGION ID(IDS_Camera.additionnal_import) ENABLED START #
import ids_peak.ids_peak as ids_peak
import numpy as np
import ids_peak.ids_peak_ipl_extension as ids_ipl_extension
import ids_peak_ipl.ids_peak_ipl as ids_ipl

# PROTECTED REGION END #    //  IDS_Camera.additionnal_import

__all__ = ["IDS_Camera", "main"]


class IDS_Camera(Device):
    """
    This class is to integrate a Zelux Thorlabs Camera.
    After installing the Server on the jive/astor you will need to use the Wizard tool 
    to difine the proparties of that particular device.

    **Properties:**

    - Device Property
        CameraID
            - Type:'str'
    """
    # PROTECTED REGION ID(IDS_Camera.class_variable) ENABLED START #
    remote_device_nodemap = None
    datastream = None
    device = None
    # PROTECTED REGION END #    //  IDS_Camera.class_variable

    # -----------------
    # Device Properties
    # -----------------

    CameraID = device_property(
        dtype='str',
        mandatory=True
    )

    # ----------
    # Attributes
    # ----------

    ExposureTime = attribute(
        dtype='DevUShort',
        access=AttrWriteType.READ_WRITE,
        label="Exposure time of the camera",
        unit="ms",
        display_unit="ms",
        doc="Exposure time of the camera  in ms ",
    )

    Gain = attribute(
        dtype='DevDouble',
        access=AttrWriteType.READ_WRITE,
    )

    FramesTrigger = attribute(
        dtype='DevUShort',
        access=AttrWriteType.READ_WRITE,
    )

    ROI = attribute(
        dtype=('DevUShort',),
        access=AttrWriteType.READ_WRITE,
        max_dim_x=4,
    )

    Image = attribute(
        dtype=(('DevUShort',),),
        max_dim_x=2474, max_dim_y=2474,
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        """Initializes the attributes and properties of the IDS_Camera."""
        Device.init_device(self)
        self._exposure_time = 20
        self._gain = 0.0
        self._frames_trigger = 0
        self._r_oi = (0,)
        self._image = ((0,),)
        # PROTECTED REGION ID(IDS_Camera.init_device) ENABLED START #
        self.info_stream("\r Try to start the IDS Camera Driver \r")
        print(self.CameraID)
        ids_peak.Library.Initialize()
        device_manager = ids_peak.DeviceManager.Instance()
        device_manager.Update()
        device_descriptors = device_manager.Devices()
        if len(device_descriptors) > 0:
            for device_descriptor in device_descriptors:
                print(device_descriptor.DisplayName())
                if self.CameraID in device_descriptor.DisplayName():
                    self.device = device_descriptor.OpenDevice(ids_peak.DeviceAccessType_Control)
                    self.remote_device_nodemap = self.device.RemoteDevice().NodeMaps()[0]
                    print("Opened Device: " + self.device.DisplayName())
            if self.remote_device_nodemap == None:
                print("Problem connecting to the camera")
                return
        
        self.remote_device_nodemap.FindNode("TriggerSelector").SetCurrentEntry("ExposureStart")
        self.remote_device_nodemap.FindNode("TriggerSource").SetCurrentEntry("Software")
        self.remote_device_nodemap.FindNode("TriggerMode").SetCurrentEntry("On")

        self.datastream = self.device.DataStreams()[0].OpenDataStream()
        payload_size = self.remote_device_nodemap.FindNode("PayloadSize").Value()
        for i in range(self.datastream.NumBuffersAnnouncedMinRequired()):
            buffer = self.datastream.AllocAndAnnounceBuffer(payload_size)
            self.datastream.QueueBuffer(buffer)
            
        self.datastream.StartAcquisition()
        self.remote_device_nodemap.FindNode("AcquisitionStart").Execute()
        self.remote_device_nodemap.FindNode("AcquisitionStart").WaitUntilDone()
        self.remote_device_nodemap.FindNode("ExposureTime").SetValue(self._exposure_time*1000) # in microseconds
        self.set_state(DevState.ON)
        
        # PROTECTED REGION END #    //  IDS_Camera.init_device

    def always_executed_hook(self):
        """Method always executed before any TANGO command is executed."""
        # PROTECTED REGION ID(IDS_Camera.always_executed_hook) ENABLED START #
        # PROTECTED REGION END #    //  IDS_Camera.always_executed_hook

    def delete_device(self):
        """Hook to delete resources allocated in init_device.

        This method allows for any memory or other resources allocated in the
        init_device method to be released.  This method is called by the device
        destructor and by the device Init command.
        """
        # PROTECTED REGION ID(IDS_Camera.delete_device) ENABLED START #
        # PROTECTED REGION END #    //  IDS_Camera.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_ExposureTime(self):
        # PROTECTED REGION ID(IDS_Camera.ExposureTime_read) ENABLED START #
        """Return the ExposureTime attribute."""
        return self._exposure_time
        # PROTECTED REGION END #    //  IDS_Camera.ExposureTime_read
    def write_ExposureTime(self, value):
        # PROTECTED REGION ID(IDS_Camera.ExposureTime_write) ENABLED START #
        """Set the ExposureTime attribute."""
        self._exposure_time = value
        microseconds = int(float(value)*1000)
        self.remote_device_nodemap.FindNode("ExposureTime").SetValue(microseconds) # in microseconds
        pass
        # PROTECTED REGION END #    //  IDS_Camera.ExposureTime_write
    def read_Gain(self):
        # PROTECTED REGION ID(IDS_Camera.Gain_read) ENABLED START #
        """Return the Gain attribute."""
        return self._gain
        # PROTECTED REGION END #    //  IDS_Camera.Gain_read
    def write_Gain(self, value):
        # PROTECTED REGION ID(IDS_Camera.Gain_write) ENABLED START #
        """Set the Gain attribute."""
        pass
        # PROTECTED REGION END #    //  IDS_Camera.Gain_write
    def read_FramesTrigger(self):
        # PROTECTED REGION ID(IDS_Camera.FramesTrigger_read) ENABLED START #
        """Return the FramesTrigger attribute."""
        return self._frames_trigger
        # PROTECTED REGION END #    //  IDS_Camera.FramesTrigger_read
    def write_FramesTrigger(self, value):
        # PROTECTED REGION ID(IDS_Camera.FramesTrigger_write) ENABLED START #
        """Set the FramesTrigger attribute."""
        pass
        # PROTECTED REGION END #    //  IDS_Camera.FramesTrigger_write
    def read_ROI(self):
        # PROTECTED REGION ID(IDS_Camera.ROI_read) ENABLED START #
        """Return the ROI attribute."""
        return self._r_oi
        # PROTECTED REGION END #    //  IDS_Camera.ROI_read
    def write_ROI(self, value):
        # PROTECTED REGION ID(IDS_Camera.ROI_write) ENABLED START #
        """Set the ROI attribute."""
        pass
        # PROTECTED REGION END #    //  IDS_Camera.ROI_write
    def read_Image(self):
        # PROTECTED REGION ID(IDS_Camera.Image_read) ENABLED START #
        """Return the Image attribute."""
        return self._image
        # PROTECTED REGION END #    //  IDS_Camera.Image_read
    # --------
    # Commands
    # --------


    @command(
        dtype_out='DevString',
    )
    @DebugIt()
    def StartAcqusition(self):
        # PROTECTED REGION ID(IDS_Camera.StartAcqusition) ENABLED START #
        """
        This command start the loop of acquiring a image from the camera
        :rtype: PyTango.DevString
        """
        return ""
        # PROTECTED REGION END #    //  IDS_Camera.StartAcqusition

    @command(
        dtype_in='DevString',
        doc_in="A JSON converted in to a string with the following structure",
    )
    @DebugIt()
    def ChangeParameters(self, argin):
        # PROTECTED REGION ID(IDS_Camera.ChangeParameters) ENABLED START #
        """
            This command allows the user to change multiple parameters of the camera at the same time such as:
            Exposure Time
            ROI
            Gain
        :param argin: A JSON converted in to a string with the following structure
        :type argin: PyTango.DevString

        :rtype: PyTango.DevVoid
        """
        pass
        # PROTECTED REGION END #    //  IDS_Camera.ChangeParameters

    @command(
    )
    @DebugIt()
    def StopAcqusition(self):
        # PROTECTED REGION ID(IDS_Camera.StopAcqusition) ENABLED START #
        """
        Stops the loop that takes images
        :rtype: PyTango.DevVoid
        """
        pass
        # PROTECTED REGION END #    //  IDS_Camera.StopAcqusition

    @command(
    )
    @DebugIt()
    def Snap(self):
        # PROTECTED REGION ID(IDS_Camera.Snap) ENABLED START #
        """
        Takes a image and send it to the user
        :rtype: PyTango.DevVoid
        """
        self.get_image()
        pass
        # PROTECTED REGION END #    //  IDS_Camera.Snap

# ----------
# Run server
# ----------

# PROTECTED REGION ID(IDS_Camera.custom_code) ENABLED START #
    def get_image(self):
        self.remote_device_nodemap.FindNode("TriggerSoftware").Execute()
        buffer = self.datastream.WaitForFinishedBuffer(100)

        # convert to RGB
        raw_image = ids_ipl_extension.BufferToImage(buffer)

        color_image = raw_image.ConvertTo(ids_ipl.PixelFormatName_Mono8)
        self.datastream.QueueBuffer(buffer)
        picture = color_image.get_numpy_3D()

        t_image = np.array(picture,dtype = np.uint16)
        self._image = t_image[:, :, 0]

        return
# PROTECTED REGION END #    //  IDS_Camera.custom_code


def main(args=None, **kwargs):
    """Main function of the IDS_Camera module."""
    # PROTECTED REGION ID(IDS_Camera.main) ENABLED START #
    return run((IDS_Camera,), args=args, **kwargs)
    # PROTECTED REGION END #    //  IDS_Camera.main

# PROTECTED REGION ID(IDS_Camera.custom_functions) ENABLED START #
# PROTECTED REGION END #    //  IDS_Camera.custom_functions


if __name__ == '__main__':
    main()
