from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class AplicacaoEscala(Base):
    __tablename__ = 'aplicacao_escala'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_avaliacao = Column(Integer, ForeignKey('avaliacao.id'), nullable=False)
    id_escala = Column(Integer, ForeignKey('escala.id'), nullable=False)
    pontuacao_total = Column(Integer, nullable=False, default=0)
    
    avaliacao = relationship("Avaliacao", back_populates="aplicacoes_escala")
    escala = relationship("Escala", back_populates="aplicacoes_escala")
    respostas = relationship("RespostaItem" , back_populates="aplicacao_escala", cascade="all, delete-orphan")
    
    def calcular_pontuacao_total(self):
        """Voltar aqui porque a pontuação total deve ser calculada a partir das escalas que foram usadas"""
        self.pontuacao_total = sum(resposta.pontuacao for resposta in self.respostas if resposta.pontuacao is not None)
    
    def __repr__(self):
        return f"<AplicacaoEscala(id={self.id}, id_avaliacao={self.id_avaliacao}, id_escala={self.id_escala}, pontuacao_total={self.pontuacao_total})>"