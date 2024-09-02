# Copyright requirement:
# 個々の発言のうち国立国会図書館長を含む国立国会図書館職員の発言及びデータベース自体の著作権は国立国会図書館に帰属しています。
# その他の発言の著作権は個々の発言者に帰属し、その利用については、原則として、著作権者の許諾が必要となります。ただし、著作権の保護期間が満了している発言者の場合や、著作権法の権利制限規定が適用される場合（私的使用のための複製、引用、政治上の演説又は陳述に該当する箇所の利用、報道、電子計算機による情報解析等）には、著作権法の定める条件に従って、著作権者の許諾を得ることなくご利用いただけます。著作権者の許諾の要否、許諾を得ることなく利用できる場合の利用条件等については、ご自身でご確認ください
# so if we modify/analyze it seems to be fine as long as it's extensive
# For the statements, there seems to be an api
import time
import requests
import json
import os
from tqdm.auto import tqdm
base_dir = "data/jp"
def get_all_meetings():
    global base_dir
    # format for json is
    # {
    #     "numberOfRecords": 総結果件数 ,
    #     "numberOfReturn": 返戻件数 ,
    #     "startRecord": 開始位置 ,
    #     "nextRecordPosition": 次開始位置 ,
    #     "meetingRecord":[
    #         {
    #         "issueID": 会議録ID ,
    #         "imageKind": イメージ種別（会議録・目次・索引・附録・追録） ,
    #         "searchObject": 検索対象箇所（議事冒頭・本文） ,
    #         "session": 国会回次 ,
    #         "nameOfHouse": 院名 ,
    #         "nameOfMeeting": 会議名 ,
    #         "issue": 号数 ,
    #         "date": 開催日付 ,
    #         "closing": 閉会中フラグ ,
    #         "speechRecord":[
    #             {
    #             "speechID": 発言ID ,
    #             "speechOrder": 発言番号 ,
    #             "speaker": 発言者名 ,
    #             "speakerYomi": 発言者よみ（※会議単位出力のみ） ,
    #             "speakerGroup": 発言者所属会派（※会議単位出力のみ） ,
    #             "speakerPosition": 発言者肩書き（※会議単位出力のみ） ,
    #             "speakerRole": 発言者役割（※会議単位出力のみ） ,
    #             "speech": 発言（※会議単位出力のみ） ,
    #             "startPage": 発言が掲載されている開始ページ（※会議単位出力のみ） ,
    #             "createTime": レコード登録日時（※会議単位出力のみ） ,
    #             "updateTime": レコード更新日時（※会議単位出力のみ） ,
    #             "speechURL": 発言URL ,
    #             },
    #             {
    #             （次の発言情報）
    #             }
    #         ],
    #         "meetingURL": 会議録テキスト表示画面のURL ,
    #         "pdfURL": 会議録PDF表示画面のURL（※存在する場合のみ） ,
    #         },
    #         {
    #         （次の会議録情報）
    #         }
    #     ]
    # }
    # Format recorded will be
    # i_date_nameOfHouse_nameOfMeeting.json
    base_url = f"https://kokkai.ndl.go.jp/api/meeting?from=0000-01-01&until=9999-12-31&maximumRecords=10&recordPacking=json&startRecord="
    diet_statements_dir = base_dir+"/diet_statements"
    os.makedirs(diet_statements_dir, exist_ok=True)
    collected_statements = os.listdir(diet_statements_dir)
    i = 0
    for statement in collected_statements:
        i = max(i, int(statement.split("_")[0]))
    collected_statements = sorted(collected_statements)
    i += 1
    output = json.loads(requests.get(base_url+str(i)).text)
    all_records = output['numberOfRecords']
    progress_bar = tqdm(
        range(1, all_records),
        initial=i,
        desc="Steps",
    )
    while i < all_records:
        meetings = output["meetingRecord"]
        for meeting in meetings:
            nameOfHouse = meeting["nameOfHouse"]
            date = meeting["date"]
            nameOfMeeting = meeting["nameOfMeeting"]
            filename = f"{diet_statements_dir}/{i}_{date}_{nameOfHouse}_{nameOfMeeting}.json"
            with open(filename, "wb") as f:
                f.write(json.dumps(meeting, ensure_ascii=False).encode("utf8"))
            i += 1
            progress_bar.update(1)

        assert i == output['nextRecordPosition']

        time.sleep(5)
        output = json.loads(requests.get(base_url+str(i)).text)




if __name__ == "__main__":
    get_all_meetings()