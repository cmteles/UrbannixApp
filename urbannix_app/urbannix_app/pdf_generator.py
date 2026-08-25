"""
pdf_generator.py
Gera o PDF do orçamento para a Urbannix enviar ao cliente pelo WhatsApp.
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

NOME_EMPRESA = "Urbannix Estamparia"


def gerar_pdf_orcamento(orcamento, itens, caminho_saida):
    """
    orcamento: linha (sqlite3.Row) vinda de get_orcamento_detalhado
    itens: lista de linhas (sqlite3.Row) com os itens do orçamento
    caminho_saida: caminho do arquivo .pdf a ser gerado
    """
    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle(
        "Titulo", parent=styles["Title"], alignment=TA_CENTER, fontSize=18
    )
    subtitulo_style = ParagraphStyle(
        "Subtitulo", parent=styles["Normal"], alignment=TA_CENTER, textColor=colors.grey
    )
    normal = styles["Normal"]

    doc = SimpleDocTemplate(
        caminho_saida,
        pagesize=A4,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
    )

    elementos = []

    elementos.append(Paragraph(NOME_EMPRESA, titulo_style))
    elementos.append(Paragraph(f"Orçamento Nº {orcamento['id']:04d}", subtitulo_style))
    elementos.append(Spacer(1, 0.8 * cm))

    dados_cliente = [
        ["Cliente:", orcamento["cliente_nome"]],
        ["Telefone:", orcamento["cliente_telefone"] or "-"],
        ["Data:", str(orcamento["data"])[:16]],
        ["Status:", orcamento["status"]],
    ]
    tabela_cliente = Table(dados_cliente, colWidths=[3.5 * cm, 12 * cm])
    tabela_cliente.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    elementos.append(tabela_cliente)
    elementos.append(Spacer(1, 0.8 * cm))

    cabecalho = ["Item", "Qtd.", "Valor Unit.", "Subtotal"]
    linhas = [cabecalho]
    total = 0.0
    for item in itens:
        subtotal = item["quantidade"] * item["preco_unitario"]
        total += subtotal
        linhas.append(
            [
                item["produto_nome"],
                str(item["quantidade"]),
                f"R$ {item['preco_unitario']:.2f}",
                f"R$ {subtotal:.2f}",
            ]
        )

    linhas.append(["", "", "TOTAL", f"R$ {total:.2f}"])

    tabela_itens = Table(linhas, colWidths=[7.5 * cm, 2 * cm, 3.5 * cm, 3.5 * cm])
    tabela_itens.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2b2d42")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                ("GRID", (0, 0), (-1, -2), 0.5, colors.grey),
                ("LINEABOVE", (0, -1), (-1, -1), 1, colors.black),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    elementos.append(tabela_itens)

    if orcamento["observacoes"]:
        elementos.append(Spacer(1, 0.8 * cm))
        elementos.append(Paragraph("<b>Observações:</b>", normal))
        elementos.append(Paragraph(orcamento["observacoes"], normal))

    elementos.append(Spacer(1, 1.2 * cm))
    elementos.append(
        Paragraph("Orçamento válido por 7 dias. Obrigado pela preferência!", subtitulo_style)
    )

    doc.build(elementos)
    return caminho_saida
