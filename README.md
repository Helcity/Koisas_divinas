# Koisas_divinas
Simulação Monte Carlos Koisas Divinas Dofuas

# Dofus Eterna Colheita - Simulador de Eficiência de Caixas

Este script Python utiliza uma simulação de Monte Carlo para analisar a estratégia de uso das "Koisas Divinas" na missão Eterna Colheita do jogo Dofus. Especificamente, ele compara a eficiência relativa de usar a caixa global (3 Koisas) versus a caixa de etapa específica (6 Koisas) para obter novos arquimonstros.

**Importante:** Esta versão da simulação foca *exclusivamente* na decisão de qual caixa abrir a cada passo, assumindo que o jogador *sempre* escolherá a opção matematicamente mais eficiente (maior `Probabilidade_Novo / Custo`). Ela **não** simula a aquisição de Koisas Divinas nem encontros aleatórios com arquimonstros. O objetivo é entender a tendência de escolha (Global vs. Específica) ao longo do processo de completar a coleção *apenas* via caixas, partindo de um estado inicial definido pelo usuário.

## Funcionalidades

* **Interface Gráfica Simples (Tkinter/ttk):** Permite ao usuário:
    * Definir o número de simulações a serem executadas.
    * Inserir o estado inicial da missão (número de monstros já capturados em cada etapa relevante - 20 a 34).
* **Simulação de Monte Carlo:** Roda múltiplas simulações partindo do estado inicial fornecido.
* **Lógica de Decisão Baseada em Eficiência:** Em cada etapa da simulação, calcula a eficiência de ambas as opções de caixa e escolhe a melhor.
    * `Eficiência = Probabilidade_Obter_Novo / Custo_Koisa`
* **Análise Estatística:** Calcula estatísticas descritivas sobre os resultados das simulações (número total de caixas abertas, número de caixas globais vs. específicas, proporções).
* **Visualização:** Gera histogramas mostrando a distribuição do número total de caixas abertas, e o número de caixas globais e específicas utilizadas em todas as simulações.

## Como Usar

### Pré-requisitos

* Python 3.x instalado.
* Bibliotecas Python: `pandas`, `matplotlib`, `numpy`. Instale-as usando pip:
    ```bash
    pip install pandas matplotlib numpy
    ```

### Execução

1.  Salve o código como `dofus_sim_gui.py` (ou outro nome .py).
2.  Execute o script a partir do seu terminal:
    ```bash
    python dofus_sim_gui.py
    ```

### Interface Gráfica

1.  **Número de Simulações:** Insira quantas vezes você deseja que a simulação completa seja executada (e.g., 1000). Mais simulações geram resultados estatisticamente mais robustos, mas levam mais tempo.
2.  **Estado Inicial:** Para cada etapa (20 a 34), insira quantos arquimonstros você *já capturou*. Os valores padrão correspondem ao exemplo original da consulta, mas você deve atualizá-los para o seu progresso atual.
3.  **Iniciar Simulação:** Clique neste botão para começar. A interface pode parecer congelada durante a execução se o número de simulações for muito alto. Uma barra de progresso indicará o andamento.
4.  **Resultados:** Após a conclusão, as estatísticas principais serão exibidas na área de texto inferior, e uma janela com os gráficos (histogramas) será mostrada.

## Lógica da Simulação (Versão Atual)

1.  A simulação começa com o estado de captura fornecido pelo usuário.
2.  **Não há simulação de encontro aleatório de monstros.**
3.  **Não há simulação de ganho ou limite de Koisas Divinas.**
4.  Em um loop, até que todos os 286 monstros sejam considerados "capturados":
    a. Calcula a eficiência da caixa global (`Prob_Global_Novo / 3`).
    b. Calcula a eficiência da caixa específica para *cada* etapa ainda incompleta (`Prob_Etapa_Novo / 6`).
    c. Identifica a maior eficiência entre a global e a *melhor* das específicas.
    d. Simula a abertura da caixa correspondente à maior eficiência.
    e. Se um monstro *novo* for obtido (simulado probabilisticamente), o estado de captura é atualizado.
    f. Registra qual tipo de caixa foi aberta (global ou específica).
5.  Ao final de uma simulação, registra o número total de caixas abertas e a contagem para cada tipo.
6.  Repete o processo para o número de simulações solicitado.
7.  Agrega os resultados de todas as simulações para análise estatística e visualização.

## Limitações

* **Não modela a aquisição de Koisas:** A simulação assume que sempre é possível abrir a caixa mais eficiente, ignorando o custo real e como as Koisas são obtidas (que na prática vêm de capturas aleatórias não simuladas aqui).
* **Não modela capturas aleatórias:** Ignora o fato de que o jogador continua capturando monstros fora do sistema de caixas, o que na realidade acelera o processo e altera o estado inicial para as decisões de caixa.
* **Foco na Eficiência Pura:** A simulação responde à pergunta: "Se eu completasse a coleção *apenas* abrindo caixas e *sempre* escolhendo a mais eficiente, qual seria a tendência de uso entre caixas globais e específicas?".

Esta ferramenta é útil para entender a dinâmica da *decisão* baseada em eficiência, mas não representa o tempo real ou o custo total em Koisas para completar a missão no jogo.
