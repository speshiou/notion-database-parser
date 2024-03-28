import requests
from urllib.parse import urljoin
from datetime import datetime


class NotionClient:
    def __init__(self, notion_key):
        self.notion_key = notion_key
        self.default_headers = {
            "Authorization": f"Bearer {self.notion_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }
        self.session = requests.Session()
        self.session.headers.update(self.default_headers)
        self.NOTION_BASE_URL = "https://api.notion.com/v1/"

    def query_database(
        self, db_id, filter_object=None, sorts=None, start_cursor=None, page_size=None
    ):
        db_url = urljoin(self.NOTION_BASE_URL, f"databases/{db_id}/query")
        params = {}
        if filter_object is not None:
            params["filter"] = filter_object
        if sorts is not None:
            params["sorts"] = sorts
        if start_cursor is not None:
            params["start_cursor"] = start_cursor
        if page_size is not None:
            params["page_size"] = page_size

        return self.session.post(db_url, json=params)


class NotionParser:
    text_types = ["rich_text", "title"]

    def response_to_records(self, db_response):
        records = []
        for result in db_response["results"]:
            records.append(self.get_record(result))
        return records

    def get_record(self, result):
        record = {"id": result["id"]}
        for name in result["properties"]:
            if self.is_supported(result["properties"][name]):
                record[name] = self.get_property_value(result["properties"][name])
            else:
                print(f"skip column {name}")

        return record

    def is_supported(self, prop):
        if prop.get("type") in [
            "checkbox",
            "date",
            "number",
            "rich_text",
            "title",
            "multi_select",
            "relation",
        ]:
            return True
        else:
            return False

    def get_property_value(self, prop):
        prop_type = prop.get("type")
        if prop_type in self.text_types:
            return self.get_text(prop)
        elif prop_type == "date":
            return self.get_date(prop)
        elif prop_type == "multi_select":
            return self.get_selections(prop)
        elif prop_type == "relation":
            return self.get_relations(prop)
        else:
            return prop.get(prop_type)

    def get_text(self, text_object):
        text = ""
        text_type = text_object.get("type")
        for rt in text_object.get(text_type):
            text += rt.get("plain_text")
        return text

    def get_date(self, date_object):
        date_value = date_object.get("date")
        if date_value is not None:
            if date_value.get("end") is None:
                return date_value.get("start")
            else:
                start = datetime.fromisoformat(date_value.get("start"))
                end = datetime.fromisoformat(date_value.get("end"))
                return end - start
        return None

    def get_selections(self, data):
        selections = []
        for selection in data.get("multi_select"):
            selections.append(selection["name"])
        return selections

    def get_relations(self, data):
        relations = []
        for relation in data.get("relation"):
            relations.append(relation["id"])
        return relations
