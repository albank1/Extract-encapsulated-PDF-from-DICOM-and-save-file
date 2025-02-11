This is a work in progress

The main objective was to have a DICOM receiver for encapsulated pdf ECG files. This would be listening and once a DICOM file is received it would be tested to see if it contains and encapsulated PDF and if so extract and save this into a folder..

The program runs a DICOM SCP service (AET and Port set in the .ini file) that will access DICOM files and if they are DICOM encapsulated pdf will store the pdfs in a folder setup in the .ini file.

