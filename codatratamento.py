import pandas as pd
import unidecode
from fuzzywuzzy import fuzz
from datetime import datetime

class codatratamento:
    dataAtual = datetime.now().date()

    # >>>>>>>>>>>>>>>>>==================<<<<<<<<<<<<<<<<<<<<<
    # >>>>>>>>>>>>>>>>>    CONSTRUTOR    <<<<<<<<<<<<<<<<<<<<<
    # >>>>>>>>>>>>>>>>>==================<<<<<<<<<<<<<<<<<<<<<
    def __init__ (self, dataFrame, dicionarioModelo, dicionarioInterpretado=None):
        self.dataFrame = dataFrame
        self.dicionarioModelo = dicionarioModelo
        self.dicionarioInterpretado = dicionarioInterpretado
    
    # >>>>>>>>>>>>>>>>>=========================<<<<<<<<<<<<<<<<<<<<<
    # >>>>>>>>>>>>>>>>>    MÉTODOS DO OBJETO    <<<<<<<<<<<<<<<<<<<<<
    # >>>>>>>>>>>>>>>>>=========================<<<<<<<<<<<<<<<<<<<<<
    def trataNomeBairro (self, coluna):
        if self.dicionarioInterpretado == None:
            print("ERRO: SEM DICIONARIO INTERPRETADO! Dicionario a ser interpretado não encontrado no estanciamento desta Classe.")
            return
        
        self.dataFrame[coluna] = self.dataFrame[coluna].apply(codatratamento.trataEInvertTipoLogra)
        self.dataFrame[coluna] = self.dataFrame[coluna].apply(codatratamento.stripEMaiusculoSemAcento)

        def percorreDictInterpretado(x):
            return self.dicionarioInterpretado.get(x, x)
        self.dataFrame[coluna] = self.dataFrame[coluna].apply(percorreDictInterpretado)
        
        self.dataFrame[coluna] = self.dataFrame[coluna].apply(lambda x : codatratamento.buscaEAtualizaDict(x, self.dicionarioModelo, self.dicionarioInterpretado))

        return self.dataFrame[coluna]

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
    def dfToExcel(dataFrame, nomeArquivoOrigem, dataOutputPath):
        print("----- Transformando DBF em EXCEL para a pasta output, aguarde! -----")
        dataFrame.to_excel(dataOutputPath + nomeArquivoOrigem + '.xlsx', index=False)
        print("----- Transformação realizada! -----")
    
    @staticmethod
    def dictGetValue(dicionario):
        print(" >>>>>> Lista de VALORES do Dicionario Modelo")
        valores = list(dicionario.values())
        for i, valor in enumerate(valores):
            print(f"\u001b[32;1m[{i}]\u001b[0m - {valor}")
        indiceEscolhido = int(input(">>>> Insira o indice desejado para atribuir como valor: "))

        while indiceEscolhido < 0 or indiceEscolhido >= len(valores):
            indiceEscolhido = int(input(f">>>> Indice {indiceEscolhido} não encontrado, digite um indice valido: "))

        valor = valores[indiceEscolhido]
        return valor
    
    @staticmethod
    def dictGetKey(dicionario):
        print(" >>>>>> Lista de CHAVES do Dicionario Modelo")
        chaves = list(dicionario.keys())
        for i, chave in enumerate(chaves):
            print(f"\u001b[32;1m[{i}]\u001b[0m - {chave}")
        indiceEscolhido = int(input(">>>> Insira o indice desejado para atribuir como valor: "))

        while indiceEscolhido < 0 or indiceEscolhido >= len(chaves):
            indiceEscolhido = int(input(f">>>> Indice {indiceEscolhido} não encontrado, digite um indice valido: "))

        valor = chaves[indiceEscolhido]
        return valor
    
    @staticmethod
    def buscaEAtualizaDict(x, dicionarioModelo, dicionarioInterpretado):
            if dicionarioModelo.get(x) != None:
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
                    best_match_value = codatratamento.dictGetValue(dicionarioModelo)
                    print(f"\n\u001b[0m>>> Adicionado no Dicionario Interpretado: Chave {x} | Valor: {best_match_value}\u001b[0m")

                dicionarioInterpretado[x] = best_match_value

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
