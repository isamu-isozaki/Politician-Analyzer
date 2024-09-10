# Copyright
# 1．当ホームページのコンテンツの利用について
# 　当ホームページで公開している情報（以下「コンテンツ」といいます。）は、どなたでも以下の1）～7）に従って、複製、公衆送信、翻訳・変形等の翻案等、自由に利用できます。商用利用も可能です。また、数値データ、簡単な表・グラフ等は著作権の対象ではありませんので、これらについては本利用ルールの適用はなく、自由に利用できます。
# 　コンテンツ利用に当たっては、本利用ルールに同意したものとみなします。

# 1）　出典の記載について
# ア　コンテンツを利用する際は出典を記載してください。出典の記載方法は以下のとおりです。
# （出典記載例）
# 出典：総務省ホームページ （当該ページのURL）
# 出典：「○○動向調査」（総務省） （当該ページのURL） （○年○月○日に利用）　など
# イ　コンテンツを編集・加工等して利用する場合は、上記出典とは別に、編集・加工等を行ったことを記載してください。なお、編集・加工した情報を、あたかも国（又は府省等）が作成したかのような態様で公表・利用してはいけません。
# （コンテンツを編集・加工等して利用する場合の記載例）
# 「○○動向調査」（総務省） （当該ページのURL）を加工して作成
# 「○○動向調査」（総務省） （当該ページのURL）をもとに○○株式会社作成　など
# 2）　第三者の権利を侵害しないようにしてください
# ア　コンテンツの中には、第三者（国以外の者をいいます。以下同じ。）が著作権その他の権利を有している場合があります。第三者が著作権を有しているコンテンツや、第三者が著作権以外の権利（例：写真における肖像権、パブリシティ権等）を有しているコンテンツについては、特に権利処理済であることが明示されているものを除き、利用者の責任で、当該第三者から利用の許諾を得てください。
# イ　コンテンツのうち第三者が権利を有しているものについては、出典の表記等によって第三者が権利を有していることを直接的又は間接的に表示・示唆しているものもありますが、明確に第三者が権利を有している部分の特定・明示等を行っていないものもあります。利用する場合は利用者の責任において確認してください。
# ウ　外部データベース等とのAPI（Application Programming Interface）連携等により取得しているコンテンツについては、その提供元の利用条件に従ってください。
# エ　第三者が著作権等を有しているコンテンツであっても、著作権法上認められている引用など、著作権者等の許諾なしに利用できる場合があります。
# 3）　個別法令による利用の制約があるコンテンツについて
# ア　一部のコンテンツには、個別法令により利用に制約がある場合があります。特に、以下に記載する法令についてはご注意ください。詳しくはリンク先ページをご参照ください。
# 政党助成法に基づく政党交付金使途等報告書の利用に当たっての制約について
# 4）　本利用ルールが適用されないコンテンツについて
# 以下のコンテンツについては、本利用ルールの適用外です。
# ア　組織や特定の事業を表すシンボルマーク、ロゴ、キャラクターデザイン
# イ　具体的かつ合理的な根拠の説明とともに、別の利用ルールの適用を明示しているコンテンツ
# （別の利用ルールの適用を明示しているコンテンツは、本利用ルールの別紙に列挙しています。）
# 5）　準拠法と合意管轄について
# ア　本利用ルールは、日本法に基づいて解釈されます。
# イ　本利用ルールによるコンテンツの利用及び本利用ルールに関する紛争については、当該紛争に係るコンテンツ又は利用ルールを公開している組織の所在地を管轄する地方裁判所を、第一審の専属的な合意管轄裁判所とします。
# 6）　免責について
# ア　国は、利用者がコンテンツを用いて行う一切の行為（コンテンツを編集・加工等した情報を利用することを含む。）について何ら責任を負うものではありません。
# イ　コンテンツは、予告なく変更、移転、削除等が行われることがあります。
# 7）　その他
# ア　本利用ルールは、著作権法上認められている引用などの利用について、制限するものではありません。
# イ　本利用ルールは、平成28年1月25日に定めたものです。本利用ルールは、政府標準利用規約（第2.0版）に準拠しています。本利用ルールは、今後変更される可能性があります。既に政府標準利用規約の以前の版にしたがってコンテンツを利用している場合は、引き続きその条件が適用されます。
# ウ　本利用ルールは、クリエイティブ・コモンズ・ライセンスの表示4.0 国際（https://creativecommons.org/licenses/by/4.0/legalcode.ja別ウィンドウで開きます に規定される著作権利用許諾条件。以下「CC BY」といいます。）と互換性があり、本利用ルールが適用されるコンテンツはCC BYに従うことでも利用することができます。
# It seems like just compiling statistics from these documents with attribution may be fine as I've seen articles like these
import requests
from bs4 import BeautifulSoup
import os
from tqdm.auto import tqdm
import time

def clean_name(text: str):
    return text.replace("\n", "").replace(" ", "").replace("\u3000", "").replace('"', "")
def get_link_from_onclick(text: str):
    return text.split("window.open('")[1].split("',")[0]
def get_balance_pdfs(balance_urls: list[tuple[str, str]]):
    base_url = "https://www.soumu.go.jp/senkyo/seiji_s/seijishikin"
    for balance_url in tqdm(balance_urls):
        name, base_link = balance_url[0], balance_url[1]
        os.makedirs("data/jp/money_for_parties/balance/"+name, exist_ok=True)
        time.sleep(5)
        response = requests.get(base_link)
        soup = BeautifulSoup(response.content, "html.parser").find_all("a", href=True)
        balance_dir = "data/jp/money_for_parties/balance/"+name
        for a_elem in tqdm(soup):
            pdf_name = balance_dir + "/" + clean_name(a_elem.text)+".pdf"
            if os.path.exists(pdf_name):
                continue
            if not a_elem["href"].endswith("pdf"):
                continue
            pdf_link = base_url+a_elem["href"].split("..")[1]
            time.sleep(5)
            pdf_response = requests.get(pdf_link)
            with open(pdf_name, 'wb') as f:
                f.write(pdf_response.content)

def get_use_of_grants(use_of_grants_urls: list[tuple[str, str]]):
    for use_of_grants_url in tqdm(use_of_grants_urls):
        name, base_link = use_of_grants_url[0], use_of_grants_url[1]
        base_path = "data/jp/money_for_parties/use_of_grants/"+name
        os.makedirs(base_path, exist_ok=True)

        response = requests.get(base_link)
        soup = BeautifulSoup(response.content, "html.parser").find("table",{"id":"list"}).find_all("tr")[1].find_all("td")
        # the 4 columns are 政党本部	政党支部	総括文書 （支部分）   総括文書（本部及び支部分）

        home_base = soup[0].find_all("a", href=True)
        bases = soup[1].find_all("a", href=True)
        combined_bases = soup[2].find_all("a", href=True)
        combined_home_and_bases = soup[3].find_all("a", href=True)
        for a_elem in tqdm(combined_home_and_bases):
            party_name = clean_name(a_elem.text)
            party_path = base_path + "/" + party_name
            file_name = party_path+"/総括文書（本部及び支部分).pdf"
            if os.path.exists(file_name):
                continue
            os.makedirs(party_path, exist_ok=True)
            party_link = "https://www.soumu.go.jp"+get_link_from_onclick(a_elem["onclick"])
            time.sleep(5)
            pdf_response = requests.get(party_link)

            with open(file_name, 'wb') as f:
                f.write(pdf_response.content)
        for table_column in [home_base, combined_bases]:
            for a_elem in tqdm(table_column):
                party_name = clean_name(a_elem.text)
                party_path = base_path + "/" + party_name
                os.makedirs(party_path, exist_ok=True)
                party_link = base_link + a_elem["href"]
                time.sleep(5)
                party_response = requests.get(party_link)
                party_soup = BeautifulSoup(party_response.content, "html.parser").find("table",{"id":"list"}).find_all("a", href=True)
                for party_doc_a_elem in party_soup:
                    party_doc_link = "https://www.soumu.go.jp"+get_link_from_onclick(party_doc_a_elem["onclick"])
                    party_doc_name = clean_name(party_doc_a_elem.text)+".pdf"
                    file_name = party_path+"/"+party_doc_name
                    if os.path.exists(file_name):
                        continue
                    pdf_response = requests.get(party_doc_link)
                    with open(file_name, 'wb') as f:
                        f.write(pdf_response.content)


        for a_elem in tqdm(bases):
            party_name = clean_name(a_elem.text)
            party_path = base_path + "/" + party_name
            os.makedirs(party_path, exist_ok=True)
            party_link = base_link + a_elem["href"]
            time.sleep(5)
            party_response = requests.get(party_link)
            party_soup = BeautifulSoup(party_response.content, "html.parser").find("div",{"id":"list"}).find_all("a", href=True)
            for party_base_a_elem in party_soup:
                # the site seems to use onClick attribute to open pdf in new window instead of href
                party_base_link = "https://www.soumu.go.jp"+get_link_from_onclick(party_base_a_elem["onclick"])
                party_base_name = clean_name(party_base_a_elem.text)+".pdf"
                file_name = party_path+"/"+party_base_name
                if os.path.exists(file_name):
                    continue
                time.sleep(5)
                pdf_response = requests.get(party_base_link)
                with open(file_name, 'wb') as f:
                    f.write(pdf_response.content)


def get_balances_and_use_of_grants():
    base_url = "https://www.soumu.go.jp"
    response = requests.get("https://www.soumu.go.jp/senkyo/seiji_s/seijishikin/")
    soup = BeautifulSoup(response.content, "html.parser")
    # print(soup.prettify)
    balance_and_use_of_grants_parts = soup.prettify().split("報道資料・報告書の要旨はこちら")
    balance_parts, use_of_grants_parts = balance_and_use_of_grants_parts[1], balance_and_use_of_grants_parts[2]
    balance_parts, use_of_grants_parts = BeautifulSoup(balance_parts, "html.parser"), BeautifulSoup(use_of_grants_parts, "html.parser")
    balance_urls = []
    balance_url_htmls = balance_parts.find_all("a", href=True)
    for a_elem in balance_url_htmls:
        if "公表" not in a_elem.text:
            continue
        name = clean_name(a_elem.text)
        link = base_url+a_elem["href"]
        balance_urls.append((name, link))
    use_of_grants_urls = []
    use_of_grants_htmls = use_of_grants_parts.find_all("a", href=True)

    for a_elem in use_of_grants_htmls:
        if "公表" not in a_elem.text:
            continue
        name = clean_name(a_elem.text)
        link = base_url+a_elem["href"]
        use_of_grants_urls.append((name, link))
    get_balance_pdfs(balance_urls)
    get_use_of_grants(use_of_grants_urls)

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/jp/money_for_parties", exist_ok=True)
    os.makedirs("data/jp/money_for_parties/balance", exist_ok=True)
    os.makedirs("data/jp/money_for_parties/use_of_grants", exist_ok=True)

    get_balances_and_use_of_grants()