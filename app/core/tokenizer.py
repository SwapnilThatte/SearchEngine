import string
import nltk
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords


# Ensure resources are downloaded
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('punkt_tab', quiet=True)

class Tokenizer:
    def __init__(self):
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))
        self.punctuation = set(string.punctuation)

    def process(self, text: str) -> list[str]:
        # 1. Lowercase
        text = text.lower()
        
        # 2. Tokenize (NLTK is smarter than split)
        tokens = nltk.word_tokenize(text)
        
        # 3. Filter & Stem
        valid_tokens = []
        for t in tokens:
            if t in self.punctuation or t in self.stop_words:
                continue
            if not t.isalnum(): # Remove pure punctuation/garbage
                continue
            valid_tokens.append(self.stemmer.stem(t))
            
        return valid_tokens