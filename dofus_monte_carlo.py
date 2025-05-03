import random
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
import time
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

# --- Configurações Constantes ---
TOTAL_ARCHMONSTERS = 286
# Custos são usados apenas para cálculo de eficiência relativa
GLOBAL_BOX_COST = 3
SPECIFIC_BOX_COST = 6

# Define as etapas e o número total de monstros em cada uma
STAGES_INFO = {i: 20 for i in range(20, 34)}
STAGES_INFO[34] = 6

# Estado inicial padrão (pode ser alterado na GUI)
DEFAULT_INITIAL_CAPTURES = {
    20: 17, 21: 10, 22: 15, 23: 9, 24: 13, 25: 9, 26: 12, 27: 11,
    28: 13, 29: 14, 30: 8, 31: 7, 32: 12, 33: 8, 34: 5
}

# --- Geração da Lista Mestra de Monstros (Feito uma vez) ---
master_monster_list = []
monster_id_counter = 0
for stage, count in STAGES_INFO.items():
    for _ in range(count):
        master_monster_list.append((f"m_{monster_id_counter}", stage))
        monster_id_counter += 1
# Usado para mapear rapidamente monstro -> etapa
monster_to_stage_map = {mid: stage for mid, stage in master_monster_list}

# --- Funções Auxiliares da Simulação (Adaptadas) ---

def get_initial_simulation_state(user_captures_per_stage):
    """ Cria o estado inicial baseado nos dados do usuário."""
    captured_monster_ids = set()
    current_captures_per_stage = user_captures_per_stage.copy()
    monsters_in_stage = {stage: [] for stage in STAGES_INFO}
    for mid, stage in master_monster_list:
        monsters_in_stage[stage].append(mid)

    # Seleciona aleatoriamente os IDs capturados iniciais para cada etapa
    total_initial_count = 0
    for stage, num_captured in user_captures_per_stage.items():
         total_initial_count += num_captured
         if stage not in STAGES_INFO: continue # Ignora etapas inválidas se houver
         available_in_stage = monsters_in_stage[stage]
         if num_captured > 0:
            # Garante que não seleciona mais do que existe ou tenta com 0
            actual_num_to_capture = min(num_captured, len(available_in_stage))
            if actual_num_to_capture > 0:
               captured_sample = random.sample(available_in_stage, actual_num_to_capture)
               captured_monster_ids.update(captured_sample)
            if actual_num_to_capture != num_captured:
                 print(f"Aviso: Etapa {stage}: Solicitado {num_captured}, mas capturado {actual_num_to_capture} (limite da etapa).")


    # Verifica a contagem inicial total
    if len(captured_monster_ids) != total_initial_count:
        print(f"Alerta: Contagem inicial de IDs ({len(captured_monster_ids)}) não bate com soma fornecida ({total_initial_count}). Pode haver sobreposição se monstros forem mal atribuídos (não deve acontecer com master_list correta).")

    return {
        "captured_ids": captured_monster_ids,
        "captures_per_stage": current_captures_per_stage,
        "total_captured": len(captured_monster_ids),
        # "koisas": 0, # Removido - não simulamos mais aquisição/gasto
        "steps": 0, # Contador de ABERTURAS DE CAIXA
        "global_boxes_opened": 0,
        "specific_boxes_opened": 0,
    }

def calculate_efficiencies(state):
    """ Calcula a eficiência da caixa global e de cada caixa específica."""
    total_captured = state["total_captured"]
    captures_per_stage = state["captures_per_stage"]

    if total_captured >= TOTAL_ARCHMONSTERS:
        return 0, {}, None, 0 # Simulação acabou para este estado

    # Eficiência Global
    prob_global_new = (TOTAL_ARCHMONSTERS - total_captured) / TOTAL_ARCHMONSTERS
    eff_global = prob_global_new / GLOBAL_BOX_COST if GLOBAL_BOX_COST > 0 else float('inf')

    # Eficiência Específica
    eff_stages = {}
    best_stage_eff = -1
    best_stage_id = None
    for stage, total_in_stage in STAGES_INFO.items():
        captured_in_stage = captures_per_stage.get(stage, 0)
        if captured_in_stage < total_in_stage: # Só calcula se a etapa não está completa
            remaining_in_stage = total_in_stage - captured_in_stage
            prob_stage_new = remaining_in_stage / total_in_stage
            eff_stage = prob_stage_new / SPECIFIC_BOX_COST if SPECIFIC_BOX_COST > 0 else float('inf')
            eff_stages[stage] = eff_stage
            if eff_stage > best_stage_eff:
                best_stage_eff = eff_stage
                best_stage_id = stage
        else:
             eff_stages[stage] = 0 # Etapa completa

    if best_stage_id is None: # Todas as etapas completas (deveria ser pego pelo total_captured >= TOTAL)
         best_stage_eff = 0

    return eff_global, eff_stages, best_stage_id, best_stage_eff

def simulate_box_opening_decision(state):
    """ Decide qual caixa abrir baseado na eficiência e simula a abertura, atualizando estado."""
    eff_global, _, best_stage_id, best_stage_eff = calculate_efficiencies(state)

    if eff_global == 0 and best_stage_eff == 0:
         # print("Nenhuma caixa tem eficiência > 0, todos capturados?")
         return False # Não há mais o que fazer

    use_global_box = (eff_global >= best_stage_eff) or (best_stage_id is None)

    new_monster_obtained = False
    opened_box_type = None

    state["steps"] += 1 # Incrementa passo (abertura de caixa)

    if use_global_box:
        state["global_boxes_opened"] += 1
        opened_box_type = "Global"
        # Simula abrir caixa global: pega um monstro aleatório dos 286
        chosen_monster_id, chosen_stage_id = random.choice(master_monster_list)

        if chosen_monster_id not in state["captured_ids"]:
            new_monster_obtained = True
            state["captured_ids"].add(chosen_monster_id)
            # Usa o mapa para garantir a etapa correta
            actual_stage_id = monster_to_stage_map[chosen_monster_id]
            state["captures_per_stage"][actual_stage_id] = state["captures_per_stage"].get(actual_stage_id, 0) + 1
            state["total_captured"] += 1

    else: # Usa caixa específica
        state["specific_boxes_opened"] += 1
        opened_box_type = f"Specific (Stage {best_stage_id})"
        # Pega os monstros da melhor etapa
        monsters_in_best_stage = [m[0] for m in master_monster_list if m[1] == best_stage_id]

        if not monsters_in_best_stage:
             print(f"Erro: Tentando abrir caixa da etapa {best_stage_id}, mas não há monstros listados para ela.")
             return False # Algo deu errado

        # Simula abrir caixa específica: pega um monstro aleatório DENTRO da etapa
        chosen_monster_id = random.choice(monsters_in_best_stage)

        if chosen_monster_id not in state["captured_ids"]:
            new_monster_obtained = True
            state["captured_ids"].add(chosen_monster_id)
            state["captures_per_stage"][best_stage_id] = state["captures_per_stage"].get(best_stage_id, 0) + 1
            state["total_captured"] += 1

    # Log simplificado (opcional)
    # print(f"Step {state['steps']}: Opened {opened_box_type}. New: {new_monster_obtained}. Total captured: {state['total_captured']}")
    return True # Caixa foi aberta (mesmo que duplicada)

# --- Função Principal da Simulação (Uma Rodada - Adaptada) ---
def run_single_simulation(initial_captures_config):
    """ Executa uma simulação completa apenas abrindo caixas eficientes."""
    state = get_initial_simulation_state(initial_captures_config)

    while state["total_captured"] < TOTAL_ARCHMONSTERS:
        opened = simulate_box_opening_decision(state)

        if not opened: # Se não conseguiu abrir (ex: tudo completo)
             # print("Simulação terminada: não foi possível abrir mais caixas.")
             break

        # Segurança contra loops infinitos
        if state["steps"] > TOTAL_ARCHMONSTERS * 5: # Limite (deve ser alcançado bem antes)
             print(f"Alerta: Simulação excedeu limite de {TOTAL_ARCHMONSTERS * 5} passos. Interrompendo.")
             break

    # Retorna os resultados finais da simulação
    return {
        "total_box_openings": state["steps"],
        "global_boxes_opened": state["global_boxes_opened"],
        "specific_boxes_opened": state["specific_boxes_opened"],
    }

# --- Execução da Simulação de Monte Carlo (Adaptada) ---
def run_monte_carlo(num_simulations, initial_captures_config, progress_callback=None):
    """ Roda N simulações e coleta os resultados."""
    all_results = []
    start_time = time.time()
    print(f"Iniciando {num_simulations} simulações com a configuração inicial fornecida...")
    for i in range(num_simulations):
        result = run_single_simulation(initial_captures_config)
        all_results.append(result)
        if progress_callback and (i + 1) % (num_simulations // 20 if num_simulations >= 20 else 1) == 0:
             progress_callback(i + 1, num_simulations) # Atualiza GUI

    end_time = time.time()
    duration = end_time - start_time
    print(f"Simulações concluídas em {duration:.2f} segundos.")
    if progress_callback: # Finaliza a barra de progresso
        progress_callback(num_simulations, num_simulations, duration)
    return pd.DataFrame(all_results)

# --- Análise e Visualização (Adaptada) ---
def analyze_and_visualize(results_df, num_simulations, text_output_widget=None):
    """ Calcula estatísticas e gera gráficos a partir dos resultados."""
    analysis_text = "--- Análise Estatística dos Resultados ---\n\n"
    analysis_text += results_df.describe().to_string() + "\n\n"

    # Contagem média de uso das caixas
    avg_global = results_df['global_boxes_opened'].mean()
    avg_specific = results_df['specific_boxes_opened'].mean()
    analysis_text += f"Uso Médio de Caixas por Simulação:\n"
    analysis_text += f"  - Caixas Globais (3 Koisas): {avg_global:.2f}\n"
    analysis_text += f"  - Caixas Específicas (6 Koisas): {avg_specific:.2f}\n"

    total_avg_boxes = avg_global + avg_specific
    if total_avg_boxes > 0:
      ratio_global = avg_global / total_avg_boxes * 100 if total_avg_boxes else 0
      analysis_text += f"  - Proporção Média Global: {ratio_global:.1f}%\n"
      analysis_text += f"  - Proporção Média Específica: {100 - ratio_global:.1f}%\n"
    else:
      analysis_text += "  - Nenhuma caixa foi utilizada em média (verificar estado inicial).\n"

    # Comparação direta
    global_more_used = (results_df['global_boxes_opened'] > results_df['specific_boxes_opened']).sum()
    specific_more_used = (results_df['specific_boxes_opened'] > results_df['global_boxes_opened']).sum()
    equal_used = (results_df['specific_boxes_opened'] == results_df['global_boxes_opened']).sum()

    analysis_text += "\nComparação de Predominância de Uso por Simulação:\n"
    analysis_text += f"  - Global mais usada: {global_more_used}/{num_simulations} ({global_more_used/num_simulations*100:.1f}%)\n"
    analysis_text += f"  - Específica mais usada: {specific_more_used}/{num_simulations} ({specific_more_used/num_simulations*100:.1f}%)\n"
    analysis_text += f"  - Uso igual ou zero: {equal_used}/{num_simulations} ({equal_used/num_simulations*100:.1f}%)\n"

    print(analysis_text) # Imprime no console também
    if text_output_widget:
         text_output_widget.configure(state='normal')
         text_output_widget.delete('1.0', tk.END)
         text_output_widget.insert(tk.END, analysis_text)
         text_output_widget.configure(state='disabled')


    # Visualizações
    try:
        plt.style.use('ggplot')
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        fig.suptitle('Resultados da Simulação de Abertura de Caixas (Eterna Colheita)', fontsize=16)

        # Histograma do total de aberturas de caixa
        axes[0].hist(results_df['total_box_openings'], bins=30, color='skyblue', edgecolor='black')
        axes[0].set_title('Distribuição do Total de Caixas Abertas')
        axes[0].set_xlabel('Nº Total de Caixas Abertas para Completar')
        axes[0].set_ylabel('Frequência (Nº de Simulações)')
        avg_steps = results_df['total_box_openings'].mean()
        axes[0].axvline(avg_steps, color='red', linestyle='dashed', linewidth=1)
        axes[0].text(avg_steps*1.05, axes[0].get_ylim()[1]*0.9, f'Média: {avg_steps:.0f}', color='red')

        # Histograma do uso de caixas globais
        axes[1].hist(results_df['global_boxes_opened'], bins=max(10, results_df['global_boxes_opened'].nunique()), color='lightcoral', edgecolor='black')
        axes[1].set_title('Distribuição do Uso de Caixas Globais (3 Koisas)')
        axes[1].set_xlabel('Nº de Caixas Globais Abertas')
        axes[1].set_ylabel('Frequência')
        axes[1].axvline(avg_global, color='blue', linestyle='dashed', linewidth=1)
        axes[1].text(avg_global*1.05, axes[1].get_ylim()[1]*0.9, f'Média: {avg_global:.1f}', color='blue')

        # Histograma do uso de caixas específicas
        axes[2].hist(results_df['specific_boxes_opened'], bins=max(10, results_df['specific_boxes_opened'].nunique()), color='lightgreen', edgecolor='black')
        axes[2].set_title('Distribuição do Uso de Caixas Específicas (6 Koisas)')
        axes[2].set_xlabel('Nº de Caixas Específicas Abertas')
        axes[2].set_ylabel('Frequência')
        axes[2].axvline(avg_specific, color='purple', linestyle='dashed', linewidth=1)
        axes[2].text(avg_specific*1.05, axes[2].get_ylim()[1]*0.9, f'Média: {avg_specific:.1f}', color='purple')

        plt.tight_layout(rect=[0, 0.03, 1, 0.95]) # Ajusta para título principal
        plt.show()
    except Exception as e:
         messagebox.showerror("Erro na Plotagem", f"Não foi possível gerar os gráficos: {e}")


# --- Interface Gráfica (Tkinter) ---
class SimulationApp:
    def __init__(self, master):
        self.master = master
        master.title("Simulador Eterna Colheita - Eficiência de Caixas")
        master.geometry("650x750") # Ajuste tamanho conforme necessário

        self.style = ttk.Style()
        self.style.theme_use('clam') # Escolha um tema (clam, alt, default, classic)

        # Frame principal
        main_frame = ttk.Frame(master, padding="10")
        main_frame.pack(expand=True, fill=tk.BOTH)

        # --- Configurações da Simulação ---
        config_frame = ttk.LabelFrame(main_frame, text="Configurações", padding="10")
        config_frame.pack(fill=tk.X, pady=5)

        ttk.Label(config_frame, text="Número de Simulações:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.num_simulations_entry = ttk.Entry(config_frame, width=10)
        self.num_simulations_entry.grid(row=0, column=1, padx=5, pady=5)
        self.num_simulations_entry.insert(0, "1000") # Valor padrão

        # --- Estado Inicial (Capturas por Etapa) ---
        initial_state_frame = ttk.LabelFrame(main_frame, text="Estado Inicial (Monstros Capturados por Etapa)", padding="10")
        initial_state_frame.pack(fill=tk.X, pady=5)

        self.stage_entries = {}
        row, col = 0, 0
        sorted_stages = sorted(STAGES_INFO.keys())
        for i, stage in enumerate(sorted_stages):
            ttk.Label(initial_state_frame, text=f"Etapa {stage} ({STAGES_INFO[stage]}):").grid(row=row, column=col, padx=5, pady=2, sticky=tk.W)
            entry = ttk.Entry(initial_state_frame, width=5)
            entry.grid(row=row, column=col+1, padx=5, pady=2)
            entry.insert(0, str(DEFAULT_INITIAL_CAPTURES.get(stage, 0))) # Valor padrão
            self.stage_entries[stage] = entry
            col += 2
            if col >= 6: # Ajuste número de colunas
                 row += 1
                 col = 0

        # --- Botão de Iniciar ---
        self.start_button = ttk.Button(main_frame, text="Iniciar Simulação", command=self.run_simulation_from_gui)
        self.start_button.pack(pady=10)

        # --- Barra de Progresso ---
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, padx=10, pady=5)
        self.progress_label = ttk.Label(main_frame, text="")
        self.progress_label.pack(pady=2)


        # --- Área de Saída de Texto ---
        output_frame = ttk.LabelFrame(main_frame, text="Resultados da Análise", padding="10")
        output_frame.pack(expand=True, fill=tk.BOTH, pady=5)

        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, height=15, state='disabled')
        self.output_text.pack(expand=True, fill=tk.BOTH)


    def update_progress(self, current_step, total_steps, duration=None):
         percentage = (current_step / total_steps) * 100
         self.progress_var.set(percentage)
         status_text = f"Progresso: {current_step}/{total_steps} ({percentage:.1f}%)"
         if duration is not None:
              status_text = f"Concluído {total_steps} simulações em {duration:.2f}s."
         self.progress_label.config(text=status_text)
         self.master.update_idletasks() # Força atualização da GUI


    def run_simulation_from_gui(self):
        # Desabilita botão para evitar cliques múltiplos
        self.start_button.config(state=tk.DISABLED)
        self.progress_var.set(0)
        self.progress_label.config(text="Iniciando...")
        self.output_text.configure(state='normal')
        self.output_text.delete('1.0', tk.END)
        self.output_text.insert(tk.END, "Validando entradas e preparando simulação...\n")
        self.output_text.configure(state='disabled')
        self.master.update_idletasks()


        # Validar e obter número de simulações
        try:
            num_simulations = int(self.num_simulations_entry.get())
            if num_simulations <= 0:
                raise ValueError("Número de simulações deve ser positivo.")
        except ValueError as e:
            messagebox.showerror("Erro na Entrada", f"Número de simulações inválido: {e}")
            self.start_button.config(state=tk.NORMAL)
            return

        # Validar e obter capturas iniciais
        initial_captures = {}
        total_cap_gui = 0
        try:
            for stage, entry in self.stage_entries.items():
                captured = int(entry.get())
                total_in_stage = STAGES_INFO[stage]
                if not (0 <= captured <= total_in_stage):
                    raise ValueError(f"Etapa {stage}: Valor '{captured}' inválido. Deve ser entre 0 e {total_in_stage}.")
                initial_captures[stage] = captured
                total_cap_gui += captured
            if total_cap_gui >= TOTAL_ARCHMONSTERS:
                 raise ValueError(f"Total inicial de capturas ({total_cap_gui}) é igual ou maior que o total de monstros ({TOTAL_ARCHMONSTERS}). Simulação não pode iniciar.")

        except ValueError as e:
            messagebox.showerror("Erro na Entrada", f"Contagem de capturas inválida: {e}")
            self.start_button.config(state=tk.NORMAL)
            return

        # Limpa área de texto antes de rodar
        self.output_text.configure(state='normal')
        self.output_text.delete('1.0', tk.END)
        self.output_text.insert(tk.END, f"Iniciando {num_simulations} simulações...\nConfiguração Inicial (Total: {total_cap_gui}):\n{initial_captures}\n\nAguarde...\n")
        self.output_text.configure(state='disabled')
        self.master.update_idletasks()


        # Executar simulações em background seria ideal, mas para simplificar, rodamos direto
        # (Pode congelar a GUI para N muito grande)
        try:
            results = run_monte_carlo(num_simulations, initial_captures, self.update_progress)
            analyze_and_visualize(results, num_simulations, self.output_text)
            messagebox.showinfo("Simulação Concluída", f"{num_simulations} simulações foram concluídas com sucesso. Verifique os resultados e os gráficos.")
        except Exception as e:
             messagebox.showerror("Erro na Simulação", f"Ocorreu um erro durante a simulação ou análise: {e}")
             # Atualiza a área de texto com o erro
             self.output_text.configure(state='normal')
             self.output_text.insert(tk.END, f"\n\nERRO: {e}")
             self.output_text.configure(state='disabled')


        # Reabilita o botão
        self.start_button.config(state=tk.NORMAL)
        self.progress_label.config(text="Pronto.")


# --- Ponto de Entrada Principal ---
if __name__ == "__main__":
    root = tk.Tk()
    app = SimulationApp(root)
    root.mainloop()
