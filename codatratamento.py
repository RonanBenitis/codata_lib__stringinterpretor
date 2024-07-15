from datetime import datetime
import numpy
import pandas as pd
import unidecode
from fuzzywuzzy import fuzz
import json

# ATUALIZE A DATA COM A DATA DE ENVIO DO ARQUIVO
data_modificacao = datetime.now().date()

class CodaTratamento:
    # >>>>>>>>>>>>>>>>>==================<<<<<<<<<<<<<<<<<<<<<
    # >>>>>>>>>>>>>>>>>    CONSTRUTOR    <<<<<<<<<<<<<<<<<<<<<
    # >>>>>>>>>>>>>>>>>==================<<<<<<<<<<<<<<<<<<<<<
    def __init__ (self):
        self.dict_modelo = self._load_modelo_dict()
        self.dict_intepretado = self._load_interpretado_dict()
        self.log_dicio_interpret = {}
        self._bkp_interpretado_dict(self.dict_intepretado)

        print(f'\nData de atualização inserida: >>>>>>>>>>> \u001b[32;1m{data_modificacao}\u001b[0m <<<<<<<<<<<')
        print("\u001b[32;1mLembre-se de conferir se todos os bairros estão com coordenadas\u001b[0m\n")
    
    # >>>>>>>>>>>>>>>>>=========================<<<<<<<<<<<<<<<<<<<<<
    # >>>>>>>>>>>>>>>>>    MÉTODOS DO OBJETO    <<<<<<<<<<<<<<<<<<<<<
    # >>>>>>>>>>>>>>>>>=========================<<<<<<<<<<<<<<<<<<<<<
    def trata_nome_bairro (self, serie):
        if self.dict_intepretado == None:
            print("ERRO: SEM DICIONARIO INTERPRETADO! Dicionario a ser interpretado não encontrado no estanciamento desta Classe.")
            return
        serie = serie.apply(lambda x: str(x))
        serie = serie.apply(CodaTratamento.trata_e_invert_tipo_logra)
        serie = serie.apply(CodaTratamento.strip_e_maiusculo_sem_acento)  
        serie = serie.apply(lambda x : CodaTratamento.busca_e_atualiza_dict(x, 
                                                                         self.dict_modelo, 
                                                                         self.dict_intepretado, 
                                                                         self.log_dicio_interpret))
        self._update_interpretado_dict()
        print(f"\u001b[32;1m*** Processo finalizado! ***\u001b[0m")
        return serie

    def _get_dict_interpretado(self):
        return self.dict_intepretado
    
    def _load_modelo_dict(self):
        # Carrega dicionario bairro_tratado
        with open ("settings/bairros_tratado.json", "r", encoding='utf8') as f: 
            bairro_tratado_dict = json.load(f)
            return bairro_tratado_dict
        
    def _load_interpretado_dict(self):
        with open ("settings/bairros_corresp.json", "r", encoding='utf8') as f: 
            bairros_corresp_dict = json.load(f)
            return bairros_corresp_dict
        
    def _bkp_interpretado_dict(self, dict_bairros_corresp):
        template_bkp = 'settings/dict_bkp/bairros_corresp_bkp_{}.json'

        # Backup versão inicial dictInterpretado
        with open(template_bkp.format(data_modificacao), 'w', encoding='utf8') as file: 
            json.dump(dict_bairros_corresp, file, ensure_ascii=False)

    def _update_interpretado_dict(self):
        # Salva versão atualizada dictInterpretado
        with open('settings/bairros_corresp.json', 'w', encoding='utf8') as file: 
            json.dump(self._get_dict_interpretado(), file, ensure_ascii=False)
            
    # >>>>>>>>>>>>>>>>>=========================<<<<<<<<<<<<<<<<<<<<<
    # >>>>>>>>>>>>>>>>>    MÉTODOS DA CLASSE    <<<<<<<<<<<<<<<<<<<<<
    # >>>>>>>>>>>>>>>>>=========================<<<<<<<<<<<<<<<<<<<<<
    @staticmethod
    def strip_e_maiusculo_sem_acento (x):
        x = x.strip()
        return unidecode.unidecode(x.upper())
    
    @staticmethod 
    def df_to_excel(data_frame, nome_arquivo_origem):
        print("----- Transformando DBF em EXCEL para a pasta output, aguarde! -----")
        data_frame.to_excel(nome_arquivo_origem + '.xlsx', index=False)
        print("----- Transformação realizada! -----")
    
    @staticmethod
    def get_list_key_or_value(dicionario, indice_keys_or_values):
        Keys_or_values = ( ("CHAVES", list(dicionario.keys())), ("VALORES", list(dicionario.values())) )
        iKV = indice_keys_or_values # >>> 0 para buscar CHAVES >>> 1 para buscar VALORES

        print(f" >>>>>> Lista de {Keys_or_values[iKV][0]} do Dicionario Modelo")
        lista_keys_or_values = Keys_or_values[iKV][1]
        for i, valor in enumerate(lista_keys_or_values):
            print(f"\u001b[32;1m[{i}]\u001b[0m - {valor}")
        indice_escolhido = int(input(">>>> Insira o indice desejado para atribuir como valor: "))

        while indice_escolhido < 0 or indice_escolhido >= len(lista_keys_or_values):
            indice_escolhido = int(input(f">>>> Indice {indice_escolhido} não encontrado, digite um indice valido: "))

        valor = lista_keys_or_values[indice_escolhido]
        return valor
    
    @staticmethod
    def busca_e_atualiza_dict(x, dicionario_modelo, dict_intepretado, log):
            if dict_intepretado.get(x) != None:
                return dict_intepretado.get(x)
            elif dicionario_modelo.get(x) != None:
                return dicionario_modelo.get(x)
            elif x in dicionario_modelo.values():
                return x
            elif x is numpy.nan or x is None or str(x).upper() == 'NAN':
                return {'': ''}
            else:
                print(f"\n\u001b[31;1m>>>> BAIRRO_WARNING_01\u001b[0m VALOR \u001b[31;1m'{x}'\u001b[0m FORA DO DICIONARIO INTERPRETADO!")
                
                matches = {}
                for dict in [dict_intepretado.items(), dicionario_modelo.items()]:
                    for chave, valor in dict:
                        matches[chave] = {'valor': valor, 'proximidade': fuzz.ratio(x, chave)}

                best_match_key = max(matches, key=lambda k: matches[k]['proximidade'])
                best_match_value = matches[best_match_key]['valor']
                best_match_prox = matches[best_match_key]['proximidade']
                
                print(f"  >> Chave mais proximo nos dicionarios: '{best_match_key}' | Proximidade: {best_match_prox} | Valor desta chave: '{best_match_value}'")
                resp = str(input("\u001b[32;1mPergunta:\u001b[0m A comparação está correta?\n   >>> s/n: "))

                if resp == "s":
                    print(f"\u001b[32;1m>>> Adicionado no Dicionario Interpretado! Chave: {x} | Valor: {best_match_value}\u001b[0m")
                else:
                    best_match_value = CodaTratamento.getListKeyOrValue(dicionario_modelo, 1)
                    print(f"\n\u001b[32;1m>>> Adicionado no Dicionario Interpretado: Chave {x} | Valor: {best_match_value}\u001b[0m")

                dict_intepretado[x] = best_match_value
                log[x] = best_match_value
                with open('log_cdt_interpret.json', 'w', encoding='utf8') as f: json.dump(log, f, ensure_ascii=False)

                return best_match_value
                
    @staticmethod
    def trata_e_invert_tipo_logra(x):
        tipoLog_to_bairroApi = {
            "PQ": "PQ. ",
            "JD": "JD. ",
            "VL": "VL. ",
            "AV": "AV. ",
            "R": "R. ",
            "TRV": "TRV. ",
            "PR": "PR. ",
            "ROD": "ROD. ",
            "RES": "RES. ",
            "COND": "COND. ",
            "EST": "EST. ",
            "BL": "BL. ",
            "QD": "QD. ",
            "LT": "LT. ",
            "CJ": "CJ. ",
            "KM": "KM. ",
            "Bº" : "", 
            }
        
        if "," in x:
            bairro = x.split(",")
            bairro[1] = bairro[1].strip().replace(".","")
            tipoBairro = tipoLog_to_bairroApi.get(bairro[1], bairro[1])
            bairro = f"{tipoBairro}{bairro[0]}"
            return bairro
        else:
            return x
