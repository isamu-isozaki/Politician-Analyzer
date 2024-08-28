# Politician-Analyzer
The goal of this project is to use data publicly available to analyze politicians in an unbiased way.
The motivation for this was I don't think at least I am currently voting intelligently. I do not know most candidates other than their party except for maybe presidents. However, even for presidents, I do not vote for one or another based so much so on policy but rather personality which I do believe is a common and huge issue. One solution that I found was by Assistant Professor [Yusuke Narita](https://www.yusuke-narita.com/) on his book [here](https://www.amazon.co.jp/22%E4%B8%96%E7%B4%80%E3%81%AE%E6%B0%91%E4%B8%BB%E4%B8%BB%E7%BE%A9-%E9%81%B8%E6%8C%99%E3%81%AF%E3%82%A2%E3%83%AB%E3%82%B4%E3%83%AA%E3%82%BA%E3%83%A0%E3%81%AB%E3%81%AA%E3%82%8A%E3%80%81%E6%94%BF%E6%B2%BB%E5%AE%B6%E3%81%AF%E3%83%8D%E3%82%B3%E3%81%AB%E3%81%AA%E3%82%8B-SB%E6%96%B0%E6%9B%B8-%E6%88%90%E7%94%B0%E6%82%A0%E8%BC%94/dp/4815615608) where he proposed voting for policies instead of candidates. I do believe we are not quite there yet but I think there should be more transparency on what kind of policies each candidate will have if they get back into office, what kind of incentives the candidate may have based on money coming in(through coorporations, foreign nations, religion etc), and overall what the candidate promises for the voters and whether the candidate accomplished this in the past.

In the beginning this will be just a large scraped database of all public data but I do want to expand this to match a certain voter with a certain party etc based on their political beliefs and also highlight the pros and cons of each candidate possibly using LLMs. This project is still in it's infancy but the main goal is to give something a bit like mass media but more comprehensible/without opion/a political spin on facts.

Supported languages/regions will currently only be Japan and United States but may expand with help from contributors

The stages of this is
1. Scrape all the publicly available data. We want to gather
 -  The laws passed by them and under them
 -  Treaties formed with outside nations
 -  Money recieved including salary/lobbying
 -  Criminal history/What was he sued for and did he win the case etc
 -  Budget proposals
 -  Who did he assign to which posiiton
 -  All records of talking in congress etc
I may add other items here but this can differ based on country/position

For this step, I mainly want to only use government issued data. One issue is for some facts they might not be available there ex amount of money
recieved from x company.
2. Cleaning data/Create database. I plan to use mysql.
3. Create webui/data searching functionality. For example, searching politicians by name, elastic search to see what their opinion is on certain political issues
4. Experiment with adding AI to make this more interpertable/Examine if bias is introduced