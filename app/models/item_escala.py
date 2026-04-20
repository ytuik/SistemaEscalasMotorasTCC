from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class ItemEscala(Base):
    __tablename__ = 'item_escala'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_escala = Column(Integer, ForeignKey('escala.id'), nullable=False)
    numero_item = Column(Integer, nullable=False, autoincrement=True, unique=True)
    descricao = Column(Text, nullable=False)
    pontuacao_maxima = Column(Integer, nullable=True)
    
    escala = relationship("Escala", back_populates="itens")
    respostas_item = relationship("RespostaItem", back_populates="item_escala")
    
    def __repr__(self):
        return f"<ItemEscala(id={self.id}, id_escala={self.id_escala}, numero_item={self.numero_item}, descricao='{self.descricao}', pontuacao_maxima={self.pontuacao_maxima})>"