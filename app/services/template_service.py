"""
Template_Service.py - Gerenciamento de templates de avaliação

Resposabilidades:
    - Verificar a existência de templates de avaliação pré-definidos e gera-los caso não existam.
    - Criar uma cópia preenchível para cada nova avaliação.
    - Abrir a pasta de templates para o usuário, facilitando o acesso e a organização dos arquivos.
"""
import os
import platform
import shutil
from datetime import date
from pathlib import Path



TEMPLATE_PATH = Path("data/templates/avaliacao_template.xlsx")
AVALIACOES_PATH = Path("data/avaliacoes")

def verificar_template():
    """Verifica se o template de avaliação existe. Se não existir, gera um novo template."""
    if not TEMPLATE_PATH.exists():
        from scripts.gerar_template_avaliacao import gerar_template_avaliacao
        TEMPLATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        gerar_template_avaliacao(TEMPLATE_PATH)

def criar_copia_template_avaliacao(nome_paciente: str, data_avaliacao: date| None = None) -> Path:
    """Cria uma cópia do template de avaliação para uma nova avaliação.

    O arquivo é salvo em:
        data/avaliacoes/{nome_paciente}_{DD-MM-YYYY}.xlsx
        
    Parametros:
        nome_paciente (str): O nome do paciente.
        data_avaliacao (date, opcional): A data da avaliação. Se não fornecida, usa a data atual.
        
    Retorna:
        Path: O caminho para o arquivo da nova avaliação.
    """
    
    verificar_template()
    AVALIACOES_PATH.mkdir(parents=True, exist_ok=True)
    data = data_avaliacao or date.today()
    nome_arquivo = f"{nome_paciente}_{data.strftime('%d-%m-%Y')}.xlsx"
    destino = AVALIACOES_PATH / nome_arquivo
    
    contador = 1
    while destino.exists():
        nome_arquivo = f"{nome_paciente}_{data.strftime('%d-%m-%Y')}_{contador}.xlsx"
        destino = AVALIACOES_PATH / nome_arquivo
        contador += 1
    
    shutil.copy(TEMPLATE_PATH, destino)
    return destino

def abrir_pasta_templates(caminho_arquivo: Path):
    """Abre a pasta de templates para o usuário."""
    pasta = caminho_arquivo.parent.resolve()
    sistema = platform.system()
    try:
        if sistema == "Windows":
            os.startfile(pasta)
        elif sistema == "Darwin":  # macOS
            os.system(f"open {pasta}")
        else:  # Linux e outros
            os.system(f"xdg-open {pasta}")
    except Exception as e:
        print(f"Não foi possível abrir a pasta de templates: {e}")
        print(f"Por favor, acesse manualmente: {pasta}")
        
def iniciar_avaliacao_xlsx(nome_paciente: str, data_avaliacao: date| None = None) -> Path:
    
    """Inicia uma nova avaliação criando uma cópia do template e abre a pasta de avaliações."""
    arquivo = criar_copia_template_avaliacao(nome_paciente, data_avaliacao)
    print(f"Avaliação criada: {arquivo}")
    abrir_pasta_templates(arquivo)