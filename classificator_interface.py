import pandas as pd
from transformers import BertTokenizer, BertForSequenceClassification
import torch


class QuestionClassifier:
    def __init__(self):
        self.df = pd.read_csv('data/context.csv')
        self.label2id = {label: idx for idx, label in enumerate(self.df['context'].unique())}
        self.id2label = {idx: label for label, idx in self.label2id.items()}
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=len(self.label2id))
        self.model.load_state_dict(torch.load("data/classify_model.pt", map_location=torch.device('cpu')))
        self.model.eval()
        print("Classifier is ready")

    def classify_question(self, question):
        inputs = self.tokenizer(question, return_tensors='pt', truncation=True, padding=True)
        inputs = {key: val.to(self.model.device) for key, val in inputs.items()}
        with torch.no_grad():
            outputs = self.model(**inputs)
        logits = outputs.logits
        pred = torch.argmax(logits, dim=-1).cpu().numpy()[0]
        return self.id2label[pred]