from datetime import date
from dateutil import parser as dtparser

def calcular_idade(data_nascimento: date) -> int:
    """Calcula a idade exata considerando anos bissextos e o dia do aniversário."""
    hoje = date.today()
    return hoje.year - data_nascimento.year - ((hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day))

def parse_data(valor: str) -> date:
    """
    Converte uma string de data para um objeto date.
    Suporta múltiplos formatos, priorizando o dia primeiro (DD-MM-YYYY).
    """
    if not valor or str(valor).strip() == "":
        raise ValueError("A data fornecida está vazia.")
    
    return dtparser.parse(str(valor), dayfirst=True).date()