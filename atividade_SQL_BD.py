# =======================================================
# 📊 Atividade Prática — SQL, Relacionamentos e Análise de Dados
# Desenvolvido por Claudinez | Python + Streamlit + Plotly
# =======================================================

import streamlit as st
import plotly.express as px
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv
import os
from datetime import datetime

# ---- CONFIGURAÇÃO ----
load_dotenv()
st.set_page_config(page_title="📊 Dashboard de Vendas", layout="wide")

# Conexão Supabase (usa .env com fallback para valores fornecidos)
SUPABASE_URL = os.getenv("SUPABASE_URL") or "https://lbqmatwzwmwsvgpmzmrm.supabase.co"
SUPABASE_KEY = (
    os.getenv("SUPABASE_ANON_KEY")
    or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxicW1hdHd6d213c3ZncG16bXJtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIyMDc1NjgsImV4cCI6MjA3Nzc4MzU2OH0.uQdyvnb-S6GA8rkOtGOOgUldf04pqbWaPhtuRggQHKc"
)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---- CONSULTA DADOS ----
produtos = supabase.table("produtos").select("*").execute()
vendas = supabase.table("vendas").select("*").execute()

df_produtos = pd.DataFrame(produtos.data)
df_vendas = pd.DataFrame(vendas.data)

# ---- TABELAS NO INÍCIO ----
if df_vendas.empty or df_produtos.empty:
    st.error("⚠️ Nenhum dado encontrado nas tabelas 'produtos' ou 'vendas'.")
else:
    st.header("📋 Tabelas Originais")
    col_t1, col_t2 = st.columns(2)
    # Campos selecionados conforme solicitado
    with col_t1:
        st.subheader("Tabela: Produtos (seleção)")
        prod_cols = [c for c in ["nome_produto", "categoria", "preco_unitario"] if c in df_produtos.columns]
        st.dataframe(df_produtos[prod_cols], width='stretch')
    with col_t2:
        st.subheader("Tabela: Vendas (seleção)")
        vend_cols = [c for c in ["id_venda", "quantidade", "desconto", "data_venda"] if c in df_vendas.columns]
        df_vendas_sel = df_vendas[vend_cols].copy()
        if "data_venda" in df_vendas_sel.columns:
            try:
                df_vendas_sel["data_venda"] = pd.to_datetime(df_vendas_sel["data_venda"], errors="coerce")
                df_vendas_sel["data_venda"] = df_vendas_sel["data_venda"].dt.strftime("%d/%m/%Y")
            except Exception as e:
                st.warning(f"Não foi possível formatar data em Vendas: {e}")
        st.dataframe(df_vendas_sel, width='stretch')


st.header("🔗 Resumo (Vendas + Produtos) com Valor Total")
st.markdown("""
Mostra apenas os campos solicitados e calcula `valor_total = quantidade * preco_unitario`.
Campos vazios são mantidos como estão.
""")

# Faz o merge localmente, evitando necessidade de função RPC no Supabase
try:
    # Garantir tipos numéricos
    for col in ["quantidade", "preco_unitario", "desconto"]:
        if col in df_vendas.columns:
            df_vendas[col] = pd.to_numeric(df_vendas[col], errors="coerce")
        if col in df_produtos.columns:
            df_produtos[col] = pd.to_numeric(df_produtos[col], errors="coerce")

    df = pd.merge(df_vendas, df_produtos, on="id_produto", how="inner")
    # Calcula valor_total sem alterar campos vazios
    if {"quantidade", "preco_unitario"}.issubset(df.columns):
        df["valor_total"] = df["quantidade"] * df["preco_unitario"]

    # Formatar data_venda (DD/MM/YYYY) mantendo vazios como NaN
    if "data_venda" in df.columns:
        try:
            df["data_venda"] = pd.to_datetime(df["data_venda"], errors="coerce")
            df["data_venda"] = df["data_venda"].dt.strftime("%d/%m/%Y")
        except Exception as e:
            st.warning(f"Não foi possível formatar data na Tabela Resumo: {e}")

    # Seleção final de colunas
    final_cols = [
        c for c in [
            "id_venda",
            "nome_produto",
            "categoria",
            "quantidade",
            "preco_unitario",
            "desconto",
            "data_venda",
            "valor_total",
        ] if c in df.columns
    ]

    st.subheader("📋 Tabela Resumo (seleção)")
    st.dataframe(
        df[final_cols],
        width='stretch',
        column_config={
            "id_venda": st.column_config.NumberColumn("ID", width="small"),
            "nome_produto": st.column_config.TextColumn("Produto", width="medium"),
            "categoria": st.column_config.TextColumn("Categoria", width="small"),
            "quantidade": st.column_config.NumberColumn("Qtd", width="small"),
            "preco_unitario": st.column_config.NumberColumn("Preço Unitário", format="R$ %.2f", width="small"),
            "desconto": st.column_config.NumberColumn("Desconto", width="small"),
            "data_venda": st.column_config.TextColumn("Data", width="small"),
            "valor_total": st.column_config.NumberColumn("Valor Total", format="R$ %.2f", width="small"),
        }
    )
except Exception as e:
    st.error(f"Erro ao relacionar dados localmente: {e}")

# ---- TABELA COM TRATAMENTO DE NULOS ----
st.header("🧮 Tabela Resumo (tratamento de nulos)")
try:
    df_nulos = df.copy()
    # Tratar nulos em campos numéricos
    # quantidade e desconto: manter 0 quando nulos
    for col in ["quantidade", "desconto"]:
        if col in df_nulos.columns:
            df_nulos[col] = pd.to_numeric(df_nulos[col], errors="coerce").fillna(0)
    # preco_unitario: converter e não preencher com 0; vamos imputar média
    if "preco_unitario" in df_nulos.columns:
        df_nulos["preco_unitario"] = pd.to_numeric(df_nulos["preco_unitario"], errors="coerce")

    # Tratar nulos em textos
    for col in ["nome_produto", "categoria"]:
        if col in df_nulos.columns:
            df_nulos[col] = df_nulos[col].fillna("—")

    # Formatar data e tratar nulos
    if "data_venda" in df_nulos.columns:
        df_nulos["data_venda_dt"] = pd.to_datetime(df_nulos["data_venda"], errors="coerce")
        df_nulos["data_venda"] = df_nulos["data_venda_dt"].dt.strftime("%d/%m/%Y")
        df_nulos["data_venda"] = df_nulos["data_venda"].fillna("—")

    # Imputar preço médio quando preco_unitario estiver ausente
    if {"preco_unitario", "nome_produto", "categoria"}.issubset(df_nulos.columns):
        # média por produto (ignora NaNs automaticamente)
        prod_mean = df_nulos.groupby("nome_produto", dropna=False)["preco_unitario"].mean()
        # média por categoria
        cat_mean = df_nulos.groupby("categoria", dropna=False)["preco_unitario"].mean()
        # aplicar por produto
        mask_na = df_nulos["preco_unitario"].isna()
        df_nulos.loc[mask_na, "preco_unitario"] = df_nulos.loc[mask_na, "nome_produto"].map(prod_mean)
        # aplicar por categoria onde ainda está NaN
        mask_na = df_nulos["preco_unitario"].isna()
        df_nulos.loc[mask_na, "preco_unitario"] = df_nulos.loc[mask_na, "categoria"].map(cat_mean)
        # aplicar média global como último recurso
        global_mean = df_nulos["preco_unitario"].mean()
        df_nulos["preco_unitario"] = df_nulos["preco_unitario"].fillna(global_mean)

    # Recalcular valor_total com nulos tratados (usando preço imputado quando necessário)
    if {"quantidade", "preco_unitario"}.issubset(df_nulos.columns):
        df_nulos["valor_total"] = df_nulos["quantidade"] * df_nulos["preco_unitario"]

    # Seleção final de colunas
    final_cols_nulos = [
        c for c in [
            "id_venda",
            "nome_produto",
            "categoria",
            "quantidade",
            "preco_unitario",
            "desconto",
            "data_venda",
            "valor_total",
        ] if c in df_nulos.columns
    ]

    # Tratamento de datas faltantes: ocultar linhas ou imputar mediana
    if "data_venda" in df_nulos.columns:
        opt = st.radio(
            "Tratamento para datas faltantes",
            ("Ocultar linhas com data vazia", "Imputar data mediana"),
            index=0,
            horizontal=True,
        )
    else:
        opt = "Ocultar linhas com data vazia"

    df_nulos_display = df_nulos.copy()
    if opt == "Ocultar linhas com data vazia":
        df_nulos_display = df_nulos_display[df_nulos_display["data_venda"] != "—"]
    else:
        # Imputar mediana de data nas linhas com data vazia
        try:
            if "data_venda_dt" in df_nulos_display.columns:
                series = df_nulos_display["data_venda_dt"].dropna()
                if not series.empty:
                    # calcular mediana robusta para datetime
                    median_val = int(series.astype("int64").median())
                    median_dt = pd.to_datetime(median_val)
                    mask = df_nulos_display["data_venda"] == "—"
                    df_nulos_display.loc[mask, "data_venda_dt"] = median_dt
                    df_nulos_display.loc[mask, "data_venda"] = df_nulos_display.loc[mask, "data_venda_dt"].dt.strftime("%d/%m/%Y")
        except Exception as _:
            pass

    # Opcional: ocultar linhas com campos de texto vazios (nome, categoria, data)
    hide_empty = st.checkbox(
        "Ocultar linhas com campos vazios (Produto/Categoria/Data)", value=True
    )
    if hide_empty:
        for col in ["nome_produto", "categoria", "data_venda"]:
            if col in df_nulos_display.columns:
                df_nulos_display = df_nulos_display[df_nulos_display[col] != "—"]
                df_nulos_display = df_nulos_display[
                    df_nulos_display[col].astype(str).str.strip() != ""
                ]
except Exception as e:
    st.error(f"Erro ao processar nulos na Tabela Resumo: {e}")

# ---- FILTROS ADICIONAIS ----
st.sidebar.header('Filtros Adicionais')

# Filtro por data
if 'data_venda_dt' in df_nulos_display.columns and not df_nulos_display['data_venda_dt'].empty:
    min_date = df_nulos_display['data_venda_dt'].min().date()
    max_date = df_nulos_display['data_venda_dt'].max().date()

    start_date = st.sidebar.date_input('Data Inicial', min_date, format="DD/MM/YYYY")
    end_date = st.sidebar.date_input('Data Final', max_date, format="DD/MM/YYYY")

    # Converter as datas selecionadas para datetime para comparação
    start_date_dt = datetime.combine(start_date, datetime.min.time())
    end_date_dt = datetime.combine(end_date, datetime.max.time())

    df_filtered = df_nulos_display[
        (df_nulos_display['data_venda_dt'] >= start_date_dt) &
        (df_nulos_display['data_venda_dt'] <= end_date_dt)
    ]
else:
    df_filtered = df_nulos_display.copy()

# Filtro por categoria
if 'categoria' in df_filtered.columns and not df_filtered['categoria'].empty:
    unique_categories = df_filtered['categoria'].unique().tolist()
    selected_categories = st.sidebar.multiselect('Filtrar por Categoria', unique_categories, unique_categories)
    df_filtered = df_filtered[df_filtered['categoria'].isin(selected_categories)]

# Atualizar df_source para os gráficos usarem o DataFrame filtrado
df_source = df_filtered.copy()

try:
    # Botão de exportar para CSV
    if not df_filtered.empty:
        csv = df_filtered.to_csv(index=False).encode('utf-8')
        st.sidebar.download_button(
            label="Exportar Dados Filtrados para CSV",
            data=csv,
            file_name="dados_filtrados.csv",
            mime="text/csv",
        )
        st.dataframe(
            df_filtered[final_cols_nulos],
            width='stretch',
            column_config={
                "id_venda": st.column_config.NumberColumn("ID", width="small"),
                "nome_produto": st.column_config.TextColumn("Produto", width="medium"),
                "categoria": st.column_config.TextColumn("Categoria", width="small"),
                "quantidade": st.column_config.NumberColumn("Qtd", width="small"),
                "preco_unitario": st.column_config.NumberColumn("Preço Unitário", format="R$ %.2f", width="small"),
                "desconto": st.column_config.NumberColumn("Desconto", width="small"),
                "data_venda": st.column_config.TextColumn("Data", width="small"),
                "valor_total": st.column_config.NumberColumn("Valor Total", format="R$ %.2f", width="small"),
            }
        )
except Exception as e:
    st.error(f"Erro ao montar tabela com nulos tratados: {e}")

# ---- ANÁLISES E VISUALIZAÇÕES ----
st.header("📈 Análises e Visualizações")

# Seletor de gráficos na barra lateral
chart_selection = st.sidebar.selectbox(
    'Selecione o Gráfico para Visualizar',
    (
        'Faturamento por Categoria',
        'Evolução Diária e Dias de Pico',
        'Top 10 Produtos'
    )
)

try:
    df_metrics = df_source.copy()

    # Converter data para datetime para gráficos temporais
    if 'data_venda' in df_metrics.columns:
        df_metrics['data_venda_dt'] = pd.to_datetime(df_metrics['data_venda'], format='%d/%m/%Y', errors='coerce')

    # 1) Faturamento por categoria e Faturamento médio por categoria
    if chart_selection == 'Faturamento por Categoria':
        if 'categoria' in df_metrics.columns:
            cat_rev = (
                df_metrics.groupby('categoria', dropna=False)['valor_total'].sum().reset_index()
            )
            cat_avg = (
                df_metrics.groupby('categoria', dropna=False)['valor_total'].mean().reset_index()
            )
            st.subheader('Faturamento Médio (Barras) e Total (Pizza) por Categoria')
            col_barras, col_pizza = st.columns(2)
            with col_barras:
                fig_cat_avg = px.bar(
                    cat_avg,
                    x='categoria', y='valor_total',
                    color='categoria',
                    color_discrete_sequence=px.colors.qualitative.Pastel,
                    title='Médio por Categoria (Barras)',
                    labels={'categoria': 'Categoria', 'valor_total': 'Médio (R$)'}
                )
                fig_cat_avg.update_layout(showlegend=False, template='plotly_white')
                fig_cat_avg.update_traces(marker_line_color='rgba(0,0,0,0.15)', marker_line_width=1, opacity=0.9)
                st.plotly_chart(fig_cat_avg, use_container_width=True)
            with col_pizza:
                fig_cat_pie = px.pie(
                    cat_rev,
                    names='categoria', values='valor_total',
                    title='Faturamento por Categoria (Pizza)'
                )
                st.plotly_chart(fig_cat_pie, use_container_width=True)

    # 2) Evolução diária (linha) e Dias de Pico (barras)
    if chart_selection == 'Evolução Diária e Dias de Pico':
        if 'data_venda_dt' in df_metrics.columns:
            daily_rev = (
                df_metrics.dropna(subset=['data_venda_dt'])
                .groupby('data_venda_dt')['valor_total'].sum().reset_index()
                .sort_values('data_venda_dt')
            )
            st.subheader('Evolução do Faturamento Diário e Dias de Pico')
            col_line, col_peaks = st.columns(2)
            with col_line:
                fig_daily = px.line(
                    daily_rev,
                    x='data_venda_dt', y='valor_total',
                    markers=True,
                    title='Evolução do Faturamento Diário',
                    labels={'data_venda_dt': 'Data', 'valor_total': 'Faturamento (R$)'}
                )
                fig_daily.update_layout(template='plotly_white')
                st.plotly_chart(fig_daily, use_container_width=True)
            with col_peaks:
                top_n = 10
                peaks = (
                    daily_rev.sort_values('valor_total', ascending=False).head(top_n)
                )
                # Rótulo com o dia do pico (DD/MM)
                if 'data_venda_dt' in peaks.columns:
                    try:
                        peaks['dia_pico'] = peaks['data_venda_dt'].dt.strftime('%d/%m')
                    except Exception:
                        peaks['dia_pico'] = ''
                fig_peaks = px.bar(
                    peaks,
                    x='data_venda_dt', y='valor_total',
                    color='data_venda_dt',
                    text='dia_pico',
                    color_discrete_sequence=px.colors.qualitative.Pastel,
                    title=f'Dias de Pico de Faturamento (Top {top_n})',
                    labels={'data_venda_dt': 'Data', 'valor_total': 'Faturamento (R$)'}
                )
                # Ajustar posição e estilo dos rótulos
                fig_peaks.update_traces(textposition='outside',
                                        marker_line_color='rgba(0,0,0,0.15)', marker_line_width=1, opacity=0.9)
                fig_peaks.update_layout(showlegend=False, template='plotly_white')
                st.plotly_chart(fig_peaks, use_container_width=True)

    # 3) Top 10 Produtos Mais Lucrativos (barras) e Produtos com mais vendas (pizza)
    if chart_selection == 'Top 10 Produtos':
        if 'nome_produto' in df_metrics.columns:
            prod_profit = (
                df_metrics.groupby('nome_produto', dropna=False)['valor_total'].sum().reset_index()
                .sort_values('valor_total', ascending=False)
                .head(10)
            )
            # Usar unidades vendidas (soma de quantidade) em vez de contar registros
            if 'quantidade' in df_metrics.columns:
                prod_sales = (
                    df_metrics.groupby('nome_produto', dropna=False)['quantidade']
                    .sum()
                    .reset_index(name='unidades_vendidas')
                    .sort_values('unidades_vendidas', ascending=False)
                    .head(10)
                )
                sales_values_col = 'unidades_vendidas'
            else:
                # fallback: contar registros
                prod_sales = (
                    df_metrics.groupby('nome_produto', dropna=False)
                    .size()
                    .reset_index(name='num_vendas')
                    .sort_values('num_vendas', ascending=False)
                    .head(10)
                )
                sales_values_col = 'num_vendas'

            st.subheader('Top 10 Mais Lucrativos (Barras) e Mais Vendas (Pizza)')
            col_lucro, col_vendas = st.columns(2)
            with col_lucro:
                fig_top10 = px.bar(
                    prod_profit,
                    x='nome_produto', y='valor_total',
                    color='nome_produto',
                    color_discrete_sequence=px.colors.qualitative.Pastel,
                    title='Top 10 Produtos Mais Lucrativos',
                    labels={'nome_produto': 'Produto', 'valor_total': 'Faturamento (R$)'}
                )
                fig_top10.update_layout(showlegend=False, template='plotly_white')
                fig_top10.update_traces(marker_line_color='rgba(0,0,0,0.15)', marker_line_width=1, opacity=0.9)
                st.plotly_chart(fig_top10, use_container_width=True)
            with col_vendas:
                fig_top_sales_pie = px.pie(
                    prod_sales,
                    names='nome_produto', values=sales_values_col,
                    title='Top 10 Produtos por Número de Vendas (Pizza)'
                )
                st.plotly_chart(fig_top_sales_pie, use_container_width=True)
except Exception as e:
    st.error(f"Erro ao gerar análises e visualizações: {e}")

    st.sidebar.header('Filtros Adicionais')

    # Filtro por data
    min_date = df_nulos_display['data_venda_dt'].min().date()
    max_date = df_nulos_display['data_venda_dt'].max().date()

    start_date = st.sidebar.date_input('Data Inicial', min_date)
    end_date = st.sidebar.date_input('Data Final', max_date)

    # Converter as datas selecionadas para datetime para comparação
    start_date_dt = datetime.combine(start_date, datetime.min.time())
    end_date_dt = datetime.combine(end_date, datetime.max.time())

    df_filtered = df_nulos_display[
        (df_nulos_display['data_venda_dt'] >= start_date_dt) &
        (df_nulos_display['data_venda_dt'] <= end_date_dt)
    ]

    # Atualizar df_source para os gráficos usarem o DataFrame filtrado
    df_source = df_filtered.copy()

    st.dataframe(df_filtered, use_container_width=True)

    st.plotly_chart(fig_cat_pie, use_container_width=True)
