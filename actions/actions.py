# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


import pandas as pd
import numpy as np
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')
nltk.download('punkt')
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.svm import LinearSVC
from sklearn import metrics
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from joblib import dump, load
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import AllSlotsReset, SlotSet


def limpa_texto(df_texto):
    df_texto['nv_Texto'] = df_texto['Texto'].copy()
    df_texto['nv_Texto'] = df_texto['nv_Texto'].str.replace('[,.:;!?]+', ' ', regex=True).copy()
    df_texto['nv_Texto'] = df_texto['nv_Texto'].str.replace('[/<>()|\+\-\$%&#@\'\"]+', ' ', regex=True).copy()
    df_texto['nv_Texto'] = df_texto['nv_Texto'].str.replace('[0-9]+', '', regex=True)
    return df_texto    
   
   
class ActionClassificador(Action):

     def name(self) -> Text:
         return 'action_classificador'

     def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = pd.read_csv('./classificador/catalogo.csv',delimiter=';')
        df_classificador = df[['Classificação','Título','Link']].drop_duplicates().reset_index(drop=True).copy()
        classificador = load('./classificador/classificador.joblib')  
        
        msg = (tracker.latest_message)['text']
        Texto = [{'Texto': msg}]
        #print(Texto)
        str_result = 'Nenhum dado relevante informado'

        if not msg == '':
            df_texto = pd.DataFrame(Texto)
            df_texto = limpa_texto(df_texto)
            
            classifica = classificador.predict(df_texto['nv_Texto'])[0]
            titulo = df_classificador.query('Classificação == @classifica')['Título'].values[0]
            link = df_classificador.query('Classificação == @classifica')['Link'].values[0]
            str_result = 'Título: ' + titulo + ', no link: ' + link

        dispatcher.utter_message(str_result)

        return []
