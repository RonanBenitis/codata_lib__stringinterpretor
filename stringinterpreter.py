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

def string_interpretor(data_model, serie_alvo):
    '''
    Execução principal da classe. Guarda os dados da instancia e
    chama as demais funções para tratamento da serie.

    input:
    - data_model: Serie, lista ou json unidimensional dos dados modelo
    - serie_alvo: Serie dos dados a serem interpretados

    output:
    - Serie dos dados interpretados (processados)
    '''
    config(data_model)
    dict_intepretado = load_interpretado_dict()
    log_dicio_interpret = {}
    bkp_interpretado_dict(dict_intepretado)
    print(f'\u001b[32;1m>>>>>> Initializing: String interpretator\u001b[0m')

    if dict_intepretado == None:
        print(">> ERROR: SEM DICIONARIO INTERPRETADO! Dicionario a ser interpretado não encontrado no estanciamento desta Classe.")
        return
    
    serie_processada = serie_alvo.apply(lambda cell_value: str(cell_value))
    serie_processada = serie_processada.apply(strip_e_maiusculo_sem_acento)
    serie_processada = serie_processada.apply(lambda cell_value : data_interpret_updater(cell_value,
                                                                                         data_model,
                                                                                         dict_intepretado,
                                                                                         log_dicio_interpret))
    update_interpretado_dict(dict_intepretado)
    print(f"\u001b[32;1m*** Processo finalizado! ***\u001b[0m")

    return serie_processada

def config(data_model):
    '''
    Configura a estrutura de pastas da classe e reserva arquivo
    json de interpretação, os caminhos estão definidos no cabeçalho deste código

    nota:
    - datainterpret.json é criado, como padrão, com todos os valores de data_model
    em maisculo, stripped e sem acento como chaves e seus valores como o valor
    puro do data_model. Isso é feito para reduzir a quantidade de interações
    por conta das comparações que o programa fará entre o dado a ser interpretado
    e o dado modelo, além de evitar fazer 2 interpretações sobre o mesmo dado
    - Isso ocorreria pois o programa faz limpezas no dado para evitar muitas
    interações
    - Limpezas: deixa todas as comparações como upper, sem acento e stripped.
    '''
    # monta estrutura de pastas
    (data_interpret_path).mkdir(parents=True, exist_ok=True)
    (bkp_interpret_path).mkdir(parents=True, exist_ok=True)
    # reserva arquivo de interpretação
    caminho_arquivo = data_interpret_path / 'datainterpret.json'
    if not caminho_arquivo.exists():
        print('\u001b[33;1m>> DataInterpretWarning:\u001b[0m data_interpret.json não encontrado! Criando novo arquivo')
        start_dict = {strip_e_maiusculo_sem_acento(d): d for d in list(data_model)}

        with open(caminho_arquivo, 'w', encoding='utf8') as file:
            json.dump(start_dict, file, ensure_ascii=False)

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
    - Usou-se list(data_model) para iterar como uma lista independente
    se o data_model é list, json unidimensional ou serie
    '''
    if data_interpret.get(cell_value) != None:
        return data_interpret.get(cell_value)
    elif cell_value in list(data_model):
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

        # Interrompe operação se digitado 'e'
        if resp == 'e':
            raise KeyboardInterrupt

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
    data_model é json ou serie
    '''
    print(f" >>>>>> Lista de valores modelo")
    lista_data_model = list(data_model)

    for i, valor in enumerate(lista_data_model):
        print(f"\u001b[32;1m[{i}]\u001b[0m - {valor}")

    # Valida entrada
    while True:
        try:
            indice_escolhido = input(">>>> Insira o indice desejado para atribuir como valor ou digite 'e' para encerrar a aplicação: ")

            # Valida se o input de interrupção foi lançado
            # Se não, casta pra int e no erro vai pra exceção
            if indice_escolhido != 'e':
                indice_escolhido = int(indice_escolhido)
            else:
                raise KeyboardInterrupt

            if indice_escolhido < 0 or indice_escolhido >= len(data_model):
                indice_escolhido = int(input(f"Indice {indice_escolhido} não encontrado!!!"))
            else:
                break # sai do loop

        except ValueError:
            print('Valor inválido, digite um número inteiro!!!')

    valor = lista_data_model[indice_escolhido]

    return valor