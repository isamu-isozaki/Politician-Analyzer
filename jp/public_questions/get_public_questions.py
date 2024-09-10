# the data here can only be used/downloaded for private matters or for education in schools so this may not be available for the public
from bs4 import BeautifulSoup
import requests
import time
import os
base_dir = "data/jp/qna"

def clean_name(text: str):
    return text.replace("\n", "").replace(" ", "").replace("\u3000", "").replace('"', "").replace("\r", "")

def get_sangiin_qna():
    # The https://www.sangiin.go.jp/japanese/joho1/kousei/syuisyo/001/syuisyo.htm
    i = 1
    delay_between_requests = 2
    house_url = base_dir+"/sangiin"
    os.makedirs(house_url, exist_ok=True)
    while True:
        print(f"Getting {i}th Sangiin qna")
        current_dir = f"{house_url}/{i}"
        os.makedirs(current_dir, exist_ok=True)
        question_dir = current_dir+"/question"
        os.makedirs(question_dir, exist_ok=True)
        answer_dir = current_dir+"/answer"
        os.makedirs(answer_dir, exist_ok=True)


        base_url = "https://www.sangiin.go.jp/japanese/joho1/kousei/syuisyo/{:03}".format(i)
        url = f"{base_url}/syuisyo.htm"
        page = requests.get(url)
        if page.status_code != 200:
            break
        soup = BeautifulSoup(page.content, 'html.parser')
        question_names_and_politicians = soup.find_all("td", {"class": "ta_l"})
        question_names = []
        politician_names = []
        for j in range(len(question_names_and_politicians)):
            if j % 2 == 0:
                question_names.append(clean_name(question_names_and_politicians[j].text))
            else:
                politician_names.append(clean_name(question_names_and_politicians[j].text))
        questions_and_answer_htmls = soup.find_all("a", {"class": "Graylink"})
        question_urls = []
        answer_urls = []
        for j in range(len(questions_and_answer_htmls)):
            element = questions_and_answer_htmls[j]
            if j % 5 == 1:
                question_url = base_url + "/" + element["href"]
                question_urls.append(question_url)
            elif j % 5 == 2:
                answer_url = base_url + "/" + element["href"]
                if answer_url.endswith(".pdf"):
                    continue
                answer_urls.append(answer_url)
        min_size = min(len(question_urls), len(answer_urls))
        question_urls = question_urls[:min_size]
        answer_urls = answer_urls[:min_size]

        for j, question_url in enumerate(question_urls):
            question_name = question_names[j]
            politician_name = politician_names[j]
            filename = f"{question_dir}/{j}_{question_name}_{politician_name}.txt"
            if os.path.exists(filename):
                continue
            time.sleep(delay_between_requests)
            question_page = requests.get(question_url)
            question_soup = BeautifulSoup(question_page.content, "html.parser")
            question_text = question_soup.find("table").text
            with open(filename, "w", encoding='utf-8') as f:
                f.write(question_text)
        for j, answer_url in enumerate(answer_urls):
            question_name = question_names[j]
            politician_name = politician_names[j]
            filename = f"{answer_dir}/{j}_{question_name}_{politician_name}.txt"
            if os.path.exists(filename):
                continue
            time.sleep(delay_between_requests)
            answer_page = requests.get(answer_url)
            answer_soup = BeautifulSoup(answer_page.content, "html.parser")
            answer_text = answer_soup.find("table").text
            with open(filename, "w", encoding='utf-8') as f:
                f.write(answer_text)
        i += 1
def get_shuugiin_qna():
    # https://www.shugiin.go.jp/internet/itdb_shitsumona.nsf/html/shitsumon/kaiji001_l.htm
    i = 1
    delay_between_requests = 2
    house_url = base_dir+"/shuugiin"
    base_url = "https://www.shugiin.go.jp/internet/itdb_shitsumona.nsf/html/shitsumon"
    os.makedirs(house_url, exist_ok=True)
    while True:
        print(f"Getting {i}th Shuugiin qna")
        current_dir = f"{house_url}/{i}"
        os.makedirs(current_dir, exist_ok=True)
        question_dir = current_dir+"/question"
        os.makedirs(question_dir, exist_ok=True)
        answer_dir = current_dir+"/answer"
        os.makedirs(answer_dir, exist_ok=True)


        url = base_url + "/kaiji{:03}_l.htm".format(i)
        page = requests.get(url)
        if page.status_code != 200:
            break
        soup = BeautifulSoup(page.content, 'html.parser')
        num_all_qna = len(soup.find_all("tr"))-1
        question_name_elems = soup.find_all("td", {"headers": "SHITSUMON.KENMEI"})
        politician_name_elems = soup.find_all("td", {"headers": "SHITSUMON.TEISHUTSUSHA"})

        question_names = []
        politician_names = []
        for j, (question_name_elem, politician_name_elem) in enumerate(zip(question_name_elems, politician_name_elems)):
            if j == 0:
                continue
            question_names.append(clean_name(question_name_elem.text))
            politician_names.append(clean_name(politician_name_elem.text))


        question_urls = []
        answer_urls = []
        for j in range(num_all_qna):
            question_url = base_url + "/a{:03}{:03}.htm".format(i, j+1)
            answer_url = base_url + "/b{:03}{:03}.htm".format(i, j+1)
            question_urls.append(question_url)
            answer_urls.append(answer_url)

        for j, question_url in enumerate(question_urls):
            time.sleep(delay_between_requests)
            question_page = requests.get(question_url)
            question_soup = BeautifulSoup(question_page.content, "html.parser")
            question_elem = question_soup.find("div", {"id": "mainlayout"})
            question_elem.find("div", {"id": "breadcrumb"}).decompose()
            question_elem.find("h1").decompose()
            link_elems = question_elem.find_all("div", {"class": "gh21divr"})
            for link_elem in link_elems:
                link_elem.decompose()

            question_text = question_elem.text
            question_name = question_names[j]
            politician_name = politician_names[j]
            with open(f"{question_dir}/{j}_{question_name}_{politician_name}.txt", "w", encoding='utf-8') as f:
                f.write(question_text)
        for j, answer_url in enumerate(answer_urls):
            time.sleep(delay_between_requests)
            answer_page = requests.get(answer_url)
            answer_soup = BeautifulSoup(answer_page.content, "html.parser")
            answer_elem = answer_soup.find("div", {"id": "mainlayout"})
            answer_elem.find("div", {"id": "breadcrumb"}).decompose()
            answer_elem.find("h1").decompose()
            link_elems = answer_elem.find_all("div", {"class": "gh22divr"})
            for link_elem in link_elems:
                link_elem.decompose()

            answer_text = answer_elem.text
            question_name = question_names[j]
            politician_name = politician_names[j]
            with open(f"{answer_dir}/{j}_{question_name}_{politician_name}.txt", "w", encoding='utf-8') as f:
                f.write(answer_text)
        i += 1

if __name__ == "__main__":
    os.makedirs(base_dir, exist_ok=True)
    get_sangiin_qna()
    get_shuugiin_qna()
