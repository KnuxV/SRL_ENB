"""
Adding Semantic Role Labelling and Coref Resolution as spaCy pipelines
Coref resolution pipeline is commented as it is not used currently but might be in the future
"""
from spacy.language import Language
from spacy.tokens import Doc
import spacy
from allennlp.predictors.predictor import Predictor
import copy


@Language.factory("srl", default_config={
    "model_path": "structured-prediction-srl-bert.2020.12.15.tar.gz"})
def create_srl_component(nlp: Language, name: str, model_path: str):
    return SRLComponent(nlp, model_path)


class SRLComponent:
    def __init__(self, nlp: Language, model_path: str):
        if not Doc.has_extension("srl"):
            Doc.set_extension("srl", default=None)
        self.predictor = Predictor.from_path(model_path)

    def __call__(self, doc: Doc):
        predictions = self.predictor.predict(sentence=doc.text)
        doc._.srl = predictions
        return doc


# @Language.factory("coref", default_config={
#     "model_path": "coref-spanbert-large-2021.03.10.tar.gz"})
# def create_coref_component(nlp: Language, name: str, model_path: str):
#     return CorefComponent(nlp, model_path)


# class CorefComponent:
#     def __init__(self, nlp: Language, model_path: str):
#         if not Doc.has_extension("coref"):
#             Doc.set_extension("coref", default=None)
#         self.predictor = Predictor.from_path(model_path)
#
#     def __call__(self, doc: Doc):
#         predictions = self.predictor.predict(doc.text)
#         doc._.coref = predictions
#         return doc


nlp = spacy.blank('en')
# nlp.add_pipe("coref")
nlp.add_pipe("srl")


def srl_coref(text):
    doc = nlp(text)
    return doc


# def coref(doc):
#     dic_words = {ind: word for ind, word in enumerate(doc._.coref["document"])}
#     clusters = doc._.coref["clusters"]
#     res = []
#     for i in range(len(clusters)):
#         for j in range(len(clusters[i])):
#             noun_phrase = ""
#             for k in range(len(clusters[i][j])):
#                 if dic_words[clusters[i][j][k]] not in noun_phrase:
#                     noun_phrase += dic_words[clusters[i][j][k]]
#             res.append(noun_phrase)
#
#     return res


def srl_verbs(doc):
    return doc._.srl["verbs"]
