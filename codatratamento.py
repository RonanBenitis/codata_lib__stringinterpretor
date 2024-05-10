import pandas as pd
import unidecode
from fuzzywuzzy import fuzz
import json

class codatratamento:
    # >>>>>>>>>>>>>>>>>==================<<<<<<<<<<<<<<<<<<<<<
    # >>>>>>>>>>>>>>>>>    CONSTRUTOR    <<<<<<<<<<<<<<<<<<<<<
    # >>>>>>>>>>>>>>>>>==================<<<<<<<<<<<<<<<<<<<<<
    def __init__ (self, dataFrame, dicionarioModelo, dicionarioInterpretado=None):
        self.dataFrame = dataFrame
        self.dicionarioModelo = dicionarioModelo
        self.dicionarioInterpretado = dicionarioInterpretado
        self.log_dicio_interpret = {}
    
    # >>>>>>>>>>>>>>>>>=========================<<<<<<<<<<<<<<<<<<<<<
    # >>>>>>>>>>>>>>>>>    MÉTODOS DO OBJETO    <<<<<<<<<<<<<<<<<<<<<
    # >>>>>>>>>>>>>>>>>=========================<<<<<<<<<<<<<<<<<<<<<
    def trataNomeBairro (self, colunaLeitura, colunaTratada):
        if self.dicionarioInterpretado == None:
            print("ERRO: SEM DICIONARIO INTERPRETADO! Dicionario a ser interpretado não encontrado no estanciamento desta Classe.")
            return
        self.dataFrame[colunaTratada] = self.dataFrame[colunaLeitura]
        
        self.dataFrame[colunaTratada] = self.dataFrame[colunaTratada].apply(lambda x: str(x))
        self.dataFrame[colunaTratada] = self.dataFrame[colunaTratada].apply(codatratamento.trataEInvertTipoLogra)
        self.dataFrame[colunaTratada] = self.dataFrame[colunaTratada].apply(codatratamento.stripEMaiusculoSemAcento)  
        self.dataFrame[colunaTratada] = self.dataFrame[colunaTratada].apply(lambda x : codatratamento.buscaEAtualizaDict(x, self.dicionarioModelo, self.dicionarioInterpretado, self.log_dicio_interpret))

        return self.dataFrame[colunaTratada]

    def getDicionarioInterpretado(self):
        return self.dicionarioInterpretado
    
    # >>>>>>>>>>>>>>>>>=========================<<<<<<<<<<<<<<<<<<<<<
    # >>>>>>>>>>>>>>>>>    MÉTODOS DA CLASSE    <<<<<<<<<<<<<<<<<<<<<
    # >>>>>>>>>>>>>>>>>=========================<<<<<<<<<<<<<<<<<<<<<
    @staticmethod
    def stripEMaiusculoSemAcento (x):
        x = x.strip()
        return unidecode.unidecode(x.upper())
    
    @staticmethod 
    def dfToExcel(dataFrame, nomeArquivoOrigem):
        print("----- Transformando DBF em EXCEL para a pasta output, aguarde! -----")
        dataFrame.to_excel(nomeArquivoOrigem + '.xlsx', index=False)
        print("----- Transformação realizada! -----")
    
    @staticmethod
    def getListKeyOrValue(dicionario, indiceKeysOrValues):
        KeysOrValues = ( ("CHAVES", list(dicionario.keys())), ("VALORES", list(dicionario.values())) )
        iKV = indiceKeysOrValues # >>> 0 para buscar CHAVES >>> 1 para buscar VALORES

        print(f" >>>>>> Lista de {KeysOrValues[iKV][0]} do Dicionario Modelo")
        listaKeysOrValues = KeysOrValues[iKV][1]
        for i, valor in enumerate(listaKeysOrValues):
            print(f"\u001b[32;1m[{i}]\u001b[0m - {valor}")
        indiceEscolhido = int(input(">>>> Insira o indice desejado para atribuir como valor: "))

        while indiceEscolhido < 0 or indiceEscolhido >= len(listaKeysOrValues):
            indiceEscolhido = int(input(f">>>> Indice {indiceEscolhido} não encontrado, digite um indice valido: "))

        valor = listaKeysOrValues[indiceEscolhido]
        return valor
    
    @staticmethod
    def buscaEAtualizaDict(x, dicionarioModelo, dicionarioInterpretado, log):
            if dicionarioInterpretado.get(x) != None:
                return dicionarioInterpretado.get(x)
            elif dicionarioModelo.get(x) != None:
                return dicionarioModelo.get(x)
            elif x in dicionarioModelo.values():
                return x
            else:
                print(f"\n\u001b[31;1m>>>> BAIRRO_WARNING_01\u001b[0m VALOR \u001b[31;1m'{x}'\u001b[0m FORA DO DICIONARIO INTERPRETADO!")
                
                matches = {chave : {'valor' : valor, 'proximidade' : fuzz.ratio(x, chave)} for dict in [dicionarioInterpretado.items(), dicionarioModelo.items()] for chave, valor in dict}

                best_match_key = max(matches, key=lambda k: matches[k]['proximidade'])
                best_match_value = matches[best_match_key]['valor']
                best_match_prox = matches[best_match_key]['proximidade']
                
                print(f"  >> Chave mais proximo nos dicionarios: '{best_match_key}' | Proximidade: {best_match_prox} | Valor desta chave: '{best_match_value}'")
                resp = str(input("\u001b[32;1mPergunta:\u001b[0m A comparação está correta?\n   >>> s/n: "))

                if resp == "s":
                    print(f"\u001b[32;1m>>> Adicionado no Dicionario Interpretado! Chave: {x} | Valor: {best_match_value}\u001b[0m")
                else:
                    best_match_value = codatratamento.getListKeyOrValue(dicionarioModelo, 1)
                    print(f"\n\u001b[32;1m>>> Adicionado no Dicionario Interpretado: Chave {x} | Valor: {best_match_value}\u001b[0m")

                dicionarioInterpretado[x] = best_match_value
                log[x] = best_match_value
                with open('log_cdt_interpret.json', 'w', encoding='utf8') as f: json.dump(log, f, ensure_ascii=False)

                return best_match_value
                
    @staticmethod
    def trataEInvertTipoLogra(x):
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
