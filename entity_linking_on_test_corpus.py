import requests
import spacy  # version 3.0.6'

API_URL = "https://rel.cs.ru.nl/api"


def entity_linking_REL(text):
    el_result = requests.post(API_URL, json={
        "text": text,
        "spans": []
    }).json()
    # res = [str(entity[2]) + "=" + str(entity[3]) for entity in el_result]

    # ed_result = requests.post(API_URL, json={
    #     "text": text_doc,
    #     "spans": [(41, 16)]
    # }).json()
    return [res[2:4] for res in el_result]


# initialize language model
nlp = spacy.load("en_core_web_trf")

# add pipeline (declared through entry_points in setup.py)
nlp.add_pipe("entityLinker", last=True)


def entity_linker_spacy(txt):
    res = []
    doc = nlp(txt)
    all_linked_entities = doc._.linkedEntities
    for entity in all_linked_entities:
        res.append(
            [entity.get_span(), entity.get_label(), entity.get_description()])
    return res


with open("../data/info/eval/enb_test_l6.txt", "r",
          encoding="utf-8") as f, open("entity_linking.txt", 'w',
                                       encoding='utf-8') as w:
    for ind, sent in enumerate(f):
        sent = sent.rstrip()
        w.writelines(str(ind) + ": " + sent + '\n')
        w.writelines('\n')
        w.writelines('REL: span, entity\n')
        res_REL = entity_linking_REL(sent)
        for entity in res_REL:
            w.writelines(str(entity[0] + " = " + entity[1]) + '\n')
        w.writelines('\n')
        w.writelines('Spacy Entity Linker: span, entity, description\n')
        res_spacy = entity_linker_spacy(sent)
        for entity in res_spacy:
            w.writelines(str(entity[0]) + ' = ' + str(entity[1]) + '\t' + str(
                entity[2]) + '\n')
        w.writelines('\n')
        w.writelines('\n')
