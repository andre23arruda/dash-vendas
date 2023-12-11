import streamlit as st
import requests
import pandas as pd
import plotly.express as px


def format_number(value: float, prefix='') -> str:
    for unity in ['', 'mil']:
        if value < 1000:
            return f'{prefix} {value:.2f} {unity}'
        value /= 1000
    return f'{prefix} {value:.2f} milhões'

st.set_page_config(layout='wide')
st.title('DASHBOARD DE VENDAS :shopping_trolley:')

# Sidebar filtros
st.sidebar.title('Filtros')
REGIONS = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']
region = st.sidebar.selectbox('Região', REGIONS)
if region == 'Brasil':
    region = ''

all_year = st.sidebar.checkbox('Dados de todo o período', value=True)
if all_year:
    year = ''
else:
    year = st.sidebar.slider('Ano', 2020, 2023)

## Dados API
query_string = {'regiao': region.lower(), 'ano': year}
url = 'https://labdados.com/produtos'
response = requests.get(url, params=query_string)
data = pd.DataFrame.from_dict(response.json())
data['Data da Compra'] = pd.to_datetime(data['Data da Compra'], format = '%d/%m/%Y')

## Filtro vendedores
filtro_vendedores = st.sidebar.multiselect('Vendedores', data['Vendedor'].unique())
if filtro_vendedores:
    data = data[data['Vendedor'].isin(filtro_vendedores)]

## Gráfico mapa receita
receita_estados_groupby = data.groupby('Local da compra')[['Preço']].sum().sort_values('Preço', ascending=False)
receita_estados = data.drop_duplicates(subset='Local da compra')[['Local da compra', 'lat', 'lon']] \
    .merge(receita_estados_groupby, left_on='Local da compra', right_index=True) \
    .sort_values('Preço', ascending=False)

fig_map_receita = px.scatter_geo(
    receita_estados,
    lat='lat',
    lon='lon',
    scope='south america',
    size='Preço',
    template='seaborn',
    hover_name='Local da compra',
    hover_data={'lat': False, 'lon': False},
    title='Receita por Estado'
)

## Gráfico mapa vendas
count_estados = data.groupby(['Local da compra', 'lat', 'lon']).size().reset_index(name='Vendas').sort_values('Vendas', ascending=False)
fig_map_vendas = px.scatter_geo(
    count_estados,
    lat='lat',
    lon='lon',
    scope='south america',
    size='Vendas',
    template='seaborn',
    hover_name='Local da compra',
    hover_data={'lat': False, 'lon': False},
    title='Vendas por Estado'
)

## Gráfico mensal receita
receita_mensal = data.set_index('Data da Compra').groupby(pd.Grouper(freq='M'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mês'] = receita_mensal['Data da Compra'].dt.month_name()
fig_month_receita = px.line(
    receita_mensal,
    x='Mês',
    y='Preço',
    markers=True,
    range_y=(0, receita_mensal.max()),
    color='Ano',
    line_dash='Ano',
    title='Receita mensal'
)
fig_month_receita.update_layout(yaxis_title='Receita')

## Gráfico mensal vendas
vendas_mensal = data.set_index('Data da Compra').groupby(pd.Grouper(freq='M')).size().reset_index(name='Vendas')
vendas_mensal['Ano'] = vendas_mensal['Data da Compra'].dt.year
vendas_mensal['Mês'] = vendas_mensal['Data da Compra'].dt.month_name()
fig_month_vendas = px.line(
    vendas_mensal,
    x='Mês',
    y='Vendas',
    markers=True,
    range_y=(0, vendas_mensal.max()),
    color='Ano',
    line_dash='Ano',
    title='Vendas mensal'
)
fig_month_vendas.update_layout(yaxis_title='Vendas')

## Gráficos barras receita estados
fig_bar_receita_estados = px.bar(
    receita_estados.head(),
    x='Local da compra',
    y='Preço',
    text_auto=True,
    title='Top estados'
)
fig_bar_receita_estados.update_layout(yaxis_title='Receita')

## Gráficos barras vendas estados
fig_bar_vendas_estados = px.bar(
    count_estados.head(),
    x='Local da compra',
    y='Vendas',
    text_auto=True,
    title='Top estados'
)
fig_bar_vendas_estados.update_layout(yaxis_title='Vendas')

## Gráficos barras receita categorias
receita_categorias = data.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)
fig_bar_receita_categorias = px.bar(
    receita_categorias,
    text_auto=True,
    title='Receita por categoria'
)

## Gráficos barras vendas categorias
vendas_categorias = data.groupby('Categoria do Produto')[['Produto']].count()
vendas_categorias = vendas_categorias.rename(columns={'Produto': 'Vendas'})
fig_bar_vendas_categorias = px.bar(
    vendas_categorias,
    text_auto=True,
    title='Vendas por categoria'
)

## Vendedores
vendedores = pd.DataFrame(data.groupby('Vendedor')['Preço'].agg(['sum', 'count']))


tab_1, tab_2, tab_3 = st.tabs(['Receita', 'Quantidade de vendas', 'Vendedores'])

with tab_1:
    column_1, column_2 = st.columns(2)
    with column_1:
        st.metric('Receita', format_number(data['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_map_receita, use_container_width=True)
        st.plotly_chart(fig_bar_receita_estados, use_container_width=True)

    with column_2:
        st.metric('Quantidade de vendas', format_number(data.shape[0]))
        st.plotly_chart(fig_month_receita, use_container_width=True)
        st.plotly_chart(fig_bar_receita_categorias, use_container_width=True)

    st.dataframe(data)

with tab_2:
    column_1, column_2 = st.columns(2)
    with column_1:
        st.metric('Receita', format_number(data['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_map_vendas, use_container_width=True)
        st.plotly_chart(fig_bar_vendas_estados, use_container_width=True)

    with column_2:
        st.metric('Quantidade de vendas', format_number(data.shape[0]))
        st.plotly_chart(fig_month_vendas, use_container_width=True)
        st.plotly_chart(fig_bar_vendas_categorias, use_container_width=True)

with tab_3:
    qtd_vendedores = st.number_input('Quantidade de vendedores', 2, 10, 5)

    vendedores_sum = vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores)
    vendedores_sum_index = vendedores_sum.index

    vendedores_count = vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores)
    vendedores_count_index = vendedores_count.index

    column_1, column_2 = st.columns(2)
    with column_1:
        st.metric('Receita', format_number(data['Preço'].sum(), 'R$'))
        fig_receita_vendedores = px.bar(
            vendedores_sum,
            x='sum',
            y=vendedores_sum_index,
            text_auto=True,
            title=f'Top {qtd_vendedores} vendedores (receita)'
        )
        st.plotly_chart(fig_receita_vendedores)
    with column_2:
        st.metric('Quantidade de vendas', format_number(data.shape[0]))
        fig_vendas_vendedores = px.bar(
            vendedores_count,
            x='count',
            y=vendedores_count_index,
            text_auto=True,
            title=f'Top {qtd_vendedores} vendedores (vendas)'
        )
        st.plotly_chart(fig_vendas_vendedores)
