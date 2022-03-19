from typing import List, Dict

import pandas as pd
from collections import Counter
import re


def sort_json(json: list) -> List:
    """
    Function that takes the Json output of AllenNLP and moves supported, opposed predicate to the front, so that they
    are analysed before the main predicate
    Parameters
    ----------
    json    list
        the json list

    Returns
    -------
    list
        Returns a list where opposed, supported predicate are at the front (first elements)
    """
    new_json = []
    for verb in json:
        if verb["verb"] == "opposed" or verb["verb"] == "supported":
            new_json.insert(0, verb)
        else:
            new_json.append(verb)
    return new_json


def extract_keywords_from_db(df: pd.DataFrame) -> pd.DataFrame:
    c = Counter()
    for ind, row in df.Keywords.items():
        lst_keywords = row.split(", ")
        for keyword in lst_keywords:
            if keyword != '':
                c[keyword] += 1
    return pd.DataFrame(c.most_common(1000), columns=["Keyword", "Count"])


def venturini_keywords_to_dic(path_venturini_keywords="data/info/venturini_keywords") -> Dict:
    """
    Takes keywords in venturini_keywords.txt and transform them into a dictionnary where keys are the title of the keywords
    and values are the keywords
    Args:
        path_venturini_keywords (str): The path of the txt file

    Returns:
        Dict : A dictonary with titles as keys and keywords as values

    """
    dic_keywords = {}
    reg_title = re.compile(r'\d+- (.+)')
    reg_keywords = re.compile(r'^[^\n\d-].+$')
    with open(path_venturini_keywords, "r", encoding="utf-8") as f:
        for line in f:
            match_title = re.match(reg_title, line.rstrip())
            match_keywords = re.match(reg_keywords, line.rstrip())
            if match_title:
                title = match_title.group(1)
            if match_keywords:
                dic_keywords[title] = match_keywords.group(0).split(', ')
    return dic_keywords


def keyword_in_str(message: str):
    dic_venturini = venturini_keywords_to_dic()
    return_lst = []
    for title, lst_keywords in dic_venturini.items():
        for keyword in lst_keywords:
            if keyword in message:
                return_lst.append(title)
    if not return_lst:
        return ""
    else:
        # return list(set(return_lst))
        return_lst = list(set(return_lst))
        print(", ".join(return_lst))
        return ", ".join(return_lst)


def update_db_with_venturini_keywords(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return and save an updated version of the dataframe with a new column in which there is a list of keyword title from
    Venturini keywords
    Args:
        df pd.DataFrame: the initial df

    Returns:
        pd.DataFrame : the updated dataframe

    """
    df["Venturini_keywords"] = df["Message"].apply(keyword_in_str)
    return df


def fixing_year_2007(df):
    """
    There was an issue with COP13 which took place in 2007 and not in 2008. This function reads the dataFrame and
    changes the date when necessary
    Args:
        df:

    Returns:

    """

    lst_num_2007 = ["enb12343e", "enb12344e", "enb12345e", "enb12346e", "enb12347e", "enb12348e", "enb12349e",
                    "enb12350e", "enb12351e", "enb12352e", "enb12353e"]

    def fix_year(year, num):
        if num in lst_num_2007:
            return 2007
        else:
            return year

    df["Year"] = df.apply(lambda x: fix_year(x["Year"], x["Num"]), axis=1)
    return df


def expand_venturini_keywords(df):
    """
    Create a new column for each title made by Venturini and update it as a bool if that keyword is present in the Venturini_keywords column
    Args:
        df:

    Returns:

    """
    dic_venturini = venturini_keywords_to_dic()

    def expand_keywords(list_keywords, tit):
        return tit in list_keywords

    for title in dic_venturini.keys():
        df[str(title)] = df.Venturini_keywords.apply(lambda x: expand_keywords(x, title))
    return df


if __name__ == '__main__':
    # df = pd.read_pickle("data/output/df_all_message.pkl")
    # df1 = fixing_year_2007(df)
    # df2 = update_db_with_venturini_keywords(df1)
    # df2.to_pickle("data/output/df_all_message_venturini.pkl")
    # df3 = expand_venturini_keywords(df2)
    # df3.to_pickle("data/output/df_all_message_venturini_expanded.pkl")
    #
    # df = pd.read_pickle("data/output/df_all_triple.pkl")
    # df1 = fixing_year_2007(df)
    # df2 = update_db_with_venturini_keywords(df1)
    # df2.to_pickle("data/output/df_all_triple_venturini.pkl")
    dic = venturini_keywords_to_dic()
    print(dic.keys())