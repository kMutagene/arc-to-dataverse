from arctrl.arc import ARC
from arctrl.Core import conversion
from arctrl.json import JsonController
from arctrl.Core.Process import process
from arctrl.Core.arc_types import Person, ArcInvestigation, ArcStudy
from arctrl.Core.Process.material_attribute_value import MaterialAttributeValue__get_ValueText, MaterialAttributeValue__get_NameText

import json
from enum import Enum
from jsonschema import validate

def load_json_from_file(file_path):
    """Load JSON data from a file."""
    with open(file_path, mode='r', encoding='utf-8') as f:
        return json.load(f)
    
def load_arc_from_rocrate_file (file_path):
    """Load ARC from a RO-Crate file conforming to the ARC ro-crate profile."""
    with open(file_path, mode='r', encoding='utf-8') as f:
        return ARC.from_rocrate_json_string(f.read())

def load_inv_from_isa_rocrate_file (file_path):
    """Load Investigation from a RO-Crate file conforming to the ISA ro-crate profile."""
    with open(file_path, mode='r', encoding='utf-8') as f:
        return JsonController.Investigation().from_rocrate_json_string(f.read())

def load_std_from_isa_rocrate_file (file_path):
    """Load Study from a RO-Crate file conforming to the ISA ro-crate profile."""
    with open(file_path, mode='r', encoding='utf-8') as f:
        return JsonController.Study().from_rocrate_json_string(f.read())

def write_json_to_file(data, file_path):
    """Write JSON data to a file."""
    with open(file_path, mode='w', encoding='utf-8') as outfile:
        json.dump(data, outfile)

def first(iterable, condition = lambda x: True):
    """
    Returns the first item in the `iterable` that
    satisfies the `condition`.

    If the condition is not given, returns the first item of
    the iterable.

    Raises `StopIteration` if no item satysfing the condition is found.

    >>> first( (1,2,3), condition=lambda x: x % 2 == 0)
    2
    >>> first(range(3, 100))
    3
    >>> first( () )
    Traceback (most recent call last):
    ...
    StopIteration
    """

    return next(x for x in iterable if condition(x))

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