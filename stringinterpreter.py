import json
import numpy
import unidecode
from pathlib import Path
from datetime import datetime
from fuzzywuzzy import fuzz

data_modificacao = datetime.now().date()
# configurando os caminhos da estrutura de pastas
data_interpret_path = Path.cwd() / 'strinter'
bkp_interpret_path = Path.cwd() / 'strinter' / 'bkp'

def string_interpretor(list_data_model, serie):
    '''
    Execução principal da classe. Guarda os dados da instancia e
    chama as demais funções para tratamento da serie.

    input:
    - Lista dos dados modelo
    - Serie dos dados a serem interpretados

    output:
    - Serie dos dados interpretados (processados)
    '''
    config()
    dict_intepretado = load_interpretado_dict()
    log_dicio_interpret = {}
    bkp_interpretado_dict(dict_intepretado)
    print(f'\u001b[32;1m>>>>>> Initializing: String interpretator\u001b[0m')

    if dict_intepretado == None:
        print(">> ERROR: SEM DICIONARIO INTERPRETADO! Dicionario a ser interpretado não encontrado no estanciamento desta Classe.")
        return
    
    serie = serie.apply(lambda cell_value: str(cell_value))
    serie = serie.apply(strip_e_maiusculo_sem_acento)  
    serie = serie.apply(lambda cell_value : data_interpret_updater(cell_value,
                                                                list_data_model,
                                                                dict_intepretado,
                                                                log_dicio_interpret))
    update_interpretado_dict(dict_intepretado)
    print(f"\u001b[32;1m*** Processo finalizado! ***\u001b[0m")

    return serie

def config():
    '''
    Configura a estrutura de pastas da classe e reserva arquivo
    json de interpretação, os caminhos estão definidos no cabeçalho deste código
    '''
    # monta estrutura de pastas
    (data_interpret_path).mkdir(parents=True, exist_ok=True)
    (bkp_interpret_path).mkdir(parents=True, exist_ok=True)
    # reserva arquivo de interpretação
    caminho_arquivo = data_interpret_path / 'datainterpret.json'
    if not caminho_arquivo.exists():
        print('\u001b[33;1m>> DataInterpretWarning:\u001b[0m data_interpret.json não encontrado! Criando novo arquivo')
        empty_dict = {}

        with open(caminho_arquivo, 'w', encoding='utf8') as file:
            json.dump(empty_dict, file, ensure_ascii=False)

    
def load_interpretado_dict():
    with open (data_interpret_path / 'datainterpret.json', 'r', encoding='utf8') as f: 
        data_interpret = json.load(f)
        return data_interpret

def bkp_interpretado_dict(data_interpret):
    template_bkp = 'datainterpret_bkp_{}.json'

    # Backup versão inicial dictInterpretado
    with open(bkp_interpret_path / template_bkp.format(data_modificacao), 'w', encoding='utf8') as file: 
        json.dump(data_interpret, file, ensure_ascii=False)

def strip_e_maiusculo_sem_acento(string_value):
    string_value = string_value.strip()
    return unidecode.unidecode(string_value.upper())

def update_interpretado_dict(dict_intepretado):
    # Salva versão atualizada dictInterpretado
    with open(data_interpret_path / 'datainterpret.json', 'w', encoding='utf8') as file: 
        json.dump(dict_intepretado, file, ensure_ascii=False)

def data_interpret_updater(cell_value, data_model, data_interpret, log):
    '''
    Realiza as intepretações.

    input:
    - Valor a ser interpretado (string), no caso, está sendo
    uma celula de dataframe
    - Lista dos valores de referencia
    - Dicionario de interpretações
    - Dicionario de log

    output:
    > Quando há correspondencia:
    - Retorna o valor da correspondencia ou, se correto, retorna
    ela mesma

    > Quando não há correspondencia (bloco else):
    - Usuário concorda com a correspondencia: acrescenta valor
    da celula como chave e a correspondencia como valor da chave
    - Usuário não concorda com a correspondencia: usuário indica
    o valor correto da chave, sendo valor da celula
    - Registra chave e valor no log

    nota sobre normalização:
    - Para a comparação, é realizado a normalização de valores tanto para
    o data_model quanto para o valor da celula, mas, atribui-se o valor
    correspondente ao que encontra-se no data_model (com a
    formatação que estiver).
    - A normalização do data_model ocorre nessa função, a do valor da
    celula ocorre no string_interpretor
    '''
    if data_interpret.get(cell_value) != None:
        return data_interpret.get(cell_value)
    elif cell_value in data_model:
        return cell_value
    elif cell_value is numpy.nan or cell_value is None or str(cell_value).upper() == 'NAN':
        return {'': ''}
    else:
        print(f"\n\u001b[31;1m>>>> MATCH_WARNING\u001b[0m VALOR \u001b[31;1m'{cell_value}'\u001b[0m Não encontrado no Data Model e no Data Interpreted!")

        matches = {}

        # itera em lista, alimenta matches
        # Note o valor_normalized
        for valor in data_model:
            valor_normalized = strip_e_maiusculo_sem_acento(valor)
            matches[valor_normalized] = {'valor': valor, 'proximidade': fuzz.ratio(cell_value, valor_normalized)}

        # itera no dicionario, alimenta matches
        for chave, valor in data_interpret.items():
            matches[chave] = {'valor': valor, 'proximidade': fuzz.ratio(cell_value, chave)}

        best_match_key = max(matches, key=lambda k: matches[k]['proximidade'])
        best_match_value = matches[best_match_key]['valor']
        best_match_prox = matches[best_match_key]['proximidade']
        print(f"  - Correspondência mais proxima registrada: '{best_match_key}'\n  - \u001b[32;1mValor da correspondencia: '{best_match_value}'\u001b[0m\n  - Proximidade: {best_match_prox}")
        resp = str(input("A comparação está correta?\n   >>> \u001b[32;1ms\u001b[0m para sim | \u001b[32;1mn\u001b[0m ou \u001b[32;1menter\u001b[0m para não: "))

        while resp != 's' and resp != 'n' and resp != '':
            print('Opção invalida!!')
            resp = str(input("A comparação está correta?\n   >>> \u001b[32;1ms\u001b[0m para sim | \u001b[32;1mn\u001b[0m ou \u001b[32;1menter\u001b[0m para não: "))

        if resp == "s":
            print(f"\u001b[32;1m>>> Adicionado ao Data Interpreted! Chave: {cell_value} | Valor: {best_match_value}\u001b[0m")
        else:
            best_match_value = index_list(data_model)
            print(f"\n\u001b[32;1m>>> Adicionado ao Data Interpreted: Chave {cell_value} | Valor: {best_match_value}\u001b[0m")

        data_interpret[cell_value] = best_match_value
        log[cell_value] = best_match_value

        with open(data_interpret_path / 'logdatainterpret.json', 'w', encoding='utf8') as f: 
            json.dump(log, f, ensure_ascii=False)

        return best_match_value

def index_list(data_model):
    '''
    Enumera os valores modelos em indice e valor.

    inputs:
    - uma estrutura modelo que pode ser json ou lista

    outputs:
    - retorna valor correspondente ao indice indicado pelo usuário

    nota:
    - lista_data_model usa list() para comportar a coleta por indice quando
    data_model é json
    '''
    print(f" >>>>>> Lista de valores modelo")
    lista_data_model = list(data_model)

    for i, valor in enumerate(lista_data_model):
        print(f"\u001b[32;1m[{i}]\u001b[0m - {valor}")
    indice_escolhido = int(input(">>>> Insira o indice desejado para atribuir como valor: "))

    # Valida entrada
    while True:
        try:
            indice_escolhido = int(input(">>>> Insira o indice desejado para atribuir como valor: "))

            if indice_escolhido < 0 or indice_escolhido >= len(data_model):
                indice_escolhido = int(input(f"Indice {indice_escolhido} não encontrado!!!"))
            else:
                break # sai do loop

        except ValueError:
            print('Valor inválido, ditie um número inteiro!!!')

    valor = lista_data_model[indice_escolhido]

    return valor

