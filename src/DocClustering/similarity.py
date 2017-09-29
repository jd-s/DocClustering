import nltk, string
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from DocClustering.pubmed import *
from DocClustering.mesh import *
from sklearn.decomposition import PCA
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
from scipy import sparse

class similarity:

    def sim_Mesh2 (self, edge):
        terms1 = self.docList[edge["Source"]].terms
        terms2 = self.docList[edge["Dest"]].terms
        paths1 = []
        paths2 = []
        for term in terms1:
            paths1.extend (self.m.getTrees[term])
        paths1.sort(key=lambda s: len(s))
        for term in terms2:
            paths2.extend (self.m.getTrees[term])
        paths2.sort(key=lambda s: len(s))
        #paths1New = paths1
        #for term in paths1:
        #    paths1New = [x for x in paths1New if not x.startswith(term)]
        #paths2New = paths2
        #for term in paths2:
        #    paths2New = [x for x in paths2New if not x.startswith(term)]




    def sim_Mesh(self, edge):
        terms1 = []
        terms2 = []
        #print (edge["Source"] + " - "+ edge["Dest"])
        if not edge["Source"] in  self.docList:
            for doc in self.docList:
                if doc.id == edge["Source"] or  doc.id == int(edge["Source"]) or doc.id == str(edge["Source"]):
                    terms1 = doc.terms
                if doc.id == edge["Dest"] or  doc.id == int(edge["Dest"]) or doc.id == str(edge["Dest"]):
                    terms2 = doc.terms
        else:
            terms1 = self.docList[edge["Source"]].terms
            terms2 = self.docList[edge["Dest"]].terms
        union=[]
        for term in terms1:
            if term not in terms2:
                union.append (term)
        for term in terms2:
            if term not in union:
                union.append(term)
        #print(terms1)
        #print(terms2)
        #print(both)

        intersection = [common_item for common_item in terms1 if common_item in terms2]

        #union = len( both)
        if len(union) == 0:
            #print(" Union 0 " + str(len(intersection)))
            return 0.0
        else:
            return float(  len(intersection) /  len(union))

    def sim_givenPlusMesh(self, edge):
        return (float(edge["Label"]) + similarity.sim_Mesh(self,edge)) /2


    def stem_tokens(tokens):
        stemmer = nltk.stem.porter.PorterStemmer()
        return [stemmer.stem(item) for item in tokens]

    def normalize(text):
        remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)
        return similarity.stem_tokens(nltk.word_tokenize(text.lower().translate(remove_punctuation_map)))

    def sim_text_with_journal(self, edge):
        #nltk.download('punkt')

        heading1 = self.docList[edge["Source"]].title +". "+ self.docList[edge["Source"]].fulltext
        heading2 = self.docList[edge["Dest"]].title +". "+ self.docList[edge["Dest"]].fulltext

        english_stops = set(stopwords.words('english'))
        # term frequency–inverse document frequency
        vectorizer =  TfidfVectorizer(tokenizer=similarity.normalize, stop_words='english')
        tfidf = vectorizer.fit_transform([heading1, heading2])
        sim = ((tfidf * tfidf.T).A)[0,1]

        if self.docList[edge["Source"]].journal == self.docList[edge["Dest"]].journal:
            sim2 = 1
        else:
            sim2 = 0

        simg = float(sim+sim2)/2

        return simg*100

    def sim_journal(self, edge):
        if self.docList[edge["Source"]].journal == self.docList[edge["Dest"]].journal:
            sim2 = 1
        else:
            sim2 = 0
        return sim2*100

    def sim_text(self, edge):
        #nltk.download('punkt')

        heading1 = self.docList[edge["Source"]].title +". "+ self.docList[edge["Source"]].fulltext
        heading2 = self.docList[edge["Dest"]].title +". "+ self.docList[edge["Dest"]].fulltext

        english_stops = set(stopwords.words('english'))

        vectorizer =  TfidfVectorizer(tokenizer=similarity.normalize, stop_words='english')
        tfidf = vectorizer.fit_transform([heading1, heading2])
        sim = ((tfidf * tfidf.T).A)[0,1]
        print(str(sim))
        return sim*100

    def sim_textPca(self, edge):
        #nltk.download('punkt')

        heading1 = self.docList[edge["Source"]].title +". "+ self.docList[edge["Source"]].fulltext
        heading2 = self.docList[edge["Dest"]].title +". "+ self.docList[edge["Dest"]].fulltext

        english_stops = set(stopwords.words('english'))


        vectorizer =  TfidfVectorizer(tokenizer=similarity.normalize, stop_words='english', max_features=1000)
        tfidf = vectorizer.fit_transform([heading1, heading2])

        # create and apply PCA transform
        #pca = PCA(n_components=2)
        #principal_components = pca.fit_transform(tfidf)
        #tfidf = lsa.fit_transform(tfidf)
        tfidfd = tfidf.todense()

        # ----------------------------------------------------------------------------------------------------------------------
        pca_num_components=20
        reduced_data = PCA(n_components=pca_num_components).fit_transform(tfidfd)
        #print (type(tfidf))
        #print(type(reduced_data))
        tfidf2 = sparse.csr_matrix(reduced_data)
        #print(type(tfidf2))
        sim = abs((tfidf2 * tfidf2.T).A)[0, 1]
        #print (str(sim))
        return sim*100

    def sim_given(self, edge):
        return float(edge["Label"])