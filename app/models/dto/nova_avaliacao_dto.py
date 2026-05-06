from dataclasses import dataclass, field
from datetime import date

from app.models.dto.aplicacao_input_dto import AplicacaoInputDTO


@dataclass
class NovaAvaliacaoDTO:
    nome_paciente: str
    data_nascimento: date
    fisioterapeuta_id: int
    data_avaliacao: date
    observacoes: str | None = None
    aplicacoes: list[AplicacaoInputDTO] = field(default_factory=list)