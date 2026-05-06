from dataclasses import dataclass, field, field

from app.models.dto.resposta_input_dto import RespostaInputDTO


@dataclass
class AplicacaoInputDTO:
    id_escala: int
    respostas: list[RespostaInputDTO] = field(default_factory=list)