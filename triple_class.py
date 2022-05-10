"""
Triple classes,  class system where we store the results of the Semantic role labelling.
"""
import copy
import itertools
import re
from typing import List, Optional

import pandas as pd
from collections import defaultdict


class Actor:
    """
    Actor class
    name is what is written in the sentence, but we also get a dbpedia to compare and a shorter display
    two instances are equal is they're dbpedia or name are equal
    """

    def __init__(self, name: str, dbpedia="", display="", typ=""):
        self.name = name
        self.dbpedia = dbpedia
        self.display = display
        self.typ = typ

    def __eq__(self, other):
        if not isinstance(other, Actor):
            return NotImplemented
        return self.name == other.name

    def __str__(self):
        if self.display != "":
            return self.display
        else:
            return self.name

    def is_dbpedia(self):
        """

        Returns
        -------
            True if the dbpedia attributes is not empty
        """
        return self.dbpedia != ""

    def get_actor_name(self):
        return self.name

    def get_actor_display(self):
        return self.display

    def get_type(self):
        return self.typ

    def set_actor_type(self, typ):
        self.typ = typ


class Predicate:
    """
    Predicate class
    """

    def __init__(self, name: str, lemma="", typ="", neg=False, dep="",
                 is_head_root=False):
        self.name: str = name
        self.lemma: str = lemma
        self.typ: str = typ
        self.neg: bool = neg
        self.dep: str = dep
        self.is_head_root: bool = is_head_root

    def __eq__(self, other):
        if not isinstance(other, Predicate):
            return NotImplemented
        return self.name == other.name and self.neg == other.neg

    def __str__(self):
        if self.neg:
            return "not " + self.name
        else:
            return self.name

    def get_name(self):
        return self.name

    def get_lemma(self):
        return self.lemma

    def get_type(self):
        return self.typ

    def get_neg(self):
        return self.neg

    def get_dep(self):
        return self.dep

    def get_is_head_root(self):
        return self.is_head_root

    def change_neg(self):
        self.neg = not self.neg


class Message:
    """
    Message class
    """

    def __init__(self, message: str):
        self.message: str = message
        self.keywords = []

    def __eq__(self, other):
        if not isinstance(other, Message):
            return NotImplemented
        return self.message.lower() == other.message.lower()

    def __str__(self):
        return self.message

    def get_message(self):
        return self.message

    def add_keywords(self, keywords):
        if isinstance(keywords, list):
            self.keywords += keywords
        else:
            self.keywords.append(keywords)

    def get_keywords(self):
        return self.keywords


class Triple:
    """
    Triple class
    Attributes are actor, predicate, message, sentence

    There's a method to compare two instances of Triple and returns either a perfect match, or which attribute
    is different
    """

    def __init__(self, actor: Actor, predicate: Predicate, message: Message,
                 sentence: str):
        self.actor: Actor = actor
        self.predicate: Predicate = predicate
        self.message: Message = message
        self.sentence: str = sentence

    def __eq__(self, other):
        if not isinstance(other, Triple):
            return NotImplemented
        return self.actor == other.actor and self.predicate == other.predicate and self.message == other.message

    def __ne__(self, other):
        if not isinstance(other, Triple):
            return NotImplemented
        return not self.__eq__(other)
        # return self.actor != other.actor or self.predicate != other.predicate or self.message != other.message

    def __str__(self):
        return str(self.actor) + "\t" + str(self.predicate) + "\t" + str(
            self.message)

    def __hash__(self):
        return id(self.actor) + id(self.predicate) + id(self.message)

    def __lt__(self, other):
        if self.actor != other.actor:
            return self.actor.name < other.actor.name
        elif self.predicate != other.predicate:
            return self.predicate.name < other.predicate.name
        else:
            return self.message.message < other.message.message

    def __gt__(self, other):
        if self.actor != other.actor:
            return self.actor.name > other.actor.name
        elif self.predicate != other.predicate:
            return self.predicate.name > other.predicate.name
        else:
            return self.message.message > other.message.message

    def get_actor(self):
        return self.actor

    def get_predicate(self):
        return self.predicate

    def get_message(self):
        return self.message

    def get_sentence(self):
        return self.sentence

    def get_score(self, other):
        if isinstance(other, Triple):
            res_get_score = [0, 0, 0]
            if self.actor == other.actor:
                res_get_score[0] = 1
            if self.predicate == other.predicate:
                res_get_score[1] = 1
            if self.message == other.message:
                res_get_score[2] = 1
            return tuple(res_get_score)
        else:
            return [-1, -1, -1]


class Sentence:
    """
    Sentence class
    A Sentence class contains the sentence as a string and a list of triples
    (aka propositions)
    """

    def __init__(self, sentence: str, num_sentence: int):
        self.sentence: Optional[str] = sentence
        self.num_sentence: Optional[int] = num_sentence
        self.lst_triples: Optional[List[Triple]] = []

    def __str__(self):
        return self.sentence

    # def __eq__(self, other):
    #     """
    #     To compare to Sentence instances, we check if their list of triple are the same (order doesn't matter so set)
    #     Parameters
    #     ----------
    #     other sentence instance
    #         The instance of the Sentence class
    #
    #     Returns true if the two instances have the triples
    #     -------
    #
    #     """
    #     if not isinstance(other, Sentence):
    #         return NotImplemented
    #     return self.get_set() == other.get_set()

    def add_triple(self, triple: Triple):
        if isinstance(triple, Triple):
            # if triple not in self.lst_triples:
            self.lst_triples.append(triple)

    def remove_triple(self, triple_to_remove: Triple):
        if isinstance(triple_to_remove, Triple):
            # self.lst_triples = [triple for triple in self.lst_triples if triple != triple_to_remove]
            if triple_to_remove in self.lst_triples:
                self.lst_triples.remove(triple_to_remove)

    def get_lst(self):
        return self.lst_triples

    def get_sorted_list(self):
        return sorted(self.lst_triples)

    def get_set(self):
        return set(self.lst_triples)

    def get_num_sentence(self):
        return self.num_sentence

    def get_score(self, golden):
        """
        To compute Precision and Recall against the golden set.
        Precision == Total of correct triples / Total of triples in the instance
        Recall == Total of correct triples / Total of triples in the golden instance
        It is pointless to compute on a single sentence, so we return number of correct triples, number of triples,
        and number of golden triples

        Parameters
        ----------
        golden
            The instance of the sentence but generated from the golden set

        Returns
        -------
            A tuple made of tot_correct_triples, tot_triples, tot_golden_triples
        """
        if not isinstance(golden, Sentence):
            return "This is an instance of the Sentence class"
        else:
            tot_correct_triples = 0

            for triple_e in self.get_lst():
                for triple_g in golden.get_lst():
                    if triple_e == triple_g:
                        tot_correct_triples += 1
                        break
            tot_eval_triples = len(self.get_lst())
            tot_golden_triples = len(golden.get_lst())
            if tot_correct_triples < tot_golden_triples:
                print(self.num_sentence, self.sentence)
                print(tot_correct_triples, tot_eval_triples, tot_golden_triples)
                print("\n")

            return tot_correct_triples, tot_eval_triples, tot_golden_triples


class Text:
    """
    A Text class that has a list of Sentence.
    Sentences must be in the right order
    """

    def __init__(self, name: str, year: Optional[int], num: str):
        self.name: Optional[str] = name
        self.year: Optional[int] = year
        self.num: Optional[str] = num
        self.lst_sentence: Optional[List[Sentence]] = []

    def get_name(self):
        return self.name

    def get_num(self):
        return self.num

    def get_year(self):
        return self.year

    def add_sentence(self, sentence: Sentence):
        if isinstance(sentence, Sentence):
            self.lst_sentence.append(sentence)

    def get_fscore(self, golden, mode="all"):
        """
        Returns the precision, recall and  fscore given a Text instance and a golden Text instance
        Parameters
        ----------
        golden : Text instance
            The Text instance annotated manually against which we compare our model
        mode : str
            modifies the return output, if all, we return a triple (precision, recall, fscore). 
            But with either mode = "precision" "recall" or "fscore". we return only that value. 

        Returns
        -------
        a tuple (precision, recall, fscore) or one of those values by itself
        """
        tot_correct_in_text = 0
        tot_eval_in_text = 0
        tot_golden_in_text = 0
        if not isinstance(golden, Text):
            return "This is not an instance of Text"
        # Making sure there is the same number of sentences
        if not len(self.lst_sentence) == len(golden.lst_sentence):
            print(len(self.lst_sentence))
            print(len(golden.lst_sentence))
            return "The number of sentences is not the same"
        else:
            # Sentences are in the right order
            # For each sentence, we compare against the golden equiv
            for i in range(len(self.lst_sentence)):
                tot_correct_triples, tot_eval_triples, tot_golden_triples = \
                    self.lst_sentence[i].get_score(golden.lst_sentence[i])
                # Adding to the count
                tot_correct_in_text += tot_correct_triples
                tot_eval_in_text += tot_eval_triples
                tot_golden_in_text += tot_golden_triples

            precision = tot_correct_in_text / tot_eval_in_text
            recall = tot_correct_in_text / tot_golden_in_text
            fscore = 2 * precision * recall / (precision + recall)

            if mode == "all":
                return precision, recall, fscore
            elif mode == "precision":
                return precision
            elif mode == "recall":
                return recall
            elif mode == "fscore":
                return fscore
            else:
                return "erreur, check if mode is wrong"

    def triple_eval(self, golden):
        # TODO tricky bit is to compare the triples properly in each sentence properly
        pass

    def read_golden(self, path):

        regex_sentence = r'^(\d+)\t(.+)'
        regex_triple = r'^(\D.+?)\t(\D+?)\t(.+)'
        s = None
        ind = 0
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.rstrip()

                ind += 1
                match_sentence = re.match(regex_sentence, line)
                match_triple = re.match(regex_triple, line)

                if line == "":
                    # First we need to add the last sentence to the Text instance
                    if s not in self.lst_sentence:
                        self.add_sentence(s)
                if match_sentence:
                    # We've reached a new sentence
                    num_sent = match_sentence.group(1)
                    sent = match_sentence.group(2)

                    # We create a new instance of a Sentence class
                    s = Sentence(sentence=sent, num_sentence=int(num_sent))

                elif match_triple:
                    # we've matched a new triple
                    actor = match_triple.group(1)
                    predicate = match_triple.group(2)
                    message = match_triple.group(3)
                    a = Actor(name=actor)
                    if "not " in predicate:
                        match = (re.split(r'\W+', predicate))[1]
                        p = Predicate(name=match, neg=True)
                    else:
                        p = Predicate(name=predicate, neg=False)
                    # print(p.name, p.neg)
                    m = Message(message=message)
                    tr = Triple(actor=a, predicate=p, message=m, sentence=sent)
                    s.add_triple(tr)

    def doc_to_pandas_by_triples(self, save_pkl_path=None) -> pd.DataFrame:
        """
        Tranform the instance of Text into a pandas DataFrame
        Args:
            save_pkl_path:

        Returns:
            A pandas dataframe where a row is equal to a triple
        """
        exit_list = []
        for sent in self.lst_sentence:
            for trip in sent.get_lst():
                a = trip.get_actor().get_actor_name()
                a_d = trip.get_actor().get_actor_display()
                if a_d != "":
                    a = a_d
                p = trip.get_predicate().get_name()
                p_neg = "" if trip.get_predicate().get_neg() else "not"
                p_t = trip.get_predicate().get_type()
                m = trip.get_message().get_message()
                m_keywords = trip.get_message().get_keywords()
                str_keywords = ", ".join(m_keywords)
                s = trip.get_sentence()
                y = self.get_year()
                num = self.get_num()
                lst = [a, p_neg, p, p_t, m, str_keywords, s, y, num]
                exit_list.append(lst)
        print(len(exit_list))
        df = pd.DataFrame(exit_list,
                          columns=['Actor', 'Neg', 'Predicate', 'Type',
                                   'Message', 'Keywords', 'Sentence', 'Year',
                                   'Num'])
        if save_pkl_path:
            df.to_pickle(save_pkl_path)
        return df

    def doc_to_pandas_by_message(self, save_pkl_path=None) -> pd.DataFrame:
        """

        Args:
            save_pkl_path:

        Returns:
            A pandas dataframe where a row is equal to a message
        """
        exit_list = []
        for sent in self.lst_sentence:
            dic_trip = defaultdict(list)
            for trip in sent.get_lst():
                m = trip.get_message().get_message()
                dic_trip[m].append(trip)
            for lst_of_trip_same_message in dic_trip.values():
                actor_sup = []
                actor_opp = []
                for trip in lst_of_trip_same_message:
                    a = trip.get_actor().get_actor_name()
                    if trip.get_predicate().get_neg():
                        actor_opp.append(a)
                    else:
                        actor_sup.append(a)
                # Predicates and messages are all the same, so we look at the first one.
                first_trip = lst_of_trip_same_message[0]
                p = first_trip.get_predicate().get_name()
                p_t = first_trip.get_predicate().get_type()
                m = first_trip.get_message().get_message()
                m_keywords = first_trip.get_message().get_keywords()
                str_keywords = ", ".join(m_keywords)
                s = first_trip.get_sentence()
                y = self.get_year()
                num = self.get_num()
                str_actor_opp = ", ".join(actor_opp)
                str_actor_sup = ", ".join(actor_sup)
                lst = [str_actor_sup, str_actor_opp, p, p_t, m, str_keywords, s,
                       y, num]
                exit_list.append(lst)
        df = pd.DataFrame(exit_list,
                          columns=['Actor_Support', 'Actor_Opposition',
                                   'Predicate', 'Type', 'Message', 'Keywords',
                                   'Sentence', 'Year', 'Num'])
        if save_pkl_path:
            df.to_pickle(save_pkl_path)
        return df

    def doc_to_text(self, output_path):
        with open(output_path, "w", encoding="utf-8") as f:
            for sent in self.lst_sentence:
                sent_line = str(sent.get_num_sentence()) + '\t' + str(
                    sent) + '\n'
                f.write(sent_line.lower())

                for trip in sent.get_sorted_list():
                    txt = str(trip).lower().replace("_", " ").replace(" '",
                                                                      "'").replace(
                        "`", "").replace(" - ", "-") \
                        .replace(" ,", ",").replace("( ", "(").replace(" )",
                                                                       ")").replace(
                        "“", "").replace("”", "") \
                        .replace("\"", "").replace("  ", " ").replace(" / ",
                                                                      "/").replace(
                        "can not", "cannot") \
                        .replace("''", "")
                    txt = txt.replace("  ", " ")
                    f.write(txt)
                    f.write('\n')
                f.write('\n')


if __name__ == '__main__':
    text_test = Text(name="test", year=2999, num="666")
    t_golden = Text(name="golden", year=2999, num="666")
    t_golden.read_golden(
        "data/info/eval/enb_l6_golden_exported_no_norm_pred.txt")
    text_test.read_golden("data/info/eval/results_on_golden_set.txt")
    res = text_test.get_fscore(t_golden)
    # t_golden.read_golden("data/info/eval/test.txt")
    # text_test.read_golden("data/info/eval/test1.txt")
    # res = text_test.get_fscore(t_golden)
    print(res)
