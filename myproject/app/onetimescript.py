import os
from django.conf import settings
import json
import csv
import time
from app.models import DomainRank

class OneTimeScript:
    def __init__(self):
        self.file_path = os.path.join(settings.BASE_DIR, 'app', 'static', 'data', 'top-1m.csv')
        self.output_txt_path = os.path.join(settings.BASE_DIR, 'app', 'static', 'data', 'sorted-top1million.txt')
        self.output_json_path = os.path.join(settings.BASE_DIR, 'app', 'static', 'data', 'domain-rank.json')

    def check_file_existence(self):
        if not os.path.exists(self.file_path):
            print("File does not exist:", self.file_path)
            return False
        return True

    def create_sorted_arr_and_dict(self):
        # Same as before (uses self.file_path etc.)
        # Write domain-rank.json
        # return status dict
        pass

    def populate_db_from_csv(self):
        try:
            start = time.time()

            if not self.check_file_existence():
                return {'status': 'ERROR', 'msg':"File missing at " + self.file_path}

            batch_size = 10000
            batch = []
            with open(self.file_path, 'r') as file:
                reader = csv.reader(file)
                for index, row in enumerate(reader):
                    batch.append(DomainRank(domain_name=row[1], rank=int(row[0])))
                    if (index + 1) % batch_size == 0:
                        DomainRank.objects.bulk_create(batch, ignore_conflicts=True)
                        batch = []
                if batch:
                    DomainRank.objects.bulk_create(batch, ignore_conflicts=True)
            end = time.time()
            return {'status': 'SUCCESS', 'msg': f'Execution Time: {round(end - start, 2)} seconds'}

        except Exception as e:
            print(f"Error: {e}")
            return {'status': 'ERROR', 'msg': str(e)}

def update_db():
    script = OneTimeScript()
    return script.populate_db_from_csv()

def update_json():
    script = OneTimeScript()
    return script.create_sorted_arr_and_dict()
