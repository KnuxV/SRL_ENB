import os
import pandas as pd
import re
import spacy
from lxml import etree as et
import copy
from keybert import KeyBERT

from typing import List

import allennlp_srl_coref
from triple_class import Actor, Predicate, Message, Triple, Sentence, Text
from util import extract_keywords_from_db

spacy.prefer_gpu()

##############
# Global stuff
##############
# pipeline to split in sentences
nlp = spacy.load("en_core_web_trf")


# nlp.add_pipe("entityLinker", last=True)


##############
def arg_in_actors(actor_sentence: str, pronoun=True, actor_xml_path="data/info/actors.xml") -> List[str]:
    """
    Returns a list with all valid actors of the sentence that can be found in actors.xml
    Parameters
    ----------
    pronoun : bool
        False, if we don't want to query pronouns in the xml file, True if we want to return pronons as actors
    actor_sentence : str
        The ARG0 argument of AllenNLP
    actor_xml_path : str
        Path to actors.xml

    Returns
    -------
    list
        A list with all the actors present in ARG0
    """
    actor_sentence = actor_sentence.lower()
    lst_actors = []
    # Parsing the xml actors.xml
    tree = et.parse(actor_xml_path)
    root = tree.getroot()
    # 4 type of actors : country observer, generic others
    for type_actor in root:
        for actor in type_actor:
            # Excluding generic actors (committee /delegate /party / chair /manager )
            if actor.tag != "generic":
                # if pronoun == False, we skip the pronouns from the xml file
                if pronoun or (type_actor.tag != "pronoun"):
                    # Regex to match the noun phrase to the xml.
                    reg = r'\b' + re.escape(actor.text) + r'\b'
                    if re.search(reg.lower(), actor_sentence.lower(), re.IGNORECASE):
                        # Special case for Guinea / NOT PRETTY BUT MOSTLY IRRELEVANT
                        if actor.text == "Guinea":
                            if re.search(r"papua|equatorial|bissau", actor_sentence.lower()) and (
                                    actor_sentence.lower().count("guinea") == 1):
                                pass
                            else:
                                lst_actors.append(actor.attrib["dbpedia"])
                        else:
                            # If there's a dbpedia name, we use it
                            if "dbpedia" in actor.attrib:
                                lst_actors.append(actor.attrib["dbpedia"])
                            else:
                                lst_actors.append(actor.text)
    return list(set(lst_actors))


def get_dbpedia(name: str, actor_xml_path="data/info/actors.xml"):
    """
    Look for a mention of the actor in the actors.xml file. If found returns that name
    Examples : if name="The US" returns United_States
    Parameters
    ----------
    name : str
        The name of the actor
    actor_xml_path : str
        The path to actors.xml

    Returns
    -------
    str
        the dbpedia name of the actor as a string
    """
    tree = et.parse(actor_xml_path)
    root = tree.getroot()
    for type_actor in root:
        for actor in type_actor:
            if actor.text.lower() == name.lower() and "dbpedia" in actor.attrib:
                return actor.attrib["dbpedia"]
    return ""


def get_actor_type_from_xml(name: str, actor_xml_path="data/info/actors.xml"):
    tree = et.parse(actor_xml_path)
    root = tree.getroot()
    for type_actor in root:
        for actor in type_actor:
            reg = r'\b' + re.escape(actor.text) + r'\b'
            if re.search(reg.casefold(), name.casefold(), re.IGNORECASE):
                return actor.tag
    return ""


def pred_is_in_lst_predicate(lemma: str, preds_verbal_path="data/info/preds_verbal.xml"):
    """

    Parameters
    ----------
    lemma : str
        The lemma of a predicate
    preds_verbal_path : str
        The path of preds_verbal.xml

    Returns
    -------
    bool
        True if the predicate is in the list of predicates of the ENB Corpus, False if not
    """
    tree = et.parse(preds_verbal_path)
    root = tree.getroot()
    for pred in root:
        if pred.text == lemma:
            return True
    return False


def type_of_predicate(lemma: str, preds_verbal_path="data/info/preds_verbal.xml"):
    """

    Parameters
    ----------
    lemma : str
        The lemma we want to know the type of
    preds_verbal_path : str
        The path of the preds_verbal.xml

    Returns
    -------
    str
        The type of predicate, that is the attribute rtype, as found in the preds_verbal.xml
    """
    tree = et.parse(preds_verbal_path)
    root = tree.getroot()
    for pred in root:
        if "rtype" in pred.attrib and pred.text == lemma:
            return pred.attrib["rtype"]
    return "none"


def keywords_in_message(message: str) -> list:
    """
    Takes a sentence as input and returns a list of all the keywords presents in that sentence using EntityLinker,
    a spaCy pipeline
    Args:
        message (str): A string of text, most of the time it will be the message part of the Triple

    Returns:
        list: A list of keywords that are in the message
    """
    kw_model = KeyBERT(model=nlp)
    keywords = kw_model.extract_keywords(message, keyphrase_ngram_range=(1, 3), stop_words='english',
                                         use_mmr=True, diversity=0.8, top_n=10)
    keywords = [key[0] for key in keywords if key[1] > 0.8]
    return keywords


def read_dir(dir_path):
    """
    This function reads a directory, and use read_text on every text files inside that directory.
    The results are saved as a pandas' database in a pickle format.
    There is two different databases saved. One with a row for each triple, the other is a row for each message.
    Args:
        dir_path:

    Returns:
        Nothing
    """
    lst_df_triple = []
    lst_df_message = []
    # CHOOSE AND COMMENT THE TREE THAT IS NOT USED
    # ENB NO SUMMARY
    # tree = et.parse("data/info/enb_cop_no_summary.xml")
    # ALL COP EVENTS
    tree = et.parse("data/info/enb.xml")
    obj = os.scandir(dir_path)
    number_files = len([name for name in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, name))])
    for ind, entry in enumerate(obj):
        if entry.is_file():
            print(ind, "/", number_files)

            num = entry.name.split(".")[0]
            year = int(tree.xpath("//event[urls/url/@num='" + num + "']/date/@year")[0])
            event = tree.xpath("//event[urls/url/@num='" + num + "']/@title")[0]
            print(num, year, event)

            text_instance = read_text(entry.path, year=year, num=num)

            df_triple = text_instance.doc_to_pandas_by_triples()
            df_message = text_instance.doc_to_pandas_by_message()
            df_message["event"] = event
            # lst_df_triple.append(df_triple)
            lst_df_message.append(df_message)
            print(len(df_message), "messages extracted.")

    # super_df_triple = pd.concat(lst_df_triple)
    # super_df_triple.to_pickle("data/output/df_all_triple.pkl")

    super_df_message = pd.concat(lst_df_message)
    super_df_message.to_pickle("data/output/df_full_enb_corpus.pkl")

    # df_all_keywords = extract_keywords_from_db(super_df_message)
    # df_all_keywords.to_pickle("data/output/df_all_keywords.pkl")


def read_text(path, year: int, num: str) -> Text:
    """
    read the text file and extracts the relations as a Text instance.
    Args:
        path: str
            the path of the text file
        year: int
            the year of the COP summit
        num: str
            the num of the COP summit

    Returns:
        An instance of the Text class
    """
    name = path.split("/")[-1].split(".")[0]
    text_instance = Text(name=name, year=year, num=num)
    num_sentence = 1
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                doc = nlp(line.rstrip())
            except IndexError:
                print(num, line)
                continue

            # Sentencizer from spaCy
            for sentence in doc.sents:
                s = Sentence(sentence=sentence.text, num_sentence=num_sentence)

                # SRL pipeline
                doc_srl = allennlp_srl_coref.srl_coref(sentence.text)
                json_data = allennlp_srl_coref.srl_verbs(doc_srl)

                # We can't quite create the triple from the start because we need valid Actor and Pred
                dic_triple = {}
                # json_data = sort_json(json_data)
                for verb in json_data:
                    # get the verb (=pred)
                    pred = verb["verb"]
                    # tag = verb["tags"]
                    # ind = tag.index("B-V")

                    # retrieve the token of that verb // Sometimes there are identical predicates, so we store
                    # in a list, and we work with indexes of these verbs in the sentence.
                    token = [token for token in sentence if token.text == pred]

                    # If the verb is a valid predicate, we'll create a triple
                    for tok in token:
                        if pred_is_in_lst_predicate(tok.lemma_):
                            is_head_root = tok.head == sentence.root

                            p = Predicate(tok.text, lemma=tok.lemma_, typ=type_of_predicate(tok.lemma_),
                                          neg=False, dep=tok.dep_, is_head_root=is_head_root)
                            dic_triple[tok.i - sentence.start] = {"token": tok, "actor_sup": [], "actor_opp": [],
                                                                  "predicate": p, "message": "", "root": sentence.root}

                # We loop though each propositions
                for verb in json_data:
                    predicate = verb["verb"]
                    tag = verb["tags"]
                    if "B-V" not in tag:
                        continue
                    ind = tag.index("B-V")

                    line = verb["description"]

                    # regex to capture the triple
                    m_arg0 = re.search(r"\[ARG0: (.*?)]", line)
                    m_arg1 = re.search(r"\[ARG1: (.*?)]", line)
                    # Continuation of message
                    m_c_arg1 = re.search(r"\[C-ARG1: (.*?)]", line)
                    m_arg2 = re.search(r"\[ARG2: (.*?)]", line)
                    m_arg3 = re.search(r"\[ARG3: (.*?)]", line)
                    # modifier goal
                    m_argm_gol = re.search(r"\[ARGM-GOL: (.*?)]", line)
                    # adverb modifier
                    m_argm_adv = re.search(r"\[ARGM-ADV: (.*?)]", line)
                    # modifier loc
                    m_argm_loc = re.search(r"\[ARGM-LOC: (.*?)]", line)
                    # modifier cause
                    m_argm_cau = re.search(r"\[ARGM-CAU: (.*?)]", line)
                    # modifier comitative
                    m_argm_com = re.search(r"\[ARGM-COM: (.*?)]", line)
                    # Reference / relative
                    m_r_arg1 = re.search(r"\[R-ARG1: (.*?)]", line)
                    # modifier manner
                    m_argm_mnr = re.search(r"\[ARGM-MNR: (.*?)]", line)
                    # temporal modifier
                    m_argm_tmp = re.search(r"\[ARGM-TMP: (.*?)]", line)
                    neg = "ARGM-NEG" in line

                    if neg and ind in dic_triple.keys():
                        dic_triple[ind]["predicate"].change_neg()

                    # Regex on ARG0 = subject = actor
                    if m_arg0:
                        actor_sentence = m_arg0.group(1)
                        if ind in dic_triple.keys():
                            dic_triple[ind]["actor_sup"] += arg_in_actors(actor_sentence)

                    # Regex on Arg goal // on behalf of
                    if m_argm_gol:
                        arg_gol = m_argm_gol.group(1)
                        if ind in dic_triple.keys():
                            dic_triple[ind]["actor_sup"] += arg_in_actors(arg_gol)

                    # # Regex on Arg manner // on behalf of is sometimes a goal or a manner, go figure
                    if m_argm_mnr:
                        arg_mnr = m_argm_mnr.group(1)
                        if ind in dic_triple.keys():
                            dic_triple[ind]["actor_sup"] += arg_in_actors(arg_mnr)

                    # Regex on comitative argument // French with the EU
                    if m_argm_com:
                        arg_com = m_argm_com.group(1)
                        if ind in dic_triple.keys():
                            dic_triple[ind]["actor_sup"] += arg_in_actors(arg_com)

                    # Regex on ARG1 =message
                    if m_arg1:
                        message = m_arg1.group(1)
                    else:
                        message = ""
                    # Regex ARG2, only if ARG1 exists
                    if m_arg2:
                        # If valid actors present in arg2, we add them to the actor, else to the message
                        if len(arg_in_actors(m_arg2.group(1))) > 0:
                            if ind in dic_triple.keys():
                                if "opposed by" in m_arg2.group(1):
                                    dic_triple[ind]["actor_opp"] += arg_in_actors(m_arg2.group(1))
                                    message += m_arg2.group(1).split(", opposed by")[0]

                                else:
                                    dic_triple[ind]["actor_sup"] += arg_in_actors(m_arg2.group(1))

                        else:
                            # SPECIAL CASE URGE // Inversion of Arg1 and ARG 2
                            if ind in dic_triple.keys():
                                if dic_triple[ind]['token'].lemma_ == 'urge'.casefold():
                                    message = m_arg2.group(1) + " " + message
                                elif get_actor_type_from_xml(m_arg2.group(1)) == "generic":
                                    message = m_arg2.group(1) + " " + message
                                else:
                                    message += " " + m_arg2.group(1)

                    if m_arg3:
                        message += " " + m_arg3.group(1)
                    if m_argm_loc:
                        message += " " + m_argm_loc.group(1)
                    if m_argm_cau:
                        message += " " + m_argm_cau.group(1)
                    if m_c_arg1:
                        message += " " + m_c_arg1.group(1)

                    # Regex on Arg adv // France for the EU ...
                    if m_argm_adv:
                        arg_adv = m_argm_adv.group(1)
                        # if there's an actor in the adverbial clause, we add to the actors
                        if len(arg_in_actors(arg_adv)) > 0:
                            if ind in dic_triple.keys():
                                dic_triple[ind]["actor_sup"] += arg_in_actors(arg_adv)
                        else:
                            # Checking if there's a verb in the clause
                            clause_has_a_verb = False
                            for ta in tag:
                                if "ARGM-ADV" in ta:
                                    ind_m = tag.index(ta)
                                    if ind_m in dic_triple.keys():
                                        clause_has_a_verb = True
                            if not clause_has_a_verb:
                                message += " " + arg_adv
                    # Adding the message to the dic
                    # ARBITRARY rule, if message empty but there is a Temporal argument then, this is the message
                    if message == "" and m_argm_tmp:
                        message += m_argm_tmp.group(1)
                    if ind in dic_triple.keys() and message != "":
                        dic_triple[ind]["message"] = message

                    # Case // Japan supported by Iran, declared...
                    # Trying wo and len(arg_in_actors(message)) > 0
                    if predicate.casefold() == "supported" and actor_sentence.startswith("by") and \
                            str(sentence.root) != predicate.casefold():
                        if message.casefold() == "this":
                            continue
                        # In that case we want to add the actors to the HEAD OF THE HEAD OF THE PREDICATE
                        # WTF RIGHT?! China opposed by Britain, China is head of opposed. And the head of china
                        # is the real predicate
                        if ind in dic_triple.keys():
                            root = sentence.root
                            if root.i - sentence.start in dic_triple.keys():
                                dic_triple[root.i - sentence.start]["actor_sup"] += arg_in_actors(actor_sentence)
                                del dic_triple[ind]

                            else:
                                token = dic_triple[ind]['token']
                                head_verb = token.head.head
                                if head_verb.i - sentence.start in dic_triple.keys():
                                    dic_triple[head_verb.i - sentence.start]["actor_opp"] += arg_in_actors(
                                        actor_sentence)
                                    del dic_triple[ind]

                    # case opposed by
                    # Trying without and len(arg_in_actors(message)) > 0
                    elif predicate.casefold() == "opposed" and str(sentence.root) != predicate.casefold() and \
                            (actor_sentence.startswith("by") or message.casefold() == "which" or m_r_arg1):

                        if message.casefold() == "this":
                            continue
                        root = sentence.root
                        if ind in dic_triple.keys():
                            token = dic_triple[ind]['token']
                            head_verb = token.head.head
                            if root.i - sentence.start in dic_triple.keys():
                                dic_triple[root.i - sentence.start]["actor_opp"] += arg_in_actors(actor_sentence)
                                # she suggested doing something, which norway opposed
                                # we need to remove ", which (...) from the message
                                if message.casefold() == "which" or m_r_arg1:
                                    message = dic_triple[root.i - sentence.start]["message"]
                                    new_truncated_message = (re.split(r',?\s?which', message))[0]
                                    dic_triple[root.i - sentence.start]["message"] = new_truncated_message

                            elif head_verb.i - sentence.start in dic_triple.keys():
                                dic_triple[head_verb.i - sentence.start]["actor_opp"] += arg_in_actors(actor_sentence)
                                # she suggested doing something, which norway opposed
                                # we need to remove ", which (...) from the message
                                if message.casefold() == "which" or m_r_arg1:
                                    message = dic_triple[head_verb.i - sentence.start]["message"]
                                    new_truncated_message = (re.split(r'[,\s]+which', message))[0]
                                    dic_triple[head_verb.i - sentence.start]["message"] = new_truncated_message
                            del dic_triple[ind]

                # We have cases with V1/V2ing V1 to V2 to remove
                for ind, dic in dic_triple.items():
                    # We keep triples that have a message and at least a valid actor
                    if len(dic['actor_sup']) < 1 or dic['message'] == "":
                        continue
                        # We do not care about xcomp (Open clausal complement) predicates,
                        # unless there are equiv w the root
                        # https://github.com/clir/clearnlp-guidelines/blob/master/md/specifications/dependency_labels.md
                    if dic['token'].dep_ == "xcomp" and dic['token'].tag_ != "VBD":
                        continue

                    m = Message(message=dic["message"])
                    keywords = keywords_in_message(dic["message"])
                    m.add_keywords(keywords)

                    lst_actor_sup = list(set(dic['actor_sup']).difference(set(dic['actor_opp'])))
                    for actor in lst_actor_sup:
                        a = Actor(name=str(actor), dbpedia=get_dbpedia(str(actor)), typ=get_actor_type_from_xml(actor))

                        tr = Triple(actor=a, predicate=dic["predicate"], message=m,
                                    sentence=sentence.text)
                        s.add_triple(triple=tr)
                    lst_actor_opp = dic["actor_opp"]
                    if len(lst_actor_opp) > 0:
                        for actor in lst_actor_opp:
                            a = Actor(name=str(actor), dbpedia=get_dbpedia(str(actor)),
                                      typ=get_actor_type_from_xml(actor))
                            p_opp = copy.deepcopy(dic["predicate"])
                            p_opp.change_neg()
                            tr = Triple(actor=a, predicate=p_opp, message=m,
                                        sentence=sentence.text)
                            s.add_triple(triple=tr)

                if len(s.get_lst()) > 0:
                    # Pronoun / Coref resolution
                    lst_to_add = []
                    lst_to_remove = []
                    for triple in s.get_lst():
                        # We look for a triple with Actor = pronoun and pred.token.dep = ccomp
                        # and pred.token.head = root
                        # When we found it, we look
                        pred = triple.get_predicate()
                        if triple.get_actor().get_type() == "pronoun" and \
                                pred.get_dep() == "ccomp" and pred.get_is_head_root():
                            for triple_y in s.get_lst():
                                pred_y = triple_y.get_predicate()
                                if pred_y.get_dep() == "ROOT" and "could" not in triple_y.get_message().get_message():
                                    a = triple_y.get_actor()
                                    p = triple.get_predicate()
                                    m = triple.get_message()
                                    se = triple.get_sentence()
                                    tr = Triple(actor=a, predicate=p, message=m, sentence=se)
                                    #
                                    lst_to_add.append(tr)
                                    lst_to_remove.append(triple_y)
                                    lst_to_remove.append(triple)

                    [s.remove_triple(t) for t in lst_to_remove]

                    for trip in s.get_lst():
                        if trip.get_actor().get_type() == "pronoun":
                            s.remove_triple(trip)
                    [s.add_triple(t) for t in lst_to_add]
                if len(s.get_lst()) > 0:
                    text_instance.add_sentence(sentence=s)
                    num_sentence += 1
    return text_instance


if __name__ == '__main__':
    # EVAL BIT
    eval_instance = read_text(path="data/info/eval/enb_test_l6.txt", year=2999, num="666")
    eval_instance.doc_to_text(output_path="data/info/eval/results_on_golden_set.txt")
    # df = eval_instance.doc_to_pandas_by_message()

    # test_inst = read_text("data/info/eval/enb_test_l6.txt", year=2999, num="666")
    # df_test = test_inst.doc_to_pandas_by_message("test.pkl")

    # read_dir("data/raw/txt_boiler")
