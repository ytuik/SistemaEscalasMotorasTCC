from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Escala(Base):
    __tablename__ = 'escala'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(255), unique=True)
    descricao: Mapped[str | None] = mapped_column(Text)
    pontuacao_maxima: Mapped[int | None]
    pontuacao_corte: Mapped[int | None]
    
    itens: Mapped[list["ItemEscala"]] = relationship(back_populates="escala", cascade="all, delete-orphan")
    aplicacoes_escala: Mapped[list["AplicacaoEscala"]] = relationship(back_populates="escala", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Escala(id={self.id}, nome='{self.nome}')>"