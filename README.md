# Relation Extraction on the ENB corpus
## An NLP analysis of a corpus of international negotiations related to climate change.

The ENB corpus (which stands for `Earth Negotiations Bulletin`) is a corpus of diplomatic negotiations regarding the environment and sustainable developments. It is composed of daily reports and summaries written in simplified English of various conferences and international summits.  
This study focuses solely on Volume 12 of the ENB which deals with `climate change`. We have analysed a subsection of volume 12, namely the `Conferences of Parties` (COP) reports.
COP summits take place once a year, every year except 2020 since 1995. Countries and international organisations gather and discuss the climate.  
The goal is to analyse these reports of COP events using NLP (Natural language processing) tools to provide a quicker and better understanding of the texts.  
These reports are available here: [Volume 12 ENB](https://enb.iisd.org/enb/vol12/).


We have crawled the HTML reports. They are available in `data/raw` in HTML or raw text. The folder cop_no_summary contains only COP events, minus the summaries on which each summit ends.  

After the text was crawled, we used an NLP technique called Semantic Role Labeling (SRL) to extract triples from the text. A triple is made of the actor, the verb, and the message.  
- `Actors` in the ENB corpus are normalised. Actors can be countries (sometimes referred to as the person representing them), groups of countries or organisations.  
- `Predicates` are normalised too in the ENB corpus. The corpus is written to be as objective as possible, to achieve this, The only predicates available to reporters are those which don't emit a judgement. There are three categories of predicates (support, opposition and declaration). In this study, nominal predicates are excluded.  
- `Messages` are made of the rest of the sentence. They correspond to what the actors want to say.  
  
For example, the sentence below gives four triples:  
<p style="text-align: center;">**Finland, on behalf of the European Union (EU), highlighted the stern review and stressed the need for long-term action where adaptation complements mitigation**</p>  

| ACTORS | PREDICATE | MESSAGE |  
| ------ | --------- | ------- |  
| ACTOR1 = european union | PREDICATE1 = stressed | MESSAGE1 = the need for long-term action where adaptation complements mitigation |  
| ACTOR2 = finland | PREDICATE1 = stressed | MESSAGE1 = the need for long-term action where adaptation complements mitigation |  
| ACTOR1 = european union | PREDICATE2 = highlighted | MESSAGE2 = the stern review |  
| ACTOR2 = finland | PREDICATE2 = highlighted | MESSAGE2 = the stern review |  
  
  
Messages are rarely as simple as the one above. They are often long and complex. We have enriched them with key-phrases using the key-phrase extraction module from [KeyBERT](https://github.com/MaartenGr/KeyBERT).  
10 clusters related to the corpus have been created using Venturini's work ([Three maps and three misunderstandings: A digital mapping of climate diplomacy, Venturni et al. 2014](https://journals.sagepub.com/doi/full/10.1177/2053951714543804)). Each message is annotated with these clusters.  

Results are stored in `pandas databases` saved in pickle. They are available in data/output.  
- `data/output/df_all_message_venturini_categorical.pkl` contains the results for Vol12 of the ENB corpus focused on COP summits only.  
- `data/output/df_full_enb_corpus_categorical.pkl` contains the results for the entire Vol12 of the ENB corpus.  


## 1st step: crawling

The data from the [Volume 12](https://enb.iisd.org/enb/vol12/) has been crawled from HTML to raw text using requests, BeautifulSoup and Lxml libraries.  
A summary in XML is available:  
- `data/info/enb.xml` for all events
- `data/infoenb_cop_no_summary.xml` for Cop events only  
In the file, a metadata breakdown of the climate summits is available with information such as title, year, type of events, country, city, number of issues, name of the text file and URL.  


Here is the example of the first COP event in Berlin in 1995.  
```xml
    <event title="1995-COP-1" type="COP">
        <title>First Conference of the Parties to the Framework Convention on Climate Change</title>
        <date year="1995">28 March - 7 April 1995</date>
        <place country="Germany">Berlin, Germany</place>
        <urls>
            <url issue="12" date="28 March 1995" num="1212000e">https://enb.iisd.org//vol12/1212000e.html</url>
            <url issue="13" date="29 March 1995" num="1213000e">https://enb.iisd.org//vol12/1213000e.html</url>
            <url issue="14" date="30 March 1995" num="1214000e">https://enb.iisd.org//vol12/1214000e.html</url>
            <url issue="15" date="31 March 1995" num="1215000e">https://enb.iisd.org//vol12/1215000e.html</url>
            <url issue="16" date="3 April 1995" num="1216000e">https://enb.iisd.org//vol12/1216000e.html</url>
            <url issue="17" date="4 April 1995" num="1217000e">https://enb.iisd.org//vol12/1217000e.html</url>
            <url issue="18" date="5 April 1995" num="1218000e">https://enb.iisd.org//vol12/1218000e.html</url>
            <url issue="19" date="6 April 1995" num="1219000e">https://enb.iisd.org//vol12/1219000e.html</url>
            <url issue="20" date="7 April 1995" num="1220000e">https://enb.iisd.org//vol12/1220000e.html</url>
            <url issue="21" date="Summary" num="1221000e">https://enb.iisd.org//vol12/1221000e.html</url>
        </urls>
    </event>
```

The raw text in Relation_extraction_ENB/data/raw/ has been crawled with two methods:  
- in `data/raw/text`, we have retrieved only the content of ```<p></p>``` tags.  
- in `data/raw/txt_boiler`, we used [BoilerPy3](https://pypi.org/project/boilerpy3/) to extract relevant data from the text files.  

Relevant `scripts` to the crawling sections:  
- `crawl.py` was used to create the `enb.xml` and `enb_cop_no_summary.xml` files, listing all the events with their relevant metadata.  
- `download_html.py` was used to crawl the HTML content  
- `html_to_text.py` was used to convert HTML content into text  


## 2nd step : Relation Extraction
AllenNLP provides a Semantic Role Labeling (SRL) tool based on the BERT language model from 2019. A [demo](https://demo.allennlp.org/semantic-role-labeling) is available on their website.  
We have used the results of AllenNLP SRL tool as the first part of our relation extraction pipeline. AllenNLP annotates the text following the [English ProbBank Annotation Guidelines](https://verbs.colorado.edu/propbank/EPB-Annotation-Guidelines.pdf). These annotations are then used in conjunction with a set of rules to extract relations.  

| ![AllenNLP demo](/media/kevin-laptop/My Passport/Relation_extraction_ENB/Notes/demo_allennlp.png)|
|:--:|
| *Figure 1*: Simple example of an output of the AllenNLP SRL tool |  

Regarding the example of Figure 1, we see that ARG0 (PropBank equivalent of the Agent) resembles an Actors and ARG1 resembles the message.  

- `data/info/actors.xml` is an XML list containing all the valid actors in the corpus.
- `data/info/predicate.xml` is an XML list containing all the valid enunciation predicate in the corpus.  
- The script `read_text.py` performs extraction relation on all text files present in `data/raw/txt` utilising AllenNLP SRL tool as a spaCy pipeline, only keeping triples if actors and predicates are present in actors.xml and predicate.xml.  
- instances of Actors, Predicate, Messages, Triple, Sentence, Text classes are generated according to their declaration in `triple_class.py` in order to create an effective representation of the data. 
- Messages are enriched with key-phrases using KeyBERT key-phrase extraction tool.  
- Messages are annotated with clusters according to the work of Venturini. There are 10 clusters, each message can be part of zero, one or more clusters. Clusters represent various topics of international diplomatic negotiations regarding climate change.  
- `read_dir` function in `read_text.py` script saves the results of the extraction relation as a pandas database.  


## Evaluation

We use [Ruiz](https://hal.archives-ouvertes.fr/tel-01575167)'s evaluation process from his work on the same corpus. He created [a gold-set of 100 sentences](https://github.com/pruizf/pasrl/tree/master/proposition_extraction/testsets) which encapsulates most difficulties of the corpus.   
The [eval folder](data/info/eval/) contains the raw sentences, the sentences annotated manually and the sentences annotated by the system. We compared the sentences annotated by the system to the gold-set (sentences annotated manually) and calculated precision, recall and f-score.   

| System      | Precision | Recall      | F1 score | 
| ----------- | ----------- | ----------- | ----------- |
| AllenNLP   | 0.88        | 0.87   | 0.88        |
  
  

## Graphical analysis: a web app using Plotly-Dash framework

We developed an app to visualise the results of the relation extraction process on the ENB corpus. It's using the Plotly-Dash framework and is hosted on Heroky and available [here](https://srl-enb-app.herokuapp.com/). The source code is available [here](https://github.com/KnuxV/enb_heroku_app).  

The app upper-section displays a filtering system with which the user can filter the results.  
It is possible to choose a `range of years` from the full length of the ENB corpus (1995-2019) to a single year.  
One or more `actors`can be chosen to filter the database.  
The database can also be filtered by `types of predicates` (support, opposition, neutral).  
The database can be filtered with `clusters` or by `raw-text search`.  
The app is made of two pages:  
#### A Table page which displays the results as a dataframe table with the following columns:
- `Sup`, for countries supporting the proposition  
- `Opp`, for countries opposing the proposition  
- `Pred`, for predicate, the predicate linking actors and message
- `Type`, the type of predicates (support, opposition, neutral)  
- `Message`, the message of the proposition  
- `Keywords`, a list of keywords extracted from the message  
- `Sentence`, the full sentence from which the proposition is extracted  
- `Year`, the year of the conference from which the proposition is extracted  
- `Num`, the name of the text file from which the proposition is extracted, the online report is linked as a hypertext  
- `Venturini`, the presence of zero or more clusters of Venturini.  

#### A Graph page that displays 5 graphics giving insight on the database.
- A `network graph` showing collaborations between countries  
- Two `bar plots` showing the main actors in the filtered database and how propositions appear over time.  
- Two `circular plots` showing which clusters are most frequent in the corpus, and which types of predicates are most present.  

#### Credits
files actors.xml, preds_nominal.xml, preds_verbal.xml are taken from Ruiz's work (2017). See his gitHub repo : https://github.com/pruizf/pasrl/tree/master/proposition_extraction/data