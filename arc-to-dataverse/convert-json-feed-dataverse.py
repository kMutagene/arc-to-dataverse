import json
import os
import requests
import time

from dataverse_helpers import build_json_for_create_api
from dotenv import load_dotenv

load_dotenv()
# 1. Reads 2 JSONs: "Citation" metadata and other metadata (which you validate against study_schema.json).
# 2. Converts both JSONs to proprietary Dataverse format using dataverse_helpers.py.
#   > "Citation" metadata conversion is hardcoded in dataverse_helpers.py, may need to be adapted
#   > 2nd JSON should work if it validates against the schema from which the Dataverse metadata block has been generated (via `arc-metadata-blocks/`)
# 3. Feeds the converted data into the Dataverse API.

citation_jsonfile = r"C:\Users\schne\source\repos\kMutagene\arc-to-dataverse\arc-to-dataverse\citation_sample_block.json"
main_jsonfile = r"C:\Users\schne\source\repos\kMutagene\arc-to-dataverse\arc-to-dataverse\study_sample_block.json"

dataverse_url = "http://arc-testing-dataverse.qa.km.k8s.zbmed.de"
dataverse_api_token = os.getenv('DATAVERSE_API_TOKEN')
dataverse_collection_name = "arcs"

def send_api_request(method, api_subpath, dv_url, dv_api_key, retry_attempt=0, **kwargs):
    # auth via Dataverse API key
    headers = {"X-Dataverse-key": dv_api_key}

    res = requests.request(method, "%s/%s" % (dv_url, api_subpath), headers=headers, **kwargs)

    if res.status_code == 401:
        raise PermissionError()

    if res.status_code == 500 and retry_attempt <= 3:
        # Dataverse responses are sometimes flaky, so we retry on 500 Internal Server Error
        time.sleep(2 ** retry_attempt)
        return send_api_request(method, api_subpath, dv_url, dv_api_key, retry_attempt + 1, **kwargs)

    return res


with open(citation_jsonfile, "r") as infile:
    citation_data = json.loads(infile.read())
with open(main_jsonfile, "r") as infile:
    main_data = json.loads(infile.read())

dataverse_data = build_json_for_create_api(main_data, citation_data)

res = send_api_request("POST", "api/v1/dataverses/%s/datasets" % dataverse_collection_name, dataverse_url, dataverse_api_token, json=dataverse_data)

print(res.status_code, res.json())
