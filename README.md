# arc-to-dataverse

Mapping of [ARC](https://arc-rdm.org/) metadata to [Dataverse](https://dataverse.org/) as part of the #BioHackEU24 project 19: arc-isa-ro-crate machine actionability

We identified these main goals:

1. Map ARC ro-crate metadata to a custom JSON endpoint that creates an existing metadata block
2. create custom metadata blocks that represent ARC ro-crate metadata. This results in full ARC support in Dataverse
    ```mermaid
    flowchart TD
        subgraph ARC ro-crate
            subgraph ISA
                I(Investigation metadata)
                S(Study metadata)
                A(Assay metadata)
            end
            subgraph CWL
                W(Workflow)
                R(Run)
            end
        end

        subgraph "Dataverse dataset"
            CB[Citation block]
            SB[Study block]
            AB[Assay block]
        end

    I -.-> CB
    S -.-> SB
    A -.-> AB
    ```

From a software design point, we decided to create a python script that is able to read ARC information and create an output that can be submitted to Dataverse via API:

```mermaid

```

This script can be used to facilitate the automated submission (_a machine action_) of ARC metadata to Dataverse, therefore also enabling the connection between [ARC Data Hubs](https://arc-rdm.org/details/arc-data-hub/) and Dataverse, which makes Dataverse a potential search entry point for ARC metadata and increases findability of ARCs in general.

## Day 1

- project goal discussions 

## Day 2

- [poc script for custom json endpoint](./arc-to-dataverse/poc-for-custom-json-endpoint.py)

## Day 3

- [custom study metadata block]()
- decision on creating a 1-to-1 representation for the ARC on the Dataverse backend (with deep hierarchies).
  This leads to a data model that can not be displayed on the default frontend which can only display nested objects up to 2 levels. 
  This is still better than mapping/splitting ARC metadata to a flat format, as it is easier to adapt the frontend incrementally.

## Day 4

- 