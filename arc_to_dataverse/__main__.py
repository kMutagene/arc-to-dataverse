import os
import typer
from typer import Option
from typing_extensions import Annotated
import json
from domain import crate_conversion
from domain import helpers
import importlib.resources

c = importlib.resources.as_file(importlib.resources.files('schemas') / 'fairagro_minimal_metadata_block_schema_v0.3.json')
with c as f:
    __citation_schema__ = json.load(f.open(mode='rb'))

s = importlib.resources.as_file(importlib.resources.files('schemas') / 'study_block_schema.json')
with s as f:
    __study_schema__ = json.load(f.open(mode='rb'))

app = typer.Typer()

@app.command()
def convert_to_metadata_blocks(
    inputpath: Annotated[str, typer.Argument(help="the path to the ISA-RO-Crate file to convert to metadata blocks")],
    outputFolder: Annotated[str, Option(help="Output folder for the metadata blocks")] = None,
    validate: Annotated[bool, Option(help="Validate the created metadata blocks against an internal json schema. Note that dataverse performs additional checks (e.g. email validation) that might not be covered by this.")] = True,
    sourceURL: Annotated[str, Option(help="Source URL for the ARC")] = None,
    sourceAgency: Annotated[str, Option(help="Source agency of the ARC")] = None
):
    """
    Export the given ISA-RO-Crate file at `inputpath` to a set of json files that can be submitted to a dataverse instance that supports the needed metadata blocks.

    If `--outputFolder` is provided, the files will be saved to that folder (which will be created if it does not exist). 
    Otherwise, the file will be saved to the same location as the input file.

    If you want to link the created datasets to an ARC that already has an identifier (e.g., it is available on a ARC Data Hub instance),
    you can provide the URL of the ARC in `--sourceURL` and the agency that provided the ARC in `--sourceAgency`.
    """
    # Load the ARC from the given file
    arc = helpers.load_arc_from_rocrate_file(inputpath)

    # Create the citation and study metadata blocks
    citation_block = crate_conversion.create_citation_block(
        arc,
        otherIdValue=sourceURL,
        otherIdAgency=sourceAgency
    )

    study_block = crate_conversion.create_study_block(arc)

    # Validate against schemas
    if validate:
        helpers.validate(citation_block, __citation_schema__)
        helpers.validate(study_block, __study_schema__)

    if outputFolder:
        helpers.write_json_to_file(citation_block, f"{outputFolder}/citation_block.json")
        helpers.write_json_to_file(study_block, f"{outputFolder}/study_block.json")
    else:
        folder = os.path.dirname(inputpath)
        helpers.write_json_to_file(citation_block, f"{folder}/citation_block.json")
        helpers.write_json_to_file(study_block, f"{folder}/study_block.json")

@app.command()
def upload_to_dataverse(
    dataverseURL: str,
    apiToken: str,
    inputfolder: str
):
    print(f"Hello")

if __name__ == "__main__":
    app()