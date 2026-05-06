from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Fisioterapeuta(Base):
    __tablename__ = 'fisioterapeuta'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    registro_crefito: Mapped[str] = mapped_column(String(255), unique=True)
    
    avaliacoes: Mapped[list["Avaliacao"]] = relationship(back_populates="fisioterapeuta")
    
    def __repr__(self):
        return f"<Fisioterapeuta(id={self.id}, nome='{self.nome}', email='{self.email}', registro_crefito='{self.registro_crefito}')>"