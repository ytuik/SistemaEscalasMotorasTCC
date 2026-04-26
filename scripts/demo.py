"""
Interface interativa de demonstração — Sistema de Escalas Motoras.

Suporta:
  - Registro manual de avaliação (item a item no terminal)
  - Importação de avaliação via arquivo CSV
  - Consulta do perfil completo de um paciente
"""

import sys
from datetime import date
from sqlalchemy.orm import Session

from app.database import engine, Base, SessionLocal
from app.models import Fisioterapeuta, Paciente, Escala, Avaliacao
from app.services.avaliacao_service import registrar_avaliacao
from app.services.template_service import iniciar_avaliacao_xlsx
from app.services.planilha_service import importar_planilha_avaliacao
from app.exceptions import (
    EscalaNaoEncontradaError,
    FisioterapeutaNaoEncontradoError,
    PontuacaoInvalidaError,
    ItemEscalaNaoEncontradoError,
)
from scripts.gerar_template_avaliacao import gerar_template_avaliacao
from scripts.seed import popular_escalas


def inicializar():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        popular_escalas(session)


def listar_escalas(session: Session):
    print("\n── Escalas disponíveis ──────────────────────────────────────────")
    for e in session.query(Escala).order_by(Escala.id).all():
        corte = f"  corte: {e.pontuacao_corte}" if e.pontuacao_corte else ""
        maximo = f"  máx: {e.pontuacao_maxima}" if e.pontuacao_maxima else "  tempo (s)"
        print(f"  [{e.id:2}] {e.nome:<50} {maximo}{corte}")
    print()


def cadastrar_fisioterapeuta(session: Session):
    print("\n── Cadastrar fisioterapeuta ─────────────────────────────────────")
    nome = input("  Nome: ").strip()
    crefito = input("  CREFITO: ").strip()
    email = input("  E-mail: ").strip()
    fis = Fisioterapeuta(nome=nome, registro_crefito=crefito, email=email)
    session.add(fis)
    session.commit()
    print(f"  Fisioterapeuta '{nome}' cadastrado(a) com ID {fis.id}.\n")


def _selecionar_fisioterapeuta(session: Session) -> int | None:
    fisios = session.query(Fisioterapeuta).all()
    if not fisios:
        print("  Nenhum fisioterapeuta cadastrado. Use a opção [2] primeiro.\n")
        return None
    print("  Fisioterapeutas:")
    for f in fisios:
        print(f"    [{f.id}] {f.nome}  —  {f.registro_crefito}")
    return int(input("  ID do fisioterapeuta: ").strip())


def registrar_manual(session: Session):
    print("\n── Nova avaliação — entrada manual ─────────────────────────────")

    fis_id = _selecionar_fisioterapeuta(session)
    if fis_id is None:
        return

    nome = input("  Nome do paciente: ").strip()
    nasc = input("  Data de nascimento (AAAA-MM-DD): ").strip()
    obs = input("  Observações da sessão (opcional): ").strip()

    escalas_disponiveis = session.query(Escala).order_by(Escala.id).all()
    print("\n  Escalas disponíveis:")
    for e in escalas_disponiveis:
        print(f"    [{e.id}] {e.nome}")

    ids_raw = input("\n  IDs das escalas aplicadas (ex: 1,5): ").strip()
    ids = [int(x.strip()) for x in ids_raw.split(",") if x.strip()]

    escalas_respostas = []
    for eid in ids:
        escala = session.get(Escala, eid)
        if not escala:
            print(f"  Escala ID {eid} não encontrada, ignorando.")
            continue

        print(f"\n  ── {escala.nome} ──")
        respostas = {}
        for item in escala.itens:
            limite = f"0-{item.pontuacao_maxima}" if item.pontuacao_maxima else "segundos"
            while True:
                try:
                    val = input(f"    Item {item.numero_item} [{limite}] — {item.descricao}: ").strip()
                    pontuacao = int(val)
                    if item.pontuacao_maxima and not (0 <= pontuacao <= item.pontuacao_maxima):
                        print(f"    Valor fora do intervalo. Digite entre 0 e {item.pontuacao_maxima}.")
                        continue
                    break
                except ValueError:
                    print("    Digite um número inteiro.")
            respostas[item.numero_item] = pontuacao

        escalas_respostas.append({"escala_nome": escala.nome, "respostas": respostas})

    try:
        avaliacao = registrar_avaliacao(
            session,
            nome_paciente=nome,
            data_nascimento=date.fromisoformat(nasc),
            fisioterapeuta_id=fis_id,
            data_avaliacao=date.today(),
            observacoes=obs or None,
            escalas_respostas=escalas_respostas,
        )
        print(f"\n  Avaliação registrada com sucesso — ID {avaliacao.id}.")
        _exibir_resultado_avaliacao(session, avaliacao.id)
    except (EscalaNaoEncontradaError, FisioterapeutaNaoEncontradoError,
            PontuacaoInvalidaError, ItemEscalaNaoEncontradoError) as e:
        print(f"\n  Erro ao registrar avaliação: {e}\n")


def registrar_csv(session: Session):
    print("\n── Nova avaliação — importação XLSX ─────────────────────────────")

    gerar = input("  Gerar template de exemplo antes de importar? [s/n]: ").strip().lower()
    if gerar == "s":
        caminho_template = input("  Caminho para salvar o template (ex: template.xlsx): ").strip()
        gerar_template_avaliacao(caminho_template)
        print("  Preencha o arquivo e execute a importação novamente.\n")
        return

    filepath = input("  Caminho do arquivo XLSX: ").strip()

    try:
        resultado = importar_planilha_avaliacao(session, filepath)
    except Exception as e:
        print(f"\n  Erro ao processar o arquivo: {e}\n")
        return

    if resultado["status"] == "ok":
        escalas = ", ".join(resultado["escalas_importadas"])
        print(f"  [ok]  {resultado['paciente']} — {resultado['data_avaliacao']}"
              f"  |  ID {resultado['avaliacao_id']}  |  {escalas}")
    else:
        print(f"  [erro] {resultado['paciente']} — {resultado['data_avaliacao']}"
              f"  |  {resultado['mensagem']}")
    print()


def perfil_paciente(session: Session):
    print("\n── Perfil do paciente ───────────────────────────────────────────")
    pacientes = session.query(Paciente).order_by(Paciente.nome).all()
    if not pacientes:
        print("  Nenhum paciente cadastrado.\n")
        return

    for p in pacientes:
        print(f"  [{p.id}] {p.nome}  —  nasc. {p.data_nascimento}")
    pid = int(input("  ID do paciente: ").strip())

    paciente = session.get(Paciente, pid)
    if not paciente:
        print("  Paciente não encontrado.\n")
        return

    print(f"\n  Paciente : {paciente.nome}")
    print(f"  Nascimento: {paciente.data_nascimento}  |  Cadastro: {paciente.data_cadastro}")

    avaliacoes = (
        session.query(Avaliacao)
        .filter_by(id_paciente=paciente.id)
        .order_by(Avaliacao.data)
        .all()
    )

    if not avaliacoes:
        print("  Sem avaliações registradas.\n")
        return

    for av in avaliacoes:
        print(f"\n  Avaliação #{av.id} — {av.data}  |  Fisioterapeuta: {av.fisioterapeuta.nome}")
        if av.observacoes:
            print(f"  Observações: {av.observacoes}")
        for ap in av.aplicacoes_escala:
            alerta = ""
            if (ap.escala.pontuacao_corte and ap.pontuacao_total is not None
                    and ap.pontuacao_total < ap.escala.pontuacao_corte):
                alerta = f"  ⚠  abaixo do corte ({ap.escala.pontuacao_corte})"
            maximo = f"/{ap.escala.pontuacao_maxima}" if ap.escala.pontuacao_maxima else " s"
            print(f"\n    Escala: {ap.escala.nome}")
            print(f"    Total : {ap.pontuacao_total}{maximo}{alerta}")
            for r in ap.respostas:
                lim = f"/{r.item_escala.pontuacao_maxima}" if r.item_escala.pontuacao_maxima else ""
                print(f"      item {r.item_escala.numero_item:2}: {r.pontuacao}{lim}"
                      f"  — {r.item_escala.descricao}")
    print()


def _exibir_resultado_avaliacao(session: Session, avaliacao_id: int):
    av = session.get(Avaliacao,avaliacao_id)
    if not av:
        return
    print(f"\n  Resumo da avaliação #{av.id}:")
    for ap in av.aplicacoes_escala:
        alerta = ""
        if (ap.escala.pontuacao_corte and ap.pontuacao_total is not None
                and ap.pontuacao_total < ap.escala.pontuacao_corte):
            alerta = f"  ⚠  abaixo do corte ({ap.escala.pontuacao_corte})"
        maximo = f"/{ap.escala.pontuacao_maxima}" if ap.escala.pontuacao_maxima else " s"
        print(f"    {ap.escala.nome}: {ap.pontuacao_total}{maximo}{alerta}")
    print()


def iniciar_avaliacao_planilha(session: Session):
    print("\n── Iniciar avaliação — planilha Excel ───────────────────────────")
    print("  [1] Criar nova planilha para preencher")
    print("  [2] Importar planilha já preenchida")
    escolha = input("\n  Opção: ").strip()

    if escolha == "1":
        fis_id = _selecionar_fisioterapeuta(session)
        if fis_id is None:
            return
        nome = input("  Nome do paciente: ").strip()
        arquivo = iniciar_avaliacao_xlsx(nome)
        print(f"\n  Arquivo criado: {arquivo}")
        print("  Preencha a planilha e use esta opção [5] → [2] para importar.\n")

    elif escolha == "2":
        filepath = input("  Caminho do arquivo xlsx preenchido: ").strip()
        try:
            resultado = importar_planilha_avaliacao(session, filepath)
        except Exception as e:
            print(f"\n  Erro ao processar o arquivo: {e}\n")
            return

        if resultado["status"] == "ok":
            escalas = ", ".join(resultado["escalas_importadas"])
            print(f"\n  [ok] Avaliação registrada — ID {resultado['avaliacao_id']}")
            print(f"  Paciente : {resultado['paciente']}")
            print(f"  Data     : {resultado['data_avaliacao']}")
            print(f"  Escalas  : {escalas}\n")
            _exibir_resultado_avaliacao(session, resultado["avaliacao_id"])
        else:
            print(f"\n  [erro] {resultado['mensagem']}\n")
    else:
        print("  Opção inválida.\n")


def menu():
    opcoes = [
        ("1", "Listar escalas disponíveis",                 listar_escalas),
        ("2", "Cadastrar fisioterapeuta",                    cadastrar_fisioterapeuta),
        ("3", "Registrar avaliação — entrada manual",        registrar_manual),
        ("4", "Registrar avaliação — importar XLSX",         registrar_csv),
        ("5", "Iniciar avaliação — abrir planilha Excel",    iniciar_avaliacao_planilha),
        ("6", "Ver perfil de um paciente",                   perfil_paciente),
        ("0", "Sair",                                        None),
    ]

    print("\n╔══════════════════════════════════════════╗")
    print("║   Sistema de Escalas Motoras  v0.1       ║")
    print("╚══════════════════════════════════════════╝")

    with SessionLocal() as session:
        while True:
            print("\n── Menu ─────────────────────────────────────────────────────")
            for k, desc, _ in opcoes:
                print(f"  [{k}] {desc}")
            escolha = input("\n  Opção: ").strip()

            if escolha == "0":
                print("  Encerrando.\n")
                sys.exit(0)

            fn = next((f for k, _, f in opcoes if k == escolha), None)
            if fn:
                fn(session)
            else:
                print("  Opção inválida.")


if __name__ == "__main__":
    inicializar()
    menu()
