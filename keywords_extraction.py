import pandas as pd
import spacy
from keybert import KeyBERT


def keywords_in_message(message: str, model, use="maxsum") -> list:
    """
    Takes a sentence as input and returns a list of all the keywords presents in that sentence using EntityLinker,
    a spaCy pipeline
    Args:
        message (str): A string of text, most of the time it will be the message part of the Triple

    Returns:
        list: A list of keywords that are in the message
    """
    kw_model = KeyBERT(model=model)
    keywords_mmr = kw_model.extract_keywords(message, keyphrase_ngram_range=(1, 3), stop_words='english',
                                             use_mmr=True, diversity=0.8, top_n=10)
    keywords_maxsum = kw_model.extract_keywords(message, keyphrase_ngram_range=(1, 3), stop_words='english',
                                                use_maxsum=True, diversity=1, top_n=10)

    keywords_maxsum = [key[0] for key in keywords_maxsum if key[1] > 0.7]
    keywords_mmr = [key[0] for key in keywords_mmr if key[1] > 0.7]
    if use == "maxsum":
        return keywords_maxsum
    elif use == "mmr":
        return keywords_mmr
    else:
        return [None]


nlp = spacy.load("en_core_web_trf")

if __name__ == "__main__":
    res = []
    with open("data/info/eval/enb_test_l6.txt", 'r', encoding="utf-8") as f:
        for line in f:

            sentence = line.rstrip()
            max_sum = keywords_in_message(line.rstrip(), nlp, "maxsum")
            mmr = keywords_in_message(line.rstrip(), nlp, "mmr")
            res.append(
                [sentence, ", ".join(max_sum), ", ".join(mmr)]
            )

    df = pd.DataFrame(data=res, columns=["Sentence", "MaxSum", "MMR"])
    df.to_csv('data/output/example_keywords.csv', index=False)

