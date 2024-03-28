import pandas as pd


class DataLoader:
    def __init__(self, notion_client, pandas_converter):
        self.notion_client = notion_client
        self.converter = pandas_converter

    def load_db(self, db_id):
        page_count = 1
        print(f"Loading page {page_count}")
        db_response = self.notion_client.query_database(db_id)
        records = []
        if db_response.ok:
            db_response_obj = db_response.json()
            records.extend(self.converter.response_to_records(db_response_obj))

            while db_response_obj.get("has_more"):
                page_count += 1
                print(f"Loading page {page_count}")
                start_cursor = db_response_obj.get("next_cursor")
                db_response = self.notion_client.query_database(
                    db_id, start_cursor=start_cursor
                )
                if db_response.ok:
                    db_response_obj = db_response.json()
                    records.extend(self.converter.response_to_records(db_response_obj))
        return pd.DataFrame(records)
