"""
Small script that takes a finished database of extraction relation in Pandas and transform columns into
categorical for faster use.
"""

import pandas as pd


def transform_columns_categorical(df_ini):
    """

    Args:
        df_ini: pd.DataFrame
            the initial DataFrame

    Returns: pd.DataFrame
        A DataFrame where the columns that can be categorical are categorical

    """
    df = df_ini.copy()
    # There is a finite number of Predicate, Type, Year and event
    df["Predicate"] = df["Predicate"].astype("category")
    df["Type"] = df["Type"].astype("category")
    # df["Year"] = df["Year"].astype("category")
    if 'Venturini_keywords' in df.columns:
        df["Venturini_keywords"] = df["Venturini_keywords"].astype("category")
    if 'event' in df.columns:
        df["event"] = df["event"].apply(lambda x: str(x))
        df["event"] = df["event"].astype("category")
    return df


if __name__ == "__main__":
    df_message_venturini = pd.read_pickle("data/output/df_all_message_venturini.pkl")
    df_message_venturini = transform_columns_categorical(df_message_venturini)
    df_message_venturini.to_pickle("data/output/df_all_message_venturini_categorical.pkl")

    df_full_enb = pd.read_pickle("data/output/df_full_enb_corpus.pkl")
    df_full_enb = transform_columns_categorical(df_full_enb)
    df_full_enb.to_pickle("data/output/df_full_enb_corpus_categorical.pkl")
