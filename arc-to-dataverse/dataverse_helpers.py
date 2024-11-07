import sys

MDS_MAIN_METADATA_BLOCK_NAME = "Studies"
CONTROLLED_VOCAB_FIELDS = []


def convert_dict(d, type_name_prefix=""):
    fields = {}
    for type_name in d:
        if type(d[type_name]) is dict:
            field = convert_compound_field(type_name_prefix + type_name, d[type_name], use_full_type_names=(type_name_prefix != ""))
        elif type(d[type_name]) is list:
            field = convert_multiple_field(type_name_prefix + type_name, d[type_name], use_full_type_names=(type_name_prefix != ""))
        else:
            field = convert_primitive_field(type_name_prefix + type_name, d[type_name], multiple=False)

        if field:
            fields[type_name] = field

    return fields


def convert_compound_field(type_name, value, multiple=False, use_full_type_names=False):
    if multiple:
        value = list(map(lambda x: convert_dict(x, type_name_prefix=type_name + "." if use_full_type_names else ""), value))
        if len(value) == 0:
            return
    else:
        value = convert_dict(value, type_name_prefix=type_name + "." if use_full_type_names else "")
        if not value:
            return

    return {"typeName": type_name, "typeClass": "compound", "multiple": multiple, "value": value}


def convert_multiple_field(type_name, value, print_warnings=False, use_full_type_names=False):
    if len(value) == 0:
        if print_warnings:
            sys.stderr.write('WARNING: Skipping "%s", cannot tell type of empty multiple field\n' % type_name)
        return

    if type(value[0]) is dict:
        return convert_compound_field(type_name, value, multiple=True, use_full_type_names=use_full_type_names)
    elif type(value[0]) is list:
        sys.stderr.write('ERROR: Skipping "%s", not implemented\n' % type_name)
    else:
        return convert_primitive_field(type_name, value, multiple=True)


def convert_primitive_field(type_name, value, multiple=False):
    type_class = "controlledVocabulary" if type_name in CONTROLLED_VOCAB_FIELDS else "primitive"
    if type(value) == int or type(value) == float:
        value = str(value)
    elif type(value) == bool:
        value = "Yes" if value else "No"
    elif type(value) == str and type_class == "primitive":
        value = value.strip()
        if not value:
            return
    elif type_class == "controlledVocabulary" and multiple:
        value.sort()
    return {"typeName": type_name, "typeClass": type_class, "multiple": multiple, "value": value}


def convert_json_to_dataverse_json(dataset, print_warnings=False, use_full_type_names=False, type_name_prefix="Studies."):
    fields = []

    for key in dataset:
        if use_full_type_names:
            type_name = type_name_prefix + key
        else:
            type_name = key

        if type(dataset[key]) is dict:
            field = convert_compound_field(type_name, dataset[key], use_full_type_names=use_full_type_names)
        elif type(dataset[key]) is list:
            field = convert_multiple_field(type_name, dataset[key], print_warnings=print_warnings, use_full_type_names=use_full_type_names)
        else:
            field = convert_primitive_field(type_name, dataset[key])

        if field:
            fields.append(field)

    return fields


# Converts "Citation", must be adapted based on what you put in so that the output conforms to the Dataverse citation block structure.
def build_citation_metadata(dataset):
    citation_keys = ['title', 'author', 'datasetContact', 'dsDescription', 'subject', 'keyword', 'productionDate', 'distributionDate', 'otherId']
    citation_metadata = {key: dataset["citation"][key] for key in citation_keys if key in dataset["citation"]}
    return citation_metadata


# Always converts MDS_MAIN, and could be extended if you want to convert more blocks. "Citation" is converted by above method instead.
def convert_resource_to_metadata_blocks(resource):
    metadata_blocks = {}
    metadata_blocks[MDS_MAIN_METADATA_BLOCK_NAME] = {
        "fields": convert_json_to_dataverse_json(resource, use_full_type_names=True, type_name_prefix="Studies."),
        "displayName": MDS_MAIN_METADATA_BLOCK_NAME
    }

    return metadata_blocks


def build_json_for_create_api(data_main, data_citation):
    if "nonStudyDetails" in data_main and "useRights" in data_main[
            "nonStudyDetails"] and "label" in data_main["nonStudyDetails"]["useRights"]:
        license_name = data_main["nonStudyDetails"]["useRights"]["label"]
    else:
        license_name = "Not applicable"

    result = {
        "datasetVersion": {
            "license": {
                "name": license_name
            },
            "metadataBlocks": {
                "citation": {
                    "fields": convert_json_to_dataverse_json(build_citation_metadata(data_citation)),
                    "displayName": "Citation Metadata"
                },
                **convert_resource_to_metadata_blocks(data_main)
            }
        }
    }
    return result
