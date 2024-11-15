from arctrl.arc import ARC
from domain import helpers

def create_citation_block(
    arc: ARC,
    otherIdValue: str = None,
    otherIdAgency: str = None
):
    """
    Create a citation metadata block from the given ARC.
    """
    citation_block = {}
    citation = {}

    # check if we can just omit this and the block still being valid
    if otherIdValue and otherIdAgency:
        citation["otherId"] = [{"otherIdValue": otherIdValue, "otherIdAgency": otherIdAgency}]
    else:
        citation["otherId"] = [{"otherIdValue": "not provided", "otherIdAgency":"not provided"}]

    citation["title"] = arc.ISA.Title
    citation["author"] = [helpers.map_person_to_author(person) for person in arc.ISA.GetAllPersons()]
    citation["datasetContact"] = helpers.get_contacts(arc.ISA.GetAllPersons())
    citation["dsDescription"] = [{"dsDescriptionValue": arc.ISA.Description}]
    citation["subject"] = helpers.get_subjects(arc.ISA)
    citation_block["citation"] = citation

    return citation_block

def create_study_block(arc: ARC):
    study_block = {}
    studies = [
        {
            "additionalType": "schema.org/Dataset",
            "identifier": study.Identifier,
            "about": [
                {
                    "parameterValue": helpers.get_process_parameters(study)
                }
            ]
        } 
        for study
        in arc.ISA.Studies
    ]

    study_block["study"] = studies
    return study_block