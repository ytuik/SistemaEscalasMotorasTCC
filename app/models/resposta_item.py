from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class RespostaItem(Base):
    __tablename__ = 'resposta_item'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_aplicacao_escala: Mapped[int] = mapped_column(ForeignKey('aplicacao_escala.id'))
    id_item_escala: Mapped[int] = mapped_column(ForeignKey('item_escala.id'))
    pontuacao: Mapped[int]  # Em segundos para escalas de tempo
    
    aplicacao_escala: Mapped["AplicacaoEscala"] = relationship(back_populates="respostas")
    item_escala: Mapped["ItemEscala"] = relationship(back_populates="respostas_item")
    
    def __repr__(self):
        return f"<RespostaItem(id={self.id}, id_aplicacao_escala={self.id_aplicacao_escala}, id_item_escala={self.id_item_escala}, pontuacao={self.pontuacao})>"