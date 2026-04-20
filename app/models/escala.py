from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database import Base

class Escala(Base):
    __tablename__ = 'escala'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(255), nullable=False, unique=True)
    descricao = Column(Text, nullable=True)
    pontuacao_maxima = Column(Integer, nullable=True)
    pontuacao_corte = Column(Integer, nullable=True)
    
    itens = relationship("ItemEscala", back_populates="escala", cascade="all, delete-orphan")
    aplicacoes_escala = relationship("AplicacaoEscala", back_populates="escala", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Escala(id={self.id}, nome='{self.nome}', descricao='{self.descricao}')>"