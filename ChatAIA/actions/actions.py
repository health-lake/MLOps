# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import AllSlotsReset, SlotSet
import pandas as pd
import random
from datetime import datetime, timedelta

def gen_datetime(min_year=1900, max_year=datetime.now().year):
    start = datetime.now() + timedelta(days=1)
    end = start + timedelta(days=7)
    resultado = start + (end - start) * random.random()
    resultado = resultado.replace(hour=8 + random.randrange(10), minute=0, second=0, microsecond=0)
    return resultado.strftime("%d/%m/%Y %H:%M")

def geraListaDatas(tam):
  datas = []
  for i in range(tam):
    datas.append(gen_datetime())
  return sorted(list(set(datas)))

def tratarCPF(cpf):
  cpfTratado = "".join(c for c in cpf if c.isdigit()).zfill(11)
  return '{}.{}.{}-{}'.format(cpfTratado[:3], cpfTratado[3:6], cpfTratado[6:9], cpfTratado[9:])  

def CarregarDados():
    dados = pd.read_csv("./Agendamentos.csv", index_col=0)
    return dados

def SalvarDados(dados):
    dados.to_csv("./Agendamentos.csv")    

def InserirAgendamento(dados, Data, Nome, Cpf, Convenio):
    return dados.append(pd.DataFrame([[Data, Nome, Cpf, Convenio]], columns=dados.columns), ignore_index=True)
    
def ConsultarAgendamento(dados, Cpf):
    return dados.query("CPF == '{0}'".format(Cpf))

def RemoverAgendamento(dados, Cpf):
    return dados.query("CPF != '{0}'".format(Cpf))

class ActionInformarDataAgendamento(Action):

     def name(self) -> Text:
         return "action_informa_data_agendamento"

     def criaBotao(self, variavel, valor):
        payload = "data de agendamento "+valor
        btn = { "type": "postback",
                "title": "{}".format(valor),
                "payload": payload}
        return btn

     def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        botoes = []
        
        for data in geraListaDatas(10):
            botoes.append(self.criaBotao("dataAgendamento", data))
        
        dispatcher.utter_button_message("Por favor escolha a data que melhor lhe atenderá dentre as disponíveis:", botoes)

        return []

class ActionInserirAgendamento(Action):

     def name(self) -> Text:
         return "action_inserir_agendamento"

     def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        varNome = tracker.get_slot("nomeCompleto")
        varCpf = tracker.get_slot("cpf")
        varCpf = tratarCPF(varCpf)
        varConvenio = tracker.get_slot("convenio")
        varDataAgendamento = tracker.get_slot("dataAgendamento")

        dados = CarregarDados()

        consulta = ConsultarAgendamento(dados, varCpf)
        mensagem = ""

        if consulta.empty:
            dados = InserirAgendamento(dados, varDataAgendamento, varNome, varCpf, varConvenio)
            SalvarDados(dados)

            mensagem = "Seu agendamento foi efetuado com sucesso:\n * NOME: {0} \n * CONVENIO: {1} \n * CPF: {2} \n * DATA DA COLETA: {3}"\
                .format(varNome, varConvenio, varCpf, varDataAgendamento)
        else:
            mensagem = "Desculpe mas não foi possível realizar seu agendamento, pois já existe um agendamento vigente para este cpf."
        
        dispatcher.utter_message(mensagem)

        nome = tracker.get_slot('nome')
        return [AllSlotsReset(), SlotSet("nome", nome)]        

class ActionConsultarAgendamento(Action):

     def name(self) -> Text:
         return "action_consultar_agendamento"

     def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        varCpf = tracker.get_slot("cpf")
        varCpf = tratarCPF(varCpf)

        dados = CarregarDados()
        dados = ConsultarAgendamento(dados, varCpf)
        mensagem = "nenhum agendamento encontrado para o cpf {0}".format(varCpf)
        if not dados.empty:
            mensagem = "Estes foram os agendamentos que encontrei para este cpf:\n\n"
            for r in dados.values:
                mensagem += "* Data do Agendamento: {0} \n * Nome: {1} \n * CPF: {2} \n * Convenio: {3}".format(*r)
                mensagem += "\n\n"
        dispatcher.utter_message(mensagem)

        nome = tracker.get_slot('nome')
        return [AllSlotsReset(), SlotSet("nome", nome)]