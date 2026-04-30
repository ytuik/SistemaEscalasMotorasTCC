from dataclasses import dataclass
from datetime import date

from app.models.dto.resposta_item_dto import RespostaItemDTO


@dataclass
class PontoHistoricoDTO:
    data: date
    avaliacao_id: int
    pontuacao: int | None
    pontuacao_maxima: int | None
    pontuacao_corte: int | None
    abaixo_do_corte: bool
    respostas_que_variaram: tuple[RespostaItemDTO]
    fisioterapeuta: str