import requests
"""
Download all the .html files
"""
with open("data/raw/lst_of_url.txt", "r", encoding="utf-8") as txt_f:
    for link in txt_f:
        url = link.rstrip()
        r = requests.get(url)
        suffix = url.split("/")[-1]
        with open("data/raw/html/" + suffix, "w", encoding="utf-8") as html_f:
            html_f.write(str(r.content, 'utf-8'))
