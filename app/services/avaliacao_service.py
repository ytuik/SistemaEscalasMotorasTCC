"""
Avaliacao_Service - Logica central para a avaliacao, incluindo a criacao de avaliacoes, aplicacao de avaliacoes, e calculo de resultados.

Responsabilidades:
- Criar novas avaliacoes com base em escalas e itens de escala.
- Permitir cadastro via arquivo CSV e entrada manual.
- Aplicar avaliacoes a pacientes, registrando respostas e calculando pontuacao total.
- Fornecer resultados e interpretacoes com base nas pontuacoes calculadas.

Pendente:
- Implementar validacao de dados de entrada.
- Conversao de nome do fisioterapeuta e nome da escala tem que ser feita antes daqui, para evitar problemas de nome duplicado.
- Mudar para receber o id da escala ao invés do nome, para evitar problemas de nome duplicado.
"""

from datetime import date
from sqlalchemy.orm import Session
from app.exceptions import FisioterapeutaNaoEncontradoError, EscalaNaoEncontradaError
from app.exceptions.itemEscalaNaoEncontradoError import ItemEscalaNaoEncontradoError
from app.exceptions.pontuacaoInvalidaError import PontuacaoInvalidaError
from app.models import Escala, ItemEscala, Avaliacao, RespostaItem, AplicacaoEscala
from app.models.fisioterapeuta import Fisioterapeuta
from app.services.paciente_service import obter_ou_criar_paciente




"""
Registra uma avaliação completa para um paciente.

Se o paciente ainda não existir no banco (identificado por nome +
data de nascimento), ele é criado automaticamente — pois o paciente
só é cadastrado no momento da primeira avaliação.

Parâmetros
----------
session : Session
    Sessão SQLAlchemy ativa.
nome_paciente : str
    Nome completo do paciente.
data_nascimento : date
    Data de nascimento do paciente.
fisioterapeuta_id : int
    ID do fisioterapeuta que conduz a avaliação.
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
def registrar_avaliacao(
    session: Session,
    *,
    nome_paciente: str,
    data_nascimento: date,
    fisioterapeuta_id: str,
    data_avaliacao: date,
    observacoes: str | None = None,
    escalas_respostas: list[dict]
    ) -> Avaliacao:
    
        #Busca fisioterapeuta existente ou lança erro se não encontrado
        fisioterapeuta = session.query(Fisioterapeuta).get(fisioterapeuta_id)
        if not fisioterapeuta:
            raise FisioterapeutaNaoEncontradoError(fisioterapeuta_id)
        
        paciente = obter_ou_criar_paciente(session, nome_paciente, data_nascimento, data_avaliacao)
        
        avaliacao = Avaliacao(
            id_fisioterapeuta=fisioterapeuta_id,
            id_paciente=paciente.id,
            data=data_avaliacao,
            observacoes=observacoes or None
        )
        session.add(avaliacao)
        session.flush() # Garante que a avaliação tenha um ID para relacionamentos futuros
        
        for bloco_respostas in escalas_respostas:
            _registrar_aplicacao_escala(session, avaliacao, bloco_respostas)
        
        session.commit()
        return avaliacao
        
        
"""Registra a aplicação de uma escala em uma avaliação, incluindo as respostas dos itens."""
def _registrar_aplicacao_escala(session: Session, avaliacao: Avaliacao, bloco_respostas: dict):
    nome_escala = bloco_respostas["escala_nome"]
    respostas = bloco_respostas["respostas"]
    
    escala = session.query(Escala).filter_by(nome=nome_escala).first()
    if not escala:
        raise EscalaNaoEncontradaError(nome_escala)
    
    aplicacao = AplicacaoEscala(
        id_avaliacao=avaliacao.id,
        id_escala=escala.id
    )
    
    session.add(aplicacao)
    session.flush() # Garante que a aplicação tenha um ID para relacionamentos futuros
    
    itens_por_numero = {item.numero: item for item in escala.itens}
    
    for numero_item, pontuacao in respostas.items():
        numero_item = int(numero_item) # Garantir que seja inteiro
        item = itens_por_numero.get(numero_item)
        
        if not item:
            raise ItemEscalaNaoEncontradoError(numero_item, nome_escala)
        
        if (item.pontuacao_maxima is not None and not (0 <= pontuacao <= item.pontuacao_maxima)):
            raise PontuacaoInvalidaError(item.descricao, pontuacao, item.pontuacao_maxima)
        
        session.add(RespostaItem(
            id_aplicacao_escala=aplicacao.id,
            id_item_escala=item.id,
            pontuacao=int(pontuacao)
        ))
        
    session.flush() # Garante que as respostas sejam salvas para o cálculo da pontuação total
    aplicacao.calcular_pontuacao_total()
    session.flush() # Salva a pontuação total calculada