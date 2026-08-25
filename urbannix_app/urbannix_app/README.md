# Urbannix — Sistema de Orçamentos, Financeiro e Estoque

Sistema simples em Python + Streamlit para a Urbannix cadastrar clientes,
controlar estoque e gerar orçamentos em PDF para enviar pelo WhatsApp.

## Estrutura do projeto

```
urbannix_app/
├── app.py              # Telas do sistema (Streamlit)
├── database.py         # Acesso ao banco SQLite (clientes, produtos, orçamentos)
├── pdf_generator.py     # Geração do PDF do orçamento
├── requirements.txt    # Bibliotecas necessárias
├── urbannix.db          # Banco de dados (criado automaticamente na 1ª execução)
└── orcamentos_pdf/     # PDFs dos orçamentos gerados
```

## Como rodar no seu computador

1. Instale o Python (3.10 ou mais recente): https://www.python.org/downloads/
2. Abra o terminal dentro da pasta `urbannix_app`
3. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```
4. Rode o sistema:
   ```
   streamlit run app.py
   ```
5. Vai abrir uma aba no navegador (geralmente `localhost:8501`) com o sistema
   funcionando. Pelo celular, ele também abre no navegador (Chrome/Safari).

## Como usar

1. **Clientes** → cadastre os clientes da Urbannix (nome, telefone, endereço)
2. **Produtos / Estoque** → cadastre os produtos/estampas com preço e estoque
3. **Novo orçamento** → escolha o cliente, adicione os itens, e clique em
   "Finalizar orçamento e gerar PDF". O estoque é atualizado automaticamente.
4. Baixe o PDF gerado e envie pelo WhatsApp Web ou pelo celular
5. **Orçamentos** → veja o histórico e mude o status (Pendente/Aprovado/Recusado).
   Ao marcar como **Aprovado**, o sistema já cria automaticamente um
   lançamento "a receber" em Financeiro, no valor total do orçamento.
6. **Financeiro** → acompanhe:
   - Totais de "a receber", "a pagar", recebido e pago no mês (no topo)
   - Gráfico de faturamento dos últimos 6 meses
   - Listas de contas a receber/pagar pendentes, com botão para marcar como
     quitadas
   - Lançamentos manuais (ex: compra de insumos, aluguel, contas fixas)
   - Histórico de tudo que já foi pago/recebido

## Como sua esposa acessa pelo celular, de qualquer lugar

Rodando só no seu PC, o sistema só funciona na mesma rede Wi-Fi. Para acessar
de qualquer lugar (loja, na rua, etc.), publique de graça em:

**Streamlit Community Cloud** (https://streamlit.io/cloud)
1. Crie uma conta gratuita (pode entrar com GitHub)
2. Suba esse projeto num repositório no GitHub
3. No Streamlit Cloud, clique em "New app", aponte pro repositório e pro
   arquivo `app.py`
4. Em poucos minutos você recebe um link (tipo `urbannix.streamlit.app`) que
   funciona em qualquer celular com internet, como um app

## Próximos passos sugeridos

- Tela de "Financeiro" com contas a pagar/receber e relatório de faturamento
- Login simples (usuário/senha) para proteger o sistema
- Editar/excluir clientes, produtos e orçamentos já cadastrados
- Alerta automático de estoque baixo na tela inicial
- Numeração e logo personalizados no PDF do orçamento
