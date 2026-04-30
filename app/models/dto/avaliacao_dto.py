from dataclasses import dataclass, field
from datetime import date
from app.models.dto.aplicacao_dto import AplicacaoDTO

@dataclass
class AvaliacaoDTO:
    id: int
    data: date
    fisioterapeuta_nome: str
    observacoes: str | None
    aplicacoes: list[AplicacaoDTO] = field(default_factory=list)