import re
import requests
from bs4 import BeautifulSoup as bS
from lxml import etree as eT


def create_xlm_tree(root, title, full_title, type_of_event,  year, date, place, urls):
    """
    <tr><th colspan="4"><a name="1995-INC-11"></a></th></tr>  +  <tr><th colspan="4"><h3>Eleventh Session of The INC for the Framework Convention on Climate Change (UNFCCC)</h3>INC 11 | 6-17 February 1995 | New York, USA</th></tr>
    :param type_of_event:
    :param root: the root of the html tree
    :param full_title: also present in the table header, self explenatory as of its nature
    :param title: title of the event = <a name = xxx>
    :param year: in the <a name = xxx>, first four digits are the year of the event
    :param date: in the text of the next header, separated by |
    :param place: in the text of the header, seprated by |
    :param urls: a list of urls : next elements in between headers
    :return: a xml file with all the info, year and country are attributes
    """
    xml_event = eT.SubElement(root, "event")
    xml_event.set("title", title)
    xml_event.set("type", type_of_event)
    xml_title = eT.SubElement(xml_event, "title")
    xml_title.text = full_title

    xml_date = eT.SubElement(xml_event, "date")
    # title looks like THIS "1995-INC-11" so we keep the first four char
    xml_date.set("year", year)
    xml_date.text = date

    country = place.split(", ")[-1]
    xml_place = eT.SubElement(xml_event, "place")
    xml_place.text = place
    xml_place.set("country", country)

    xml_urls = eT.SubElement(xml_event, "urls")

    for url_link in urls:
        xml_url = eT.SubElement(xml_urls, "url")
        xml_url.text = url_link[2]
        xml_url.set("issue", url_link[0])
        xml_url.set("date", url_link[1])
        xml_url.set("num", url_link[2].split("/")[-1].split(".")[0])


url = "https://enb.iisd.org/enb/vol12/"

# Main website
r = requests.get(url)
# root
root_link = "https://enb.iisd.org/"
soup = bS(r.content, "html.parser")


def divide_into_event(soup_elem, root, cop_no_summary=True):
    """

    :param cop_no_summary: We do two trees, the full tree with all events, and a tree for only cop events
    :param root: main_tag of the tree
    :param soup_elem: the bS element
    :return: the name of the event + the date of the event and the html urls of all the issues of this event
    """
    table = soup_elem.find_all("tr")

    headers = [tr for tr in table if tr.find('th') and not re.match(r"^[0-9]+$", tr.text)]

    # each event is a double line of th
    # 1st line <tr><th colspan="4"><a name="1995-COP-1"></a></th></tr>
    # 2nd line  <th colspan="4"><h3>First Conference of the Parties to the Framework Convention on Climate Change</h3>COP 1 | 28 March - 7 April 1995 | Berlin, Germany</th>
    for i in range(0, len(headers), 2):
        first_header = headers[i]
        second_header = headers[i + 1]

        title = first_header.find("a").get('name')
        full_title = second_header.h3.text
        year = title[:4]
        main_text_in_th = second_header.th.find(text=True, recursive=False)
        # main text looks like that COP 1 | 28 March - 7 April 1995 | Berlin, Germany
        # we make a regex to identify each part
        reg = re.compile(r"(.+)\s\|\s(.+)\s\|\s(.+)")
        match = re.match(reg, main_text_in_th)
        # I don't know if we care about that
        print(main_text_in_th)
        if match:
            event = match.group(1)
            date = match.group(2)
            place = match.group(3)
        else:
            event, date, place = "NULL", "NULL", "NULL"

        # type_of_event is the event without any numbers
        type_of_event = re.match(r"[a-zA-Z]+", event).group(0)

        # ONLY COP NO SUMMARY, it's type != COP we skip and go to the next header
        if cop_no_summary and type_of_event != "COP":
            continue
        # next lines after the two headers contains urls, we use next sibling
        lst_of_urls = []
        tr = second_header

        not_a_header = True
        while not_a_header:
            tr = tr.next_sibling
            if tr == "\n":
                continue
            if tr is None:
                # end of file
                break
            if tr.find("th") is not None:
                # We found the next header
                not_a_header = False
                break
            else:
                link = tr.find('a', attrs={'class': 'html'})
                full_url = root_link + link["href"]
                issue_number = tr.td.text[7:]
                date_of_day = tr.td.next_sibling.text
                # ONLY COP NO SUMMARY, if date =  Summary, we ship that url
                if cop_no_summary and date_of_day == "Summary":
                    continue
                lst_of_urls.append([issue_number, date_of_day, full_url])

        create_xlm_tree(root, title, full_title, type_of_event, year, date, place, lst_of_urls)


if __name__ == "__main__":
    # FULL TREE //initialise xml tree
    enb = eT.Element("enb")
    # launch function
    divide_into_event(soup, enb, cop_no_summary=False)

    # create tree
    tree = eT.ElementTree(enb)
    tree.write("data/info/enb.xml", encoding="utf-8", xml_declaration=True)

    # ONLY COP NO SUMMARY //initialise xml tree
    enb = eT.Element("enb")
    # launch function
    divide_into_event(soup, enb, cop_no_summary=True)

    # create tree
    tree = eT.ElementTree(enb)
    tree.write("data/info/enb_cop_no_summary.xml", encoding="utf-8", xml_declaration=True)
