from datetime import date, datetime
from pathlib import Path
from typing import Literal

from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from sqlalchemy.orm import Session

from app.models.dto.aplicacao_dto import AplicacaoDTO
from app.models.dto.avaliacao_dto import AvaliacaoDTO
from app.models.dto.historico_escala_dto import HistoricoEscalaDTO
from app.models.dto.perfil_dto import PerfilDTO
from app.models.dto.resumo_executivo_dto import ResumoExecutivoDTO
from app.services.paciente_service import (
    historico_escala,
    perfil_completo,
    resumo_executivo,
)

_DIR_SAIDA = Path("data/relatorios")

_COR_CABECALHO = HexColor("#1F4E79")
_COR_ALERTA = HexColor("#FFC7CE")
_COR_BORDA = HexColor("#B8B8B8")
_COR_LINHA_PAR = HexColor("#F5F5F5")


def _estilos() -> dict:
    base = getSampleStyleSheet()
    return {
        "titulo": ParagraphStyle(
            "titulo",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=20,
            textColor=_COR_CABECALHO,
            alignment=TA_CENTER,
            spaceAfter=6,
        ),
        "subtitulo": ParagraphStyle(
            "subtitulo",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=13,
            textColor=HexColor("#444444"),
            alignment=TA_CENTER,
            spaceAfter=4,
        ),
        "secao": ParagraphStyle(
            "secao",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=12,
            textColor=_COR_CABECALHO,
            spaceBefore=10,
            spaceAfter=4,
        ),
        "subsecao": ParagraphStyle(
            "subsecao",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10,
            textColor=HexColor("#2E4057"),
            spaceBefore=6,
            spaceAfter=2,
        ),
        "corpo": ParagraphStyle(
            "corpo",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
        ),
        "corpo_neg": ParagraphStyle(
            "corpo_neg",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=14,
        ),
        "alerta": ParagraphStyle(
            "alerta",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10,
            textColor=HexColor("#C00000"),
            leading=14,
        ),
        "rodape": ParagraphStyle(
            "rodape",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER,
        ),
    }


def _estilo_tabela_base() -> TableStyle:
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), _COR_CABECALHO),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("TOPPADDING", (0, 0), (-1, 0), 6),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, _COR_BORDA),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 1), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 4),
    ])


def _rodape_factory(paciente_nome: str, data_geracao: datetime):
    def _rodape(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.grey)
        largura, _ = A4
        texto = (
            f"Paciente: {paciente_nome}  |  "
            f"Gerado em: {data_geracao.strftime('%d/%m/%Y %H:%M')}  |  "
            f"Página {doc.page}"
        )
        canvas.drawCentredString(largura / 2, 15 * mm, texto)
        canvas.restoreState()

    return _rodape


def _caminho_saida(paciente_nome: str, sufixo: str) -> Path:
    _DIR_SAIDA.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"{paciente_nome.replace(' ', '_')}_{sufixo}_{ts}.pdf"
    return _DIR_SAIDA / nome_arquivo


def _bloco_capa(paciente_nome: str, titulo: str, data_geracao: datetime, estilos: dict) -> list:
    return [
        Spacer(1, 40 * mm),
        Paragraph("Sistema de Escalas Motoras", estilos["subtitulo"]),
        Spacer(1, 6 * mm),
        Paragraph(titulo, estilos["titulo"]),
        Spacer(1, 10 * mm),
        Paragraph(paciente_nome, estilos["subtitulo"]),
        Spacer(1, 6 * mm),
        Paragraph(f"Gerado em {data_geracao.strftime('%d/%m/%Y às %H:%M')}", estilos["rodape"]),
        PageBreak(),
    ]


def _bloco_info_paciente(perfil: PerfilDTO, estilos: dict) -> list:
    elementos = [Paragraph("Dados do Paciente", estilos["secao"])]
    dados = [
        ["Nome", perfil.nome],
        ["Data de Nascimento", perfil.data_nascimento],
        ["Idade", f"{perfil.idade} anos"],
        ["Data de Cadastro", perfil.data_cadastro],
        ["Total de Avaliações", str(perfil.total_avaliacoes)],
    ]
    t = Table(dados, colWidths=[50 * mm, 120 * mm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, _COR_LINHA_PAR]),
    ]))
    elementos.append(t)
    return elementos


def _bloco_resumo_executivo(resumo: ResumoExecutivoDTO, estilos: dict) -> list:
    elementos = [Paragraph("Resumo Executivo", estilos["secao"])]

    ultima = resumo.data_ultima_avaliacao.strftime("%d/%m/%Y") if resumo.data_ultima_avaliacao else "—"
    dados = [
        ["Total de avaliações", str(resumo.total_avaliacoes)],
        ["Última avaliação", ultima],
    ]
    t = Table(dados, colWidths=[60 * mm, 110 * mm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    elementos.append(t)
    elementos.append(Spacer(1, 4 * mm))

    if resumo.alertas:
        elementos.append(Paragraph("Alertas — Pontuações Abaixo do Corte", estilos["subsecao"]))
        linhas = [["Escala", "Pontuação", "Corte", "Data"]]
        for alerta in resumo.alertas:
            linhas.append([
                alerta.escala_nome,
                str(alerta.pontuacao) if alerta.pontuacao is not None else "—",
                str(alerta.pontuacao_corte) if alerta.pontuacao_corte is not None else "—",
                alerta.data_avaliacao.strftime("%d/%m/%Y"),
            ])
        t_alertas = Table(linhas, colWidths=[80 * mm, 30 * mm, 30 * mm, 30 * mm])
        estilo = _estilo_tabela_base()
        for i in range(1, len(linhas)):
            estilo.add("BACKGROUND", (0, i), (-1, i), _COR_ALERTA)
        t_alertas.setStyle(estilo)
        elementos.append(t_alertas)
    else:
        elementos.append(Paragraph(
            "Sem alertas — todas as pontuações estão dentro do esperado.",
            estilos["corpo"],
        ))

    return elementos


def _bloco_aplicacao(aplicacao: AplicacaoDTO, estilos: dict) -> list:
    elementos = [Paragraph(aplicacao.escala_nome, estilos["subsecao"])]

    pont_str = str(aplicacao.pontuacao_total) if aplicacao.pontuacao_total is not None else "—"
    max_str = f"/{aplicacao.pontuacao_maxima}" if aplicacao.pontuacao_maxima else ""
    pct_str = f" ({aplicacao.percentual}%)" if aplicacao.percentual is not None else ""
    corte_str = f" | Corte: {aplicacao.pontuacao_corte}" if aplicacao.pontuacao_corte is not None else ""
    linha = f"Pontuação: {pont_str}{max_str}{pct_str}{corte_str}"

    if aplicacao.abaixo_do_corte:
        linha += " ⚠ ABAIXO DO CORTE"
        elementos.append(Paragraph(linha, estilos["alerta"]))
    else:
        elementos.append(Paragraph(linha, estilos["corpo_neg"]))

    if aplicacao.respostas:
        linhas = [["Item", "Descrição", "Pontuação", "Máximo"]]
        for r in aplicacao.respostas:
            linhas.append([
                str(r.numero_item),
                r.descricao,
                str(r.pontuacao),
                str(r.pontuacao_maxima) if r.pontuacao_maxima is not None else "—",
            ])
        t = Table(linhas, colWidths=[12 * mm, 110 * mm, 22 * mm, 22 * mm])
        estilo = _estilo_tabela_base()
        for i in range(1, len(linhas)):
            if i % 2 == 0:
                estilo.add("BACKGROUND", (0, i), (-1, i), _COR_LINHA_PAR)
        t.setStyle(estilo)
        elementos.append(t)

    elementos.append(Spacer(1, 3 * mm))
    return elementos


def _bloco_avaliacao(avaliacao: AvaliacaoDTO, numero: int, estilos: dict) -> list:
    elementos = []
    data_fmt = avaliacao.data.strftime("%d/%m/%Y")
    titulo = f"Avaliação #{numero} — {data_fmt} | Fisioterapeuta: {avaliacao.fisioterapeuta_nome}"
    elementos.append(Paragraph(titulo, estilos["secao"]))

    if avaliacao.observacoes:
        elementos.append(Paragraph(f"Observações: {avaliacao.observacoes}", estilos["corpo"]))

    for aplicacao in avaliacao.aplicacoes:
        elementos.extend(_bloco_aplicacao(aplicacao, estilos))

    elementos.append(Spacer(1, 4 * mm))
    return elementos


def _bloco_historico_escala(historico: HistoricoEscalaDTO, estilos: dict) -> list:
    elementos = [Paragraph(f"Histórico — {historico.escala_nome}", estilos["secao"])]

    corte_str = str(historico.pontuacao_corte) if historico.pontuacao_corte is not None else "—"
    max_str = str(historico.pontuacao_maxima) if historico.pontuacao_maxima is not None else "—"
    meta = [
        ["Pontuação de corte", corte_str],
        ["Pontuação máxima", max_str],
        ["Tendência geral", historico.tendencia],
    ]
    t_meta = Table(meta, colWidths=[60 * mm, 110 * mm])
    t_meta.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    elementos.append(t_meta)
    elementos.append(Spacer(1, 4 * mm))

    if not historico.pontos:
        elementos.append(Paragraph("Nenhum ponto de histórico encontrado.", estilos["corpo"]))
        return elementos

    elementos.append(Paragraph("Evolução da Pontuação", estilos["subsecao"]))
    linhas = [["Data", "Fisioterapeuta", "Pontuação", "%", "Variação", "Itens Alterados"]]
    pontuacao_anterior: int | None = None

    for ponto in historico.pontos:
        pont_str = str(ponto.pontuacao) if ponto.pontuacao is not None else "—"

        if ponto.pontuacao is not None and ponto.pontuacao_maxima:
            pct_str = f"{round(ponto.pontuacao / ponto.pontuacao_maxima * 100, 1)}%"
        else:
            pct_str = "—"

        if pontuacao_anterior is not None and ponto.pontuacao is not None:
            delta = ponto.pontuacao - pontuacao_anterior
            variacao_str = f"+{delta}" if delta > 0 else str(delta) if delta < 0 else "="
        else:
            variacao_str = "—"

        alterados_str = str(len(ponto.respostas_que_variaram)) if pontuacao_anterior is not None else "—"

        linhas.append([
            ponto.data.strftime("%d/%m/%Y"),
            ponto.fisioterapeuta,
            pont_str,
            pct_str,
            variacao_str,
            alterados_str,
        ])
        pontuacao_anterior = ponto.pontuacao

    t_evolucao = Table(linhas, colWidths=[25 * mm, 55 * mm, 24 * mm, 20 * mm, 22 * mm, 24 * mm])
    estilo = _estilo_tabela_base()
    for i, ponto in enumerate(historico.pontos, start=1):
        if ponto.abaixo_do_corte:
            estilo.add("BACKGROUND", (0, i), (-1, i), _COR_ALERTA)
        elif i % 2 == 0:
            estilo.add("BACKGROUND", (0, i), (-1, i), _COR_LINHA_PAR)
    t_evolucao.setStyle(estilo)
    elementos.append(t_evolucao)
    return elementos


def _bloco_escala_agrupada(
    escala_nome: str,
    itens: list[tuple[AvaliacaoDTO, AplicacaoDTO]],
    estilos: dict,
) -> list:
    elementos = [Paragraph(escala_nome, estilos["secao"])]

    _, primeiro = itens[0]
    corte_str = str(primeiro.pontuacao_corte) if primeiro.pontuacao_corte is not None else "—"
    max_str = str(primeiro.pontuacao_maxima) if primeiro.pontuacao_maxima is not None else "—"
    meta = [["Pontuação de corte", corte_str], ["Pontuação máxima", max_str]]
    t_meta = Table(meta, colWidths=[60 * mm, 110 * mm])
    t_meta.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    elementos.append(t_meta)
    elementos.append(Spacer(1, 4 * mm))

    linhas = [["Data", "Fisioterapeuta", "Pontuação", "%", "Variação", "Status"]]
    pontuacao_anterior: int | None = None

    for av, ap in itens:
        pont_str = str(ap.pontuacao_total) if ap.pontuacao_total is not None else "—"
        pct_str = f"{ap.percentual}%" if ap.percentual is not None else "—"

        if pontuacao_anterior is not None and ap.pontuacao_total is not None:
            delta = ap.pontuacao_total - pontuacao_anterior
            variacao_str = f"+{delta}" if delta > 0 else str(delta) if delta < 0 else "="
        else:
            variacao_str = "—"

        status = "Abaixo do corte" if ap.abaixo_do_corte else "OK"
        linhas.append([
            av.data.strftime("%d/%m/%Y"),
            av.fisioterapeuta_nome,
            pont_str,
            pct_str,
            variacao_str,
            status,
        ])
        pontuacao_anterior = ap.pontuacao_total

    t = Table(linhas, colWidths=[25 * mm, 55 * mm, 24 * mm, 20 * mm, 22 * mm, 24 * mm])
    estilo = _estilo_tabela_base()
    for i, (_, ap) in enumerate(itens, start=1):
        if ap.abaixo_do_corte:
            estilo.add("BACKGROUND", (0, i), (-1, i), _COR_ALERTA)
        elif i % 2 == 0:
            estilo.add("BACKGROUND", (0, i), (-1, i), _COR_LINHA_PAR)
    t.setStyle(estilo)
    elementos.append(t)

    valores = [ap.pontuacao_total for _, ap in itens if ap.pontuacao_total is not None]
    if len(valores) >= 2:
        delta = valores[-1] - valores[0]
        if delta > 0:
            tendencia = f"Melhora de {delta} pontos ao longo do acompanhamento"
        elif delta < 0:
            tendencia = f"Piora de {abs(delta)} pontos ao longo do acompanhamento"
        else:
            tendencia = "Pontuação estável ao longo do acompanhamento"
        elementos.append(Spacer(1, 3 * mm))
        elementos.append(Paragraph(f"Tendência: {tendencia}", estilos["corpo"]))

    elementos.append(Spacer(1, 6 * mm))
    return elementos


def gerar_relatorio_pdf(
    session: Session,
    paciente_id: int,
    tipo_relatorio: Literal["completo", "por_escala", "escala", "periodo"],
    id_escala: int | None = None,
    data_inicio: date | None = None,
    data_fim: date | None = None,
    caminho_saida: str | None = None,
) -> str:
    """
    Gera um relatório PDF e retorna o caminho do arquivo gerado.

    tipo_relatorio:
    - "completo": Histórico clínico completo em ordem cronológica
    - "por_escala": Todas as avaliações agrupadas por escala, com tendência
    - "escala": Histórico de uma escala específica (requer id_escala)
    - "periodo": Avaliações filtradas por data (requer data_inicio e/ou data_fim)
    """
    if tipo_relatorio == "escala" and id_escala is None:
        raise ValueError("id_escala é obrigatório para tipo_relatorio='escala'")
    if tipo_relatorio == "periodo" and data_inicio is None and data_fim is None:
        raise ValueError("data_inicio ou data_fim são obrigatórios para tipo_relatorio='periodo'")
    if data_inicio and data_fim and data_inicio > data_fim:
        raise ValueError("data_inicio não pode ser posterior a data_fim")

    estilos = _estilos()
    data_geracao = datetime.now()
    elementos: list = []
    paciente_nome: str = ""

    if tipo_relatorio == "completo":
        perfil = perfil_completo(session, paciente_id)
        resumo = resumo_executivo(session, paciente_id)
        paciente_nome = perfil.nome
        elementos += _bloco_capa(perfil.nome, "Relatório Clínico Completo", data_geracao, estilos)
        elementos += _bloco_info_paciente(perfil, estilos)
        elementos.append(Spacer(1, 4 * mm))
        elementos += _bloco_resumo_executivo(resumo, estilos)
        elementos.append(PageBreak())
        elementos.append(Paragraph("Histórico de Avaliações", estilos["secao"]))
        for i, av in enumerate(perfil.avaliacoes, start=1):
            elementos += _bloco_avaliacao(av, i, estilos)
        caminho = Path(caminho_saida) if caminho_saida else _caminho_saida(perfil.nome, "completo")

    elif tipo_relatorio == "por_escala":
        perfil = perfil_completo(session, paciente_id)
        resumo = resumo_executivo(session, paciente_id)
        paciente_nome = perfil.nome
        elementos += _bloco_capa(perfil.nome, "Relatório por Escala", data_geracao, estilos)
        elementos += _bloco_info_paciente(perfil, estilos)
        elementos.append(Spacer(1, 4 * mm))
        elementos += _bloco_resumo_executivo(resumo, estilos)
        elementos.append(PageBreak())

        escalas_dict: dict[str, list[tuple[AvaliacaoDTO, AplicacaoDTO]]] = {}
        for av in perfil.avaliacoes:
            for ap in av.aplicacoes:
                escalas_dict.setdefault(ap.escala_nome, []).append((av, ap))

        for escala_nome in sorted(escalas_dict.keys()):
            elementos += _bloco_escala_agrupada(escala_nome, escalas_dict[escala_nome], estilos)

        caminho = Path(caminho_saida) if caminho_saida else _caminho_saida(perfil.nome, "por_escala")

    elif tipo_relatorio == "escala":
        hist = historico_escala(session, paciente_id, id_escala)
        perfil = perfil_completo(session, paciente_id)
        paciente_nome = hist.paciente_nome
        elementos += _bloco_capa(
            hist.paciente_nome,
            f"Histórico — {hist.escala_nome}",
            data_geracao,
            estilos,
        )
        elementos += _bloco_info_paciente(perfil, estilos)
        elementos.append(Spacer(1, 4 * mm))
        elementos += _bloco_historico_escala(hist, estilos)
        caminho = Path(caminho_saida) if caminho_saida else _caminho_saida(
            hist.paciente_nome, f"escala_{id_escala}"
        )

    else:  # periodo
        perfil = perfil_completo(session, paciente_id)
        resumo = resumo_executivo(session, paciente_id)
        paciente_nome = perfil.nome

        avaliacoes_filtradas = [
            av for av in perfil.avaliacoes
            if (data_inicio is None or av.data >= data_inicio)
            and (data_fim is None or av.data <= data_fim)
        ]

        inicio_str = data_inicio.strftime("%d/%m/%Y") if data_inicio else "início"
        fim_str = data_fim.strftime("%d/%m/%Y") if data_fim else "hoje"
        elementos += _bloco_capa(
            perfil.nome,
            f"Relatório por Período — {inicio_str} a {fim_str}",
            data_geracao,
            estilos,
        )
        elementos += _bloco_info_paciente(perfil, estilos)
        elementos.append(Spacer(1, 4 * mm))

        resumo_periodo = ResumoExecutivoDTO(
            paciente_nome=resumo.paciente_nome,
            data_nascimento=resumo.data_nascimento,
            total_avaliacoes=len(avaliacoes_filtradas),
            data_ultima_avaliacao=max((av.data for av in avaliacoes_filtradas), default=None),
            ultima_pontuacao_por_escala=[],
            alertas=[
                a for a in resumo.alertas
                if (data_inicio is None or a.data_avaliacao >= data_inicio)
                and (data_fim is None or a.data_avaliacao <= data_fim)
            ],
        )
        elementos += _bloco_resumo_executivo(resumo_periodo, estilos)
        elementos.append(PageBreak())
        elementos.append(Paragraph(f"Avaliações — {inicio_str} a {fim_str}", estilos["secao"]))

        if avaliacoes_filtradas:
            for i, av in enumerate(avaliacoes_filtradas, start=1):
                elementos += _bloco_avaliacao(av, i, estilos)
        else:
            elementos.append(Paragraph(
                "Nenhuma avaliação encontrada para o período informado.",
                estilos["corpo"],
            ))

        caminho = Path(caminho_saida) if caminho_saida else _caminho_saida(
            perfil.nome, f"periodo_{data_geracao.strftime('%Y%m%d')}"
        )

    rodape = _rodape_factory(paciente_nome, data_geracao)
    doc = SimpleDocTemplate(
        str(caminho),
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=25 * mm,
    )
    doc.build(elementos, onFirstPage=rodape, onLaterPages=rodape)
    return str(caminho)
