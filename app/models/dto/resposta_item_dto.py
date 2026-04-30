from dataclasses import dataclass


@dataclass
class RespostaItemDTO:
    numero_item: int
    descricao: str
    pontuacao: int
    pontuacao_maxima: int | None