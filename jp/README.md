Currently, the links I will use are below. I will most likely not get to all the links in this list immediately
 - 政治資金収支報告書及び政党交付金使途等報告書: https://www.soumu.go.jp/senkyo/seiji_s/seijishikin/
 - 国会会議録： https://kokkai.ndl.go.jp/#/
 - 日本法令索引: https://hourei.ndl.go.jp/#/
 - 法律本文: https://laws.e-gov.go.jp/
 - 参議院： https://www.sangiin.go.jp/
 - 衆議院: https://www.shugiin.go.jp/internet/index.nsf/html/index.htm
 - 参議院質問主意書: https://www.sangiin.go.jp/japanese/joho1/kousei/syuisyo/213/syuisyo.htm
 - 衆議院質問主意書: https://www.shugiin.go.jp/internet/itdb_shitsumon.nsf/html/shitsumon/menu_m.htm
 - 財務省（予算、関税、国債の情報）: https://www.mof.go.jp/policy/index.html
 - 帝国議会会議録検索システム(this may be optional): https://teikokugikai-i.ndl.go.jp/#/
 - 文部科学省: https://www.mext.go.jp/b_menu/b004.htm
 - 外務省: https://www.mofa.go.jp/mofaj/annai/index.html
 - 経済産業省: https://www.meti.go.jp/
 - 裁判所: https://www.courts.go.jp/app/hanrei_jp/search1
 - 東京都: https://www.metro.tokyo.lg.jp/tosei/jore/jore/index.html
I think I'll add all prefectures/cities for their individual laws+who proposed them

Slight issues:
1. Currently there seems to be a law against downloading 政党交付金使途等報告書 so you are only allowed to view the contents through browsers. I did ask the government whether say taking a photo or writing down what's in there is allowed which I doubt but for now, 政党交付金使途等報告書 will not be included.
2. There may definitely be a lot of copyright restrictions here which will only allow me to show the processed result and not necessarily all the data scraped

1. Scrape all the publicly available data. We want to gather
 - 政治資金収支報告書及び政党交付金使途等報告書: 政治資金収支報告書 is done. scraping 政党交付金使途等報告書 was illegal. ocr is yet to be done
 - 国会会議録：scraping script creation successful
 - 日本法令索引: Currently scraping. For the contents of the law I didn't touch it yet
2. Cleaning data/Create database. I plan to use mysql.
 The database design I'm thinking is
 - Politician table. Foreign key will be party, law
 - Party table. Foreign key will be funding, president
 - Law. File path to law text, politicians who made that law(with first author). Link to meeting discussion
 - Meeting. Meeting name, date
 - Speech. Speech in meeting has foreign key of previous statement+speaker who is politician
 - Funds. For this I'm not decided yet but I think it'll be connected to a party district table/individual politicians if I can find them
 



