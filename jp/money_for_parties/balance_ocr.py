from openai import OpenAI
import base64
from io import BytesIO
import PIL
import sys
import PIL.Image
from transformers import AutoTokenizer
client = OpenAI(
    base_url="http://0.0.0.0:8000/v1",
    api_key="token-abc123",
)
from io import StringIO
import matplotlib.pyplot as plt
import pandas as pd
import os
import json
from tqdm.auto import tqdm
def encode_image(image_path):
    # from https://community.openai.com/t/how-to-load-a-local-image-to-gpt4-vision-using-api/533090/3
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
def get_answer2question(base64_image, question, extra_body, temperature=0.5):
    chat_response = client.chat.completions.create(
        model=".cache/models--Qwen--Qwen2-VL-7B-Instruct-GPTQ-Int4/snapshots/dec510a35a3e9b6481b6427c7a08984df2402535/",
        messages=[
            {
                "role": "system",
                "content": [
                    {"type": "text", "text": "You're a helpful agent. Please only output Japanese"}
                ]
            },
            {
                "role": "user",
                "content": [
                    # NOTE: The prompt formatting with the image token `<image>` is not needed
                    # since the prompt will be processed automatically by the API server.
                    {"type": "text", "text": question},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
                ],
            },
        ],
        temperature=temperature,
        extra_body=extra_body
    )
    return chat_response.choices[0].message.content
def get_question_constraint(index):
    questions = []
    constraints = []
    if index == 1:
        questions.append({"name": "主たる事務所の所在地", "type": str, "question": "主たる事務所の所在地はどこですか？主たる事務所の所在地のみを出力をしてください。", "extra_body": {}})
        questions.append({"name": "代表者の氏名", "type": str, "question": "代表者の氏名は？代表者の氏名のみを出力をしてください", "extra_body": {}})
        questions.append({"name": "会計責任者の氏名", "type": str, "question": "会計責任者の氏名は？会計責任者の氏名のみを出力をしてください", "extra_body": {}})
        questions.append({"name": "事務担当者の氏名", "type": str, "question": "事務担当者の氏名は？事務担当者の氏名のみを出力をしてください", "extra_body": {}})
        questions.append({"name": "政治団体の区分", "type": str, "question": "政治団体の区分は？政治団体の区分のみを出力をしてください", "extra_body": {}})
        questions.append({"name": "活動区域の区分", "type": str, "question": "活動区域の区分は？活動区域の区分のみを出力をしてください", "extra_body": {}})
        questions.append({"name": "資金管理団体の指定の有無", "type": str, "question": "資金管理団体の指定の有無は？資金管理団体の指定の有無のみを出力をしてください", "extra_body": {"guided_choice": ["有", "無"]}})
        questions.append({"name": "国会議員関係政治団体の区分", "type": str, "question": "国会議員関係政治団体の区分は？国会議員関係政治団体の区分のみを出力をしてください", "extra_body": {}})
        questions.append({"name": "国会議員関係政治団体の区分の中の公職の候補者全員の氏名", "type": str, "question": "国会議員関係政治団体の区分の中の公職の候補者全員の氏名は？国会議員関係政治団体の区分の中の公職の候補者全員の氏名のみを出力をしてください", "extra_body": {}})
        questions.append({"name": "資金管理団体の指定の期間", "type": str, "question": "資金管理団体の指定の期間は？資金管理団体の指定の期間のみを出力をしてください", "extra_body": {}})
        questions.append({"name": "国会議員関係政治団体に関する特例の適用期間", "type": str, "question": "国会議員関係政治団体に関する特例の適用期間は？国会議員関係政治団体に関する特例の適用期間のみを出力をしてください", "extra_body": {}})
    elif index == 2:
        # ensure 本年の収入額+前年からの繰越額 = 収入総額  = 支出総額+翌年への繰越額 if not redo
        questions.append({"name": "収入総額", "type": int, "question": "収入総額は？句読点なしの数字のみで出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
        questions.append({"name": "前年からの繰越額", "type": int, "question": "前年からの繰越額は？句読点なしの数字のみで出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
        questions.append({"name": "本年の収入額", "type": int, "question": "本年の収入額は？句読点なしの数字のみで出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
        constraints.append({"type": "add", "lhs": [1, 2], "rhs": [0]})
        questions.append({"name": "支出総額", "type": int, "question": "支出総額は？句読点なしの数字のみで出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
        questions.append({"name": "翌年への繰越額", "type": int, "question": "翌年への繰越額は？句読点なしの数字のみで出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
        constraints.append({"type": "add", "lhs": [3, 4], "rhs": [0]})
        
        questions.append({"name": "個人の負担する党費又は会費の金額", "type": int, "question": "個人の負担する党費又は会費の金額は？句読点なしの数字のみで出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
        questions.append({"name": "個人の負担する党費又は会費の員数", "type": int, "question": "個人の負担する党費又は会費の員数は？句読点なしの数字のみで出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
        questions.append({"name": "（ア）個人からの寄附", "type": int, "question": "（ア）個人からの寄附は？句読点なしの数字のみで出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
        # Ensure that below is smaller or equal to above
        questions.append({"name": "（ア）個人からの（うち特定寄附）", "type": int, "question": "（ア）個人からの（うち特定寄附）は？句読点なしの数字のみで出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
        questions.append({"name": "（イ）法人その他の団体からの寄附", "type": int, "question": "（イ）法人その他の団体からの寄附は？句読点なしの数字のみで出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
        questions.append({"name": "（ウ）政治団体からの寄附", "type": int, "question": "（ウ）政治団体からの寄附は？句読点なしの数字のみで出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
        # Ensure （ア）＋（イ）＋（ウ） is equal to 小計
        questions.append({"name": "小計　（ア）＋（イ）＋（ウ）", "type": int, "question": "小計　（ア）＋（イ）＋（ウ）は？句読点なしの数字のみで出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
        constraints.append({"type": "add", "lhs": [7, 9, 10], "rhs": [11]})
        # less than or equal to
        constraints.append({"type": "lte", "lhs": [8], "rhs": [7]})
        # Ensure below is lower than above
        questions.append({"name": "(寄附のうち寄附のあっせんによるもの）", "type": int, "question": "(寄附のうち寄附のあっせんによるもの）は？句読点なしの数字のみで出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
        constraints.append({"type": "lte", "lhs": [12], "rhs": [11]})
        
        questions.append({"name": "イ　政党匿名寄附", "type": int, "question": "イ　政党匿名寄附は？句読点なしの数字のみで出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
        # Ensure 小計＋イ　is below
        questions.append({"name": "合計　（ア＋イ）", "type": int, "question": "合計　（ア＋イ）は？句読点なしの数字のみで出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
        constraints.append({"type": "add", "lhs": [11, 13], "rhs": [14]})
    elif index == 3:
        # 事業からの収入（機関紙誌など）
        questions.append({"name": "事業からの収入（機関紙誌など）", "type": "csv", "question": "事業の種類,金額,備考をCSV形式で出力してください。情報がない行,計や合計を含めないでください。金額は句読点なしで数字のみで出力してください。説明は含めずcsvのみを出力してください。出力は```\n事業の種類,金額,備考で始めてください", "extra_body": {
            "guided_regex": "```\n事業の種類,金額,備考\n([^,]*,[0-9]*,[^,]*\n)*```"
        }})
        constraints.append({"type": "csv_add", "lhs": "金額", "rhs": 1})
        questions.append({"name": "この頁の小計", "type": str, "question": "この頁の小計は？句読点なしの数字のみで出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
        questions.append({"name": "合計", "type": str, "question": "合計は？句読点なしの数字のみで出力してください。もし空白なら0と出力してください。","extra_body":  {"guided_regex": "[0-9]*"}})
    elif index == 4:
        # 借入金
        questions.append({"name": "借入金", "type": "csv", "question": "借入先,金額,備考をCSV形式で出力してください。情報がない行,計や合計を含めないでください。金額は句読点なしで数字のみで出力してください。説明は含めずcsvのみを出力してください。出力は```\n借入先,金額,備考で始めてください", "extra_body": {
            "guided_regex": "```\n借入先,金額,備考\n([^,]*,[0-9]*,[^,]*\n)*```"
        }})
        constraints.append({"type": "csv_add", "lhs": "金額", "rhs": 1})
        questions.append({"name": "この頁の小計", "type": int, "question": "この頁の小計は？句読点なしの数字のみで出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
        questions.append({"name": "合計", "type": int, "question": "合計は？句読点なしの数字のみで出力してください。もし空白なら0と出力してください。", "extra_body": {"guided_regex": "[0-9]*"}})
    elif index == 5:
        # 本部又は支部からの交付金からの収入
        questions.append({"name": "本部又は支部からの交付金からの収入", "type": "csv", "question": "交付金を供与した本部又は支部の名称,金額,年月日,主たる事務所の所在地をCSV形式で出力してください。情報がない行,計や合計を含めないでください。年月日は/で分けてください。金額は句読点なしで数字のみで出力してください。説明は含めずcsvのみを出力してください。出力は```\n交付金を供与した本部又は支部の名称,金額,年月日,主たる事務所の所在地で始めてください", "extra_body": {
            "guided_regex": "```\n交付金を供与した本部又は支部の名称,金額,年月日,主たる事務所の所在地\n([^,]*,[0-9]*,[^,]*,[^,]*\n)*```"
        }})
        # after parsing the sum of 金額 must be この頁の小計 and the 合計 must be the sum of all この頁の小計
        constraints.append({"type": "csv_add", "lhs": "金額", "rhs": 1})
        
        questions.append({"name": "この頁の小計", "type": int, "question": "この頁の小計は？句読点なしの数字のみで出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
        questions.append({"name": "合計", "type": int, "question": "合計は？句読点なしの数字のみで出力してください。もし空白なら0と出力してください。", "extra_body": {"guided_regex": "[0-9]*"}})
        
    elif index == 6:
        # その他の収入
        questions.append({"name": "その他の収入", "type": "csv", "question": "摘要,金額,備考をCSV形式で出力してください。情報がない行,計や合計を含めないでください。金額は句読点なしで数字のみで出力してください。説明は含めずcsvのみを出力してください。出力は```\n摘要,金額,備考で始めてください", "extra_body": {
            "guided_regex": "```\n摘要,金額,備考\n([^,]*,[0-9]*,[^,]*\n)*```"
        }})
        constraints.append({"type": "csv_add", "lhs": "金額", "rhs": 1})
        questions.append({"name": "この頁の小計", "type": int, "question": "この頁の小計は？句読点なしの数字のみで出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
        questions.append({"name": "一件１０万円未満のものの有無", "type": str, "question": "一件１０万円未満のものという項目はありますか？’あります’か’ありません’のみで出力してください。", "extra_body": {"guided_choice": ["あります", "ありません"]}})
        questions.append({"name": "一件１０万円未満のもの", "type": int, "question": "一件１０万円未満のものは？句読点なしの数字のみで出力してください。もし空白なら0と出力してください。", "extra_body": {"guided_regex": "[0-9]*"}})
        questions.append({"name": "合計の有無", "type": str, "question": "合計という項目はありますか？’あります’か’ありません’のみで出力してください。", "extra_body": {"guided_choice": ["あります", "ありません"]}})
        questions.append({"name": "合計", "type": int, "question": "合計は？句読点なしの数字のみで出力してください。もし空白なら0と出力してください。", "extra_body": {"guided_regex": "[0-9]*"}})
    elif index == 7:
        # 寄付の内約
        questions.append({"name": "寄付の内約", "type": "csv", "question": "寄付者の氏名（又は名称）,金額,年月日,住所（又は所在地）,職業（又は代表者の氏名）,備考をCSV形式で出力してください。情報がない行,計や合計を含めないでください。金額は句読点なしで数字のみで出力してください。年月日は/で分けてください。説明は含めずcsvのみを出力してください。出力は```\n寄付者の氏名（又は名称）,金額,年月日,住所（又は所在地）,職業（又は代表者の氏名）,備考で始めてください", "extra_body": {
            "guided_regex": "```\n寄付者の氏名（又は名称）,金額,年月日,住所（又は所在地）,職業（又は代表者の氏名）,備考\n([^,]*,[0-9]*,[^,]*,[^,]*,[^,]*,[^,]*\n)*```"
        }})
        constraints.append({"type": "csv_add", "lhs": "金額", "rhs": 1})
        questions.append({"name": "この頁の小計", "type": int, "question": "この頁の小計は？句読点なしの数字のみで出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
        questions.append({"name": "その他の寄附の有無", "type": str, "question": "その他の寄附という項目はありますか？’あります’か’ありません’のみで出力してください。", "extra_body": {"guided_choice": ["あります", "ありません"]}})
        questions.append({"name": "その他の寄附", "type": int, "question": "その他の寄附は？句読点なしの数字のみで出力してください。もし空白なら0と出力してください。", "extra_body": {"guided_regex": "[0-9]*"}})
        questions.append({"name": "合計の有無", "type": str, "question": "合計という項目はありますか？この頁の小計ではなく合計という項目です。’あります’か’ありません’のみで出力してください。", "extra_body": {"guided_choice": ["あります", "ありません"]}})
        questions.append({"name": "合計", "type": int, "question": "合計は？句読点なしの数字のみで出力してください。もし空白なら0と出力してください。", "extra_body": {"guided_regex": "[0-9]*"}})
    elif index == 13:
        # ensure 本年の収入額+前年からの繰越額 = 収入総額  = 支出総額+翌年への繰越額 if not redo
        questions.append({"name": "（１）人件費", "type": int, "question": "（１）人件費は？句読点なしの数字のみで出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
        questions.append({"name": "（２）光熱水費", "type": int, "question": "（２）光熱水費は？句読点なしの数字のみで出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
        questions.append({"name": "（３）備品・消耗品費", "type": int, "question": "（３）備品・消耗品費は？句読点なしの数字のみで出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
        questions.append({"name": "（４）事務所費", "type": int, "question": "（４）事務所費は？句読点なしの数字のみで出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
        questions.append({"name": "経常経費の小計", "type": int, "question": "経常経費の小計は？句読点なしの数字のみで出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
        
        constraints.append({"type": "add", "lhs": [0, 1, 2, 3], "rhs": [4]})
        questions.append({"name": "（１）組織活動費", "type": int, "question": "（１）組織活動費は？句読点なしの数字のみで出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
        questions.append({"name": "（２）選挙関係費", "type": int, "question": "（２）選挙関係費は？句読点なしの数字のみで出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
        questions.append({"name": "（３）機関紙誌", "type": int, "question": "（３）機関紙誌の発行その他の事業費は？句読点なしの数字のみで出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
        questions.append({"name": "ア　機関紙誌の発行事業費", "type": int, "question": "ア　機関紙誌の発行事業費は？句読点なしの数字のみで出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
        questions.append({"name": "イ　宣伝事業費", "type": int, "question": "イ　宣伝事業費は？句読点なしの数字のみで出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
        questions.append({"name": "ウ　政治資金パーティー開催事業費", "type": int, "question": "ウ　政治資金パーティー開催事業費は？句読点なしの数字のみで出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
        questions.append({"name": "エ　その他の事業費", "type": int, "question": "エ　その他の事業費は？句読点なしの数字のみで出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
        questions.append({"name": "（４）調査研究費", "type": int, "question": "（４）調査研究費は？句読点なしの数字のみで出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
        questions.append({"name": "（５）寄附・交付金", "type": int, "question": "（５）寄附・交付金は？句読点なしの数字のみで出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
        questions.append({"name": "（６）その他の経費", "type": int, "question": "（６）その他の経費は？句読点なしの数字のみで出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
        questions.append({"name": "政治活動費の小計", "type": int, "question": "政治活動費の小計は？句読点なしの数字のみで出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
        questions.append({"name": "合計", "type": int, "question": "合計は？句読点なしの数字のみで出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
        constraints.append({"type": "add", "lhs": [5, 6, 7, 12, 13, 14], "rhs": [15]})
        constraints.append({"type": "add", "lhs": [4, 15], "rhs": [16]})
    elif index == 14:
        # 経常経費（人件費を除く。）の内約
        questions.append({"name": "経常経費（人件費を除く。）の内約", "type": "csv", "question": "支出の目的,金額,年月日,支出を受けたものの氏名（団体にあっては、その名称）,支出を受けたものの住所（団体にあっては、主たる事務所の所在地）,備考をCSV形式で出力してください。情報がない行,計や合計を含めないでください。年月日は/で分けてください。金額は句読点なしで数字のみで出力してください。説明は含めずcsvのみを出力してください。出力は```\n支出の目的,金額,年月日,支出を受けたものの氏名（団体にあっては、その名称）,支出を受けたものの住所（団体にあっては、主たる事務所の所在地）,備考で始めてください", "extra_body": {
            "guided_regex": "```\n支出の目的,金額,年月日,支出を受けたものの氏名（団体にあっては、その名称）,支出を受けたものの住所（団体にあっては、主たる事務所の所在地）,備考\n([^,]*,[0-9]*,[^,]*,[^,]*,[^,]*,[^,]*\n)*```"
        }})
        constraints.append({"type": "csv_add", "lhs": "金額", "rhs": 1})
        questions.append({"name": "この頁の小計", "type": int, "question": "この頁の小計は？句読点なしの数字のみで出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
        questions.append({"name": "その他の支出の有無", "type": str, "question": "その他の支出という項目はありますか？’あります’か’ありません’のみで出力してください。", "extra_body": {"guided_choice": ["あります", "ありません"]}})
        questions.append({"name": "その他の支出", "type": int, "question": "その他の支出は？句読点なしの数字のみで出力してください。もし空白なら0と出力してください。", "extra_body": {"guided_regex": "[0-9]*"}})
        questions.append({"name": "合計の有無", "type": str, "question": "合計という項目はありますか？この頁の小計ではなく合計という項目です。’あります’か’ありません’のみで出力してください。", "extra_body": {"guided_choice": ["あります", "ありません"]}})
        questions.append({"name": "合計", "type": int, "question": "合計は？句読点なしの数字のみで出力してください。もし空白なら0と出力してください。", "extra_body": {"guided_regex": "[0-9]*"}})
    elif index == 15:
        #　政治活動費の内約
        # "guided_choice": ["有", "無"]}})
        questions.append({"name": "政治活動費の内約", "type": "csv", "question": "支出の目的,金額,年月日,支出を受けたものの氏名（又は名称）,支出を受けたものの住所（又は名称）,備考をCSV形式で出力してください。情報がない行,計や合計を含めないでください。年月日は/で分けてください。金額は句読点なしで数字のみで出力してください。説明は含めずcsvのみを出力してください。出力は```\n支出の目的,金額,年月日,支出で始めてください", "extra_body": {
            "guided_regex": "```\n支出の目的,金額,年月日,支出を受けたものの氏名（又は名称）,支出を受けたものの住所（又は名称）,備考\n([^,]*,[0-9]*,[^,]*,[^,]*,[^,]*,[^,]*\n)*```"
        }})
        constraints.append({"type": "csv_add", "lhs": "金額", "rhs": 1})
        questions.append({"name": "この頁の小計", "type": int, "question": "この頁の小計は？句読点なしの数字のみで出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
        questions.append({"name": "その他の支出の有無", "type": str, "question": "その他の支出という項目はありますか？’あります’か’ありません’のみで出力してください。", "extra_body": {"guided_choice": ["あります", "ありません"]}})
        questions.append({"name": "その他の支出", "type": int, "question": "その他の支出は？句読点なしの数字のみで出力してください。もし空白なら0と出力してください。", "extra_body": {"guided_regex": "[0-9]*"}})
        questions.append({"name": "合計の有無", "type": str, "question": "合計という項目はありますか？この頁の小計ではなく合計という項目です。’あります’か’ありません’のみで出力してください。", "extra_body": {"guided_choice": ["あります", "ありません"]}})
        questions.append({"name": "合計", "type": int, "question": "合計は？句読点なしの数字のみで出力してください。もし空白なら0と出力してください。", "extra_body": {"guided_regex": "[0-9]*"}})
    elif index == 16:
        # 本部又は支部に対して供与した交付金に係る支出の内約
        questions.append({"name": "本部又は支部に対して供与した交付金に係る支出の内約", "type": "csv", "question": "支出項目,金額,年月日,交付金の供与を受けた本部又は支部の名称,主たる事務所の所在地,備考をCSV形式で出力してください。情報がない行,計や合計を含めないでください。年月日は/で分けてください。金額は句読点なしで数字のみで出力してください。説明は含めずcsvのみを出力してください。出力は```\n支出項目,金額,年月日,交付金の供与を受けた本部又は支部の名称,主たる事務所の所在地,備考で始めてください", "extra_body": {
            "guided_regex": "```\n支出項目,金額,年月日,交付金の供与を受けた本部又は支部の名称,主たる事務所の所在地,備考\n([^,]*,[0-9]*,[^,]*,[^,]*,[^,]*,[^,]*\n)*```"
        }})
        constraints.append({"type": "csv_add", "lhs": "金額", "rhs": 1})
        questions.append({"name": "この頁の小計", "type": int, "question": "この頁の小計は？句読点なしの数字のみで出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
        questions.append({"name": "合計の有無", "type": str, "question": "合計という項目はありますか？この頁の小計ではなく合計という項目です。’あります’か’ありません’のみで出力してください。", "extra_body": {"guided_choice": ["あります", "ありません"]}})
        questions.append({"name": "合計", "type": int, "question": "合計は？句読点なしの数字のみで出力してください。もし空白なら0と出力してください。", "extra_body": {"guided_regex": "[0-9]*"}})
    elif index == 17:
        # 資産等の状況
        questions.append({"name": "ア　土地の有無", "type": str, "question": "ア　土地の有無は？有か無でのみ答えてください。", "extra_body": {"guided_choice": ["有", "無"]}})
        questions.append({"name": "イ　建物の有無", "type": str, "question": "イ　建物の有無は？有か無でのみ答えてください。", "extra_body": {"guided_choice": ["有", "無"]}})
        questions.append({"name": "ウ　建物の所有を目的とする地上権又は土地の貸借権の有無", "type": str, "question": "ウ　建物の所有を目的とする地上権又は土地の貸借権の有無は？有か無でのみ答えてください。", "extra_body": {"guided_choice": ["有", "無"]}})
        questions.append({"name": "エ　取得の価格が１００万円を超える動産の有無", "type": str, "question": "エ　取得の価格が１００万円を超える動産の有無は？有か無でのみ答えてください。", "extra_body": {"guided_choice": ["有", "無"]}})
        questions.append({"name": "オ　貯金（普通預金及び当座預金を除く。）又は貯金（普通貯金を除く。）の有無", "type": str, "question": "オ　貯金（普通預金及び当座預金を除く。）又は貯金（普通貯金を除く。）の有無は？有か無でのみ答えてください。", "extra_body": {"guided_choice": ["有", "無"]}})
        questions.append({"name": "カ　金銭信託の有無", "type": str, "question": "カ　金銭信託の有無は？有か無でのみ答えてください。", "extra_body": {"guided_choice": ["有", "無"]}})
        questions.append({"name": "キ　有価証券の有無", "type": str, "question": "キ　有価証券の有無は？有か無でのみ答えてください。", "extra_body": {"guided_choice": ["有", "無"]}})
        questions.append({"name": "ク　出資により権利の有無", "type": str, "question": "ク　出資により権利の有無は？有か無でのみ答えてください。", "extra_body": {"guided_choice": ["有", "無"]}})
        questions.append({"name": "ケ　貸付先ごとの残高が１００万円を超える貸付金の有無", "type": str, "question": "ケ　貸付先ごとの残高が１００万円を超える貸付金の有無は？有か無でのみ答えてください。", "extra_body": {"guided_choice": ["有", "無"]}})
        questions.append({"name": "コ　支払われた金額が１００万円を超える敷金の有無", "type": str, "question": "コ　支払われた金額が１００万円を超える敷金の有無は？有か無でのみ答えてください。", "extra_body": {"guided_choice": ["有", "無"]}})
        questions.append({"name": "サ　取得の価格が１００万円を超える施設の利用に関する権利の有無", "type": str, "question": "サ　取得の価格が１００万円を超える施設の利用に関する権利の有無は？有か無でのみ答えてください。", "extra_body": {"guided_choice": ["有", "無"]}})
        questions.append({"name": "シ　借入先ごとの残高が１００万円を超える借入金の有無", "type": str, "question": "シ　借入先ごとの残高が１００万円を超える借入金の有無は？有か無でのみ答えてください。", "extra_body": {"guided_choice": ["有", "無"]}})
    elif index == 18:
        # 資産等の内約
        questions.append({"name": "資産等の内約", "type": "csv", "question": "摘要,金額,年月日,備考をCSV形式で出力してください。情報がない行,計や合計を含めないでください。年月日は/で分けてください。金額は句読点なしで数字のみで出力してください。説明は含めずcsvのみを出力してください。出力は```\n摘要,金額,年月日,備考で始めてください", "extra_body": {
            "guided_regex": "```\n摘要,金額,年月日,備考\n([^,]*,[0-9]*,[^,]*,[^,]*\n)*```"
        }})
        questions.append({"name": "この頁の小計", "type": int, "question": "この頁の小計は？句読点なしの数字のみで出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
    return questions, constraints

def get_content(image_url, temperature=0.5, debug=False):
    # print("Processing", image_url)
    base64_image = encode_image(image_url)
    index = int(get_answer2question(base64_image, "上の’（その’で始まる箇所の数字を出力してください。数字のみを出力してください。", {
        "guided_regex": "[0-9]+"
    }))
    handwritten = get_answer2question(base64_image, "手書きの箇所はありますか？’あります’か’ありません’でのみ答えてください。", {
        "guided_choice": ["あります", "ありません"]
    }) == "あります"
    handwritten_corrected = get_answer2question(base64_image, "手書きで修正した箇所はありますか？’あります’か’ありません’でのみ答えてください。", {
        "guided_choice": ["あります", "ありません"]
    }) == "あります"
    while index >= 21:
        index = int(get_answer2question(base64_image, "上の’（その’で始まる箇所の数字を出力してください。数字のみを出力してください。", {
            "guided_regex": "[0-9]+"
        }))
    if index not in [1, 2, 3, 4, 5, 6, 7, 13, 14, 15, 16, 17, 18, 20]:
        print(f"Got index {index} for {image_url}")
        raise Exception(f"Got index {index} for {image_url}")
    if debug:
        print(f"Index found was {index}")
    questions, constraints = get_question_constraint(index)
    output = {
        "index": index,
        "handwritten": handwritten,
        "handwritten_corrected": handwritten_corrected
    }
    for question in questions:
        while True:
            try:
                question_text, extra_body, name, data_type = question["question"], question["extra_body"], question["name"], question["type"]
                chat_completion = get_answer2question(base64_image, question_text, extra_body, temperature=temperature)
                
                if data_type == "csv":
                    chat_completion = chat_completion.replace("```\n", "").split("\n```")[0]
                    if len(chat_completion) > 0:
                        assert "," in chat_completion
                    if debug:
                        print("chat completion was ", chat_completion)
                    temp_path = StringIO(chat_completion)
                    data = pd.read_csv(temp_path, sep=",")
                    if data.isnull().values.any():
                        print(chat_completion)
                        raise Exception("Failed pandas format")
                    data = data.to_dict()
                else:
                    data = chat_completion
                    
                output[name] = data
                if debug:
                    print("name:", name, ",output:", data)
                break
            except Exception as e:
                print("Got error", e)
                continue

    if debug:
        print(f"Output {output}")
    return output
def main():
    balance_dir = sys.argv[1]
    temperature = float(sys.argv[2])
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2-VL-7B-Instruct-GPTQ-Int4")

    image_paths = []
    for date_dir in os.listdir(balance_dir):
        date_path = f"{balance_dir}/{date_dir}"
        for party_dir in os.listdir(date_path):
            party_path = f"{date_path}/{party_dir}"
            if os.path.isdir(party_path):
                for image_name in os.listdir(party_path):
                    image_path = f"{party_path}/{image_name}"
                    image_paths.append(image_path)
    for image_path in tqdm(image_paths):
        temperature_str = str(temperature).replace(".", "_")
        json_path = image_path.replace(".jpg", f"_temperature_{temperature_str}.json")
        if os.path.exists(json_path):
            continue
        try:
            output = get_content(image_path, temperature=temperature, debug=False)
            with open(json_path, "w") as f:
                json.dump(output, f, indent=6)
        except:
            continue
if __name__ == "__main__":
    main()