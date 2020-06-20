from sklearn.base import TransformerMixin
import re

class RegexTransformer(TransformerMixin):
    def __init__(self, regex, sub=''):
        self._regex = regex
        self._sub = sub
  
    def fit(self, X, y=None):
        return self
  
    def transform(self, X, y=None):
        return re.sub(self._regex, self._sub, X)

    
class Lowercaser(TransformerMixin):
    def fit(self, X, y=None):
        return self
  
    def transform(self, X):
        return X.lower()

class StopWordsRemover(TransformerMixin):
    def __init__(self, corpus):
        self.corpus = corpus
  
    def fit(self, X, y=None):
        return self
  
    def transform(self, X):
        return ' '.join([word for word in X.split() if word not in self.corpus])

class Lemmatizer(TransformerMixin):
    def __init__(self, lemmatizer, stemmer=None):
        self._lemmatizer = lemmatizer
        self._stemmer = stemmer
  
    def fit(self, X, y=None):
        return self
  
    def transform(self, X):
        text = ' '.join([self._lemmatizer.parse(word)[0].normal_form for word in X.split()])
        if self._stemmer is not None:
            text = ' '.join([self._stemmer.stem(word) for word in text.split()])
        return text
