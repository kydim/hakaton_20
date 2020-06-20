import pickle

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
    with open(os.path.join(src, 'prep_pipeline.pickle'), 'rb') as f:
        prep_pipeline = pickle.load(f)
    
    with open(os.path.join(src, 'feature_pipeline.pickle'), 'rb') as f:
        feature_pipline = pickle.load(f)
    
    with open(os.path.join(src, 'model.pickle'), 'rb') as f:
        model = pickle.load(f)
    
    return prep_pipeline, feature_pipline, model


if __name__ == "__main__":
    src = './pickle'
    prep_pipeline, feature_pipline, model = load_pipline_model(src)
    
    example_txt = ['М. Лесная\nНемного уставшие овощи, может, кому-то нужны \nЖду Вас']
    processed_txt = [prep_pipeline.transform(i) for i in example_txt]
    ex_features = feature_pipline.transform(processed_txt)
    
    predict = anchored_topic_model.predict_proba(ex_features)[0].argmax(1)
    # must be 'овощи, фрукты' or just 0
    print([(MAPPING.get(pr), t) for pr, t in zip(predict, example_txt)])