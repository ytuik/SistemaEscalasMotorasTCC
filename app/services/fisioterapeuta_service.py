from sqlalchemy.orm import Session
from app.models.fisioterapeuta import Fisioterapeuta


def obter_fisioterapeuta_por_crefito(session: Session, crefito: str) -> Fisioterapeuta | None:
    return session.query(Fisioterapeuta).filter_by(registro_crefito=crefito).first()