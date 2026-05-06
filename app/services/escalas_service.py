from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.escala import Escala

def obter_escalas(
    session: Session, 
    skip: int = 0, 
    limit: int = 100
) -> list[Escala]:
    """
    Retorna as escalas cadastradas no banco de dados, 
    ordenadas alfabeticamente.
    """
    stmt = select(Escala).order_by(Escala.nome).offset(skip).limit(limit)
    
    return list(session.scalars(stmt).all())

def obter_escala_por_id(session: Session, id_escala: int) -> Escala | None:
    """
    Retorna a escala correspondente ao ID fornecido, ou None se não encontrada.
    """
    return session.get(Escala, id_escala)