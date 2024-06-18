from transformers import pipeline
from typing import List, Dict

def adv_extract(text, keyword):
    # nlp = spacy.load('en_core_web_sm')

    # # Preprocess the text data
    # doc = nlp(text)

    # # Named Entity Recognition (NER)
    # entities = [(entity.text, entity.label_) for entity in doc.ents]

    question_answering = pipeline("question-answering")
    answers = question_answering({
        'question': f'What is the {keyword}?',
        'context': text
    })
    return answers