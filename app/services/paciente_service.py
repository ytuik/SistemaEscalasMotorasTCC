"""
Paciente_Service - Responsável por toda a lógica relacionada a pacientes, incluindo criação, atualização e consulta de informações dos pacientes.
"""

from datetime import date
from sqlalchemy.orm import Session
from app.models.paciente import Paciente


def criar_paciente(session: Session, nome: str, data_nascimento: date, data_cadastro: date) -> Paciente:
    paciente = Paciente(nome=nome, data_nascimento=data_nascimento, data_cadastro=data_cadastro)
    session.add(paciente)
    session.commit()
    return paciente

def obter_paciente_por_id(
    session: Session,
    paciente_id: int
) -> Paciente | None:
    return session.query(Paciente).filter_by(id=paciente_id).first()

def obter_paciente_por_nome_data_nascimento(
    session: Session,
    nome: str,
    data_nascimento: date
) -> Paciente | None:
    return session.query(Paciente).filter_by(nome=nome, data_nascimento=data_nascimento).first()

def obter_ou_criar_paciente(
    session: Session,
    nome: str,
    data_nascimento: date,
    data_cadastro: date
) -> Paciente:
    paciente = obter_paciente_por_nome_data_nascimento(session, nome, data_nascimento)
    if not paciente:
        paciente = Paciente(nome=nome, data_nascimento=data_nascimento, data_cadastro=data_cadastro)
        session.add(paciente)
        session.flush()
    return paciente