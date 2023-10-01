import pandas as pd
import numpy as np
import ast
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle


def stem(text, ps = PorterStemmer()):
    y = []
    
    for i in text.split():
        y.append(ps.stem(i))
    
    return ' '.join(y)


def convert(obj):
    L = []
    for i in ast.literal_eval(obj):
        L.append(i.replace(' ', ''))
    return L


def load_from_csv_and_preprocess(csv_path):
    df = pd.read_csv(csv_path)
    df.rename(columns = {'index':'book_id'}, inplace = True)
    df.rename(columns = {'Title':'title'}, inplace = True)
    keys = list(df.keys())
    idx = [0, 1, 2, 3, 6, 9]

    filter_keys = [ keys[i] for i in idx ]
    df = df[filter_keys]

    
    df['authors'] = df['authors'].apply(convert)
    df['categories'] = df['categories'].apply(convert)
    df['description'] = df['description'].apply(lambda x: x.split())
    df['publisher'] = df['publisher'].apply(lambda x: [x.replace(' ', '')])
    # df['year'] = df['publishedDate'].apply(lambda x: [x.split('-')[0]])
    # df['ratingsCount'] = df['ratingsCount'].apply(lambda x: [str(x)])
    
    
    df['tags'] = df['description'] + df['authors'] + df['publisher'] + df['categories']
    
    books = df[['book_id', 'title', 'tags']]
    books['tags'] = books['tags'].apply(lambda x: ' '.join(x))
    books['tags'] = books['tags'].apply(lambda x: x.lower())
    
    ps = PorterStemmer()
    books['tags'] = books['tags'].apply(lambda x: stem(x, ps))
    return books
    
    
    
def calculate_distance_vectors(books_df, max_words):
    print('Calculating Distance Vectors. . .')
    cv = CountVectorizer(max_features=max_words, stop_words='english')

    book_vectors = cv.fit_transform(books_df['tags']).toarray()
    distance_vectors = cosine_similarity(book_vectors)
    print('Distance Vectors Generated')
    return distance_vectors.astype(np.float16)
    
    
def recommend(book_index, distance_vectors, num_to_recommend=5):
    distances = distance_vectors[book_index]
    book_list = sorted(list(zip(books['book_id'], distances)), reverse=True, key=lambda x: x[1])[1:num_to_recommend+1]
    
    book_index = [ x[0] for x in book_list ]
    return book_index



def add_book(book_dict, book_df, save_paths, max_words):
    print('Adding new book. . .')
    book_dict['description'] = book_dict['description'].split()
    book_dict['authors'] = [x.replace(' ', '') for x in book_dict['authors']]
    book_dict['categories'] = [book_dict['categories'].replace(' ', '')]
    book_dict['publisher'] = [book_dict['publisher'].replace(' ', '')]
    
    tags  = book_dict['description'] + book_dict['authors'] + book_dict['publisher'] + book_dict['categories']
    tags = ' '.join(tags)
    tags = tags.lower()
    tags = stem(tags)

    new_dict = {
        'book_id': [book_dict['book_id']],
        'title': [book_dict['title']],
        'tags': [tags]
    }
    
    new_book_df = pd.DataFrame(new_dict)
    books = pd.concat([book_df, new_book_df]).reset_index(drop=True)
    distance_vectors = calculate_distance_vectors(books, max_words)
    save_pickle(books, save_paths[0])
    save_pickle(distance_vectors, save_paths[1])
    return books, distance_vectors


def save_pickle(obj, f_path):
    with open(f_path, 'wb') as handle:
        pickle.dump(obj, handle)
    print('Object saved as pickle')
    

def load_pickle(f_path):
    with open(f_path, 'rb') as handle:
        obj = pickle.load(handle)
    print('Object loaded from pickle.')
    return obj


if __name__ == '__main__':
    books_path = './preprocessed_books_dataframe.pickle'
    dist_vec_path = './distance_vectors.pickle'
    max_words = 8000
    # =======================================================
    # Import from csv file, preprocess and save as pickle (only once)
    # =======================================================
    csv_path = './books.csv'
    books = load_from_csv_and_preprocess(csv_path)
    save_pickle(books, 'preprocessed_books_dataframe.pickle')

    
    # =======================================================
    # Calculate distance vectors and save as pickle (only once)
    # =======================================================
    distance_vectors = calculate_distance_vectors(books_df=books, max_words=max_words)
    save_pickle(distance_vectors, 'distance_vectors.pickle')
    
    # =======================================================
    # Loading pickle files (both needed)
    # =======================================================
    books = load_pickle(books_path)
    print(books.shape)
    distance_vectors = load_pickle(dist_vec_path)
    print(distance_vectors.shape)
    
    
    # =======================================================
    # Adding a new book
    # =======================================================
    book_dict = {
        'book_id' : 200001,
        'title': 'Deep Learning With Python',
        'description': 'This is a book about deep learning using the Tensorflow library and Keras API.',
        'authors' : ['Francois Chollet'],
        'categories': 'Self-Help',
        'publisher': 'Manning Publications',
    }
    books, distance_vectors = add_book(book_dict, books, save_paths=[books_path, dist_vec_path], max_words=max_words)
    
    
    book_dict = {
        'book_id' : 200002,
        'title': 'Deep Learning for Vision Systems',
        'description': 'This is a very good book about deep learning for Computer vision tasks using the Tensorflow library and Keras API.',
        'authors' : ['Mohamed Elgendy'],
        'categories': 'Self-Help',
        'publisher': 'Manning Publications',
    }
    books, distance_vectors = add_book(book_dict, books, save_paths=[books_path, dist_vec_path], max_words=max_words)
    
    # exit()
    book_title = 'Deep Learning With Python'
    index = books[ books['title'] == book_title ].index[0]


    idx = recommend(index, distance_vectors, 10)

    # printing book title from book_id / book_index
    for i in idx:
        print(books[books['book_id'] == i].values[0][1])

