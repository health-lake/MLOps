import pandas as pd
from joblib import load
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

import requests

from random import randint

def limpa_texto(df_texto):
    df_texto['nv_Texto'] = df_texto['Texto'].copy()
    df_texto['nv_Texto'] = df_texto['nv_Texto'].str.replace('[,.:;!?]+', ' ', regex=True).copy()
    df_texto['nv_Texto'] = df_texto['nv_Texto'].str.replace('[/<>()|\+\-\$%&#@\'\"]+', ' ', regex=True).copy()
    df_texto['nv_Texto'] = df_texto['nv_Texto'].str.replace('[0-9]+', '', regex=True)
    return df_texto    
   
class ActionClassificador(Action):

    def name(self) -> Text:
        return 'action_classificador'

    def run(self, dispatcher, tracker, domain):
            
        df = pd.read_csv("/bot/actions/catalogo.csv",delimiter=";")
        df_classificador = df[['Classificação','Título','Link']].drop_duplicates().reset_index(drop=True).copy()
        classificador = load('/bot/actions/classificador.joblib')  

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
