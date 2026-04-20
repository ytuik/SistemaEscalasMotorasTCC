from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship
from app.database import Base

class Paciente(Base):
    __tablename__ = 'paciente'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(255), nullable=False)
    data_nascimento = Column(Date, nullable=False)
    data_cadastro = Column(Date, nullable=False)
    
    avaliacoes = relationship("Avaliacao", back_populates="paciente")
    
    def __repr__(self):
        return f"<Paciente(id={self.id}, nome='{self.nome}', data_nascimento={self.data_nascimento}, data_cadastro={self.data_cadastro})>"