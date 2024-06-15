import nltk
import spacy
from transformers import pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict

nlp = spacy.load('en_core_web_sm')
sentencizer = nltk.data.load('tokenizers/punkt/english.pickle')

# Load the text data
text = "Mount Everest, also known as Sagarmatha in Nepal, is the highest mountain in the world. It stands at an elevation of 8,848.86 meters (29,031.7 feet) above sea level. Many climbers attempt to reach its summit, facing extreme conditions and challenges."

# Define the keyword
keyword = "Sagarmatha"

# Preprocess the text data
doc = nlp(text)

# Named Entity Recognition (NER)
entities = [(entity.text, entity.label_) for entity in doc.ents]

# Part-of-Speech (POS) Tagging
pos_tags = [(token.text, token.pos_) for token in doc]

# Dependency Parsing
dependencies = [(token.text, token.dep_, token.head.text, token.head.pos_) for token in doc]

# Sentiment Analysis
sentiment_analysis = pipeline("sentiment-analysis")
sentiment = sentiment_analysis(text)

# Question Answering
question_answering = pipeline("question-answering")
answers = question_answering({
    'question': f'What is the {keyword}?',
    'context': text
})

# Extract relevant sentences
sentences = sentencizer.tokenize(text)

# Calculate the TF-IDF vector
vectorizer = TfidfVectorizer(max_features=5000)
tfidf = vectorizer.fit_transform(sentences)

# Calculate the cosine similarity between the keyword and the sentences
similarity = cosine_similarity(tfidf)

# Get the most similar sentences
most_similar_sentences = []
for i, sentence in enumerate(sentences):
    if sentence.lower().startswith(keyword.lower()):
        most_similar_sentences.append(sentence)

# Extract relevant information
relevant_info: List[Dict[str, str]] = []
for sentence in most_similar_sentences:
    entities_in_sentence = [(entity.text, entity.label_) for entity in nlp(sentence).ents]
    relevant_info.extend([{"entity": entity, "label": label} for entity, label in entities_in_sentence])

print("Relevant info:")
print(relevant_info)
print(answers)