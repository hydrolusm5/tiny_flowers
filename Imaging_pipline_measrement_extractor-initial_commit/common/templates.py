



xml_output_dict = {
    "PatientID": [],
    "PatientName": [],
    "StudyDate": [],
    "ModalitiesInStudy": [],
    "QueryRetrieveLevel": [],
    "PatientBirthDate": [],
    "PatientSex": [],
    "SourceApplicationEntityTitle": [],
    "SOPClassesInStudy": [],
    "StudyTime": [],
    "AccessionNumber": [],
    "StudyID": [],
    "StudyInstanceUID": [],
    "StudyDescription": [],
    "SpecificCharacterSet": [],
    "RetrieveAETitle": []
}

xml_tag_dictionary = {
  0:'Volume',
  1:'Area',
  2:'Shape Compactness',
  3:'Min',
  4:'Max',
  5:'Mean',
  6:'SDev',
  7:'d1',
  8:'d2',
  9:'d1xd2',
  10:'Avg.Diameter',
  '00080052':'QueryRetrieveLevel',
  '00080054':'RetrieveAETitle',
  '00100020':'PatientID',
  '0020000D':'StudyInstanceUID',
  '00020016':'SourceApplicationEntityTitle'
}