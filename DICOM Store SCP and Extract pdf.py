###############################################################################
# Hosts a DICOM Storage SCP where the IP Address is the address of the PC
# and the AE Title and Port and storage location are defined in the ini file as
# [DICOM settings]
# AET: MY_SCP
# PORT: 104
# 
# [STORAGE LOCATION]
# Folder: dicom_storage
# Alban Killingback July 2024
################################################################################

import os
import configparser
import logging
import pydicom
from pydicom.dataset import Dataset
from pydicom.uid import EncapsulatedPDFStorage
from pynetdicom import AE, evt, debug_logger
from pynetdicom.sop_class import Verification
from pynetdicom.sop_class import (
    CTImageStorage,
    MRImageStorage,
    PositronEmissionTomographyImageStorage,
    RTImageStorage,
    RTDoseStorage,
    RTStructureSetStorage,
    RTPlanStorage,
    SecondaryCaptureImageStorage,
    DigitalXRayImageStorageForPresentation,
    DigitalXRayImageStorageForProcessing,
    DigitalMammographyXRayImageStorageForPresentation,
    DigitalMammographyXRayImageStorageForProcessing,
    DigitalIntraOralXRayImageStorageForPresentation,
    DigitalIntraOralXRayImageStorageForProcessing,
    EnhancedSRStorage,
    ComprehensiveSRStorage,
    BasicTextSRStorage,
    XRayAngiographicImageStorage,
    XRayRadiofluoroscopicImageStorage,
    NuclearMedicineImageStorage,
    UltrasoundImageStorage,
    VLPhotographicImageStorage,
    VLEndoscopicImageStorage,
    VLMicroscopicImageStorage,
    VLSlideCoordinatesMicroscopicImageStorage,
    VLPhotographicImageStorage,
    EnhancedPETImageStorage,
    EnhancedCTImageStorage,
    EnhancedMRImageStorage,
    SegmentationStorage,
    SurfaceSegmentationStorage,
    ParametricMapStorage,
    EncapsulatedCDAStorage
)

# Enable logging for debugging purposes
# debug_logger()

# load the COM port number from the config file
config = configparser.ConfigParser()
config.read(r'DICOM Store SCP WORKING.ini')
ae_title = config['DICOM settings']['AET']
server_address = '127.0.0.1'  # Listen on all available network interfaces
server_port = int(config['DICOM settings']['PORT'])
storage_location = config['STORAGE LOCATION']['Folder']
output_folder = r'c:\temp'

# Define the storage directory
storage_dir = storage_location
if not os.path.exists(storage_dir):
    os.makedirs(storage_dir)

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Function to extract PDF from DICOM and save with MRN_DOB format
def extract_pdf_from_dicom(dicom_file_path, output_folder):
    # Read the DICOM file
    ds = pydicom.dcmread(dicom_file_path)
    
    # Extract the MRN and DOB from the DICOM file
    mrn = ds.PatientID
    dob = ds.PatientBirthDate
    
    # Format the DOB to YYYYMMDD
    dob_formatted = dob if len(dob) == 8 else f'{dob[:4]}{dob[4:6]}{dob[6:]}'
    
    # Construct the output filename
    output_filename = os.path.join(output_folder, f'{mrn}_{dob_formatted}.pdf')
    
    # Extract the PDF data and save to output file
    if 'EncapsulatedDocument' in ds:
        pdf_data = ds.EncapsulatedDocument
        with open(output_filename, 'wb') as pdf_file:
            pdf_file.write(pdf_data)

# Define a handler for the C-STORE request
def handle_store(event):
    """Handle a C-STORE request event."""
    ds = event.dataset
    ds.file_meta = event.file_meta

    # Create a filename based on the SOP Instance UID
    filename = os.path.join(storage_dir, f'{ds.SOPInstanceUID}.dcm')

    # Save the DICOM file
    ds.save_as(filename, write_like_original=False)

    # If the SOP Class UID is for Encapsulated PDF Storage, extract and save the PDF
    if ds.SOPClassUID == EncapsulatedPDFStorage:
        extract_pdf_from_dicom(filename, output_folder)

    return 0x0000  # Success status

# Define a handler for the C-ECHO request
def handle_echo(event):
    """Handle a C-ECHO request event."""
    return 0x0000  # Success status

# Initialize the Application Entity (AE)
ae = AE()

# Add supported presentation contexts for storage SOP classes
storage_sop_classes = [
    CTImageStorage,
    MRImageStorage,
    PositronEmissionTomographyImageStorage,
    RTImageStorage,
    RTDoseStorage,
    RTStructureSetStorage,
    RTPlanStorage,
    SecondaryCaptureImageStorage,
    DigitalXRayImageStorageForPresentation,
    DigitalXRayImageStorageForProcessing,
    DigitalMammographyXRayImageStorageForPresentation,
    DigitalMammographyXRayImageStorageForProcessing,
    DigitalIntraOralXRayImageStorageForPresentation,
    DigitalIntraOralXRayImageStorageForProcessing,
    EnhancedSRStorage,
    ComprehensiveSRStorage,
    BasicTextSRStorage,
    XRayAngiographicImageStorage,
    XRayRadiofluoroscopicImageStorage,
    NuclearMedicineImageStorage,
    UltrasoundImageStorage,
    VLPhotographicImageStorage,
    VLEndoscopicImageStorage,
    VLMicroscopicImageStorage,
    VLSlideCoordinatesMicroscopicImageStorage,
    VLPhotographicImageStorage,
    EnhancedPETImageStorage,
    EnhancedCTImageStorage,
    EnhancedMRImageStorage,
    SegmentationStorage,
    SurfaceSegmentationStorage,
    ParametricMapStorage,
    EncapsulatedPDFStorage,
    EncapsulatedCDAStorage,
]

for sop_class in storage_sop_classes:
    ae.add_supported_context(sop_class)

# Add supported presentation context for Verification SOP Class
ae.add_supported_context(Verification)

# Define the handlers for the supported services
handlers = [
    (evt.EVT_C_STORE, handle_store),
    (evt.EVT_C_ECHO, handle_echo),
]

# AET, Port are loaded from ini file and IP is the host IP

# Start the SCP
print(f'Starting DICOM Storage SCP on {server_address}:{server_port} with AE title {ae_title}')
ae.start_server((server_address, server_port), ae_title=ae_title, evt_handlers=handlers)
