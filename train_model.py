import pickle
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

# Sample Training Data (Mee dataset ki thagattu change cheskovachu)
data = {
    'text': [
        'High revenue steady growth profit',
        'Loss due to heavy operational expenses',
        'Confidential financial report refund details',
        'Standard non-confidential daily summary profit',
        'Negative return unexpected loss statement'
    ],
    'label': ['Profit', 'Loss', 'Confidential', 'Profit', 'Loss']
}

df = pd.DataFrame(data)

# Vectorization & Model Training
vectorizer = CountVectorizer()
X = vectorizer.fit_transform(df['text'])
y = df['label']

model = MultinomialNB()
model.fit(X, y)

# Save Model and Vectorizer (.pkl files)
with open('model.pkl', 'wb') as f:
    pickle.dump(model, f)

with open('vectorizer.pkl', 'wb') as f:
    pickle.dump(vectorizer, f)

print("Model and Vectorizer successfully saved!")