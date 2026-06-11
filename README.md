# IDS Camera - Tango Device Server

This repository contains the driver for controlling an IDS Camera with the Tango Control, using the `ids_peak` library.

After cloning this repository with the following command

```
git clone https://github.com/Golp-Voxel/Tango-IDS_Camera.git
```

It is necessary to create the `tango-env` using the following command:

```
python -m venv tango-env
```

After activating it you can install all the models to run this tool by using the command:

```
pip install -r Requirements.txt
pip install ids-peak-afl
```

To complete the installation, it is necessary to copy the `IDS_Camera.bat.temp` template, remove the `.temp`, and change the paths to the installation folder. And the command to activate the env created `tango-env\Scripts\activate`.

**NOTE**: The camera needs to be connected to a **USB 3** port on the PC, otherwise the image acquisition fails.

## Device Properties

After installing the Server on the jive/astor you will need to use the Wizard tool to define the properties of that particular device:

- `CameraID` (**mandatory**) - part of the display name of the camera. On `init_device` the server scans the connected IDS cameras and opens the one whose display name contains this ID, configures the software trigger, and starts the acquisition stream.

## Attributes

- [ExposureTime](#exposuretime)
- [Image](#image)
- [Gain / FramesTrigger / ROI](#gain--framestrigger--roi) (write not implemented yet)

### ExposureTime

Read/write attribute with the exposure time of the camera in milliseconds (`DevDouble`), accepting precision until the microsecond (e.g. `20.001` ms).

```python
IDS_Camera.ExposureTime = 20.0   # ms
```

### Image

Read-only image attribute (`DevUShort`, up to 2474 x 2474) with the last picture taken by [Snap](#snap) (Mono8 converted).

```python
image = IDS_Camera.Image
```

### Gain / FramesTrigger / ROI

Read/write attributes (`DevDouble` / `DevUShort` / `DevUShort` array). The writes are not implemented yet.

## Available commands

- [Snap](#snap)
- [Not implemented yet](#not-implemented-yet)

### Snap

Triggers the camera (software trigger), converts the acquired buffer to Mono8, and stores the picture in the [Image](#image) attribute. It returns an empty error string on success, or the error message (e.g. when the camera is not on a USB 3 port).

```python
Snap()
```

### Not implemented yet

`StartAcqusition()`, `StopAcqusition()`, and `ChangeParameters(argin)` exist on the device but are placeholders.

**TODO**: Implemente the start streaming and stop.

## Example of Tango Client code

```python
import tango
import numpy as np
import matplotlib.pyplot as plt

IDS_Camera = tango.DeviceProxy(<IDS_Tango_location_on_the_database>)
print(IDS_Camera.state())
IDS_Camera.set_timeout_millis(9000)

# Set the exposure time to 20 ms
IDS_Camera.ExposureTime = 20.0

# Take a picture and plot it
IDS_Camera.Snap()
image = np.array(IDS_Camera.Image)
plt.imshow(image)
plt.show()
```

The notebook [`ids-peak-python-sample-jupyter.ipynb`](ids-peak-python-sample-jupyter.ipynb) contains the IDS peak sample used as base for this Device Server.

# References

- [Rapid Prototyping with IDS peak](https://en.ids-imaging.com/kb-article/items/rapid-prototyping-ids-peak.html)
