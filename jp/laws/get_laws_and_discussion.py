# I couldn't find copyright atm
"""
When analyzing the request packets when reading individual laws I found requests in the format
GET /law/api/v1/detail/lawDetail?lawId=0000020484&billId= HTTP/2

Then next
GET /law/api/v1/detail/relationUrl?lawId=0000020484 HTTP/2

Then
GET /law/api/v1/detail/history?lawId=0000020484 HTTP/2

Then
GET /law/api/v1/detail/lawlist HTTP/2


Then
GET /law/api/v1/detail/reviced?lawId=0000020484 HTTP/2

For getting the next law
GET /law/api/v1/search/list?order=1&page=2&perpage=1 HTTP/2

and got 
GET /law/api/v1/detail/lawlist?billIds=009011001 HTTP/2

it seemed like here both the law and bill was requested as both are used to populate this request
For search we will try
GET /law/api/v1/search/validate?order=1&page=1&perpage=20 HTTP/2

For getting list
GET /law/api/v1/search/validate?order=1&page=1&perpage=20 HTTP/2

then
GET /law/api/v1/search/detail?order=1&page=1&perpage=20 HTTP/2
"""

import traceback
import requests

import os
import json
from tqdm.auto import tqdm
from copy import deepcopy
import time
# dummy length
MAX_FILENAME_LENGTH: int = 128

base_dir = "data/jp"

def populate_law_and_bill_ids(data: dict, all_law_ids: dict, all_bill_ids: dict):
    for law_elem in data["data"]:
        if len(law_elem["law_id"]) == 0:
            assert len(law_elem["bill_id"]) > 0
            all_bill_ids[law_elem["bill_id"]] = law_elem
        elif len(law_elem["bill_id"]) == 0:
            assert len(law_elem["law_id"]) > 0
            all_law_ids[law_elem["law_id"]] = law_elem
        else:
            print(f"Both bill id nor law id were found in {law_elem}")
            # In this case, I think prioritize bill_id as currently the examples are
            """
            {'bill_id': '100101001', 'law_id': '0000039225', 'subject': '国民貯蓄組合法の一部を改正する法律案', 'sname': None, 'type': '法律案', 'div': 
            '閣法', 'announcement': '（第1回国会 閣法 第1号） （提出者：内閣）（昭和22年法律第99号）', 'order_date': '3220701', 'subject_admin': '国民貯蓄組合法の一部を改正する法律案', 'bill_sub_id': 1, 
            'sts_cd': '4', 'correct_flg': False, 'search_div': '2'}
            """
            all_bill_ids[law_elem["bill_id"]] = law_elem
def get_bill_data_from_bill_id(bill_id: str, existing_bill_ids: list, all_bill_ids: dict, i: int, bills_dir: str, delay_between_requests: int = 3):
    """
    for bills
    GET /law/api/v1/detail/lawDetail?lawId=&billId=115902007 HTTP/2
    GET /law/api/v1/detail/lawlist?billIds=115902007 HTTP/2
    GET /law/api/v1/detail/relationUrl?lawId=&billIds=115902007 HTTP/2
    without a bill there is no 審議経過 for bills
    """
    base_url = "http://hourei.ndl.go.jp"
    output = {}
    output["original"] = all_bill_ids[bill_id]
    time.sleep(delay_between_requests)
    output["lawDetail"] = requests.get(f"{base_url}/law/api/v1/detail/lawDetail?lawId=&billId={bill_id}").json()
    output["relationUrl"] = requests.get(f"{base_url}/law/api/v1/detail/relationUrl?lawId=&billIds={bill_id}").json()
    output["lawlist"] = requests.get(f"{base_url}/law/api/v1/detail/lawlist?billIds={bill_id}").json()
    name = output["original"]["subject"]
    max_name_length = MAX_FILENAME_LENGTH - len(f"{i}__{bill_id}.json")
    name = name[-max_name_length:]
    filename = f"{bills_dir}/{i}_{name}_{bill_id}.json"
    with open(filename, "wb") as f:
        f.write(json.dumps(output, ensure_ascii=False).encode("utf8"))
    existing_bill_ids.append(bill_id)

def get_laws():
    base_url = "http://hourei.ndl.go.jp"
    delay_between_requests = 2
    laws_and_bills_base_dir = base_dir+"/laws_and_bills"
    os.makedirs(base_dir, exist_ok=True)
    os.makedirs(laws_and_bills_base_dir, exist_ok=True)

    laws_dir = laws_and_bills_base_dir+"/laws"
    os.makedirs(laws_dir, exist_ok=True)
    bills_dir = laws_and_bills_base_dir+"/bills"
    os.makedirs(bills_dir, exist_ok=True)
    if not os.path.exists(laws_and_bills_base_dir+"/all_law_ids.json"):
        all_law_ids = {}
        all_bill_ids = {}
        data = requests.get(f"{base_url}/law/api/v1/search/detail?order=1&page=1&perpage=100").json()
        populate_law_and_bill_ids(data, all_law_ids, all_bill_ids)


        total_pages = data["total_pages"]
        # first gather all law and bill ids
        for i in tqdm(range(2, total_pages)):
            time.sleep(delay_between_requests)
            data = requests.get(f"{base_url}/law/api/v1/search/detail?order=1&page={i}&perpage=100").json()
            populate_law_and_bill_ids(data, all_law_ids, all_bill_ids)

        with open(laws_and_bills_base_dir+"/all_law_ids.json", "wb") as f:
            f.write(json.dumps(all_law_ids, ensure_ascii=False).encode("utf8"))

        with open(laws_and_bills_base_dir+"/all_bill_ids.json", "wb") as f:
            f.write(json.dumps(all_bill_ids, ensure_ascii=False).encode("utf8"))
    else:
        with open(laws_and_bills_base_dir+"/all_law_ids.json", 'r', encoding="utf-8") as f:
            all_law_ids = json.load(f)
        with open(laws_and_bills_base_dir+"/all_bill_ids.json", 'r', encoding="utf-8") as f:
            all_bill_ids = json.load(f)
    existing_law_files = os.listdir(laws_dir)
    existing_law_ids = [existing_law_file.split("_")[2].split(".")[0] for existing_law_file in existing_law_files]
    existing_bill_files = os.listdir(bills_dir)
    existing_bill_ids = [existing_bill_file.split("_")[2].split(".")[0] for existing_bill_file in existing_bill_files]

    progress_bar = tqdm(
        range(len(all_law_ids)),
        desc="Law steps",
    )
    for i, law_id in enumerate(all_law_ids):
        progress_bar.update(1)
        if law_id in existing_law_ids:
            continue

        name = all_law_ids[law_id]["subject"]
        time.sleep(delay_between_requests)
        output = {}
        output["original"] = all_law_ids[law_id]
        output["lawDetail"] = requests.get(f"{base_url}/law/api/v1/detail/lawDetail?lawId={law_id}").json()
        output["relationUrl"] = requests.get(f"{base_url}/law/api/v1/detail/relationUrl?lawId={law_id}").json()
        output["history"] = requests.get(f"{base_url}/law/api/v1/detail/history?lawId={law_id}").json()
        # I'm not sure what revice is but it covers 被改正法令 so I think this is supposed to be revised
        output["revised"] = requests.get(f"{base_url}/law/api/v1/detail/reviced?lawId={law_id}").json()
        # I couldn't figure out what http://hourei.ndl.go.jp/law/api/v1/detail/lawlist does without any parameters. It does seem to make sense for bill ids as they provide the bill ids
        max_name_length = MAX_FILENAME_LENGTH - len(f"{i}__{law_id}.json")
        name = name[-max_name_length:]
        filename = f"{laws_dir}/{i}_{name}_{law_id}.json"
        with open(filename, "wb") as f:
            f.write(json.dumps(output, ensure_ascii=False).encode("utf8"))
        bill_id = output["lawDetail"]["data"][0]["detail"][0]["bill_id"]
        if bill_id is not None:
            get_bill_data_from_bill_id(bill_id, existing_bill_ids, all_bill_ids, i, bills_dir, delay_between_requests)

    progress_bar = tqdm(
        range(len(all_law_ids)),
        desc="Bills steps",
    )
    for i, bill_id in tqdm(enumerate(all_bill_ids)):
        progress_bar.update(1)
        if bill_id in existing_bill_ids:
            continue
        time.sleep(delay_between_requests)
        get_bill_data_from_bill_id(bill_id, existing_bill_ids, all_bill_ids, i, bills_dir, delay_between_requests)

if __name__ == "__main__":
    while True:
        try:
            get_laws()
        except KeyboardInterrupt:
            raise Exception()
        except:
            print(traceback.format_exc())