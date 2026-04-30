from dataclasses import dataclass, field
from app.models.dto.resposta_item_dto import RespostaItemDTO

@dataclass
class AplicacaoDTO:
    escala_nome: str
    pontuacao_total: int | None
    pontuacao_maxima: int | None
    pontuacao_corte: int | None
    abaixo_do_corte: bool
    respostas: list[RespostaItemDTO] = field(default_factory=list)

    @property
    def percentual(self) -> float | None:
        """Percentual atingido em relação ao máximo (quando aplicável)."""
        if self.pontuacao_total is not None and self.pontuacao_maxima:
            return round(self.pontuacao_total / self.pontuacao_maxima * 100, 1)
        return None