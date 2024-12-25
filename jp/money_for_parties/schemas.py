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