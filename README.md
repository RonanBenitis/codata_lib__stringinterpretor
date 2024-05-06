<img src="https://dados.mogidascruzes.sp.gov.br/uploads/group/2023-03-03-142612.332110Captura-de-tela-2023-03-02-082822.png" alt="Codata logo" width="200" style="clip-path: polygon(54% 12%, 83% 31%, 83% 67%, 54% 86%, 23% 67%, 23% 31%);"/>

# Sobre este Script de Tratamentos
Classe Python destinado a tratamento diverso de dados, recebendo, em seu construtor, um DataFrame, um dicionario e, opcionalmente, um dicionario para armazenamento de interpretação de dados.

### Exemplo de utilização da Clase
Essa classe, atualmente, é utilizada para interpretação de bairros em um DataFrame, retornando o valor correspondendo ao nome correto (e bairro correto) frente ao abairramento atual do município, utilizando a biblioteca FuzzyWuzzy para retornar as proximidades de nomes.
Após a interpretação dos nomes pelo FuzzyWuzzy e validação por um usuário dos valores interpretados (somente os valores que não estão nos dicionarios), é alimentado o dicionario de interpretação, fazendo com que a cada execução a sua biblioteca se torne mais rica de interpretações.