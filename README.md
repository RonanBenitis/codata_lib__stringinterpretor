<img src="https://dados.mogidascruzes.sp.gov.br/uploads/group/2023-03-03-142612.332110Captura-de-tela-2023-03-02-082822.png" alt="Codata logo" width="200" style="clip-path: polygon(54% 12%, 83% 31%, 83% 67%, 54% 86%, 23% 67%, 23% 31%);"/>

# Sobre String Interpreter (strinter)
Código destinado à interpretar um `series` de string (normalmente, uma coluna de um DataFrame) frente a uma lista de string modelo.

## Funcionamento do String Interpreter (strinter)
Para iniciar o **String Interpreter**, passe nos parametros da função `string_interpretor` uma lista (ou json) dos valores modelos e, em seguida, o `series` que se deseja comparar, tendo como retorno um `series` com os valores interpretados.

Essa aplicação gera o diretorio `strinter` e dentro dele estará:
- `datainterpret.json`: chave e valor das interpretações realizadas, sendo atualizado **na conclusão da aplicação**;
- `log`: chave e valor que estão sendo interpretadas em tempo real, como segurança para caso a aplicação seja interrompida antes de sua conclusão.
  - Caso isso aconteça, envie o valor deste log para dentro do datainterpret.json caso deseje.
- `bkp`: Diretorio contendo o ultimo estado do datainterpret.json antes da execução. As novas versões do bkp são salvas tendo em vista a data de execução.

### Exemplo de utilização
Suponha-se que temos uma coluna de montadoras de carros, todas escritas de diversas formas. Utilizando o `String Interpretor`, conseguimos realizar essa correção com as interpretações da biblioteca `fuzzywuzzy`, tendo controle se a interpretação está correta ou não (corrigindo a interpretação, se necessário) e, concluida a operação, nas proximas execuções o `datainterpret.json` estará alimentado e será utilizado, logo, não sendo necessário passar pela operação de interpretação para as que já foram realizadas.

```
import pandas as pd
import stringinterpreter as strinter

# Lista modelo
data_model = ['Toyota', 'Honda', 'Ford', 'Chevrolet', 'Volkswagen']
# Lista de montadoras com valores repetidos e escritos de diversas formas
montadoras = [
    'Toyota', 'toyota', 'TOYOTA', 'Toiota', 'Tpyota',
    'Honda', 'honda', 'HONDA', 'Hnda', 'Hondaa',
    'Ford', 'ford', 'FORD', 'Frod', 'Foord',
    'Chevrolet', 'chevrolet', 'CHEVROLET', 'Chevrollet', 'Chevy',
    'Volkswagen', 'volkswagen', 'VOLKSWAGEN', 'Volkswagn', 'VW'
]

serie_montadoras = pd.Series(montadoras)
serie_montadoras = strinter.string_interpretor(data_model, serie_montadoras)

print(serie_montadoras)
'''
output:
0         Toyota
1         Toyota
2         Toyota
3         Toyota
4         Toyota
5          Honda
6          Honda
7          Honda
8          Honda
9          Honda
10          Ford
11          Ford
12          Ford
13          Ford
14          Ford
15     Chevrolet
16     Chevrolet
17     Chevrolet
18     Chevrolet
19     Chevrolet
20    Volkswagen
21    Volkswagen
22    Volkswagen
23    Volkswagen
24    Volkswagen
'''
```