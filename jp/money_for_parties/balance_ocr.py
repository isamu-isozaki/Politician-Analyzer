from openai import OpenAI
import base64
import sys
client = OpenAI(
    base_url="http://0.0.0.0:8000/v1",
    api_key="token-abc123",
)
import sys
from io import StringIO
import pandas as pd
import os
import json
from tqdm.auto import tqdm
from outlines.fsm.json_schema import build_regex_from_schema
# generated from 1. Having the model output the json format it prefers and
# 2. I went to https://www.liquid-technologies.com/online-json-to-schema-converter
revenue_json_schema = schema = """{
  "$schema": "http://json-schema.org/draft-04/schema#",
  "type": "object",
  "properties": {
    "1 収支の総括表": {
      "type": "object",
      "properties": {
        "収入総額": {
          "type": "string"
        },
        "（前年からの繰越額）": {
          "type": "string"
        },
        "（本年の収入額）": {
          "type": "string"
        },
        "支出総額": {
          "type": "string"
        },
        "翌年への繰越額": {
          "type": "string"
        }
      },
      "required": [
        "収入総額",
        "（前年からの繰越額）",
        "（本年の収入額）",
        "支出総額",
        "翌年への繰越額"
      ]
    },
    "2 収入項目別金額の内訳": {
      "type": "object",
      "properties": {
        "(1)個人の負担する党費又は会費": {
          "type": "object",
          "properties": {
            "金額": {
              "type": "string"
            },
            "員数（党費又は会費を納入した人の数）": {
              "type": "string"
            }
          },
          "required": [
            "金額",
            "員数（党費又は会費を納入した人の数）"
          ]
        },
        "(2)寄附": {
          "type": "object",
          "properties": {
            "ア 寄附（イを除く。）の区分": {
              "type": "object",
              "properties": {
                "（ア）個人からの寄附": {
                  "type": "string"
                },
                "（ア）個人からの寄附（うち特定寄附）": {
                  "type": "string"
                },
                "（イ）法人その他の団体からの寄附": {
                  "type": "string"
                },
                "（ウ）政治団体からの寄附": {
                  "type": "string"
                },
                "小計（ア）+（イ）+（ウ）": {
                  "type": "string"
                },
                "（寄附のうち寄附のあっせんによるもの）": {
                  "type": "string"
                }
              },
              "required": [
                "（ア）個人からの寄附",
                "（ア）個人からの寄附（うち特定寄附）",
                "（イ）法人その他の団体からの寄附",
                "（ウ）政治団体からの寄附",
                "小計（ア）+（イ）+（ウ）",
                "（寄附のうち寄附のあっせんによるもの）"
              ]
            },
            "イ 政党匿名寄附": {
              "type": "string"
            },
            "合計 （ア＋イ）": {
              "type": "string"
            }
          },
          "required": [
            "ア 寄附（イを除く。）の区分",
            "イ 政党匿名寄附",
            "合計 （ア＋イ）"
          ]
        }
      },
      "required": [
        "(1)個人の負担する党費又は会費",
        "(2)寄附"
      ]
    }
  },
  "required": [
    "1 収支の総括表",
    "2 収入項目別金額の内訳"
  ]
}"""
revenue_regex = build_regex_from_schema(schema, whitespace_pattern=r"[\r\n ]*")
revenue_regex = "```json\n"+revenue_regex+"\n```"
costs_schema = """{
  "$schema": "http://json-schema.org/draft-04/schema#",
  "type": "object",
  "properties": {
    "支出の総括表": {
      "type": "object",
      "properties": {
        "1 経常経費": {
          "type": "object",
          "properties": {
            "人件費": {
              "type": "string"
            },
            "光熱水費": {
              "type": "string"
            },
            "備品・消耗品費": {
              "type": "string"
            },
            "事務所費": {
              "type": "string"
            },
            "小計": {
              "type": "string"
            }
          },
          "required": [
            "人件費",
            "光熱水費",
            "備品・消耗品費",
            "事務所費",
            "小計"
          ]
        },
        "2 政治活動費": {
          "type": "object",
          "properties": {
            "組織活動費": {
              "type": "string"
            },
            "選挙関係費": {
              "type": "string"
            },
            "機関紙誌の発行その他の事業費": {
              "type": "string"
            },
            "調査研究費": {
              "type": "string"
            },
            "寄附・交付金": {
              "type": "string"
            },
            "その他の経費": {
              "type": "string"
            },
            "小計": {
              "type": "string"
            },
            "合計": {
              "type": "string"
            }
          },
          "required": [
            "組織活動費",
            "選挙関係費",
            "機関紙誌の発行その他の事業費",
            "調査研究費",
            "寄附・交付金",
            "その他の経費",
            "小計",
            "合計"
          ]
        }
      },
      "required": [
        "1 経常経費",
        "2 政治活動費"
      ]
    }
  },
  "required": [
    "支出の総括表"
  ]
}"""

costs_regex = build_regex_from_schema(costs_schema, whitespace_pattern=r"[\r\n ]*")
costs_regex = "```json\n"+costs_regex+"\n```"
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
        questions.append({"name": "収支の状況", "type": dict, "question":  f"Do an OCR to output a python dictionary. This is the schema: {revenue_json_schema}. 数字は分割せずにまとめてください。", "extra_body": {"guided_regex": revenue_regex}})
        constraints.append({"type": "add", "lhs": ["収支の状況/1 収支の総括表/（前年からの繰越額）", "収支の状況/1 収支の総括表/（本年の収入額）"], "rhs": ["収支の状況/1 収支の総括表/収入総額"]})
        constraints.append({"type": "add", "lhs": ["収支の状況/1 収支の総括表/支出総額", "収支の状況/1 収支の総括表/翌年への繰越額"], "rhs": ["収支の状況/1 収支の総括表/収入総額"]})
        constraints.append({"type": "add", "lhs": ["収支の状況/2 収入項目別金額の内訳/(2)寄附/ア 寄附（イを除く。）の区分/（ア）個人からの寄附", "収支の状況/2 収入項目別金額の内訳/(2)寄附/ア 寄附（イを除く。）の区分/（イ）法人その他の団体からの寄附", "収支の状況/2 収入項目別金額の内訳/(2)寄附/ア 寄附（イを除く。）の区分/（ウ）政治団体からの寄附"], "rhs": ["収支の状況/2 収入項目別金額の内訳/(2)寄附/ア 寄附（イを除く。）の区分/小計（ア）+（イ）+（ウ）"]})
        constraints.append({"type": "add", "lhs": ["収支の状況/2 収入項目別金額の内訳/(2)寄附/ア 寄附（イを除く。）の区分/小計（ア）+（イ）+（ウ）", "収支の状況/2 収入項目別金額の内訳/(2)寄附/イ 政党匿名寄附"], "rhs": ["収支の状況/2 収入項目別金額の内訳/(2)寄附/合計 （ア＋イ）"]})
    elif index == 3:
        # 事業からの収入（機関紙誌など）
        questions.append({"name": "事業からの収入（機関紙誌など）", "type": "csv", "question": "事業の種類,金額,備考をCSV形式で出力してください。情報がない行,計や合計を含めないでください。金額は句読点なしで数字のみで出力してください。説明は含めずcsvのみを出力してください。出力は```\n事業の種類,金額,備考で始めてください", "extra_body": {
            "guided_regex": "```\n事業の種類,金額,備考\n([^,]*,[0-9]*,[^,]*\n)*```[\s\S]*"
        }})
        constraints.append({"type": "csv_add", "lhs": "事業からの収入（機関紙誌など）/金額", "rhs": "この頁の小計"})
        questions.append({"name": "この頁の小計", "type": str, "question": "この頁の小計は？句読点なしの数字のみで出力してください。もし空白なら0と出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
        questions.append({"name": "合計", "type": str, "question": "合計は？句読点なしの数字のみで出力してください。もし空白なら0と出力してください。","extra_body":  {"guided_regex": "[0-9]*"}})
    elif index == 4:
        # 借入金
        questions.append({"name": "借入金", "type": "csv", "question": "借入先,金額,備考をCSV形式で出力してください。情報がない行,計や合計を含めないでください。金額は句読点なしで数字のみで出力してください。説明は含めずcsvのみを出力してください。出力は```\n借入先,金額,備考で始めてください", "extra_body": {
            "guided_regex": "```\n借入先,金額,備考\n([^,]*,[0-9]*,[^,]*\n)*```[\s\S]*"
        }})
        constraints.append({"type": "csv_add", "lhs": "借入金/金額", "rhs": "この頁の小計"})
        questions.append({"name": "この頁の小計", "type": int, "question": "この頁の小計は？句読点なしの数字のみで出力してください。もし空白なら0と出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
        questions.append({"name": "合計", "type": int, "question": "合計は？句読点なしの数字のみで出力してください。もし空白なら0と出力してください。", "extra_body": {"guided_regex": "[0-9]*"}})
    elif index == 5:
        # 本部又は支部からの交付金からの収入
        questions.append({"name": "本部又は支部からの交付金からの収入", "type": "csv", "question": "交付金を供与した本部又は支部の名称,金額,年月日,主たる事務所の所在地をCSV形式で出力してください。情報がない行,計や合計を含めないでください。年月日は/で分けてください。金額は句読点なしで数字のみで出力してください。説明は含めずcsvのみを出力してください。出力は```\n交付金を供与した本部又は支部の名称,金額,年月日,主たる事務所の所在地で始めてください", "extra_body": {
            "guided_regex": "```\n交付金を供与した本部又は支部の名称,金額,年月日,主たる事務所の所在地\n([^,]*,[0-9]*,[^,]*,[^,]*\n)*```[\s\S]*"
        }})
        # after parsing the sum of 金額 must be この頁の小計 and the 合計 must be the sum of all この頁の小計
        constraints.append({"type": "csv_add", "lhs": "本部又は支部からの交付金からの収入/金額", "rhs": "この頁の小計"})

        questions.append({"name": "この頁の小計", "type": int, "question": "この頁の小計は？句読点なしの数字のみで出力してください。もし空白なら0と出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
        questions.append({"name": "合計", "type": int, "question": "合計は？句読点なしの数字のみで出力してください。もし空白なら0と出力してください。", "extra_body": {"guided_regex": "[0-9]*"}})

    elif index == 6:
        # その他の収入
        questions.append({"name": "その他の収入", "type": "csv", "question": "摘要,金額,備考をCSV形式で出力してください。情報がない行,計や合計を含めないでください。金額は句読点なしで数字のみで出力してください。説明は含めずcsvのみを出力してください。出力は```\n摘要,金額,備考で始めてください", "extra_body": {
            "guided_regex": "```\n摘要,金額,備考\n([^,]*,[0-9]*,[^,]*\n)*```[\s\S]*"
        }})
        constraints.append({"type": "csv_add", "lhs": "その他の収入/金額", "rhs": "この頁の小計"})
        questions.append({"name": "この頁の小計", "type": int, "question": "この頁の小計は？句読点なしの数字のみで出力してください。もし空白なら0と出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
        questions.append({"name": "一件１０万円未満のものの有無", "type": str, "question": "一件１０万円未満のものという項目はありますか？’あります’か’ありません’のみで出力してください。", "extra_body": {"guided_choice": ["あります", "ありません"]}})
        questions.append({"name": "一件１０万円未満のもの", "type": int, "question": "一件１０万円未満のものは？句読点なしの数字のみで出力してください。もし空白なら0と出力してください。", "extra_body": {"guided_regex": "[0-9]*"}})
        questions.append({"name": "合計の有無", "type": str, "question": "合計という項目はありますか？’あります’か’ありません’のみで出力してください。", "extra_body": {"guided_choice": ["あります", "ありません"]}})
        questions.append({"name": "合計", "type": int, "question": "合計は？句読点なしの数字のみで出力してください。もし空白なら0と出力してください。", "extra_body": {"guided_regex": "[0-9]*"}})
    elif index == 7:
        # 寄附の内訳
        questions.append({"name": "寄附の内訳", "type": "csv", "question": "寄附者の氏名（又は名称）,金額,年月日,住所（又は所在地）,職業（又は代表者の氏名）,備考をCSV形式で出力してください。情報がない行,計や合計を含めないでください。金額は句読点なしで数字のみで出力してください。年月日は/で分けてください。説明は含めずcsvのみを出力してください。出力は```\n寄附者の氏名（又は名称）,金額,年月日,住所（又は所在地）,職業（又は代表者の氏名）,備考で始めてください", "extra_body": {
            "guided_regex": "```\n寄附者の氏名（又は名称）,金額,年月日,住所（又は所在地）,職業（又は代表者の氏名）,備考\n([^,]*,[0-9]*,[^,]*,[^,]*,[^,]*,[^,]*\n)*```[\s\S]*"
        }})
        constraints.append({"type": "csv_add", "lhs": "寄附の内訳/金額", "rhs": "この頁の小計"})
        questions.append({"name": "この頁の小計", "type": int, "question": "この頁の小計は？句読点なしの数字のみで出力してください。もし空白なら0と出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
        questions.append({"name": "その他の寄附の有無", "type": str, "question": "その他の寄附という項目はありますか？’あります’か’ありません’のみで出力してください。", "extra_body": {"guided_choice": ["あります", "ありません"]}})
        questions.append({"name": "その他の寄附", "type": int, "question": "その他の寄附は？句読点なしの数字のみで出力してください。もし空白なら0と出力してください。", "extra_body": {"guided_regex": "[0-9]*"}})
        questions.append({"name": "合計の有無", "type": str, "question": "合計という項目はありますか？この頁の小計ではなく合計という項目です。’あります’か’ありません’のみで出力してください。", "extra_body": {"guided_choice": ["あります", "ありません"]}})
        questions.append({"name": "合計", "type": int, "question": "合計は？句読点なしの数字のみで出力してください。もし空白なら0と出力してください。", "extra_body": {"guided_regex": "[0-9]*"}})
    elif index == 8:
        # 寄附のうち寄附のあっせんによるものの内訳
        questions.append({"name": "あっせん者の区分", "type": str, "question": "あっせん者の区分は？個人、法人・その他の団体、政治団体のうち一つを出力してください。", "extra_body": {"guided_choice": ["個人", "法人・その他の団体", "政治団体"]}})
        questions.append({"name": "寄附のうち寄附のあっせんによるものの内訳", "type": "csv", "question": "寄附のあっせん者の氏名（又は名称）,金額,提供年月日,集めた期間,住所（又は所在地）,職業（又は代表者の氏名）,備考をCSV形式で出力してください。情報がない行,計や合計を含めないでください。金額は句読点なしで数字のみで出力してください。年月日は/で分けてください。説明は含めずcsvのみを出力してください。出力は```\n寄附のあっせん者の氏名（又は名称）,金額,提供年月日,集めた期間,住所（又は所在地）,職業（又は代表者の氏名）,備考で始めてください", "extra_body": {
            "guided_regex": "```\n寄附のあっせん者の氏名（又は名称）,金額,提供年月日,集めた期間、住所（又は所在地）,職業（又は代表者の氏名）,備考\n([^,]*,[0-9]*,[^,]*,[^,]*,[^,]*,[^,]*,[^,]*\n)*```[\s\S]*"
        }})
        constraints.append({"type": "csv_add", "lhs": "寄附のうち寄附のあっせんによるものの内訳/金額", "rhs": "この頁の小計"})
        questions.append({"name": "この頁の小計", "type": int, "question": "この頁の小計は？句読点なしの数字のみで出力してください。もし空白なら0と出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
        questions.append({"name": "その他の寄附の有無", "type": str, "question": "その他の寄附という項目はありますか？’あります’か’ありません’のみで出力してください。", "extra_body": {"guided_choice": ["あります", "ありません"]}})
        questions.append({"name": "その他の寄附", "type": int, "question": "その他の寄附は？句読点なしの数字のみで出力してください。もし空白なら0と出力してください。", "extra_body": {"guided_regex": "[0-9]*"}})
        questions.append({"name": "合計の有無", "type": str, "question": "合計という項目はありますか？この頁の小計ではなく合計という項目です。’あります’か’ありません’のみで出力してください。", "extra_body": {"guided_choice": ["あります", "ありません"]}})
        questions.append({"name": "合計", "type": int, "question": "合計は？句読点なしの数字のみで出力してください。もし空白なら0と出力してください。", "extra_body": {"guided_regex": "[0-9]*"}})
    elif index == 9:
        # 政党匿名寄附の内訳
        questions.append({"name": "政党匿名寄附の内訳", "type": "csv", "question": "政党匿名寄附を受けた場所,金額,年月日,備考をCSV形式で出力してください。情報がない行,計や合計を含めないでください。金額は句読点なしで数字のみで出力してください。年月日は/で分けてください。説明は含めずcsvのみを出力してください。出力は```\n政党匿名寄附を受けた場所,金額,年月日,備考で始めてください", "extra_body": {
            "guided_regex": "```\n政党匿名寄附を受けた場所,金額,年月日,備考\n([^,]*,[0-9]*,[^,]*,[^,]*\n)*```[\s\S]*"
        }})
        # 政治資金パーティーの対価に係る収入の内訳
        questions.append({"name": "政治資金パーティーの対価に係る収入の内訳", "type": "csv", "question": "対価の支払をした者の氏名（団体にあっては、その名称）,金額,年月日,住所（団体にあっては、主たる事務所の所在地）,職業（団体にあっては、代表者の氏名）,備考をCSV形式で出力してください。情報がない行,計や合計を含めないでください。金額は句読点なしで数字のみで出力してください。年月日は/で分けてください。説明は含めずcsvのみを出力してください。出力は```\n対価の支払をした者の氏名（団体にあっては、その名称）,金額,年月日,住所（団体にあっては、主たる事務所の所在地）,職業（団体にあっては、代表者の氏名）,備考で始めてください", "extra_body": {
            "guided_regex": "```\n対価の支払をした者の氏名（団体にあっては、その名称）,金額,年月日,住所（団体にあっては、主たる事務所の所在地）,職業（団体にあっては、代表者の氏名）,備考\n([^,]*,[0-9]*,[^,]*,[^,]*,[^,]*,[^,]*\n)*```[\s\S]*"
        }})
        constraints.append({"type": "csv_add", "lhs": "政治資金パーティーの対価に係る収入の内訳/金額", "rhs": "この頁の小計"})
        questions.append({"name": "この頁の小計", "type": int, "question": "この頁の小計は？句読点なしの数字のみで出力してください。もし空白なら0と出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
        questions.append({"name": "合計の有無", "type": str, "question": "合計という項目はありますか？この頁の小計ではなく合計という項目です。’あります’か’ありません’のみで出力してください。", "extra_body": {"guided_choice": ["あります", "ありません"]}})
        questions.append({"name": "合計", "type": int, "question": "合計は？句読点なしの数字のみで出力してください。もし空白なら0と出力してください。", "extra_body": {"guided_regex": "[0-9]*"}})
    elif index == 12:
        # 政治資金パーティーの対価に係る収入のうち対価の支払のあっせんによるものの内訳
        questions.append({"name": "政治資金パーティーの名称", "type": str, "question": "政治資金パーティーの名称は何ですか？", "extra_body": {}})
        questions.append({"name": "対価の支払のあっせん者の区分", "type": str, "question": "対価の支払のあっせん者の区分は何ですか？", "extra_body": {}})

        questions.append({"name": "政治資金パーティーの対価に係る収入のうち対価の支払のあっせんによるものの内訳", "type": "csv", "question": "対価の支払をした者の氏名（団体にあっては、その名称）,金額,提供年月日,集めた期間,住所（団体にあっては、主たる事務所の所在地）,職業（団体にあっては、代表者の氏名）,備考をCSV形式で出力してください。情報がない行,計や合計を含めないでください。金額は句読点なしで数字のみで出力してください。年月日は/で分けてください。説明は含めずcsvのみを出力してください。出力は```\n対価の支払をした者の氏名（団体にあっては、その名称）,金額,提供年月日,集めた期間,住所（団体にあっては、主たる事務所の所在地）,職業（団体にあっては、代表者の氏名）,備考で始めてください", "extra_body": {
            "guided_regex": "```\n対価の支払をした者の氏名（団体にあっては、その名称）,金額,提供年月日,集めた期間,住所（団体にあっては、主たる事務所の所在地）,職業（団体にあっては、代表者の氏名）,備考\n([^,]*,[0-9]*,[^,]*,[^,]*,[^,]*,[^,]*,[^,]*\n)*```[\s\S]*"
        }})
        constraints.append({"type": "csv_add", "lhs": "政治資金パーティーの対価に係る収入のうち対価の支払のあっせんによるものの内訳/金額", "rhs": "この頁の小計または合計"})
        questions.append({"name": "この頁の小計または合計", "type": int, "question": "この頁の小計または合計は？句読点なしの数字のみで出力してください。もし空白なら0と出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
    elif index == 13:
        questions.append({"name": "支出の総括表", "type": dict, "question": "Do an OCR to output a python dictionary. 数字は分割せずにまとめてください。数字の項目が空白の場合０と出力してください。小計と合計も含めてください。", "extra_body": {"guided_regex": costs_regex}})

        constraints.append({"type": "add", "lhs": ["支出の総括表/支出の総括表/1 経常経費/人件費", "支出の総括表/支出の総括表/1 経常経費/光熱水費", "支出の総括表/支出の総括表/1 経常経費/備品・消耗品費", "支出の総括表/支出の総括表/1 経常経費/事務所費"], "rhs": ["支出の総括表/支出の総括表/1 経常経費/小計"]})
        constraints.append({"type": "add", "lhs": ["支出の総括表/支出の総括表/2 政治活動費/組織活動費", "支出の総括表/支出の総括表/2 政治活動費/選挙関係費", "支出の総括表/支出の総括表/2 政治活動費/機関紙誌の発行その他の事業費", "支出の総括表/支出の総括表/2 政治活動費/調査研究費", "支出の総括表/支出の総括表/2 政治活動費/寄附・交付金", "支出の総括表/支出の総括表/2 政治活動費/その他の経費"], "rhs": ["支出の総括表/支出の総括表/2 政治活動費/小計"]})
        constraints.append({"type": "add", "lhs": ["支出の総括表/支出の総括表/1 経常経費/小計", "支出の総括表/支出の総括表/2 政治活動費/小計"], "rhs": ["支出の総括表/支出の総括表/2 政治活動費/合計"]})
    elif index == 14:
        # 経常経費（人件費を除く。）の内訳
        questions.append({"name": "経常経費（人件費を除く。）の内訳", "type": "csv", "question": "支出の目的,金額,年月日,支出を受けたものの氏名（団体にあっては、その名称）,支出を受けたものの住所（団体にあっては、主たる事務所の所在地）,備考をCSV形式で出力してください。情報がない行,計や合計を含めないでください。年月日は/で分けてください。金額は句読点なしで数字のみで出力してください。説明は含めずcsvのみを出力してください。出力は```\n支出の目的,金額,年月日,支出を受けたものの氏名（団体にあっては、その名称）,支出を受けたものの住所（団体にあっては、主たる事務所の所在地）,備考で始めてください", "extra_body": {
            "guided_regex": "```\n支出の目的,金額,年月日,支出を受けたものの氏名（団体にあっては、その名称）,支出を受けたものの住所（団体にあっては、主たる事務所の所在地）,備考\n([^,]*,[0-9]*,[^,]*,[^,]*,[^,]*,[^,]*\n)*```[\s\S]*"
        }})
        constraints.append({"type": "csv_add", "lhs": "経常経費（人件費を除く。）の内訳/金額", "rhs": "この頁の小計"})
        questions.append({"name": "この頁の小計", "type": int, "question": "この頁の小計は？句読点なしの数字のみで出力してください。もし空白なら0と出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
        questions.append({"name": "その他の支出の有無", "type": str, "question": "その他の支出という項目はありますか？’あります’か’ありません’のみで出力してください。", "extra_body": {"guided_choice": ["あります", "ありません"]}})
        questions.append({"name": "その他の支出", "type": int, "question": "その他の支出は？句読点なしの数字のみで出力してください。もし空白なら0と出力してください。", "extra_body": {"guided_regex": "[0-9]*"}})
        questions.append({"name": "合計の有無", "type": str, "question": "合計という項目はありますか？この頁の小計ではなく合計という項目です。’あります’か’ありません’のみで出力してください。", "extra_body": {"guided_choice": ["あります", "ありません"]}})
        questions.append({"name": "合計", "type": int, "question": "合計は？句読点なしの数字のみで出力してください。もし空白なら0と出力してください。", "extra_body": {"guided_regex": "[0-9]*"}})
    elif index == 15:
        #　政治活動費の内訳
        # "guided_choice": ["有", "無"]}})
        # questions.append({"name": "政治活動費の内訳", "type": "csv", "question": "支出の目的,金額,年月日,支出を受けたものの氏名（又は名称）,支出を受けたものの住所（又は名称）,備考をCSV形式で出力してください。情報がない行,計や合計を含めないでください。年月日は/で分けてください。金額は句読点なしで数字のみで出力してください。説明は含めずcsvのみを出力してください。出力は```\n支出の目的,金額,年月日,支出で始めてください", "extra_body": {
        #     "guided_regex": "```\n支出の目的,金額,年月日,支出を受けたものの氏名（又は名称）,支出を受けたものの住所（又は名称）,備考\n([^,]*,[0-9]*,[^,]*,[^,]*,[^,]*,[^,]*\n)*```[\s\S]*"
        # }})
        questions.append({"name": "政治活動費の内訳", "type": "csv", "question": "支出の目的,金額,年月日,支出を受けたものの氏名（又は名称）,支出を受けたものの住所（又は名称）,備考をCSV形式で出力してください。情報がない行,計や合計を含めないでください。年月日は/で分けてください。金額は句読点なしで数字のみで出力してください。説明は含めずcsvのみを出力してください。出力は```\n支出の目的,金額,年月日,支出で始めてください", "extra_body": {
            "guided_regex": "```\n支出の目的,金額,年月日,支出を受けたものの氏名（又は名称）,支出を受けたものの住所（又は名称）,備考\n([^,]*,[^,]*,[^,]*,[^,]*,[^,]*,[^,]*\n)*```[\s\S]*"
        }})
        constraints.append({"type": "csv_add", "lhs": "政治活動費の内訳/金額", "rhs": "この頁の小計"})
        questions.append({"name": "この頁の小計", "type": int, "question": "この頁の小計は？句読点なしの数字のみで出力してください。もし空白なら0と出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
        questions.append({"name": "その他の支出の有無", "type": str, "question": "その他の支出という項目はありますか？’あります’か’ありません’のみで出力してください。", "extra_body": {"guided_choice": ["あります", "ありません"]}})
        questions.append({"name": "その他の支出", "type": int, "question": "その他の支出は？句読点なしの数字のみで出力してください。もし空白なら0と出力してください。", "extra_body": {"guided_regex": "[0-9]*"}})
        questions.append({"name": "合計の有無", "type": str, "question": "合計という項目はありますか？この頁の小計ではなく合計という項目です。’あります’か’ありません’のみで出力してください。", "extra_body": {"guided_choice": ["あります", "ありません"]}})
        questions.append({"name": "合計", "type": int, "question": "合計は？句読点なしの数字のみで出力してください。もし空白なら0と出力してください。", "extra_body": {"guided_regex": "[0-9]*"}})
    elif index == 16:
        # 本部又は支部に対して供与した交付金に係る支出の内訳
        questions.append({"name": "本部又は支部に対して供与した交付金に係る支出の内訳", "type": "csv", "question": "支出項目,金額,年月日,交付金の供与を受けた本部又は支部の名称,主たる事務所の所在地,備考をCSV形式で出力してください。情報がない行,計や合計を含めないでください。年月日は/で分けてください。金額は句読点なしで数字のみで出力してください。説明は含めずcsvのみを出力してください。出力は```\n支出項目,金額,年月日,交付金の供与を受けた本部又は支部の名称,主たる事務所の所在地,備考で始めてください", "extra_body": {
            "guided_regex": "```\n支出項目,金額,年月日,交付金の供与を受けた本部又は支部の名称,主たる事務所の所在地,備考\n([^,]*,[0-9]*,[^,]*,[^,]*,[^,]*,[^,]*\n)*```[\s\S]*"
        }})
        constraints.append({"type": "csv_add", "lhs": "本部又は支部に対して供与した交付金に係る支出の内訳/金額", "rhs": "この頁の小計"})
        questions.append({"name": "この頁の小計", "type": int, "question": "この頁の小計は？句読点なしの数字のみで出力してください。もし空白なら0と出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
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
        # 資産等の内訳
        questions.append({"name": "資産等の内訳", "type": "csv", "question": "摘要,金額,年月日,備考をCSV形式で出力してください。情報がない行,計や合計を含めないでください。年月日は/で分けてください。金額は句読点なしで数字のみで出力してください。説明は含めずcsvのみを出力してください。出力は```\n摘要,金額,年月日,備考で始めてください", "extra_body": {
            "guided_regex": "```\n摘要,金額,年月日,備考\n([^,]*,[0-9]*,[^,]*,[^,]*\n)*```[\s\S]*"
        }})
        constraints.append({"type": "csv_add", "lhs": "資産等の内訳/金額", "rhs": "この頁の小計"})

        questions.append({"name": "この頁の小計", "type": int, "question": "この頁の小計は？句読点なしの数字のみで出力してください。もし空白なら0と出力してください。", "extra_body": {"guided_regex": "[0-9]+"}})
    elif index == 19:
        # 不動産の利用の現状
        questions.append({"name": "不動産の利用の現状", "type": "csv", "question": "摘要,用途,使用者と当該資金管理団体及びその代表者との関係、使用者ごとの用途、使用者ごとの使用面積、使用者ごとの使用の対価の価格をCSV形式で出力してください。情報がない行,計や合計を含めないでください。年月日は/で分けてください。金額は句読点なしで数字のみで出力してください。説明は含めずcsvのみを出力してください。出力は```\n摘要,用途,使用者と当該資金管理団体及びその代表者との関係、使用者ごとの用途、使用者ごとの使用面積、使用者ごとの使用の対価の価格で始めてください", "extra_body": {
            "guided_regex": "```\n摘要,用途,使用者と当該資金管理団体及びその代表者との関係、使用者ごとの用途、使用者ごとの使用面積、使用者ごとの使用の対価の価格\n([^,]*,[^,]*,[^,]*,[^,]*,[^,]*,[0-9]*\n)*```[\s\S]*"
        }})
    return questions, constraints
def convert_to_digit(string):
    return ''.join(filter(str.isdigit, string))
def get_content(image_url, temperature=0.5, debug=False, max_num_retries=3):
    # print("Processing", image_url)
    num_retries = 0
    output = {}
    while True:
        try:
            base64_image = encode_image(image_url)
            # index_exists = get_answer2question(base64_image, "上に’（その’で始まり数字が書かれている場所がありますか？’あります’か’ありません’でのみ答えてください。", {
            #     "guided_choice": ["あります", "ありません"]
            # }) == "あります"
            # if not index_exists:
            #   raise Exception("Index did not exist")
            #   return {"failed": True}

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
            if index not in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]:
                print(f"Got index {index} for {image_url}")
                output["index"] = index
                raise Exception(f"Got index {index} for {image_url}")
            if debug:
                print(f"Index found was {index}")
            questions, constraints = get_question_constraint(index)
            output = {
                "index": index,
                "handwritten": handwritten,
                "handwritten_corrected": handwritten_corrected,
                "failed": False
            }
            # if handwritten or handwritten_corrected:
            #   raise Exception("handwritten")
            #   output["failed"] = True
            #   return output
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
                            data = data.replace({np.nan: 'N/A'})
                            if debug:
                              print("panda dataframe is")
                              print(data)
                            if data.isnull().values.any():
                                data = data.replace(pd.NA, 'N/A')
                                if "金額" in data.columns:
                                  data["金額"] = data["金額"].replace('N/A', '0')
                            data = data.to_dict()
                            data_output = {}
                            for key in data:
                                data_output[key] = [data[key][key_output] for key_output in data[key]]
                            data = data_output
                        elif data_type == dict:
                            data = chat_completion
                            data = data.replace("```json\n", "")
                            data = data.replace("\n```", "")
                            data = json.loads(data)

                        else:
                            data = chat_completion

                        output[name] = data
                        if debug:
                            print("name:", name, ",output:", data)
                        break
                    except KeyboardInterrupt as e:
                        raise KeyboardInterrupt(e)
                    except Exception as e:
                        print("Got error", e, f"for {image_url}")
                        num_retries += 1
                        if num_retries >= max_num_retries:
                            output["failed"] = True
                            return output
                        continue
            for constraint in constraints:
                if constraint["type"] == "add":
                    if debug:
                        print("constraint:", constraint)
                    lhs = 0
                    for lhs_elem_name in constraint["lhs"]:
                        lhs_elem_splits = lhs_elem_name.split("/")
                        lhs_elem = output
                        for lhs_elem_split in lhs_elem_splits:
                            lhs_elem = lhs_elem[lhs_elem_split]
                        if isinstance(lhs_elem, str):
                            lhs_elem = convert_to_digit(lhs_elem)
                            if lhs_elem == "":
                              lhs_elem = 0
                        lhs += int(lhs_elem)
                    rhs = 0
                    for rhs_elem_name in constraint["rhs"]:
                        rhs_elem_splits = rhs_elem_name.split("/")
                        rhs_elem = output
                        for rhs_elem_split in rhs_elem_splits:
                            rhs_elem = rhs_elem[rhs_elem_split]
                        if isinstance(rhs_elem, str):
                            rhs_elem = convert_to_digit(rhs_elem)
                            if rhs_elem == "":
                              rhs_elem = 0
                        rhs += int(rhs_elem)
                    if debug:
                        print(lhs, rhs)
                    if lhs != rhs:
                        raise Exception(f"for {constraint} lhs and rhs do not add up for lhs: {lhs} and rhs: {rhs} for {image_url}")
                elif constraint["type"] == "csv_add":
                    output_dict, money_list = constraint["lhs"].split("/")[0], constraint["lhs"].split("/")[1]
                    lhs = 0
                    if debug:
                        print("constraint:", constraint)
                    for money_elem in output[output_dict][money_list]:
                        if isinstance(money_elem, str):
                            money_elem = convert_to_digit(money_elem)
                            if money_elem == "":
                                money_elem = 0
                        lhs += int(money_elem)
                    rhs = output[constraint["rhs"]]
                    if isinstance(rhs, str):
                        rhs = convert_to_digit(rhs)
                    if rhs == "":
                      rhs = 0
                    rhs = int(rhs)
                    if debug:
                        print(lhs, rhs)
                    if lhs != rhs:
                        raise Exception(f"for {constraint} lhs and rhs do not add up for lhs: {lhs} and rhs: {rhs} for {image_url}")
            break
        except KeyboardInterrupt as e:
            raise KeyboardInterrupt(e)
        except Exception as e:
            print("Got error", e, f"for {image_url}")
            num_retries += 1
            if num_retries >= max_num_retries:
                output["failed"] = True
                return output
            continue

    if debug:
        print(f"Output {output}")
    return output

def main():
    image_paths = []
    balance_dir = sys.argv[1]
    temperature = float(sys.argv[2])
    redo_failed = int(sys.argv[3])
    max_num_retries = int(sys.argv[4])
    factor = int(sys.argv[5])
    debug = bool(sys.argv[6])
    file_name = None
    if len(sys.argv) > 7:
      file_name = sys.argv[7]
    if file_name is not None:
      image_paths = [file_name]
    else:
      for date_dir in os.listdir(balance_dir):
          date_path = f"{balance_dir}/{date_dir}"
          for party_dir in os.listdir(date_path):
              party_path = f"{date_path}/{party_dir}"
              if not os.path.isdir(party_path):
                  continue
              if factor != 0:
                  if not party_path.endswith(f"_factor_1_{factor}"):
                      continue
              else:
                if "_factor_1" in party_path:
                      continue
              for image_name in os.listdir(party_path):
                  if image_name.endswith(".jpg"):
                    image_path = f"{party_path}/{image_name}"
                    image_paths.append(image_path)
    for image_path in tqdm(image_paths):
        temperature_str = str(temperature).replace(".", "_")
        json_path = image_path.replace(".jpg", f"_temperature_{temperature_str}.json")
        if os.path.exists(json_path):
            if redo_failed:
                with open(json_path, "r") as f:
                    data = json.load(f)
                if not data["failed"]:
                    continue
            else:
                continue
        output = get_content(image_path, temperature=temperature, debug=bool(debug), max_num_retries=max_num_retries)
        with open(json_path, "w") as f:
            json.dump(output, f, indent=6)

if __name__ == "__main__":
    main()