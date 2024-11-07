import json
import csv
import sys
import os
import argparse


class DataTypeNotSupportedError(Exception):
    pass


class ExternalRefNotSupportedError(Exception):
    pass


class DataverseTSVGenerator():
    def __init__(self, schema_name, flatten=False, no_required=False, output_field_lists=False):
        self.schema_name = schema_name
        self.flatten = flatten
        self.no_required = no_required
        self.output_field_lists = output_field_lists
        self.prop_name_separator = "."

        self.tsv = {
            "metadataBlock": {
                "name": schema_name,
                "displayName": schema_name
            },
            "datasetField": [],
            "controlledVocabulary": []
        }
        self.display_order_counter = 0
        self.vocab_identifier_prefixes = []
        self.top_level_prop_is_array = False
        self.defs = {}

        if self.output_field_lists:
            self.controlled_vocab_fields = []
            self.float_fields = []
            self.integer_fields = []
            self.bool_fields = []

    def _resolve_ref(self, prop_with_ref, prop_name):
        if prop_with_ref["$ref"].startswith("#/$defs/"):
            prop_with_ref.update(self.defs[prop_with_ref["$ref"].replace("#/$defs/", "")])
            del prop_with_ref["$ref"]
        else:
            sys.stderr.write('ERROR: External $refs not supported, skipping "%s"' % prop_name)
            raise ExternalRefNotSupportedError()

    def _translate_type(self, data_type, data_format):
        # NOTE: format "uri" cannot simply be translated to "url" because validation is stricter for URLs
        # Therefore, "uri" is translated to "string"
        if data_type == "string" and data_format == "date":
            return "date"
        elif data_type == "string":
            return "text"
        elif data_type == "integer":
            return "int"
        elif data_type == "number":
            return "float"
        else:
            raise DataTypeNotSupportedError()

    def _add_dataset_field_to_tsv(self, schema, field_name, field_type, advanced_search_field, allow_controlled_vocab, allow_multiples, facetable, required, parents):
        self.tsv["datasetField"].append({
            "name": field_name,
            "title": schema["title"] if "title" in schema and schema["title"] else field_name,
            "description": (schema["description"] if "description" in schema and schema["description"] else "") + ((" " + schema["input_help"]) if "input_help" in schema and schema["input_help"] else ""),
            "watermark": schema["example"] if "example" in schema else "",
            "fieldType": field_type,
            "displayOrder": self.display_order_counter,
            "advancedSearchField": advanced_search_field,
            "allowControlledVocabulary": allow_controlled_vocab,
            "allowmultiples": allow_multiples,
            "facetable": facetable,
            "displayoncreate": "FALSE" if "display_on_create" in schema and schema["display_on_create"] is False else "TRUE",
            "required": required,
            #if the datasetField is top-level, len(parents) is 1, and it should have no parent in TSV
            "parent": self.prop_name_separator.join(parents if len(parents) > 1 else []),
            "metadatablock_id": self.schema_name
        })

        self.display_order_counter += 1

        if self.output_field_lists and allow_controlled_vocab == "TRUE":
            self.controlled_vocab_fields.append(field_name)

    def _add_vocab_term_to_tsv(self, field_name, vocab_term, identifier_prefix, display_order):
        self.tsv["controlledVocabulary"].append({
            "DatasetField": field_name,
            "Value": vocab_term,
            "identifier": identifier_prefix + str(display_order),
            "displayOrder": display_order
        })

    def _add_vocab_terms_to_tsv(self, field_name, vocab_terms):
        identifier_prefix = "".join(list(map(lambda x: x[0], field_name.split(self.prop_name_separator)))).upper() + "_"
        identifier_prefix_orig, attempts = identifier_prefix, 1
        while True:
            if identifier_prefix not in self.vocab_identifier_prefixes:
                self.vocab_identifier_prefixes.append(identifier_prefix)
                break
            else:
                identifier_prefix = identifier_prefix_orig + str(attempts) + "_"
                attempts += 1
        term_display_order_counter = 0
        for term in vocab_terms:
            self._add_vocab_term_to_tsv(field_name, term, identifier_prefix, term_display_order_counter)
            term_display_order_counter += 1

    def _add_enum_prop_to_tsv(self, schema, prop_name, allow_multiples=False, required=False, parents=None):
        prop_name = self.prop_name_separator.join((parents if parents else []) + [prop_name])
        try:
            self._add_dataset_field_to_tsv(
                schema,
                prop_name,
                field_type=self._translate_type(schema["type"], schema["format"] if "format" in schema else None),
                advanced_search_field="TRUE",
                allow_controlled_vocab="TRUE",
                allow_multiples="TRUE" if allow_multiples else "FALSE",
                facetable="TRUE",
                required="TRUE" if required else "FALSE",
                parents=parents
            )
        except DataTypeNotSupportedError:
            sys.stderr.write('ERROR: Skipping array property "%s" because of unhandled item type "%s"\n' % (prop_name, schema["items"]["type"]))
            return

        if allow_multiples:
            # NOTE: This is to create a single fixed array order for fields that allow multiples, so changes in the
            # values of those fields can be detected more easily
            schema["enum"].sort()

        self._add_vocab_terms_to_tsv(prop_name, schema["enum"])

    def _add_object_prop_to_tsv(self, schema, prop_name, allow_multiples=False, required=False, parents=None, level=0):
        # TODO top_level_prop_is_array should not be necessary if level is set correctly
        sub_props_to_be_flattened = self.flatten and ((self.top_level_prop_is_array and level > 0) or (not self.top_level_prop_is_array and level > 1))
        # Object at level 0 is ignored, otherwise the entire metadata block is a single compound field
        object_prop_to_be_added = level > 0 and not sub_props_to_be_flattened

        if object_prop_to_be_added:
            self._add_dataset_field_to_tsv(
                schema,
                self.prop_name_separator.join((parents if parents else []) + [prop_name]),
                field_type="none",
                advanced_search_field="FALSE",
                allow_controlled_vocab="FALSE",
                allow_multiples="FALSE",
                facetable="FALSE",
                required="TRUE" if required else "FALSE",
                parents=parents
            )
            parents.append(prop_name)

        for sub_prop_name in schema["properties"]:
            if sub_props_to_be_flattened:
                sys.stdout.write('INFO: "%s" is a nested compound field, flattening to "%s"\n' % (sub_prop_name, prop_name + self.prop_name_separator + sub_prop_name))
                schema["properties"][sub_prop_name]["title"] = ((schema["title"] + ": ") if "title" in schema else "") + (schema["properties"][sub_prop_name]["title"] if "title" in schema["properties"][sub_prop_name] else "")
                schema["properties"][sub_prop_name]["description"] = ((schema["description"] + " ") if "description" in schema else "") + (schema["properties"][sub_prop_name]["description"] if "description" in schema["properties"][sub_prop_name] else "")
                self._add_json_schema_prop_to_tsv(schema["properties"][sub_prop_name], parents,
                                                  prop_name + self.prop_name_separator + sub_prop_name,
                                                  required=(False if not required else sub_prop_name in schema["required"]),
                                                  level=level)
            else:
                self._add_json_schema_prop_to_tsv(schema["properties"][sub_prop_name], parents,
                                                  sub_prop_name,
                                                  required=(sub_prop_name in schema["required"] if "required" in schema else False),
                                                  level=level + 1)

    def _add_array_prop_to_tsv(self, schema, prop_name, allow_multiples=False, required=False, parents=None, level=0):
        if level == 0:
            self.top_level_prop_is_array = True

        prop_metadata = {key: schema[key] if key in schema else None for key in ["title", "description", "example", "input_help", "display_on_create"]}
        schema["items"].update(prop_metadata)

        if "$ref" in schema["items"]:
            try:
                self._resolve_ref(schema["items"], prop_name)
            except ExternalRefNotSupportedError:
                return

        if schema["items"]["type"] != "object":
            # Non-object array items (e.g. string) can be added directly as repeatable field
            self._add_json_schema_prop_to_tsv(schema["items"], parents, prop_name, allow_multiples=True,
                                              required=required if level > 0 else "minItems" in schema and schema[
                                                  "minItems"] > 0, level=level)
        else:
            if not self.flatten or ((self.top_level_prop_is_array and level < 1) or (not self.top_level_prop_is_array and level < 2)): # TODO top_level_prop_is_array should not be necessary if level is set correctly
                self._add_dataset_field_to_tsv(
                    schema,
                    self.prop_name_separator.join((parents if parents else []) + [prop_name]),
                    field_type="none",
                    advanced_search_field="FALSE",
                    allow_controlled_vocab="FALSE",
                    allow_multiples="TRUE",
                    facetable="FALSE",
                    required="TRUE" if required else "FALSE",
                    parents=parents
                )
                parents.append(prop_name)

                for sub_prop_name in schema["items"]["properties"]:
                    self._add_json_schema_prop_to_tsv(schema["items"]["properties"][sub_prop_name], parents,
                                                      sub_prop_name,
                                                      allow_multiples=False,
                                                      required=(sub_prop_name in schema["items"]["required"] if "required" in schema["items"] else False),
                                                      level=level + 1)
            else:
                sys.stderr.write('ERROR: Maximum nesting level exceeded, skipping "%s"\n' % prop_name)

    def _add_boolean_prop_to_tsv(self, schema, prop_name, allow_multiples=False, required=False, parents=None):
        prop_name = self.prop_name_separator.join((parents if parents else []) + [prop_name])
        self._add_dataset_field_to_tsv(
            schema,
            prop_name,
            field_type="text",
            advanced_search_field="TRUE",
            allow_controlled_vocab="TRUE",
            allow_multiples="TRUE" if allow_multiples else "FALSE",
            facetable="TRUE",
            required="TRUE" if required else "FALSE",
            parents=parents
        )

        if self.output_field_lists:
            self.bool_fields.append(prop_name)

        self._add_vocab_terms_to_tsv(prop_name, ["Yes", "No"])

    def _add_simple_prop_to_tsv(self, schema, prop_name, allow_multiples=False, required=False, parents=None):
        prop_name = self.prop_name_separator.join((parents if parents else []) + [prop_name])
        try:
            self._add_dataset_field_to_tsv(
                schema,
                prop_name,
                field_type=self._translate_type(schema["type"], schema["format"] if "format" in schema else None),
                advanced_search_field="TRUE",
                allow_controlled_vocab="FALSE",
                allow_multiples="TRUE" if allow_multiples else "FALSE",
                facetable="FALSE",
                required="TRUE" if required else "FALSE",
                parents=parents
            )
        except DataTypeNotSupportedError:
            sys.stderr.write('ERROR: Skipping property "%s" because of unhandled type "%s"\n' % (prop_name, schema["type"]))
            return

        if self.output_field_lists and self._translate_type(schema["type"], schema["format"] if "format" in schema else None) == "float":
            self.float_fields.append(prop_name)

        if self.output_field_lists and self._translate_type(schema["type"], schema["format"] if "format" in schema else None) == "int":
            self.integer_fields.append(prop_name)

    def _add_json_schema_prop_to_tsv(self, schema, parents, prop_name="", allow_multiples=False, required=False,
                                     level=0):
        parents = parents.copy()
        if not prop_name:
            prop_name = self.schema_name

        if "$ref" in schema:
            try:
                self._resolve_ref(schema, prop_name)
            except ExternalRefNotSupportedError:
                sys.stderr.write('ERROR: Skipping property "%s" because of unsupported external ref: %s' % (prop_name, schema))
                return

        if "enum" in schema:
            self._add_enum_prop_to_tsv(schema, prop_name, allow_multiples, required if not self.no_required else False, parents)
        elif "type" in schema:
            if schema["type"] == "object":
                self._add_object_prop_to_tsv(schema, prop_name, allow_multiples, required, parents, level)
            elif schema["type"] == "array":
                self._add_array_prop_to_tsv(schema, prop_name, allow_multiples, required if not self.no_required else False,
                                            parents, level)
            elif schema["type"] == "boolean":
                self._add_boolean_prop_to_tsv(schema, prop_name, allow_multiples, required if not self.no_required else False, parents)
            else:
                self._add_simple_prop_to_tsv(schema, prop_name, allow_multiples, required if not self.no_required else False, parents)
        else:
            sys.stderr.write('ERROR: Skipping property "%s" because of unknown type: %s' % (prop_name, schema))
            return

    def _set_defs(self, defs):
        self.defs = defs

    def from_json_schema(self, schema):
        if "$defs" in schema:
            self._set_defs(schema["$defs"])

        self._add_json_schema_prop_to_tsv(schema, [self.schema_name])

        if self.output_field_lists:
            sys.stdout.write("CONTROLLED_VOCAB_FIELDS = %s\n" % self.controlled_vocab_fields)
            sys.stdout.write("FLOAT_FIELDS = %s\n" % self.float_fields)
            sys.stdout.write("INTEGER_FIELDS = %s\n" % self.integer_fields)
            sys.stdout.write("BOOL_FIELDS = %s\n" % self.bool_fields)

        return self.tsv


def main():
    parser = argparse.ArgumentParser(description="Converts JSON Schema to Dataverse custom metadata TSV files.")
    parser.add_argument("json_schema_file", help="path to JSON Schema file")
    parser.add_argument("-n", "--name", dest="name", help="set name of the metadata block. If not given, filename is used.")
    parser.add_argument("-f", "--flatten", dest="flatten", action="store_true", help="flatten property hierarchy")
    parser.add_argument("-r", "--no-required", dest="no_required", action="store_true", help="don't mark any fields as required")
    parser.add_argument("-o", "--output-field-lists", dest="output_field_lists", action="store_true", help="output field lists (CONTROLLED_VOCAB_FIELDS, FLOAT_FIELDS, INTEGER_FIELDS, BOOL_FIELDS)")
    args = parser.parse_args()

    with open(args.json_schema_file) as f:
        schema = json.load(f)

    schema_name = args.name if args.name else os.path.splitext(os.path.basename(args.json_schema_file))[0]

    tsv_generator = DataverseTSVGenerator(schema_name, args.flatten, args.no_required, args.output_field_lists)
    tsv = tsv_generator.from_json_schema(schema)

    with open(args.json_schema_file.replace(".json", ".tsv"), "w", encoding="utf-8") as f:
        fieldnames = ["#metadataBlock", "name", "dataverseAlias", "displayName", "blockURI"]
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t", quotechar="'")
        writer.writeheader()
        writer.writerow(tsv["metadataBlock"])

        fieldnames = ["#datasetField", "name", "title", "description", "watermark", "fieldType", "displayOrder", "displayFormat", "advancedSearchField", "allowControlledVocabulary", "allowmultiples", "facetable", "displayoncreate", "required", "parent", "metadatablock_id", "termURI"]
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t", quotechar="'")
        writer.writeheader()
        for row in tsv["datasetField"]:
            writer.writerow(row)
        
        fieldnames = ["#controlledVocabulary", "DatasetField", "Value", "identifier", "displayOrder"]
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        for row in tsv["controlledVocabulary"]:
            writer.writerow(row)


if __name__ == "__main__":
    main()
