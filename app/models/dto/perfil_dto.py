
from dataclasses import dataclass, field
from app.models.dto.avaliacao_dto import AvaliacaoDTO

@dataclass
class PerfilDTO:
    id: int
    nome: str
    data_nascimento: str
    data_cadastro: str
    idade: int
    total_avaliacoes: int
    avaliacoes: list[AvaliacaoDTO] = field(default_factory=list)