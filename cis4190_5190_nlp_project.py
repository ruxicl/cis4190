# -*- coding: utf-8 -*-
"""CIS4190/5190_NLP_Project.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1xO1cpjayqhzjjHhM6GkWakibvpWUuatn
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import torch
import nltk
import os

!pip install --upgrade --no-cache-dir gdown
if not os.path.exists("Reviews.csv"):
    !gdown 1_kLSwiRYtiXF7h9V1FlTqTapOHiYU5Mk

if not os.path.exists("glove.840B.300d.txt"):
  !wget https://huggingface.co/stanfordnlp/glove/resolve/main/glove.840B.300d.zip
  !unzip glove.840B.300d.zip

# Remeber to change the path here for the corresponding files you need
df = pd.read_csv('Reviews.csv')
print(df.shape)
df_subset = df.head(1000)
print(df_subset.shape)

df_subset.head()

df['Score'].value_counts().sort_index().plot(kind='bar',
                                             title='Reviews Count',
                                             figsize=(12,8)).set_xlabel('Stars')

#NLTK
nltk.download('vader_lexicon')
from nltk.sentiment import SentimentIntensityAnalyzer
from tqdm.notebook import tqdm
from sklearn.model_selection import train_test_split

sample_df = df.sample(frac=0.1, random_state=1)

X = sample_df[sample_df.columns.drop(['Score'])]
y = sample_df['Score']

# NLTK’s Pre-Trained Sentiment Analyzer
sia = SentimentIntensityAnalyzer()
res = {}
for i, row in tqdm(sample_df.iterrows(), total=len(sample_df)):
    text = row['Text']
    myid = row['Id']
    res[myid] = sia.polarity_scores(text)

data = []
for rows in res:
  data.append( round( ((res[rows]['compound']+1))*2.5, 0) )

y_pred = pd.DataFrame(data)

# accuracy = np.mean(y == y_pred)

y

y_pred

# To be finished - do not include in Milestone 2
# Logistic regression with TF-IDF
# Binary classification - positive/ negative sentiments

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

# Preprocessing

# remove all 3-star ratings
new_df = df[df.Score != 3]

# add new column for label - use convention: positive sentiments = 1, negative sentiments = 0

print(new_df.columns)
new_df['Sentiment'] = 1

new_df.loc[df.Score <= 2, 'Sentiment'] = 0

X = new_df[new_df.columns.drop(['Sentiment', 'Score'])]
y = new_df['Sentiment']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.33, random_state = 42)

text = np.array(new_df.Text)


# TF-IDF
# Tf-idf(w, d)= BoW(w, d) * log(# of reviews / # of reviews containing the word w)
#  where BoW(w, d) = # of times word w appears in review d
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(text)

print(X.shape)
print(vectorizer.get_feature_names_out())

# Logistic regression
# to do: tune the params
log_regression = LogisticRegression()
log_regression.fit(X_train, y_train)
y_predict = log_regression.predict(X_test)

accuracy = np.sum(np.array(y_test) == np.array(y_predict))

print(accuracy)

# Baseline 1: logistic regression with TF-IDF
# Multiclass classfication - predict a score 1 - 5

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score

dataset_shift_on = True

# For dataset shift, we will train the model on 4, 5 - star reviews and we will evaluate it on 1, 2 - star reviews
if dataset_shift_on:
  shifted_train_df = df.loc[df['Score'].isin([4, 5])]
  shifted_test_df = df.loc[df['Score'].isin([1, 2])]

  X_train = shifted_train_df['Text']
  y_train = shifted_train_df['Score']

  X_test = shifted_test_df['Text']
  y_test = shifted_test_df['Score']
else:
  # select features and the label
  X = df['Text']
  y = df['Score']

  # train - test split (maybe add validation too)
  X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.33, random_state = 42)


# TF-IDF
# Tf-idf(w, d)= BoW(w, d) * log(# of reviews / # of reviews containing the word w)
#  where BoW(w, d) = # of times word w appears in review d

# to do - tune params (esp. ngram_range, lowercase, max_features)
# try ngram_range=(1, 2)
transformer = TfidfVectorizer(stop_words='english', lowercase=True, max_features=150000)
X_train_tf_idf = transformer.fit_transform(X_train)
X_test_tf_idf = transformer.transform(X_test)

# Logistic regression
# to do: tune the params (esp. - suggestion: C=5e1, n_jobs = 4, random_state)
log_regression = LogisticRegression( solver='lbfgs', multi_class='multinomial')
log_regression.fit(X_train_tf_idf, y_train)
y_predict_baseline1 = log_regression.predict(X_test_tf_idf)


f1 = f1_score(y_test, y_predict_baseline1, average='weighted')
# f-1 scores
if dataset_shift_on:
  print("F1 score obtained with dataset shift on: ")
else:
  print("F1 score obtained with random split train-test (no dataset shift)")
print(f1)

# Test cell - do not include in Milestone 2

print(transformer.get_feature_names_out()[-50:])
print(y_test.shape)
# print(y_test.shape, y_predict_baseline1.shape)

# f-1 scores
print(f1)

print(len(X_test))

# Baseline 2: Random prediction
y_predict_baseline2 = np.random.randint(low = 1, high = 6, size = len(X_test))

# Baseline 3: Constant prediction
y_predict_baseline3 = np.full(len(X_test), fill_value = 5)

# Glove https://medium.com/analytics-vidhya/basics-of-using-pre-trained-glove-vectors-in-python-d38905f356db
embeddings_dict = {}
with open("/content/glove.840B.300d.txt", 'r') as f:
    for line in f:
        values = line.split()
        word = values[0]
        try:
          vector = np.asarray(values[1:], "float32")
          embeddings_dict[word] = vector
        except:
          print(values[1:])

embeddings_dict[","].shape