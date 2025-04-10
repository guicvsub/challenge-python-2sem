import streamlit as st
import pandas as pd

# ----------- Função de leitura de dados ----------- #
@st.cache_data
def carregar_dados():
    df = pd.read_excel("dataset_rede_ancora.xlsx")
    df.columns = [col.strip() for col in df.columns]  # Limpa espaços extras nos nomes das colunas
    return df

# ----------- Algoritmo QuickSort ----------- #
def quicksort(df, coluna):
    if len(df) <= 1:
        return df
    else:
        pivot = df.iloc[0]
        menores = df[df[coluna] < pivot[coluna]]
        iguais = df[df[coluna] == pivot[coluna]]
        maiores = df[df[coluna] > pivot[coluna]]
        return pd.concat([quicksort(menores, coluna), iguais, quicksort(maiores, coluna)])

# ----------- Top K com Heap ----------- #
def top_k(df, coluna, k, tipo='maiores'):
    if tipo == 'maiores':
        return df.nlargest(k, coluna)
    else:
        return df.nsmallest(k, coluna)

# ----------- Árvore de busca binária (implementação aprimorada) ----------- #
class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None

def inserir_na_arvore(root, value):
    """Insere valores mantendo a propriedade de BST"""
    if root is None:
        return Node(value)
    
    # Comparação case-insensitive
    if str(value).lower() < str(root.value).lower():
        root.left = inserir_na_arvore(root.left, value)
    else:
        root.right = inserir_na_arvore(root.right, value)
    return root

def buscar_prefixo_eficiente(node, prefixo, resultados, limite=5):
    """Busca eficiente por prefixo com limite de resultados"""
    if node is None or len(resultados) >= limite:
        return
    
    node_value = str(node.value).lower()
    prefixo = str(prefixo).lower()
    
    # Verifica se o nó atual começa com o prefixo
    if node_value.startswith(prefixo):
        resultados.append(node.value)
    
    # Decide qual ramo explorar primeiro para otimização
    if prefixo < node_value:
        buscar_prefixo_eficiente(node.left, prefixo, resultados, limite)
    if prefixo <= node_value or len(resultados) < limite:
        buscar_prefixo_eficiente(node.right, prefixo, resultados, limite)

def percorrer_em_ordem(node, resultados):
    """Percorre a árvore em ordem"""
    if node is None:
        return
    percorrer_em_ordem(node.left, resultados)
    resultados.append(node.value)
    percorrer_em_ordem(node.right, resultados)

def completar_sugestoes(root, prefixo, minimo=5):
    """Garante pelo menos 'minimo' sugestões"""
    candidatos = []
    buscar_prefixo_eficiente(root, prefixo, candidatos, minimo)
    
    # Se ainda não tem o mínimo, busca os mais próximos em ordem
    if len(candidatos) < minimo:
        todos = []
        percorrer_em_ordem(root, todos)
        # Filtra os que não estão nos candidatos e são maiores que o prefixo
        extras = [x for x in todos if x not in candidatos and str(x).lower() >= str(prefixo).lower()]
        candidatos.extend(extras[:minimo - len(candidatos)])
    
    return candidatos[:minimo]

@st.cache_data
def construir_arvore_eficiente(valores):
    """Constroi a árvore de forma balanceada para melhor performance"""
    valores_unicos = sorted(set(str(v) for v in valores if pd.notna(v) and str(v).strip() != ""))
    return _construir_arvore_balanceada(valores_unicos)

def _construir_arvore_balanceada(valores_ordenados):
    """Constroi uma árvore balanceada a partir de valores ordenados"""
    if not valores_ordenados:
        return None
    
    meio = len(valores_ordenados) // 2
    root = Node(valores_ordenados[meio])
    root.left = _construir_arvore_balanceada(valores_ordenados[:meio])
    root.right = _construir_arvore_balanceada(valores_ordenados[meio+1:])
    return root

# ----------- INTERFACE STREAMLIT ----------- #
st.set_page_config(page_title="Dashboard Rede Âncora", layout="wide")
st.title("📊 Dashboard Rede Âncora")

df = carregar_dados()

# ----------- Ordenação com QuickSort ----------- #
col1, col2 = st.columns(2)

with col1:
    coluna_ordenar = st.selectbox("🔀 Escolha a coluna para ordenar:", df.select_dtypes(include='number').columns)
    ordem = st.radio("Ordem:", ["Crescente", "Decrescente"], key="ordem_quicksort")
    if st.button("Aplicar QuickSort"):
        df_ordenado = quicksort(df, coluna_ordenar)
        if ordem == "Decrescente":
            df_ordenado = df_ordenado[::-1]
        st.dataframe(df_ordenado)

# ----------- Ordenação Parcial com Heap ----------- #
with col2:
    coluna_k = st.selectbox("🏆 Coluna para ordenação parcial:", df.select_dtypes(include='number').columns, key="coluna_k")
    k = st.slider("K (número de elementos)", 1, 10, 5, key="k_slider")
    tipo_k = st.radio("Tipo:", ["Maiores", "Menores"], key="tipo_k")
    if st.button("Ver Ordenação Parcial"):
        tipo = "maiores" if tipo_k == "Maiores" else "menores"
        resultado_k = top_k(df, coluna_k, k, tipo)
        st.dataframe(resultado_k)

# ----------- Autocomplete com Árvore Binária ----------- #
st.subheader("🔍 Autocomplete de ID do Mecânico (Árvore Binária)")
input_text = st.text_input("Digite o início do ID (ex: MEC0):", key="autocomplete_input")

if input_text and len(input_text.strip()) >= 1:  # Pelo menos 1 caractere
    arvore = construir_arvore_eficiente(df["ID_Mecanico"])
    sugestoes = completar_sugestoes(arvore, input_text.strip(), minimo=5)
    
    if sugestoes:
        st.write(f"🔎 Sugestões encontradas ({len(sugestoes)}):")
        for i, item in enumerate(sugestoes, 1):
            st.markdown(f"{i}. `{item}`")
    else:
        st.warning("Nenhum ID encontrado com esse prefixo.")

# ----------- Visualização Completa ----------- #
st.subheader("📄 Tabela Completa")
st.dataframe(df)