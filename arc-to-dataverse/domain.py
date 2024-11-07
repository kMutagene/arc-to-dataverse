from arctrl.arc import ARC
from arctrl.Core.arc_types import Person, ArcInvestigation
from arctrl.json import JsonController

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

