from sqlalchemy.orm import Session
from app.models.fisioterapeuta import Fisioterapeuta


def obter_fisioterapeuta_por_crefito(session: Session, crefito: str) -> Fisioterapeuta | None:
    return session.query(Fisioterapeuta).filter_by(registro_crefito=crefito).first()

def cadastrar_fisioterapeuta(session: Session, nome: str, registro_crefito: str) -> Fisioterapeuta:
    fisioterapeuta = Fisioterapeuta(nome=nome, registro_crefito=registro_crefito)
    session.add(fisioterapeuta)
    session.commit()
    return fisioterapeuta

def listar_fisioterapeutas(session: Session) -> list[Fisioterapeuta]:
    return session.query(Fisioterapeuta).order_by(Fisioterapeuta.nome).all()