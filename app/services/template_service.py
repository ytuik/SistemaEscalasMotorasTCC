"""
Template_Service.py - Gerenciamento de templates de avaliação

Resposabilidades:
    - Verificar a existência de templates de avaliação pré-definidos e gera-los caso não existam.
    - Criar uma cópia preenchível para cada nova avaliação.
    - Abrir a pasta de templates para o usuário, facilitando o acesso e a organização dos arquivos.
"""
from asyncio import subprocess
import logging
import os
import platform
import re
import shutil
from datetime import date
from pathlib import Path


logger = logging.getLogger(__name__)

TEMPLATE_PATH = Path("data/templates/avaliacao_template.xlsx")
AVALIACOES_PATH = Path("data/avaliacoes")

def _sanitizar_nome_arquivo(nome: str) -> str:
    """
    Remove caracteres que são inválidos para nomes de arquivos no Windows/Linux/Mac.
    Ex: 'João / Silva?' vira 'Joao_Silva'
    """
    # Substitui espaços e barras por underscore
    nome = re.sub(r'[ /\\|]', '_', nome)
    # Remove caracteres especiais proibidos pelo OS
    nome = re.sub(r'[<>:"?*]', '', nome)
    # Remove underscores duplicados
    nome = re.sub(r'_+', '_', nome)
    return nome.strip('_')

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
    nome_sanitizado = _sanitizar_nome_arquivo(nome_paciente)
    data_str = data.strftime('%d-%m-%Y')
    
    nome_arquivo = f"{nome_sanitizado}_{data_str}.xlsx"
    destino = AVALIACOES_PATH / nome_arquivo
    
    contador = 1
    while destino.exists():
        nome_arquivo = f"{nome_sanitizado}_{data_str}_{contador}.xlsx"
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
            subprocess.run(["open", str(pasta)], check=True)
        else:  # Linux e outros
            subprocess.run(["xdg-open", str(pasta)], check=True)
            
    except Exception as e:
        logger.error(f"Não foi possível abrir a pasta de templates: {e}")
        logger.info(f"Por favor, acesse manualmente: {pasta}")

def iniciar_avaliacao_xlsx(nome_paciente: str, data_avaliacao: date | None = None) -> Path:
    """Inicia uma nova avaliação criando uma cópia do template e abre a pasta de avaliações."""
    arquivo = criar_copia_template_avaliacao(nome_paciente, data_avaliacao)
    abrir_pasta_templates(arquivo)
    return arquivo