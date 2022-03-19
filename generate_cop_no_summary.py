"""
Generate all the text files regarding cop events. one text file for each day excluding the summary
"""
from lxml import etree as et
from shutil import copyfile

if __name__ == "__main__":
    # Do stuff
    tree = et.parse("data/info/enb.xml")
    root = tree.getroot()
    # We parse our enb.xml tree and only keep COP events
    for event in root:
        if event.attrib["type"] == "COP":
            children = list(event)
            # Children[0] = title, Children[1] = date, Children[2] = place, Children[3] = urls
            for url in children[3]:
                # We want to discard Summary of the cop events too
                if url.attrib["date"] != "Summary":
                    link = url.text
                    # gets the name of the file (ex : 1218000e)
                    root = link.split(".")[2].split("/")[-1]

                    # Now that we have the root, we can copy the right file from raw/txt to raw/cop_no_summary
                    copyfile("data/raw/txt/"+str(root)+".txt", "data/raw/cop_no_summary/"+str(root)+".txt")


