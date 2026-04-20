from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class RespostaItem(Base):
    __tablename__ = 'resposta_item'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_aplicacao_escala = Column(Integer, ForeignKey('aplicacao_escala.id'), nullable=False)
    id_item_escala = Column(Integer, ForeignKey('item_escala.id'), nullable=False)
    pontuacao = Column(Integer, nullable=False) # Para escalas que usam tempo o valor da pontuação será salvo em segundos
    
    aplicacao = relationship("AplicacaoEscala", back_populates="respostas_item")
    item_escala = relationship("ItemEscala", back_populates="respostas_item")
    
    def __repr__(self):
        return f"<RespostaItem(id={self.id}, id_aplicacao_escala={self.id_aplicacao_escala}, id_item_escala={self.id_item_escala}, pontuacao={self.pontuacao})>"