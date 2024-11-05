import json
import inspect
from arctrl.arc import ARC
from arctrl.Core.arc_types import Person
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

def map_person(person:Person):
    return {
        "authorName": f'{person.FirstName} {person.LastName}',
        "authorAffiliation": person.Affiliation
    }

# mandatory fields on "citation": "otherId", "title", "author", "datasetContact","dsDescription","subject"
out = {}
out["citation"] = {}
out["citation"]["otherId"] = [{"otherIdValue": "#ARCDataHubId", "otherIdAgency":"YourDataHub"}]
out["citation"]["title"] = arc.ISA.Title
out["citation"]["author"] = list(map(map_person, arc.ISA.GetAllPersons()))
out["citation"]["datasetContact"] = []
out["citation"]["dsDescription"] = []
out["citation"]["subject"] = []

print(out)
validate(instance=out, schema=fairagro_minimal_metadata_block_schema)