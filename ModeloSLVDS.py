import pandas as pd
from docplex.mp.model import Model
import re #Manipular as strings do modelo lp

def main():

    #===========================
    
    # Retirando dados das planilhas
    
    #===========================

    read_tempo = pd.read_csv("../Instancias/SLVDS/Dia_1/tprocessamento.csv")
    read_setup = pd.read_csv("../Instancias/SLVDS/Dia_1/setup.csv")
    read_produtos = pd.read_csv("../Instancias/SLVDS/Dia_1/produtos.csv")
    read_mapa_prod_grupo = pd.read_csv("../Instancias/SLVDS/Dia_1/MapaProdGrupo.csv")
    read_M = pd.read_csv("../Instancias/SLVDS/Dia_1/M.csv")
    read_modelos = pd.read_csv("../Instancias/SLVDS/Dia_1/modelos.csv")
    read_num_prod_grupo = pd.read_csv("../Instancias/SLVDS/Dia_1/NumProdutosNoGrupo.csv")


    #===========================
    
    # Conjuntos
    
    #===========================

    CONJ_J = CONJ_J = read_produtos['produto'].tolist()

    CONJ_G = CONJ_G = read_modelos['modelo'].tolist()
    CONJ_G.insert(0,0)

    
    J = len(CONJ_J)
    G = len(CONJ_G)


    #===========================
    
    # Parâmetros
    
    #===========================

    #=======================
    #Tempo processamento
    #=======================

    P = read_tempo['tempo_processamento'].tolist()
    
    #=======================
    #M
    #=======================
    
    M = read_M['M'].tolist()[0]

    #=======================
    #SETUP
    #=======================

    aux_i = read_setup['i'].tolist()
    aux_j = read_setup['j'].tolist()
    aux_setup = read_setup['setup'].tolist()

    s = []

    for prod in range(len(CONJ_J)):
        s.append([0 for prod in range(len(CONJ_J))]) 

    for i, j, valor in zip(aux_i, aux_j, aux_setup):
        s[i][j] = valor 

    #=======================
    #QUANTIDADE DE PRODUTOS EM CADA GRUPO
    #=======================


    QTD_GRUPOS = read_num_prod_grupo['NumeroProdNoGrupo'].tolist()
    QTD_GRUPOS.insert(0,0)

    #===========================
    
    # Sub-conjunto
    
    #===========================


    aux_produtos = read_mapa_prod_grupo['produto'].tolist()
    aux_grupos = read_mapa_prod_grupo['grupo'].tolist()
    SUBCONJ_Jn = []

    for grupo in CONJ_G:
        SUBCONJ_Jn.append([])

    for produto, grupo in zip(aux_produtos, aux_grupos):
        SUBCONJ_Jn[grupo].append(produto)

    print("Produtos - J", CONJ_J, "Quantidade: ", len(CONJ_J), "\n")
    print("Grupos - G", CONJ_G, "Quantidade: ", len(CONJ_J), "\n")
    print("Setup - S", s, "Quantidade: ", len(s), "\n")
    print("Subconjunto - Jn", SUBCONJ_Jn, "Quantidade: ", len(SUBCONJ_Jn), "\n")
    print("Tempo Processamento - P", P, "Quantidade: ", len(P), "\n")    


    #===========================
    
    # Criando modelo
    
    #===========================

    model = Model(name = "Modelo SLVDS")
    
    #===========================
    
    # Declarando as variáveis de decisão
    
    #===========================

    Cmax = model.continuous_var(name="Cmax")
    C = model.continuous_var_dict(keys=CONJ_J, name = "C")
    u = model.binary_var_matrix(keys1=CONJ_J, keys2 = CONJ_J, name = "u")


    #===========================
   
    # Declarando as restrições

    #===========================


    # Restricao 17

    for j in CONJ_J:
        model.add_constraint_(model.sum(u[i,j] for i in CONJ_J if i != j) == 1, ctname = "R17")

    # Restricao 18

    for i in CONJ_J:
        model.add_constraint_(model.sum(u[i,j] for j in CONJ_J if j != i) == 1, ctname = "R18")
    
    # Restricao 24

    #model.add_constraint_(C[j] >= C[i] + (P[i] + s[i,k,j]) * u[i,j] - M(2 - u[i,j] - u[j,k]))
    for i in CONJ_J:
        for j in CONJ_J:
            if i != j and j > 0:
                model.add_constraint_(C[j] >= C[i] + (P[j] + s[i][j]) * u[i,j] - M*(1-u[i,j]), ctname = "R24")

    # Restricao 20

    for j in CONJ_J:
        model.add_constraint_(Cmax >= C[j], ctname = "R20")

    # Restricao 21

    #agrupe{k in modelos}:sum{i in produto, j in produto:MapaProdGrupo[i,k]==1 and MapaProdGrupo[j,k]==1 and i!=j}x[i,j] >=NumeroProdNoGrupo[k]-1;
    for n in CONJ_G:
        model.add_constraint_(model.sum(u[i, j] for i in SUBCONJ_Jn[n] for j in SUBCONJ_Jn[n] if i != j) >= QTD_GRUPOS[n] - 1, ctname="R21")
    
    # Restricao 22

    for j in CONJ_J:
        model.add_constraint_(C[j] >= 0, ctname = "R22")
        
    model.add_constraint_(C[0] == 0, ctname="c0")

    # Restricao 23 está implícita na declaração de u como binary
    
    #===========================
   
    # Declarando função objetivo
    
    #===========================

    objetivo = Cmax

    model.minimize(objetivo)

    #===========================
   
    # Resolução do modelo
    
    #===========================


    
    solucao = model.solve(log_output=True)  
    print(solucao)
    
    # Ordenando as variáveis C em ordem crescente de valor
    C_values = [(j, C[j].solution_value) for j in CONJ_J]  # Cria uma lista de tuplas (índice, valor)
    C_values_sorted = sorted(C_values, key=lambda x: x[1])  # Ordena pela segunda posição (valor)

    # Imprime os índices das variáveis C em ordem crescente de valor
    print("\n===================== VARIÁVEIS C EM ORDEM CRESCENTE (APENAS OS ÍNDICES) =========================\n")
    for j, valor in C_values_sorted:
        print(f"C[{j}]", valor)
