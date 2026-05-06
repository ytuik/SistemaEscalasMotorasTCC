"""
Avaliacao_Service - Logica central para a avaliacao, incluindo a criacao de avaliacoes, aplicacao de avaliacoes, e calculo de resultados.

Responsabilidades:
- Criar novas avaliacoes com base em escalas e itens de escala.
- Permitir cadastro via arquivo CSV e entrada manual.
- Aplicar avaliacoes a pacientes, registrando respostas e calculando pontuacao total.
- Fornecer resultados e interpretacoes com base nas pontuacoes calculadas.
"""

from datetime import date
from sqlalchemy.orm import Session, joinedload
from app.exceptions import (
    FisioterapeutaNaoEncontradoError,
    EscalaNaoEncontradaError,
    ItemEscalaNaoEncontradoError,
    PontuacaoInvalidaError,
)
from app.models import Escala, ItemEscala, Avaliacao, RespostaItem, AplicacaoEscala, escala, paciente
from app.models import fisioterapeuta
from app.models.dto.aplicacao_input_dto import AplicacaoInputDTO
from app.models.dto.nova_avaliacao_dto import NovaAvaliacaoDTO
from app.models.fisioterapeuta import Fisioterapeuta
from app.services.paciente_service import obter_ou_criar_paciente


def registrar_avaliacao(
    session: Session,
    payload: NovaAvaliacaoDTO
    ) -> Avaliacao:

    """
    Registra uma avaliação completa para um paciente.

    Se o paciente ainda não existir no banco (identificado por nome +
    data de nascimento), ele é criado automaticamente — pois o paciente
    só é cadastrado no momento da primeira avaliação.

    Parâmetros
    ----------
    session : Session
        Sessão SQLAlchemy ativa.
    payload : NovaAvaliacaoDTO
        Dados da nova avaliação a ser registrada.
    data_avaliacao : date
        Data em que a avaliação foi realizada.
    observacoes : str, opcional
        Observações clínicas livres da sessão.
    escalas_respostas : list[dict]
        Lista de escalas aplicadas. Cada item deve ter o formato:
        {
            "escala_nome": "Escala de Equilíbrio de Berg",
            "respostas": {1: 3, 2: 4, 3: 2, ...}  # {numero_item: pontuacao}
        }

    Retorna
    -------
    Avaliacao
        Objeto da avaliação criada com todas as aplicações e respostas.
    """

    # Busca fisioterapeuta existente ou lança erro se não encontrado
    fisioterapeuta = session.get(Fisioterapeuta, payload.fisioterapeuta_id)
    if not fisioterapeuta:
        raise FisioterapeutaNaoEncontradoError(payload.fisioterapeuta_id)
    
    paciente = obter_ou_criar_paciente(session, payload.nome_paciente, payload.data_nascimento, payload.data_avaliacao)
    
    avaliacao = Avaliacao(
        paciente=paciente,
        fisioterapeuta=fisioterapeuta,
        data=payload.data_avaliacao,
        observacoes=payload.observacoes
    )
    
    
    for bloco_respostas in payload.aplicacoes:
        _registrar_aplicacao_escala(session, avaliacao, bloco_respostas)
    
    session.add(avaliacao)
    return avaliacao
        
        
def _registrar_aplicacao_escala(session: Session, avaliacao: Avaliacao, aplicacao_dto: AplicacaoInputDTO):
    """Registra a aplicação de uma escala em uma avaliação, incluindo as respostas dos itens."""
    
    escala = session.query(Escala).options(
        joinedload(Escala.itens)
    ).filter_by(id=aplicacao_dto.id_escala).first()
    if not escala:
        raise EscalaNaoEncontradaError(aplicacao_dto.id_escala)
    
    aplicacao = AplicacaoEscala(escala=escala)
    pontuacao_soma = 0
    
    itens_por_numero = {item.numero_item: item for item in escala.itens}
    
    for resposta in aplicacao_dto.respostas:
        item = itens_por_numero.get(resposta.numero_item)
        
        if not item:
            raise ItemEscalaNaoEncontradoError(resposta.numero_item, escala.nome)
        
        if (item.pontuacao_maxima is not None and not (0 <= resposta.pontuacao <= item.pontuacao_maxima)):
            raise PontuacaoInvalidaError(item.descricao, resposta.pontuacao, item.pontuacao_maxima)
        
        resposta_obj = RespostaItem(
            item_escala=item,
            pontuacao=int(resposta.pontuacao)
        )
        aplicacao.respostas.append(resposta_obj)
        pontuacao_soma += resposta.pontuacao
        
    aplicacao.pontuacao_total = pontuacao_soma
    avaliacao.aplicacoes_escala.append(aplicacao)