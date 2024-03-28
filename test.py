import os
from notion.data_loader import DataLoader
from notion import NotionClient, NotionParser

client = NotionClient(os.environ.get("NOTION_API_KEY"))
converter = NotionParser()
loader = DataLoader(client, converter)
df = loader.load_db("database_id")
