import pickle
import os
from model import utils_model
from sklearn.pipeline import Pipeline
import pymorphy2
import nltk
nltk.download("stopwords")
from nltk.stem import WordNetLemmatizer, SnowballStemmer

from nltk.corpus import stopwords

MAPPING = {
        0: 'овощи, фрукты',
        1: 'хлеб',
        2: None,
        3: 'чай, кофе, снеки',
        4: 'каши',
        5: 'обед',
        6: 'соус'
    }


def load_pipline_model(src):
    # with open(os.path.join(src, 'prep_pipeline.pickle'), 'rb') as f:
    #     prep_pipeline = pickle.load(f)

    morph = pymorphy2.MorphAnalyzer()
    prep_pipeline = Pipeline([
        ('lowercase', utils_model.Lowercaser()),
        ('remove_headers', utils_model.RegexTransformer(regex=r"[\w_-]*:.*")),
        ('remove_email', utils_model.RegexTransformer(
            regex=r"[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*")),
        ('remove_non_characters', utils_model.RegexTransformer("\W+", " ")),
        ('remove_stop_words', utils_model.StopWordsRemover(corpus=stopwords.words('russian'))),
        ('remove_digits', utils_model.RegexTransformer("[0-9_]", "")),
        ('lemmatization', utils_model.Lemmatizer(morph, stemmer=SnowballStemmer("russian")))
    ])
    prep_pipeline.fit('init')

    with open(os.path.join(src, 'feature_pipeline.pickle'), 'rb') as f:
        feature_pipline = pickle.load(f)
    
    with open(os.path.join(src, 'model.pickle'), 'rb') as f:
        model = pickle.load(f)
    
    return prep_pipeline, feature_pipline, model


if __name__ == "__main__":
    src = './pickl_models'
    prep_pipeline, feature_pipline, model = load_pipline_model(src)
    
    example_txt = [
        'М. Лесная Немного уставшие овощи, может, кому-то нужны  Жду Вас',
        'Свекла поехала раздаваться на Я.Гашека 10/85 89112288018   Морковь забрали Огурцы 1-2',
        'nХлеб от пекарни #ПудХлеба#  Санкт-Петербург  Метро Удельная , ул. Гаврская  Для одного спасателя один набор ( батон и три маленьких кирпичика)  Правило недели соблюдаем.  Забирать сегодня до 00.30  Запись под постом, точный адрес дам в личку. #музыкальный инструмент #моллюск"',
        'Бронь для Натальи (в ЛС)  Отдам Странный Студенческий Наборчик в добрые руки. В наборе два соевых соуса (открыты), лимонный джем (тоже открывался), два запечатанных клюквенных мини-джемика и овермного химии из ролтонов и бигбонов - суповая основа (собственно сам бульон), сушёные овощи, соусы. Забирать сегодня. Местоположение - возле ДАС МГУ (ул. Шверника), м.Академическая.  #мск_фудшеринг #питание'
    ]
    processed_txt = [prep_pipeline.transform(i) for i in example_txt]
    ex_features = feature_pipline.transform(processed_txt)
    
    predict = model.predict_proba(ex_features)[0].argmax(1)
    # must be 'овощи, фрукты' or just 0
    res = [(MAPPING.get(pr), t) for pr, t in zip(predict, example_txt)]
    for i in res:
        print(f'category: {i[0]}, text: {i[1]}')