import os
import json
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from nltk.stem import WordNetLemmatizer, SnowballStemmer
from corextopic import corextopic as ct
import pickle
import utils_model
import pymorphy2


MAPPING = {
        0: 'овощи, фрукты',
        1: 'хлеб',
        2: None,
        3: 'чай, кофе, снеки',
        4: 'каши',
        5: 'обед',
        6: 'соус'
    }

def load_data(path):
    with open(path, 'r') as f:
        data = json.load(f)
    return data


if __name__ == "__main__":
    #path to the file directory
    src = "/content/drive/My Drive/vk_clubs_data"
    file_name = 'sharingfood.json'
    data = load_data(os.path.join(src, file_name))
    morph = pymorphy2.MorphAnalyzer()
    prep_pipeline = Pipeline([
        ('lowercase', utils_model.Lowercaser()),
        ('remove_headers', utils_model.RegexTransformer(regex=r"[\w_-]*:.*")),
        ('remove_email', utils_model.RegexTransformer(regex=r"[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*")),
        ('remove_non_characters', utils_model.RegexTransformer("\W+", " ")),
        ('remove_stop_words', utils_model.StopWordsRemover(corpus=stopwords.words('russian'))),
        ('remove_digits', utils_model.RegexTransformer("[0-9_]", "")),
                     ('lemmatization', Lemmatizer(morph, stemmer=SnowballStemmer("russian")))
    ])
    #just for inicialization
    prep_pipeline.fit(data[0])
    prep_txt = [prep_pipeline.transform(i) for i in data]
    
    #feature inginiring
    words = set([j for i in prep_txt for j in i.split()])
    vocabulary = list(words)
    pipe = Pipeline([('count', CountVectorizer(vocabulary=vocabulary)),
                     ('tfid', TfidfTransformer())]).fit(prep_txt)
    features = pipe.transform(prep_txt)
    
    #Init anchors for classes
    first_gr = [prep_pipeline.transform(i) for i in ['овощи', 'фрукты', 'бананы', 'огурцы']]
    second_gr = [prep_pipeline.transform(i) for i in ['хлеб']]
    third_gr = [prep_pipeline.transform(i) for i in ['хороший', 'конкурс']]
    fourth_gr = [prep_pipeline.transform(i) for i in ['кофе', "чай", "какао"]]
    fith_gr = [prep_pipeline.transform(i) for i in ['овсяной', "гречневой", "гречневая"]]
    sixth_gr = [prep_pipeline.transform(i) for i in ['суп', 'обед']]
    seven_gr = [prep_pipeline.transform(i) for i in ['соус', 'майонез']]
    anchor_words = [first_gr, second_gr, third_gr, fourth_gr, fith_gr, sixth_gr, seven_gr]
    
    #fit model
    anchored_topic_model = ct.Corex(n_hidden=10, seed=2, max_iter=1000, eps=1e-3)
    anchored_topic_model.fit(features, words=vocabulary, anchors=anchor_words, anchor_strength=10)
    
    
    
    