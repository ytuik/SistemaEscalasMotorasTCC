"""
Paciente_Service - Responsável por toda a lógica relacionada a pacientes, incluindo criação, atualização e consulta de informações dos pacientes.
"""

from datetime import date
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, contains_eager
from app.exceptions import EscalaNaoEncontradaError, PacienteNaoEncontradoError
from app.models.aplicacao_escala import AplicacaoEscala
from app.models.avaliacao import Avaliacao
from app.models.dto.alerta_dto import AlertaDTO
from app.models.dto.aplicacao_dto import AplicacaoDTO
from app.models.dto.avaliacao_dto import AvaliacaoDTO
from app.models.dto.historico_escala_dto import HistoricoEscalaDTO
from app.models.dto.perfil_dto import PerfilDTO
from app.models.dto.ponto_historico_dto import PontoHistoricoDTO
from app.models.dto.resposta_item_dto import RespostaItemDTO
from app.models.dto.resumo_executivo_dto import ResumoExecutivoDTO
from app.models.paciente import Paciente
from app.models.resposta_item import RespostaItem
from app.services.escalas_service import obter_escala_por_id
from app.utils.string_parser import calcular_idade


def obter_paciente_por_id(session: Session, paciente_id: int) -> Paciente | None:
    return session.get(Paciente, paciente_id)

def obter_pacientes_por_nome(session: Session, nome: str) -> list[Paciente]:
    return session.query(Paciente).filter(Paciente.nome.ilike(f"%{nome}%")).all()

def obter_paciente_por_nome_data_nascimento(
    session: Session, nome: str, data_nascimento: date
) -> Paciente | None:
    stmt = select(Paciente).where(
        Paciente.nome == nome, 
        Paciente.data_nascimento == data_nascimento
    )
    return session.scalars(stmt).first()

def obter_ou_criar_paciente(
    session: Session, nome: str, data_nascimento: date, data_cadastro: date
) -> Paciente:
    paciente = obter_paciente_por_nome_data_nascimento(session, nome, data_nascimento)
    if not paciente:
        paciente = Paciente(nome=nome, data_nascimento=data_nascimento, data_cadastro=data_cadastro)
        session.add(paciente)
        session.flush()
    return paciente

def listar_pacientes(session: Session, skip: int = 0, limit: int = 100) -> list[Paciente]:
    """Retorna uma lista de pacientes cadastrados com paginação."""
    stmt = select(Paciente).order_by(Paciente.nome).offset(skip).limit(limit)
    return list(session.scalars(stmt).all())

def perfil_completo(session: Session, paciente_id: int) -> PerfilDTO:
    """
    Retorna o perfil completo do paciente com todas as avaliações e aplicações associadas e respostas individuais em ordem cronológica.
    """
    paciente = _obter_paciente_com_avaliacoes_completas(session, paciente_id)

    if not paciente:
        raise PacienteNaoEncontradoError(paciente_id)

    avaliacoes_dto = []
    for avaliacao in sorted(paciente.avaliacoes, key=lambda a: a.data):
        aplicacoes_dto = [_aplicacao_to_dto(ap) for ap in avaliacao.aplicacoes_escala]
        avaliacoes_dto.append(AvaliacaoDTO(
            id=avaliacao.id,
            data=avaliacao.data,
            fisioterapeuta_nome=avaliacao.fisioterapeuta.nome,
            observacoes=avaliacao.observacoes,
            aplicacoes=aplicacoes_dto
        ))

    return PerfilDTO(
        id=paciente.id,
        nome=paciente.nome,
        data_nascimento=paciente.data_nascimento.isoformat(),
        data_cadastro=paciente.data_cadastro.isoformat(),
        idade=calcular_idade(paciente.data_nascimento),
        total_avaliacoes=len(paciente.avaliacoes),
        avaliacoes=avaliacoes_dto
    )

def historico_escala(
    session: Session,
    id_paciente: int,
    id_escala: int
) -> HistoricoEscalaDTO:
    
    # 1. Busca otimizada: Carrega APENAS as avaliações e aplicações desta escala específica
    stmt = (
        select(Paciente)
        .join(Paciente.avaliacoes)
        .join(Avaliacao.aplicacoes_escala)
        .join(AplicacaoEscala.respostas)
        .join(RespostaItem.item_escala)
        .where(
            Paciente.id == id_paciente,
            AplicacaoEscala.id_escala == id_escala
        )
        .options(
            contains_eager(Paciente.avaliacoes)
            .contains_eager(Avaliacao.aplicacoes_escala)
            .contains_eager(AplicacaoEscala.respostas)
            .contains_eager(RespostaItem.item_escala)
        )
        .order_by(Avaliacao.data)
    )
    paciente = session.scalars(stmt).first()
    
    if not paciente:
        raise PacienteNaoEncontradoError(id_paciente)

    escala = obter_escala_por_id(session, id_escala)
    if not escala:
        raise EscalaNaoEncontradaError(id_escala)

    pontos = []
    respostas_anteriores: dict[int, int] | None = None  

    for avaliacao in paciente.avaliacoes:
        aplicacao = avaliacao.aplicacoes_escala[0] 
        
        abaixo = (
            escala.pontuacao_corte is not None
            and aplicacao.pontuacao_total is not None
            and aplicacao.pontuacao_total < escala.pontuacao_corte
        )

        respostas_atuais = {
            resposta.item_escala.numero_item: resposta.pontuacao
            for resposta in aplicacao.respostas
        }

        respostas_variadas = []
        for resposta in aplicacao.respostas:
            numero = resposta.item_escala.numero_item
            # É variação se for a primeira vez OU se a pontuação for diferente
            if respostas_anteriores is None or respostas_anteriores.get(numero) != resposta.pontuacao:
                respostas_variadas.append(resposta)

        items_com_variacao = tuple(
            RespostaItemDTO(
                numero_item=r.item_escala.numero_item,
                descricao=r.item_escala.descricao,
                pontuacao=r.pontuacao,
                pontuacao_maxima=r.item_escala.pontuacao_maxima
            )
            for r in sorted(respostas_variadas, key=lambda r: r.item_escala.numero_item)
        )

        pontos.append(PontoHistoricoDTO(
            data=avaliacao.data,
            avaliacao_id=avaliacao.id,
            pontuacao=aplicacao.pontuacao_total,
            pontuacao_maxima=escala.pontuacao_maxima,
            pontuacao_corte=escala.pontuacao_corte,
            abaixo_do_corte=abaixo,
            respostas_que_variaram=items_com_variacao,
            fisioterapeuta=avaliacao.fisioterapeuta.nome
        ))

        respostas_anteriores = respostas_atuais

    return HistoricoEscalaDTO(
        paciente_nome=paciente.nome,
        escala_nome=escala.nome,
        pontuacao_corte=escala.pontuacao_corte,
        pontuacao_maxima=escala.pontuacao_maxima,
        pontos=pontos
    )
    
def resumo_executivo(session: Session, paciente_id: int) -> ResumoExecutivoDTO:
    """
    Retorna o resumo clínico do paciente:
    - última pontuação registrada de cada escala
    - alertas para pontuações abaixo do ponto de corte

    É a visão que o fisioterapeuta consulta antes de uma sessão —
    rápida e direta
    """

    paciente = _obter_paciente_com_avaliacoes_completas(session, paciente_id)

    if not paciente:
        raise PacienteNaoEncontradoError(paciente_id)

    ultimas_aplicacoes_por_escala: dict[int, tuple[AplicacaoEscala, date]] = {}
    for avaliacao in paciente.avaliacoes:
        for aplicacao in avaliacao.aplicacoes_escala:
            existente = ultimas_aplicacoes_por_escala.get(aplicacao.id_escala)
            if existente is None or avaliacao.data > existente[1]:
                ultimas_aplicacoes_por_escala[aplicacao.id_escala] = (aplicacao, avaliacao.data)

    ultima_pontuacao = []
    alertas = []
    datas = [avaliacao.data for avaliacao in paciente.avaliacoes]

    for escala_id, (aplicacao, data) in sorted(ultimas_aplicacoes_por_escala.items(), key=lambda x: x[1][1]):
        aplicacao_dto = _aplicacao_to_dto(aplicacao)
        ultima_pontuacao.append(aplicacao_dto)

        if aplicacao_dto.abaixo_do_corte:
            alertas.append(AlertaDTO(
                escala_nome=aplicacao_dto.escala_nome,
                pontuacao=aplicacao_dto.pontuacao_total,
                pontuacao_corte=aplicacao_dto.pontuacao_corte,
                data_avaliacao=data
            ))

    return ResumoExecutivoDTO(
        paciente_nome=paciente.nome,
        data_nascimento=paciente.data_nascimento,
        total_avaliacoes=len(paciente.avaliacoes),
        ultima_pontuacao_por_escala=ultima_pontuacao,
        alertas=alertas,
        data_ultima_avaliacao=max(datas) if datas else None
    )

def _aplicacao_to_dto(aplicacao: AplicacaoEscala) -> AplicacaoDTO:
    abaixo = (
        aplicacao.escala.pontuacao_corte is not None
        and aplicacao.pontuacao_total is not None
        and aplicacao.pontuacao_total < aplicacao.escala.pontuacao_corte
    )
    respostas = [
        RespostaItemDTO(
            numero_item=resposta.item_escala.numero_item,
            descricao=resposta.item_escala.descricao,
            pontuacao=resposta.pontuacao,
            pontuacao_maxima=resposta.item_escala.pontuacao_maxima
        )
        for resposta in sorted(aplicacao.respostas, key=lambda r: r.item_escala.numero_item)
    ]
    return AplicacaoDTO(
        escala_nome=aplicacao.escala.nome,
        pontuacao_total=aplicacao.pontuacao_total,
        pontuacao_maxima=aplicacao.escala.pontuacao_maxima,
        pontuacao_corte=aplicacao.escala.pontuacao_corte,
        abaixo_do_corte=abaixo,
        respostas=respostas
    )
    
def _obter_paciente_com_avaliacoes_completas(session: Session, paciente_id: int) -> Paciente | None:
    """Centraliza a busca do paciente com todos os relacionamentos necessários carregados."""
    stmt = (
            select(Paciente)
            .options(
                # Carrega avaliações, aplicações, respostas e itens
                joinedload(Paciente.avaliacoes)
                .joinedload(Avaliacao.aplicacoes_escala)
                .joinedload(AplicacaoEscala.respostas)
                .joinedload(RespostaItem.item_escala),
                
                # Carrega os dados da escala
                joinedload(Paciente.avaliacoes)
                .joinedload(Avaliacao.aplicacoes_escala)
                .joinedload(AplicacaoEscala.escala) 
            )
            .where(Paciente.id == paciente_id)
        )
    return session.scalars(stmt).first()
