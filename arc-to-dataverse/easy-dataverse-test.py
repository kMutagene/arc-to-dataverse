from easyDataverse import Dataverse
import asyncio

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Connect to a Dataverse installation
dataverse = Dataverse(
  server_url="http://arc-testing-dataverse.qa.km.k8s.zbmed.de/",
  api_token="",
)
