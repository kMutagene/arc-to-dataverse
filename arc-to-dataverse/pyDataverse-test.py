from pyDataverse.api import NativeApi

from pyDataverse.models import Dataverse
from pyDataverse.utils import read_file

BASE_URL = 'http://arc-testing-dataverse.qa.km.k8s.zbmed.de/'
API_TOKEN = '73e11470-ff1c-4aa4-b480-bd59db8b774c'
api = NativeApi(BASE_URL, API_TOKEN)

resp = api.get_info_version()
resp.json()

dv = Dataverse()

resp = api.get_metadatablocks()
for m in resp.json()["data"]: print(m)

api.get_metadatablock("Studies").json()