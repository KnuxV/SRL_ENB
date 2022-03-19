from boilerpy3 import extractors
from bs4 import BeautifulSoup as bs
import os


def html_to_text_boiler(file):
    """
    using boilerpy3 to keep relevant text
    :param file: a html file
    :return: a text file
    """
    extractor = extractors.ArticleExtractor()
    text_content = extractor.get_content_from_file(html_root + html_file)
    return text_content


def html_to_text_p_tags(file):
    """
    only keeping <p>text</p>
    :param file:  a html file
    :return: a text file
    """
    soup = bs(open(file), "html.parser")
    p_tags = soup.find_all('p')
    res_file = ""

    for p_tag in p_tags:
        if not p_tag.a:
            res_file += p_tag.text + "\n"

    return res_file


# creating the cleaning text

if __name__ == "__main__":
    # All the html are stored in data/raw/html, we extract the text with boilerpy3 and store it in data/raw/txt
    html_root = "data/raw/html/"
    txt_root_boiler = "data/raw/txt_boiler/"
    txt_root_p = "data/raw/txt/"

    all_html_files = os.listdir(html_root)
    for html_file in all_html_files:
        # Version 1 boiler:
        text_content = html_to_text_boiler(html_root + html_file)
        txt_name = html_file.split('.')[0] + '.txt'
        with open(txt_root_boiler + txt_name, 'w', encoding='utf-8') as f:
            f.write(text_content)

        # Version 2 p_tags:
        text_content = html_to_text_p_tags(html_root + html_file)
        txt_name = html_file.split('.')[0] + '.txt'
        with open(txt_root_p + txt_name, 'w', encoding='utf-8') as f:
            f.write(text_content)
