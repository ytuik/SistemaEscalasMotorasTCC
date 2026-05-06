from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class AplicacaoEscala(Base):
    __tablename__ = 'aplicacao_escala'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_avaliacao: Mapped[int] = mapped_column(ForeignKey('avaliacao.id'))
    id_escala: Mapped[int] = mapped_column(ForeignKey('escala.id'))
    pontuacao_total: Mapped[int] = mapped_column(default=0)

    avaliacao: Mapped["Avaliacao"] = relationship(back_populates="aplicacoes_escala")
    escala: Mapped["Escala"] = relationship(back_populates="aplicacoes_escala")
    respostas: Mapped[list["RespostaItem"]] = relationship(back_populates="aplicacao_escala", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<AplicacaoEscala(id={self.id}, id_avaliacao={self.id_avaliacao}, id_escala={self.id_escala}, pontuacao_total={self.pontuacao_total})>"