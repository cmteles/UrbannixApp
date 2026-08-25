"""
app.py
Sistema de orçamentos, financeiro e estoque da Urbannix.
Rode com: streamlit run app.py
"""

import os
import streamlit as st

import database as db
from pdf_generator import gerar_pdf_orcamento

st.set_page_config(page_title="Urbannix - Orçamentos", page_icon="🧵", layout="centered")

db.init_db()
os.makedirs("orcamentos_pdf", exist_ok=True)

st.title("🧵 Urbannix")
st.caption("Sistema de orçamentos, financeiro e estoque")

pagina = st.sidebar.radio(
    "Menu",
    ["Novo orçamento", "Orçamentos", "Clientes", "Produtos / Estoque"],
)

# ---------------------------------------------------------------------------
# NOVO ORÇAMENTO
# ---------------------------------------------------------------------------
if pagina == "Novo orçamento":
    st.header("Novo orçamento")

    clientes = db.get_clientes()
    produtos = db.get_produtos()

    if not clientes:
        st.warning("Cadastre um cliente primeiro na aba **Clientes**.")
    elif not produtos:
        st.warning("Cadastre ao menos um produto primeiro na aba **Produtos / Estoque**.")
    else:
        cliente_opcoes = {f"{c['nome']} ({c['telefone'] or 'sem telefone'})": c["id"] for c in clientes}
        cliente_sel = st.selectbox("Cliente", list(cliente_opcoes.keys()))

        st.subheader("Itens do orçamento")

        if "itens_orcamento" not in st.session_state:
            st.session_state.itens_orcamento = []

        produto_opcoes = {
            f"{p['nome']} (estoque: {p['estoque_atual']}, R$ {p['preco_unitario']:.2f})": p
            for p in produtos
        }

        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            produto_sel = st.selectbox("Produto", list(produto_opcoes.keys()), key="produto_sel")
        with col2:
            quantidade = st.number_input("Qtd.", min_value=1, value=1, step=1, key="qtd_sel")
        with col3:
            st.write("")
            st.write("")
            if st.button("Adicionar item"):
                produto = produto_opcoes[produto_sel]
                st.session_state.itens_orcamento.append(
                    {
                        "produto_id": produto["id"],
                        "produto_nome": produto["nome"],
                        "quantidade": quantidade,
                        "preco_unitario": produto["preco_unitario"],
                    }
                )

        if st.session_state.itens_orcamento:
            st.write("**Itens adicionados:**")
            total = 0.0
            for i, item in enumerate(st.session_state.itens_orcamento):
                subtotal = item["quantidade"] * item["preco_unitario"]
                total += subtotal
                c1, c2 = st.columns([5, 1])
                c1.write(
                    f"{item['produto_nome']} — {item['quantidade']}x R$ {item['preco_unitario']:.2f} = R$ {subtotal:.2f}"
                )
                if c2.button("Remover", key=f"remover_{i}"):
                    st.session_state.itens_orcamento.pop(i)
                    st.rerun()

            st.markdown(f"### Total: R$ {total:.2f}")

            observacoes = st.text_area("Observações (opcional)")

            if st.button("✅ Finalizar orçamento e gerar PDF", type="primary"):
                cliente_id = cliente_opcoes[cliente_sel]
                itens_para_salvar = [
                    {
                        "produto_id": item["produto_id"],
                        "quantidade": item["quantidade"],
                        "preco_unitario": item["preco_unitario"],
                    }
                    for item in st.session_state.itens_orcamento
                ]
                orcamento_id = db.criar_orcamento(cliente_id, itens_para_salvar, observacoes)

                orcamento, itens = db.get_orcamento_detalhado(orcamento_id)
                caminho_pdf = f"orcamentos_pdf/orcamento_{orcamento_id:04d}.pdf"
                gerar_pdf_orcamento(orcamento, itens, caminho_pdf)

                st.session_state.itens_orcamento = []
                st.success(f"Orçamento Nº {orcamento_id:04d} criado e estoque atualizado!")

                with open(caminho_pdf, "rb") as f:
                    st.download_button(
                        "⬇️ Baixar PDF do orçamento",
                        data=f,
                        file_name=os.path.basename(caminho_pdf),
                        mime="application/pdf",
                    )
                st.info("Baixe o PDF acima e envie para o cliente pelo WhatsApp.")
        else:
            st.caption("Nenhum item adicionado ainda.")

# ---------------------------------------------------------------------------
# ORÇAMENTOS (histórico)
# ---------------------------------------------------------------------------
elif pagina == "Orçamentos":
    st.header("Orçamentos")

    orcamentos = db.get_orcamentos()
    if not orcamentos:
        st.info("Nenhum orçamento criado ainda.")
    else:
        for o in orcamentos:
            with st.expander(f"Nº {o['id']:04d} — {o['cliente_nome']} — {o['status']}"):
                orcamento, itens = db.get_orcamento_detalhado(o["id"])
                total = sum(i["quantidade"] * i["preco_unitario"] for i in itens)
                for item in itens:
                    st.write(
                        f"- {item['produto_nome']}: {item['quantidade']}x R$ {item['preco_unitario']:.2f}"
                    )
                st.write(f"**Total: R$ {total:.2f}**")

                novo_status = st.selectbox(
                    "Status",
                    ["Pendente", "Aprovado", "Recusado"],
                    index=["Pendente", "Aprovado", "Recusado"].index(o["status"])
                    if o["status"] in ["Pendente", "Aprovado", "Recusado"]
                    else 0,
                    key=f"status_{o['id']}",
                )
                if novo_status != o["status"]:
                    db.atualizar_status_orcamento(o["id"], novo_status)
                    st.rerun()

                caminho_pdf = f"orcamentos_pdf/orcamento_{o['id']:04d}.pdf"
                if os.path.exists(caminho_pdf):
                    with open(caminho_pdf, "rb") as f:
                        st.download_button(
                            "⬇️ Baixar PDF novamente",
                            data=f,
                            file_name=os.path.basename(caminho_pdf),
                            mime="application/pdf",
                            key=f"pdf_{o['id']}",
                        )

# ---------------------------------------------------------------------------
# CLIENTES
# ---------------------------------------------------------------------------
elif pagina == "Clientes":
    st.header("Clientes")

    with st.form("form_cliente", clear_on_submit=True):
        nome = st.text_input("Nome")
        telefone = st.text_input("Telefone (com DDD)")
        endereco = st.text_input("Endereço (opcional)")
        if st.form_submit_button("Cadastrar cliente"):
            if nome:
                db.add_cliente(nome, telefone, endereco)
                st.success(f"Cliente {nome} cadastrado!")
                st.rerun()
            else:
                st.error("Informe ao menos o nome.")

    st.subheader("Clientes cadastrados")
    clientes = db.get_clientes()
    if clientes:
        st.dataframe(
            [{"Nome": c["nome"], "Telefone": c["telefone"], "Endereço": c["endereco"]} for c in clientes],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.caption("Nenhum cliente cadastrado ainda.")

# ---------------------------------------------------------------------------
# PRODUTOS / ESTOQUE
# ---------------------------------------------------------------------------
elif pagina == "Produtos / Estoque":
    st.header("Produtos / Estoque")

    with st.form("form_produto", clear_on_submit=True):
        nome = st.text_input("Nome do produto/estampa")
        descricao = st.text_input("Descrição (opcional)")
        col1, col2, col3 = st.columns(3)
        preco = col1.number_input("Preço unitário (R$)", min_value=0.0, step=0.5, format="%.2f")
        estoque = col2.number_input("Estoque inicial", min_value=0, step=1)
        estoque_min = col3.number_input("Estoque mínimo", min_value=0, step=1)
        if st.form_submit_button("Cadastrar produto"):
            if nome:
                db.add_produto(nome, descricao, preco, estoque, estoque_min)
                st.success(f"Produto {nome} cadastrado!")
                st.rerun()
            else:
                st.error("Informe ao menos o nome do produto.")

    st.subheader("Produtos cadastrados")
    produtos = db.get_produtos()
    if produtos:
        for p in produtos:
            alerta = " ⚠️ estoque baixo" if p["estoque_atual"] <= p["estoque_minimo"] else ""
            col1, col2, col3 = st.columns([4, 2, 2])
            col1.write(f"**{p['nome']}**{alerta}")
            col2.write(f"R$ {p['preco_unitario']:.2f}")
            col3.write(f"Estoque: {p['estoque_atual']}")

            ajuste = st.number_input(
                f"Ajustar estoque de {p['nome']} (+entrada / -saída)",
                min_value=-9999,
                max_value=9999,
                value=0,
                step=1,
                key=f"ajuste_{p['id']}",
            )
            if st.button("Aplicar ajuste", key=f"btn_ajuste_{p['id']}"):
                if ajuste != 0:
                    db.ajustar_estoque(p["id"], ajuste)
                    st.success("Estoque atualizado!")
                    st.rerun()
            st.divider()
    else:
        st.caption("Nenhum produto cadastrado ainda.")
