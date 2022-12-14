

#**Importing Library and Data**
"""

import pandas as pd
import re
import matplotlib.pyplot as plt
import seaborn as sns

healthD = pd.read_csv('Secondary_Dataset.csv')

"""#**Data Summary**"""

healthD.info()
healthD.head()

"""#**Preliminary Text-Analysis**

##**Word Count**
"""

healthD['word_count'] = healthD['Text'].apply(lambda x: len(str(x).split(" ")))
healthD.head()

"""##**Character Count**"""

healthD['char_count'] = healthD['Text'].str.len()  # Includes the spaces
healthD.head(5)

"""#**Text Pre-Processing**

##**Transforming to lower case**
"""

healthD['Text'] = healthD['Text'].str.lower()
healthD.head()

"""##**Removing ID and regular expression using 're' library**"""

def remove_text_ids(Text):
  mention_removed_text = re.sub(r"(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", "", str(Text)) # remove any sequence of characters followed by '@' sign
  spaces_removed = re.sub(r"\s\s+", " ", str(mention_removed_text)) # remove multiple spaces
  return spaces_removed

healthD['Text'] = healthD['Text'].apply(remove_text_ids)
healthD.head()

"""##**Digits Removal**"""

def remove_digits(Text):
  return " ".join(w for w in Text.split() if not w.isdigit())

healthD['Text'] = healthD['Text'].apply(remove_digits)
healthD.head()

healthD.Text.sample(10)

"""##**Duplicate Removal**"""

duplicate_count = len(healthD['Text'])-len(healthD['Text'].drop_duplicates())
print('duplicate count:', duplicate_count)
print('total records before remove duplicates:', healthD.shape[0])

healthD = healthD.drop_duplicates(subset='Text', keep="first")
print('updated record count:', healthD.shape[0])

"""##**Remove Hyperlinks from "Text Column"**"""

import re
healthD['Text'] = healthD['Text'].apply(lambda x: re.split('https:\/\/.*', str(x))[0])

healthD.head()

"""##**Punctuations Removal**"""

healthD['Text'] = healthD['Text'].str.replace(r'[^\w\s]','') 
healthD.head()

"""##**Unique Language Identification**"""

healthD['Text'].unique()

"""##**Removing Stop Words**"""

#Remove stop words
# Load NLTK library
import nltk

# Download the stopwords to the nltk library
nltk.download('stopwords')

# Load the stopwords
from nltk.corpus import stopwords

# get the list of all stopwords from the library
stop = stopwords.words('english')
print(stop)
stop.remove('not')

print(stop)

# Remove the words in 'stop' list
def remove_stop_words(Text):
  tokens = Text.split()
  stop_removed_tokens = [t for t in tokens if t not in stop]
  convert_to_string = " ".join(stop_removed_tokens)
  return convert_to_string
  
healthD['Text'] = healthD['Text'].apply(remove_stop_words)
healthD.Text.sample(10)

"""#**Standarization of Text**

##**Stemming**
"""

from nltk.stem import PorterStemmer

stemmer = PorterStemmer()

def stemming_function(sent):
  word_list = sent.split()
  stemmed_word_list = [stemmer.stem(word) for word in word_list]
  stemmed_sentence = " ".join(stemmed_word_list)
  return stemmed_sentence

healthD['Text_stem'] = healthD['Text'].apply(stemming_function)

# Compare the content vs. stemmed content
healthD[['Text', 'Text_stem']].tail(10)

"""##**Lemmatization**"""

# Download wordnet
nltk.download('wordnet')

from nltk.stem import WordNetLemmatizer

lemmtizer = WordNetLemmatizer()

def lemmatize_function(sent):
  word_list = sent.split()
  lemma_word_list = [lemmtizer.lemmatize(word) for word in word_list]
  lemma_sentence = " ".join(lemma_word_list)
  return lemma_sentence

healthD['Text_lemmatized'] = healthD['Text'].apply(lemmatize_function)

"""**Comparison of Stemming and Lemmatize tweets**"""

healthD_standard=healthD[['Text', 'Text_stem', 'Text_lemmatized']]
healthD_standard.head(10)

"""#**Word Frequency Analysis**"""

# Create a word frequency series. (This is a pandas series)
word_frequency = pd.Series(' '.join(healthD['Text']).split()).value_counts()

word_frequency[:50]

word_count  = word_frequency
word_count = word_count[0:15,]
plt.figure(figsize=(10,10))
sns.barplot(word_count.index, word_count.values, alpha=0.8,color="blue")
plt.title('Tweets in top 15 words')
plt.ylabel('Number of Occurrences', fontsize=12)
plt.xlabel('Word', fontsize=12)
plt.show()

from PIL import Image
from wordcloud import WordCloud

corpus = list(healthD['Text'])

wordcloud = WordCloud(background_color='white', max_words=200, max_font_size=50, random_state=42).generate(str(corpus))

fig = plt.figure(1)
plt.imshow(wordcloud)
plt.axis('off')
plt.show()

"""#**Common Words Removal**"""

# Creating a list of custom stopwords
new_words_to_remove = ["food","health","foodie","amp","lol","swag","rt", "ytshorts",
                       "healthylifestyle", "healthyfood", "healthyeating", "healthyliving","know","via"]

# Remove common words
healthD['Text'] = healthD['Text'].apply(lambda x: " ".join(x for x in x.split() if x not in new_words_to_remove))
healthD.head(5)

"""Checking Updated Frequency List"""

word_frequency = pd.Series(' '.join(healthD['Text']).split()).value_counts()
word_frequency[:50]

word_frequency.to_csv('CommonWordsCloud.csv', index= True)

corpus = list(healthD['Text'])

wordcloud = WordCloud(background_color='white', max_words=200, max_font_size=50, random_state=42).generate(str(corpus))

fig = plt.figure(1)
plt.imshow(wordcloud)
plt.axis('off')
plt.show()

"""#**N-Grams: Tri-grams**"""

from sklearn.feature_extraction.text import CountVectorizer

# This function will generate most frequently occuring Tri-grams
def get_ngrams(corpus, ngram_range=(3, 3)):
    
    # Create CountVectorizer object from sklearn library with bigrams
    vec1 = CountVectorizer(ngram_range=ngram_range, max_features=2000).fit(corpus)

    # Create BoW feature representation using word frequency
    bag_of_words = vec1.transform(corpus)

    # compute sum of words
    sum_words = 3.sum(axis=0) 

    # create (word, frequency) tuples for bigrams
    words_freq = [(word, sum_words[0, idx]) for word, idx in vec1.vocabulary_.items()]
    words_freq =sorted(words_freq, key = lambda x: x[1], reverse=True)
    return words_freq

trigrams_healthD = get_ngrams(healthD['Text'].tolist(), ngram_range=(3, 3))

trigrams_healthD = pd.DataFrame(trigrams_healthD)
trigrams_healthD.columns=["Tri-gram", "Freq"]
trigrams_healthD.to_csv('trigrams_healthD.csv',index=False)

trigrams_healthD.head(5)

# Barplot of most freq Tri-grams
top_trigrams_to_show = 20

sns.set(rc={'figure.figsize':(13,8)})
h=sns.barplot(x="Tri-gram", y="Freq", data=trigrams_healthD[:top_trigrams_to_show])
h.set_xticklabels(h.get_xticklabels(), rotation=90)
plt.title('NLP - Trigram Analysis')
plt.show()

"""#**Sentiment Analysis**"""

from textblob import TextBlob
# function to calculate subjectivity
def getSubjectivity(review):
    return TextBlob(review).sentiment.subjectivity
    # function to calculate polarity
    def getPolarity(review):
        return TextBlob(review).sentiment.polarity

# function to analyze the reviews
def analysis(score):
    if score < 0:
        return 'Negative'
    elif score == 0:
        return 'Neutral'
    else:
        return 'Positive'

NLP_sentiment = pd.DataFrame(healthD[['Text_lemmatized', 'Datetime']])

NLP_sentiment['Sentiment_Score'] = NLP_sentiment['Text_lemmatized'].apply(lambda x: TextBlob(x).sentiment.polarity) 
NLP_sentiment['Analysis'] = NLP_sentiment['Sentiment_Score'].apply(analysis)
NLP_sentiment.head()
NLP_sentiment.to_csv("NLP_sentiment.csv")

"""**Count the number of positive, negative, neutral reviews**"""

#https://stackabuse.com/python-for-nlp-sentiment-analysis-with-scikit-learn/

sentiment_count = NLP_sentiment.Analysis.value_counts()
sentiment_count.to_csv("sentiment_count.csv")

sentiment_count.plot(kind='pie', autopct='%1.0f%%', colors=["lightgreen", "orange", "red"])

Sentiment_NLP = NLP_sentiment.groupby(['Datetime'])['Sentiment_Score'].mean()
Sentiment_NLP.tail(30)

# Plot twitter sentimet timeline 
Sentiment = Sentiment_NLP.plot()
plt.savefig('Sentiment_over_time_v2.png', dpi=500)

"""#**Topic Modelling**"""

!pip install pyLDAvis
import tempfile
import os
import logging
from gensim import corpora, models, similarities
from sklearn.feature_extraction.text import CountVectorizer
import pyLDAvis.gensim_models

# Setting up the environment for LDA algorithm.

TEMP_FOLDER = tempfile.gettempdir()
print('Folder "{}" will be used to save temporary dictionary and corpus.'.format(TEMP_FOLDER))
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# Convert the tweets as the text corpus.
corpus = list(healthD['Text'])

# Tokenization
healthD_text = [[word for word in str(document).split()] for document in corpus]

healthD_text[:5]

# Create a dictionary based on the tokanized words of all the tweets.
dictionary = corpora.Dictionary(healthD_text)

# Save the above dictionary as a local file for LDA model to access.
dictionary.save(os.path.join(TEMP_FOLDER, 'healthD_text.dict'))

print(healthD_text[0])
print('alphabetically sorted', sorted(healthD_text[0]))

print(healthD_text[1])
print('alphabetically sorted', sorted(healthD_text[1]))

# Print the dictionary
print(dictionary.token2id)

# Convert the text dictionary to bag of words model
corpus = [dictionary.doc2bow(text) for text in healthD_text]

text_id = 0
print(healthD_text[text_id]) # each tweet converted to tokens
print(dictionary.doc2bow(healthD_text[text_id])) # each token is represented as a id from a dictionary

"""##**Generate Topic Modelling**"""

# Construct TF-IDF features from the dictionary.
tfidf = models.TfidfModel(corpus)

# Transform the tweets as TF-IDF feature vectors
corpus_tfidf = tfidf[corpus]

total_topics = 40

lda = models.LdaModel(corpus, id2word=dictionary, num_topics=total_topics)
corpus_lda = lda[corpus_tfidf] # create a double wrapper over the original corpus: bow->tfidf->fold-in-lsi

# Print the Keyword in the 10 topics
lda.show_topics(total_topics, num_words=6)

"""##**Interactive Topic Analyzer**"""

pyLDAvis.enable_notebook()
panel = pyLDAvis.gensim_models.prepare(lda, corpus_lda, dictionary, mds='tsne')
panel
