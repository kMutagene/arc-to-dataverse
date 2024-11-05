# Building Dataverse metadata blocks to represent ARCs

The script `json_schema_to_dataverse_tsv.py` can transform a JSON Schema to the type of TSV that defines a Dataverse metadata block (MDB). Usage example:

`python scripts/json_schema_to_dataverse_tsv.py -n ExampleMdbName resources/example_schema.json`

The resulting TSV can be given to a running Dataverse instance [as described here](https://guides.dataverse.org/en/latest/admin/metadatacustomization.html#loading-tsv-files-into-a-dataverse-installation).
<details>
<summary>(Details: Creating and activating the metadata block)</summary>

Summary:
- give the TSV to `api/admin/datasetfield/load`
- download the Solr schema from your instance
- get metadata schema changes from `api/admin/index/solr/schema` and update the schema via `update-fields.sh`
- upload changed Solr schema
- trigger Solr reload, trigger Solr reindex
</details>

After these steps a Dataverse collection using the new metadata block can be created, and filled with datasets.

## Further resources:
- https://guides.dataverse.org/en/latest/admin/metadatacustomization.html#about-the-metadata-block-tsv: Technical description of the expected TSV structure
- https://github.com/IQSS/dataverse/tree/develop/scripts/api/data/metadatablocks: TSV definitions of Dataverse's default MDBs