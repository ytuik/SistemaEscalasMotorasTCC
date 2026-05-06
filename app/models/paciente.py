from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from datetime import date

class Paciente(Base):
    __tablename__ = 'paciente'
    __table_args__ = (UniqueConstraint('nome', 'data_nascimento', name='uq_paciente_nome_nasc'),)

    id: Mapped[int]  = mapped_column(primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(255))
    data_nascimento: Mapped[date]
    data_cadastro: Mapped[date]

    avaliacoes: Mapped[list["Avaliacao"]] = relationship(back_populates="paciente")
    
    def __repr__(self):
        return f"<Paciente(id={self.id}, nome='{self.nome}', data_nascimento={self.data_nascimento}, data_cadastro={self.data_cadastro})>"