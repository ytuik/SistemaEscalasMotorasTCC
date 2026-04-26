from datetime import date


def parse_data(valor: str) -> date:
    """
    Converte uma string de data para objeto date.
    Aceita DD-MM-AAAA, DD/MM/AAAA, AAAA-MM-DD e AAAA/MM/DD para ser tolerante a variações.
    """
    valor = valor.strip()

    for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d", "%Y/%m/%d"):
        try:
            from datetime import datetime
            return datetime.strptime(valor, fmt).date()
        except ValueError:
            continue

    raise ValueError(f"Formato de data não reconhecido: '{valor}'")