from datetime import date
from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Avaliacao(Base):
    __tablename__ = 'avaliacao'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_paciente: Mapped[int] = mapped_column(ForeignKey('paciente.id'))
    id_fisioterapeuta: Mapped[int] = mapped_column(ForeignKey('fisioterapeuta.id'))
    data: Mapped[date]
    observacoes: Mapped[str | None] = mapped_column(Text) 
    
    paciente: Mapped["Paciente"] = relationship(back_populates="avaliacoes")
    fisioterapeuta: Mapped["Fisioterapeuta"] = relationship(back_populates="avaliacoes")
    aplicacoes_escala: Mapped[list["AplicacaoEscala"]] = relationship(back_populates="avaliacao", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Avaliacao(id={self.id}, id_paciente={self.id_paciente}, id_fisioterapeuta={self.id_fisioterapeuta}, data={self.data})>"