from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from time import sleep
from bs4 import BeautifulSoup
import pandas as pd

# Abrindo a Hotmart
endereco = 'https://app.hotmart.com/market'

options = Options()
options.add_argument('window-size=900,660')
service = Service(ChromeDriverManager().install())
navegador = webdriver.Chrome(service=service, options=options)
navegador.get(endereco)

list_produtos = []

# Acessando a conta hotmart
cont = 0
while True:
    sleep(1)
    try:
        input_user = navegador.find_element(By.ID, 'username')
        break
    except:
        cont += 1
        if cont > 60:
            break

input('Apos selecionar aperte enter: ')
nome_arquivo_exportacao = input('Digite um nome para o arquivo CSV: ')

# Capturando a página com Beautiful Soap
tem_botao = True
passagem = 0
try:
    while True:
        cont = 0
        while True:
            sleep(1)
            page_content = navegador.page_source
            site = BeautifulSoup(page_content, 'html.parser')    
            try:
                if site.find('div', attrs={'class': 'hot-col-xl-3 hot-col-lg-4 hot-col-md-6 hot-col-sm-12 _py-3'}):
                    break
            except:
                cont += 1
                if cont > 120:
                    break

        produtos = site.find_all('div', attrs={'class': 'hot-col-xl-3 hot-col-lg-4 hot-col-md-6 hot-col-sm-12 _py-3'})
        #print(produtos)

        # Capturando informações da página    
        for produto in produtos:
            try:
                link_produto = 'https://app.hotmart.com'+(produto.find('a', attrs={'class': 'product-detail-link'})['href'])
            except:
                link_produto = '-'
            try:
                nome_produto = str(produto.find('span', attrs={'class': 'product-name _text-md-2 _text-gray-800'}).string)
            except:
                nome_produto = '-'
            try:
                qtd_avaliacoes = int(produto.find('span', attrs={'class': '_ml-1 _text-1 _text-gray-500 _font-weight _d-none _d-md-inline'}).string.lstrip('(').rstrip(')'))
            except:
                qtd_avaliacoes = '-'
            try:
                temperatura_produto = int(produto.find_all('span', attrs={'class': '_mr-1 _text-1 _text-gray-800'}, limit=2)[1].string.rstrip('°'))
            except:
                temperatura_produto = '-'
            try:
                comissao = float(produto.find('p', attrs={'class': '_mb-0 _text-3 _text-md-4 _text-green _font-weight-light'}).string.lstrip('R$ ').replace(',','.'))
            except:
                comissao = '-'
            try:
                preco = float(produto.find('p', attrs={'class': '_mb-0 _text-1 _text-gray-500'}).string.lstrip('Preço máximo do produto: R$ ').replace(',','.'))
            except:
                preco = '-'

            try:
                if comissao > 89.99 and temperatura_produto >= 21 and temperatura_produto < 81 and qtd_avaliacoes > 1:
                    list_produtos.append([nome_produto, link_produto, qtd_avaliacoes, temperatura_produto, comissao, preco])
            except:
                pass

        passagem += 1
        
        paginas = site.find_all('hot-pagination-item')
        for k, i in enumerate(paginas):
            temporario = str(i)
            if 'hot-pagination__item--active' in temporario:
                proxima_pagina = k+2
                #print(f'proxima pagina -> {proxima_pagina}')

        if navegador.find_element(By.XPATH, f'//*[@id="vulcano-market"]/div/div[4]/hot-pagination/hot-pagination-item[{proxima_pagina}]'):
            navegador.find_element(By.XPATH, f'//*[@id="vulcano-market"]/div/div[4]/hot-pagination/hot-pagination-item[{proxima_pagina}]').click()
        else:
            break

        if passagem > 20:
            break
except:
    pass
data = list_produtos
df = pd.DataFrame(data, columns=['NomeProduto', 'EnderecoWeb','Avaliacoes','Temperatura','Comissao','Preco'])

df.to_csv(f"{nome_arquivo_exportacao}.csv", encoding = 'utf-8', index = False)

navegador.close()
