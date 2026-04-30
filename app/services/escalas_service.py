from sqlalchemy.orm import Session
from app.models.escala import Escala


def obter_escalas(session: Session) -> list[Escala]:
    """Retorna todas as escalas cadastradas no banco de dados."""
    return session.query(Escala).all()

def obter_escala_por_id(session: Session, id_escala: int) -> Escala | None:
    """Retorna a escala correspondente ao ID fornecido, ou None se não encontrada."""
    return session.get(Escala, id_escala)

    
