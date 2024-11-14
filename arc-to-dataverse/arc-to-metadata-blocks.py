from arctrl.arc import ARC
from arctrl.Core import Process, Table, conversion
from arctrl.Core.Process import process
from arctrl.Core.arc_types import Person, ArcInvestigation, ArcStudy, ArcTable
from arctrl.Core.Process.material_attribute_value import MaterialAttributeValue__get_ValueText, MaterialAttributeValue__get_NameText
from arctrl.Core.Process.process_parameter_value import ProcessParameterValue
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

def get_process_parameters(study: ArcStudy):
    result = []
    for p in conversion.ARCtrl_ArcTables__ArcTables_GetProcesses(study):
        characs = process.Process_getCharacteristicValues_763471FF(p)
        for c in characs:
            result.append(
                {
                    "name": MaterialAttributeValue__get_NameText(c),
                    "value": MaterialAttributeValue__get_ValueText(c)
                }
            )
        params = process.Process_getParameterValues_763471FF(p)
        for p in params:
            result.append(
                {
                    "name": p.NameText,
                    "value": p.ValueText
                }
            )
    return result

study_block = {}
studies = [
    {
        "additionalType": "schema.org/Dataset",
        "identifier": study.Identifier,
        "about": [
            {
                "parameterValue": get_process_parameters(study)
            }
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

# write study block json file
with open(r'C:\Users\schne\source\repos\kMutagene\arc-to-dataverse\arc-to-dataverse\study_sample_block.json', mode='w', encoding='utf-8') as outfile:
    json.dump(study_block, outfile)

# write study block json file
with open(r'C:\Users\schne\source\repos\kMutagene\arc-to-dataverse\arc-to-dataverse\citation_sample_block.json', mode='w', encoding='utf-8') as outfile:
    json.dump(citation_block, outfile)