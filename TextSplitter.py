import re
from collections import Counter
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag


class TextReader:
    def __init__(self, path):
        self.path = path

    def read_and_separate_sentences(self):
        with open(self.path, 'r', encoding='utf-8') as file:
            content = file.read()
            # Using regex to split the content by the specified punctuation marks
            sentences = re.split(r'(?<=[.,!?;:])\s+', content)
            # Filter sentences that don't contain at least one word character
            sentences = [sentence for sentence in sentences if re.search(r'\w', sentence)]
        return sentences

    def most_relevant_word(self):
        sentences = self.read_and_separate_sentences()
        relevant_words = []
        for sentence in sentences:
            # List of stopwords
            stop_words = set(stopwords.words('english'))
            # Tokenize the sentence
            words = word_tokenize(sentence)
            # Remove stopwords and non-alphabetic words
            filtered_words = [word for word in words if word.lower() not in stop_words and word.isalpha()]
            # Part-of-speech tagging
            tagged_words = pos_tag(filtered_words)
            # Find the most relevant word that is not filtered
            unfiltered_word = max(words, key=lambda x: x[0])
            # Filter for nouns and verbs
            nouns_and_verbs = [word for word, pos in tagged_words if pos in ("NN", "VB", "VBG", "VBN", "VBP", "VBZ",
                                                                             "NNP", "NNS")]
            # Get the most frequent noun or verb
            word_freq = Counter(nouns_and_verbs)
            if word_freq:
                relevant_words.append(word_freq.most_common(1)[0][0])
            else:
                relevant_words.append(unfiltered_word)  # Return None if no relevant word is found
        return relevant_words
