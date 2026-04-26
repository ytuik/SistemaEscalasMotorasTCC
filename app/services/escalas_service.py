from sqlalchemy.orm import Session
from app.models.escala import Escala


def obter_escalas(session: Session) -> list[Escala]:
    """Retorna todas as escalas cadastradas no banco de dados."""
    return session.query(Escala).all()
