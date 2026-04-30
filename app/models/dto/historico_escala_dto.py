from dataclasses import dataclass, field

from app.models.dto.ponto_historico_dto import PontoHistoricoDTO


@dataclass
class HistoricoEscalaDTO:
    paciente_nome: str
    escala_nome: str
    pontuacao_corte: int | None
    pontuacao_maxima: int | None
    pontos: list[PontoHistoricoDTO] = field(default_factory=list)
    
    @property
    def variacao_total(self) -> int | None:
        """Calcula a variação total da pontuação ao longo do tempo (último ponto - primeiro ponto)."""
        valores = [pontos.pontuacao for pontos in self.pontos if pontos.pontuacao is not None]
        if len(valores) >= 2:
            return valores[-1] - valores[0]
        return None
    
    @property
    def tendencia(self) -> str:
        """Determina a tendência geral da pontuação ao longo do tempo (melhora, piora ou estável)."""
        variacao = self.variacao_total
        if variacao is None:
            return "Sem dados suficientes"
        if variacao > 0:
            return f"Melhora de {variacao} pontos"
        elif variacao < 0:
            return f"Piora de {variacao} pontos"
        else:
            return "Estável"