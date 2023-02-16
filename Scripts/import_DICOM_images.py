import bpy
import pydicom
import os
import numpy as np
from pathlib import Path

#Directory containing DICOM images
dir_path = r"D:/Test Files/CT"

##Finds all files with .dcm extension
#image_files = [f for f in os.listdir(DICOM_dir) if f.endswith('.dcm')]




dicom_set = []
for root, _, filenames in os.walk(dir_path):
    for filename in filenames:
        dcm_path = Path(root, filename)
        #if dcm_path.suffix == ".dcm":
        try:
            dicom = pydicom.dcmread(dcm_path, force=True)
            
        except IOError as e:
            print(f"Can't import {dcm_path.stem}")
        else:
            dicom_set.append(dicom.pixel_array)

dicom_set = np.asarray(dicom_set)


#Pixel spacing in X,Y direction
spacing = dicom.PixelSpacing

#CT origin coordinates
origin = np.asarray(dicom.ImagePositionPatient)
slice_spacing = dicom.SliceThickness
image_planes = dicom_set/np.max(dicom_set)




# Create an OpenVDB volume from the pixel data
import pyopenvdb as openvdb
#Creates a grid of Double precision
grid = openvdb.DoubleGrid()
#Copies image volume from numpy to VDB grid
grid.copyFromArray(image_planes.astype(float))

#Scales the grid to slice thickness and pixel size using modified identity transformation matrix. NB. Blender is Z up coordinate system
grid.transform = openvdb.createLinearTransform([[slice_spacing/100, 0, 0, 0], [0, spacing[0]/100, 0, 0], [0,0,spacing[1]/100,0], [0,0,0,1]])

#Sets the grid class to FOG_VOLUME
grid.gridClass = openvdb.GridClass.FOG_VOLUME
#Blender needs grid name to be "Density"
grid.name='density'

#Writes CT volume to a vdb file but perhaps this could be done internally in the future
openvdb.write(dir_path + "CT.vdb",grid)

# Add the volume to the scene
bpy.ops.object.volume_import(filepath=dir_path + "CT.vdb", files=[])

# Set the volume's origin to match the DICOM image position
print(origin)
bpy.context.object.location = origin/100
