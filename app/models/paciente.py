from sqlalchemy import Column, Integer, String, Date, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class Paciente(Base):
    __tablename__ = 'paciente'
    __table_args__ = (UniqueConstraint('nome', 'data_nascimento', name='uq_paciente_nome_nasc'),)

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(255), nullable=False)
    data_nascimento = Column(Date, nullable=False)
    data_cadastro = Column(Date, nullable=False)
    
    avaliacoes = relationship("Avaliacao", back_populates="paciente")
    
    def __repr__(self):
        return f"<Paciente(id={self.id}, nome='{self.nome}', data_nascimento={self.data_nascimento}, data_cadastro={self.data_cadastro})>"