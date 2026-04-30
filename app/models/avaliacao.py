from sqlalchemy import Column, Integer, Text, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Avaliacao(Base):
    __tablename__ = 'avaliacao'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_paciente = Column(Integer, ForeignKey('paciente.id'), nullable=False)
    id_fisioterapeuta = Column(Integer, ForeignKey('fisioterapeuta.id'), nullable=False)
    data = Column(Date, nullable=False)
    observacoes = Column(Text, nullable=True)
    
    paciente = relationship("Paciente", back_populates="avaliacoes")
    aplicacoes_escala = relationship("AplicacaoEscala", back_populates="avaliacao", cascade="all, delete-orphan")
    fisioterapeuta = relationship("Fisioterapeuta", back_populates="avaliacoes")
    
    def __repr__(self):
        return f"<Avaliacao(id={self.id}, id_paciente={self.id_paciente}, id_fisioterapeuta={self.id_fisioterapeuta}, data={self.data})>"