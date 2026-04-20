
from sqlalchemy import Column, Integer, String
from app.database import Base



class Fisioterapeuta(Base):
    __tablename__ = 'fisioterapeuta'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    registro_crefito = Column(String(255), nullable=False, unique=True)
    
    def __repr__(self):
        return f"<Fisioterapeuta(id={self.id}, nome='{self.nome}', email='{self.email}', registro_crefito='{self.registro_crefito}')>"