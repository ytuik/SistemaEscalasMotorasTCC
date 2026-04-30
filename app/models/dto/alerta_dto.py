from dataclasses import dataclass
from datetime import date


@dataclass
class AlertaDTO:
    escala_nome: str
    pontuacao: int | None
    pontuacao_corte: int | None
    data_avaliacao: date