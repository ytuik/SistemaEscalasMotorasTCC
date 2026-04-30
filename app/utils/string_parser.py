from datetime import date
from dateutil import parser as dtparser


def calcular_idade(data_nascimento: date) -> int:
    """Calcula a idade do paciente com base na data de nascimento."""
    hoje = date.today()
    idade = hoje.year - data_nascimento.year - ((hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day))
    return idade

def parse_data(valor: str) -> date:
    return dtparser.parse(valor, dayfirst=True).date()
