from sqlalchemy import ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class ItemEscala(Base):
    __tablename__ = 'item_escala'
    __table_args__ = (UniqueConstraint('id_escala', 'numero_item', name='uq_item_escala_numero'),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_escala: Mapped[int] = mapped_column(ForeignKey('escala.id'))
    numero_item: Mapped[int]
    descricao: Mapped[str] = mapped_column(Text)
    pontuacao_maxima: Mapped[int | None]
    
    escala: Mapped["Escala"] = relationship(back_populates="itens")
    respostas_item: Mapped[list["RespostaItem"]] = relationship(back_populates="item_escala")
    
    def __repr__(self):
        return f"<ItemEscala(id={self.id}, id_escala={self.id_escala}, numero_item={self.numero_item})>"