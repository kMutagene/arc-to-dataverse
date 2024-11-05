import json
import inspect
from enum import Enum
from arctrl.arc import ARC
from arctrl.Core.arc_types import Person, ArcInvestigation
from jsonschema import validate

def load_json_from_file(file_path):
    """Load JSON data from a file."""
    with open(file_path, 'r') as f:
        return json.load(f)
    
def load_arc_from_rocrate_file (file_path):
    """Load ARC from a RO-Crate file."""
    with open(file_path, 'r') as f:
        return ARC.from_rocrate_json_string(f.read())

fairagro_minimal_metadata_block_schema = load_json_from_file(r'C:\Users\schne\source\repos\kMutagene\arc-to-dataverse\arc-to-dataverse\fairagro_minimal_metadata_block_schema_v0.3.json')

# # If no exception is raised by validate(), the instance is valid.
# validate(instance={"name" : "Eggs", "price" : 34.99}, schema=schema)

arc = load_arc_from_rocrate_file(r'C:\Users\schne\source\repos\kMutagene\arc-to-dataverse\arc-to-dataverse\arc-ro-crate-metadata.json')

def map_person_to_author(person:Person):
    return {
        "authorName": f'{person.FirstName} {person.LastName}',
        "authorAffiliation": person.Affiliation if person.Affiliation else ""
    }

def get_contacts(persons: list[Person]):
    return [
        {
            "datasetContactName": f'{person.FirstName} {person.LastName}',
            "datasetContactEmail": person.EMail,
            "datasetContactAffiliation": person.Affiliation
        }
        for person in persons 
        if person.EMail
    ]

class Subject(Enum):
    Agricultural_Sciences = "Agricultural Sciences"
    Arts_and_Humanities = "Arts and Humanities"
    Astronomy_and_Astrophysics = "Astronomy and Astrophysics"
    Business_and_Management = "Business and Management"
    Chemistry = "Chemistry"
    Computer_and_Information_Science = "Computer and Information Science"
    Earth_and_Environmental_Sciences = "Earth and Environmental Sciences"
    Engineering = "Engineering"
    Law = "Law"
    Mathematical_Sciences = "Mathematical Sciences"
    Medicine_Health_and_Life_Sciences = "Medicine, Health and Life Sciences"
    Physics = "Physics"
    Social_Sciences = "Social Sciences"
    Other = "Other"

def get_subjects(inv: ArcInvestigation):
    subjects = [
        comment.Value 
        for comment in inv.Comments 
        if comment.Name == "Subject"
        and comment.Value in [subject.value for subject in Subject]
    ]
    if len(subjects) == 0:
        return [Subject.Other.value]
    else:
        return subjects
    


# mandatory fields on "citation": "otherId", "title", "author", "datasetContact","dsDescription","subject"
out = {}
out["citation"] = {}
out["citation"]["otherId"] = [{"otherIdValue": "#ARCDataHubId", "otherIdAgency":"YourDataHub"}]
out["citation"]["title"] = arc.ISA.Title
out["citation"]["author"] = [map_person_to_author(person) for person in arc.ISA.GetAllPersons()]
out["citation"]["datasetContact"] = get_contacts(arc.ISA.GetAllPersons())
out["citation"]["dsDescription"] = [{"dsDescriptionValue": arc.ISA.Description}]
out["citation"]["subject"] = get_subjects(arc.ISA)

validate(instance=out, schema=fairagro_minimal_metadata_block_schema)