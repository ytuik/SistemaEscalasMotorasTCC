"""
Script para popular o banco de dados - escalas motoras para avaliação de idosos

Escalas Incluidas:
    1. Escala de Equilíbrio de Berg (Berg)
    2. Mini Balance Evaluation Systems Test (Mini BESTest)
    3. Timed Up and Go (TUG)
    4. Teste de Caminhada de 10 Metros (10mWT)
    5. Dynamic Gait Index (DGI)
    6. Disabilities of the Arm, Shoulder and Hand (DASH)
    7. Teste de Sentar e Levantar 5 Vezes
    
Escalas a ser incluidas: 
    1. Teste de rolar
"""

from app.database import Base, engine, SessionLocal
import app.models
from app.models import Escala, ItemEscala

"""
Variavel que armazena as escalas a serem inseridas no banco de dados. 
Cada escala é representada por um dicionário contendo seu nome, descrição, pontuação máxima, pontuação de corte e uma lista de itens
(cada item é uma tupla com número, descrição e pontuação máxima).
"""
ESCALAS = [
        {
        "nome": "Escala de Equilíbrio de Berg",
        "descricao": (
            "Avalia o equilíbrio funcional estático e dinâmico por meio de 14 tarefas "
            "comuns à vida diária. Cada item é pontuado de 0 a 4, totalizando no máximo "
            "56 pontos. Pontuações abaixo de 21 estão associadas a risco aumentado de quedas."
        ),
        "pontuacao_maxima": 56,
        "pontuacao_corte": 21,
        "itens": [
            (1,  "Posição sentada para posição em pé", 4),
            (2,  "Permanecer em pé sem apoio", 4),
            (3,  "Permanecer sentado sem apoio", 4),
            (4,  "Posição em pé para posição sentada", 4),
            (5,  "Transferências", 4),
            (6,  "Permanecer em pé com os olhos fechados", 4),
            (7,  "Permanecer em pé com os pés juntos", 4),
            (8,  "Alcançar à frente com o braço estendido estando em pé", 4),
            (9,  "Pegar um objeto do chão a partir de uma posição em pé", 4),
            (10, "Virar-se para olhar para trás por cima dos ombros", 4),
            (11, "Girar 360 graus", 4),
            (12, "Posicionar os pés alternadamente no degrau", 4),
            (13, "Permanecer em pé com um pé à frente", 4),
            (14, "Permanecer em pé sobre um pé", 4),
        ],
    },
    {
        "nome": "Mini Balance Evaluation Systems Test (Mini BESTest)",
        "descricao": (
            "Avalia o equilíbrio dinâmico por meio de 14 itens distribuídos em quatro "
            "domínios: ajustes posturais antecipatórios, controle postural reativo, "
            "orientação sensorial e estabilidade na marcha. Cada item é pontuado de 0 a 2, "
            "totalizando no máximo 28 pontos."
        ),
        "pontuacao_maxima": 28,
        "pontuacao_corte": None,
        "itens": [
            (1, "Sentado para em pé", 2),
            (2, "Em pé na ponta dos pés", 2),
            (3, "Em pé em um pé só", 2),
            (4, "Resposta compensatória — empurrão para frente", 2),
            (5, "Resposta compensatória — empurrão para trás", 2),
            (6, "Resposta compensatória — empurrão lateral", 2),
            (7, "Orientação sensorial — superfície firme, olhos abertos e pés juntos", 2),
            (8, "Orientação sensorial — superfície de espuma olhos fechados e pés juntos", 2),
            (9, "Orientação sensorial — inclinação — olhos fechados", 2),
            (10, "Marcha com mudança de velocidade", 2),
            (11, "Marcha com rotação da cabeça horizontal", 2),
            (12, "Marcha com giro de 180 graus", 2),
            (13, "Marcha com obstáculos", 2),
            (14, "Timed Up and Go com dupla tarefa", 2)
        ],
    },
    {
        "nome": "Timed Up and Go (TUG)",
        "descricao": (
            "Avalia a mobilidade funcional e o risco de quedas pelo tempo, em segundos, "
            "que o paciente leva para levantar de uma cadeira, caminhar 3 metros, girar, "
            "retornar e sentar. Tempos acima de 21 segundos indicam maior risco de quedas "
            "em idosos comunitários."
        ),
        "pontuacao_maxima": None,
        "pontuacao_corte": None,
        "itens": [
            (1, "Tempo total em segundos para completar o percurso", None),
        ],
    },
    {
        "nome": "Teste de Caminhada de 10 Metros (10mWT)",
        "descricao": (
            "Avalia a velocidade de marcha habitual pelo tempo, em segundos, necessário "
            "para percorrer 10 metros em ritmo confortável. Permite calcular a velocidade "
            "em metros por segundo."
        ),
        "pontuacao_maxima": None,
        "pontuacao_corte": None,
        "itens": [
            (1, "Tempo total em segundos para percorrer 10 metros", None),
        ],
    },
    {
        "nome": "Dynamic Gait Index (DGI)",
        "descricao": (
            "Avalia a estabilidade da marcha durante a realização de tarefas em 8 itens, "
            "cada um pontuado de 0 a 3, totalizando no máximo 24 pontos. Pontuações abaixo "
            "de 19 estão associadas a risco de quedas em idosos."
        ),
        "pontuacao_maxima": 24,
        "pontuacao_corte": None,
        "itens": [
            (1, "Marcha em superfície plana", 3),
            (2, "Mudança na velocidade da marcha", 3),
            (3, "Marcha com rotação horizontal da cabeça", 3),
            (4, "Marcha com rotação vertical da cabeça", 3),
            (5, "Marcha e giro de 180 graus com parada rápida", 3),
            (6, "Marcha e passagem por cima de obstáculo", 3),
            (7, "Marcha com desvio de obstáculos", 3),
            (8, "Subir e descer escadas", 3),
        ],
    },
    {
        "nome": "Disabilities of the Arm, Shoulder and Hand (DASH)",
        "descricao": (
            "Questionário de autorrelato que avalia sintomas e incapacidade funcional do "
            "membro superior. Composto por 30 itens, cada um pontuado de 1 a 5, "
            "usa-se uma fórmula para trazer a pontuação para uma escala de 100 pontos, para poder ser comparada com outras escalas funcionais."
            "Quanto maior o escore, maior a incapacidade. "
        ),
        "pontuacao_maxima": 100,
        "pontuacao_corte": None,
        "itens": [
            (1,  "Abrir um pote novo ou com tampa apertada", 5),
            (2,  "Escrever", 5),
            (3,  "Girar uma chave", 5),
            (4,  "Preparar uma refeição", 5),
            (5,  "Empurrar ou abrir uma porta pesada", 5),
            (6,  "Colocar um objeto em uma prateleira acima da cabeça", 5),
            (7,  "Realizar tarefas domésticas pesadas", 5),
            (8,  "Trabalhar no jardim ou quintal", 5),
            (9,  "Arrumar a cama", 5),
            (10, "Carregar uma sacola de compras ou uma pasta", 5),
            (11, "Carregar um objeto pesado (acima de 5 kg)", 5),
            (12, "Trocar uma lâmpada acima da cabeça", 5),
            (13, "Lavar ou secar o cabelo", 5),
            (14, "Lavar as costas", 5),
            (15, "Vestir uma blusa fechada", 5),
            (16, "Usar uma faca para cortar alimento", 5),
            (17, "Atividades recreativas com pouco esforço do braço", 5),
            (18, "Atividades recreativas com força ou impacto nos braços, ombros ou mãos", 5),
            (19, "Atividades recreativas com movimentos livres do braço", 5),
            (20, "Capacidade de se locomover de um lugar para outro", 5),
            (21, "Atividade sexual", 5),
            (22, "Impacto do problema no braço nas atividades sociais", 5),
            (23, "Limitação no trabalho ou atividades cotidianas", 5),
            (24, "Dor no braço, ombro ou mão", 5),
            (25, "Dor no braço, ombro ou mão ao realizar atividade específica", 5),
            (26, "Formigamento no braço, ombro ou mão", 5),
            (27, "Fraqueza no braço, ombro ou mão", 5),
            (28, "Rigidez no braço, ombro ou mão", 5),
            (29, "Dificuldade para dormir devido à dor no braço, ombro ou mão", 5),
            (30, "Sentimento de incapacidade, falta de confiança", 5),
        ],
    },
    {
        "nome": "Teste de Sentar e Levantar 5 Vezes (TSL-5)",
        "descricao": (
            "Avalia a força de membros inferiores e o risco de quedas pelo tempo, em "
            "segundos, necessário para realizar cinco repetições de sentar e levantar "
            "de uma cadeira sem apoio dos braços. Tempos acima de 12 segundos estão "
            "associados a maior risco de quedas em idosos."
        ),
        "pontuacao_maxima": None,
        "pontuacao_corte": None,
        "itens": [
            (1, "Tempo total em segundos para completar 5 repetições de sentar e levantar", None),
        ],
    },
]

def popular_escalas(session):
    escalas_existentes = {e.nome for e in session.query(Escala).all()}
    adicionadas = 0
    
    for dados in ESCALAS:
        if dados["nome"] in escalas_existentes:
            print(f"Escala '{dados['nome']}' já existe. ")
            continue
        
        escala = Escala(
            nome=dados["nome"],
            descricao=dados["descricao"],
            pontuacao_maxima=dados["pontuacao_maxima"],
            pontuacao_corte=dados["pontuacao_corte"]
        )
        
        for numero, descricao, pontuacao_maxima in dados["itens"]:
            escala.itens.append(ItemEscala(
                numero_item=numero,
                descricao=descricao,
                pontuacao_maxima=pontuacao_maxima
            ))
            
        session.add(escala)
        adicionadas += 1
        print(f"Escala '{dados['nome']}' adicionada com {len(dados['itens'])} itens.")

    session.commit()
    return adicionadas

def run():
    print("Criando tabelas no banco de dados...")
    Base.metadata.create_all(bind=engine)
    
    print("Populando o banco de dados com escalas motoras...")
    with SessionLocal() as session:
        adicionadas = popular_escalas(session)
        print(f"Processo concluído. {adicionadas} novas escalas adicionadas.")
        
if __name__ == "__main__":
    run()