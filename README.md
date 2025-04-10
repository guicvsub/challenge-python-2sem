# challenge-python-2sem
# Dashboard Rede Âncora - Documentação

## 👨‍💻 Autores
- **Gabriel Souza Fiore** - RM553710
- **Guilherme Santiago** - RM552321

## ℹ️ Sobre o Projeto
Dashboard interativo desenvolvido em Python/Streamlit para análise de dados da Rede Âncora, implementando:

- 🔀 Ordenação com QuickSort
- 🏆 Filtragem Top-K com Heap
- 🔍 Busca por prefixo com Árvore Binária

## ⚠️ Problema no Deploy
O arquivo `requirements.txt` não foi suficiente para garantir o funcionamento no Streamlit Cloud devido a problemas com a dependência `openpyxl`.

### Solução Implementada
Adicionamos verificação e instalação automática no código principal:

```python
try:
    import openpyxl
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openpyxl"])
    import openpyxl