import streamlit as st
import requests, time
import pandas as pd

@st.cache_data
def df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

def success_message():
    success = st.success('Arquivo baixado com sucesso!', icon='✅')
    time.sleep(5)
    success.empty()

st.set_page_config(layout='wide')
st.title('DADOS BRUTOS')

## Dados API
url = 'https://labdados.com/produtos'
response = requests.get(url)
data = pd.DataFrame.from_dict(response.json())
data['Data da Compra'] = pd.to_datetime(data['Data da Compra'], format = '%d/%m/%Y')


with st.expander('Colunas'):
    columns = st.multiselect('Selecione as colunas', list(data.columns), list(data.columns))


# Sidebar filtros
st.sidebar.title('Filtros')
with st.sidebar.expander('Nome do produto'):
    products = st.multiselect('Selecione os produtos', list(data['Produto'].unique()), list(data['Produto'].unique()))
with st.sidebar.expander('Categoria'):
    categories = st.multiselect('Selecione as categorias', list(data['Categoria do Produto'].unique()), list(data['Categoria do Produto'].unique()))
with st.sidebar.expander('Preço'):
    price = st.slider('Preço', 0, 5000, (0, 5000))
with st.sidebar.expander('Frete'):
    freight = st.slider('Frete', 0, 250, (0, 250))
with st.sidebar.expander('Data da compra'):
    date = st.date_input('Data da compra', (data['Data da Compra'].min(), data['Data da Compra'].max()))
with st.sidebar.expander('Vendedor'):
    seller = st.multiselect('Selecione os Vendedores', list(data['Vendedor'].unique()), list(data['Vendedor'].unique()))
with st.sidebar.expander('Avaliação da compra'):
    evaluation = st.slider('Avaliação da compra', 1, 5, (1, 5))
with st.sidebar.expander('Tipo de Pagamento'):
    payment = st.multiselect('Tipo de pagamento', list(data['Tipo de pagamento'].unique()), list(data['Tipo de pagamento'].unique()))
with st.sidebar.expander('Quantidade de parcelas'):
    installments = st.slider('Quantidade de parcelas', 1, 24, (1, 24))

query = '''
Produto in @products and \
`Categoria do Produto` in @categories and \
@price[0] <= Preço <= @price[1] and \
@date[0] <= `Data da Compra` <= @date[1] and \
Vendedor in @seller and \
@evaluation[0] <= `Avaliação da compra` <= @evaluation[1] and \
`Tipo de pagamento` in @payment and \
@installments[0] <= `Quantidade de parcelas` <= @installments[1]
'''

filtered_data = data.query(query)
filtered_data = filtered_data[columns]

st.dataframe(filtered_data)
st.markdown(f'A tabela possui :blue[{filtered_data.shape[0]}] linhas e :blue[{filtered_data.shape[1]}] colunas')

st.markdown('Escreva um nome para o arquivo')
column_1, column_2 = st.columns(2)
with column_1:
    filename = st.text_input('', label_visibility='collapsed', value='dados')
    filename += '.csv'
with column_2:
    st.download_button(
        'Baixar dados em csv',
        data=df_to_csv(filtered_data),
        file_name=filename,
        mime='text/csv',
        on_click=success_message
    )