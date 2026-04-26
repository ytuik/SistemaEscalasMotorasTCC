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
from scripts.utils.escalas import get_escalas
from app.models import Escala, ItemEscala

"""
Variavel que armazena as escalas a serem inseridas no banco de dados. 
Cada escala é representada por um dicionário contendo seu nome, descrição, pontuação máxima, pontuação de corte e uma lista de itens
(cada item é uma tupla com número, descrição e pontuação máxima).
"""
ESCALAS = get_escalas()

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