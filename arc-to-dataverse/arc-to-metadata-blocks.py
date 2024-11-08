from arctrl.arc import ARC
from arctrl.Core import Process, Table
from arctrl.Core.arc_types import Person, ArcInvestigation, ArcStudy, ArcTable
from jsonschema import validate
import json

import domain 

study_schema = domain.load_json_from_file(r'C:\Users\schne\source\repos\kMutagene\arc-to-dataverse\arc-metadata-blocks\resources\study_schema.json')
citation_schema = domain.load_json_from_file(r'C:\Users\schne\source\repos\kMutagene\arc-to-dataverse\arc-to-dataverse\fairagro_minimal_metadata_block_schema_v0.3.json')
arc = domain.load_arc_from_rocrate_file(r'C:\Users\schne\source\repos\kMutagene\arc-to-dataverse\arc-to-dataverse\arc-ro-crate-metadata.json')

citation_block = {}
citation = {}
citation["otherId"] = [{"otherIdValue": "#ARCDataHubId", "otherIdAgency":"YourDataHub"}]
citation["title"] = arc.ISA.Title
citation["author"] = [domain.map_person_to_author(person) for person in arc.ISA.GetAllPersons()]
citation["datasetContact"] = domain.get_contacts(arc.ISA.GetAllPersons())
citation["dsDescription"] = [{"dsDescriptionValue": arc.ISA.Description}]
citation["subject"] = domain.get_subjects(arc.ISA)
citation_block["citation"] = citation

print("\nCitation:\n")
print(citation_block)
print("\n")

validate(citation_block, citation_schema)

# def get_process_sequence(study: ArcStudy):
#     return [
#         # how to get process sequence? ask lukas

#         ArcTable.GetP
#         for process
#         in study.Tables
#     ]

study_block = {}
studies = [
    {
        "additionalType": "schema.org/Dataset",
        "identifier": study.Identifier,
        "about": [
        ]
    } 
    for study
    in arc.ISA.Studies
]

study_block["study"] = studies

print("\nStudies:\n")
print(study_block)
print("\n")

validate(study_block, study_schema)