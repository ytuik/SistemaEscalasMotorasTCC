from dataclasses import dataclass, field
from datetime import date

from app.models.dto.alerta_dto import AlertaDTO
from app.models.dto.aplicacao_dto import AplicacaoDTO


@dataclass
class ResumoExecutivoDTO:
    paciente_nome: str
    data_nascimento: date
    total_avaliacoes: int
    data_ultima_avaliacao: date | None
    ultima_pontuacao_por_escala: list[AplicacaoDTO] = field(default_factory=list)
    alertas: list[AlertaDTO] = field(default_factory=list)