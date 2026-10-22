import streamlit as st
import pandas as pd
import plotly.express as px
import re

st.set_page_config(
    page_title="Dashboard de Dados",
    layout="wide"
)

st.title("Dashboard de Dados - Análise de Educação (RS)")

arquivo = st.file_uploader(
    "Envie um arquivo CSV",
    type=["csv"]
)

if arquivo is not None:
    df = pd.read_csv(arquivo, encoding='latin1', skiprows=1)
    
    col1, col2 = st.columns(2)

    col1.metric(
        "Quantidade de registos",
        df.shape[0]
    )

    col2.metric(
        "Quantidade de colunas",
        df.shape[1]
    )
    
    st.subheader("Visualização dos dados (Top 5 Cidades com Mais Escolas em 2024)")
    
    # --- LIMPEZA DOS NOMES DAS COLUNAS E ORDENAÇÃO PELAS 5 MAIORES ---
    df_exibir = df.copy()
    col_2024 = [c for c in df.columns if '2024' in c][0]
    
    df_exibir = df_exibir.nlargest(5, col_2024)
    
    novos_nomes = {}
    for c in df_exibir.columns:
        if 'Total' in c:
            ano_encontrado = re.search(r'(\d{4})', c)
            if ano_encontrado:
                novos_nomes[c] = ano_encontrado.group(1)
    df_exibir = df_exibir.rename(columns=novos_nomes)
    
    st.dataframe(df_exibir)
    
    # --- INFORMAÇÃO DAS COLUNAS ---
    st.markdown("""
    **O que significa cada coluna da tabela:**
    * **Município:** Nome do município do Rio Grande do Sul.
    * **ibge:** Código oficial de identificação do município no IBGE.
    * **latitude:** Coordenada geográfica de latitude da cidade.
    * **longitude:** Coordenada geográfica de longitude da cidade.
    * **2014 a 2024:** Quantidade de estabelecimentos de Ensino Fundamental ativos em cada ano correspondente.
    """)
    
    # --- GRÁFICO 1: EVOLUÇÃO TEMPORAL (Linhas) ---
    cols_anos = [c for c in df.columns if 'Total' in c]
    df_melt = df.melt(id_vars=['Município'], value_vars=cols_anos, var_name='ano', value_name='valor')
    df_melt['ano'] = df_melt['ano'].str.extract(r'(\d{4})')
    
    df_grafico = df_melt.groupby('ano', as_index=False)['valor'].sum()

    fig_evolucao = px.line(
        df_grafico,
        x="ano",
        y="valor",
        labels={"valor": "Total de Escolas"},
        title="Evolução do Total de Escolas de Ensino Fundamental no RS (2014-2024)"
    )

    st.plotly_chart(
        fig_evolucao,
        use_container_width=True
    )

    # Respostas para a Análise do Gráfico 1
    st.markdown("""
    ### Análise do Gráfico 1: Evolução Temporal
    * **Qual informação aparece?** O total de escolas de Ensino Fundamental ativas no estado do Rio Grande do Sul ao longo dos anos (de 2014 a 2024).
    * **Qual é o maior valor?** O maior valor ocorre no ano inicial (2014), com aproximadamente 6.350 escolas.
    * **Existe algum valor muito diferente?** Não há valores discrepantes isolados; a curva desce de forma suave e contínua.
    * **Existe aumento ou diminuição?** Há uma diminuição constante ao longo dos anos, passando de cerca de 6.350 em 2014 para cerca de 5.616 em 2024.
    * **Existem diferenças entre categorias?** As categorias aqui são os anos, mostrando a variação temporal da rede de ensino.
    * **Existe algum padrão aparente?** Sim, um padrão claro de queda gradual, associado a fatores demográficos e à consolidação de redes escolares.
    """)

    # --- MÉTRICA RESUMIDA ---
    media_escolas = df_grafico["valor"].mean()
    st.metric(
        "Média de Escolas por Ano",
        round(media_escolas, 0)
    )

    # --- GRÁFICO 2: MUNICÍPIOS COM MAIS ESCOLAS (Barras) ---
    st.markdown("---")
    df_top10 = df.nlargest(10, col_2024)

    fig_municipios = px.bar(
        df_top10,
        x="Município",
        y=col_2024,
        labels={col_2024: "Total de Escolas (2024)"},
        title="Top 10 Municípios com Maior Quantidade de Escolas (2024)"
    )

    st.plotly_chart(
        fig_municipios,
        use_container_width=True
    )

    # Respostas para a Análise do Gráfico 2
    st.markdown("""
    ### Análise do Gráfico 2: Top 10 Municípios (2024)
    * **Qual informação aparece?** Os 10 municípios do Rio Grande do Sul que possuem a maior quantidade de escolas de Ensino Fundamental em 2024.
    * **Qual é o maior valor?** O maior valor pertence a Porto Alegre, que ultrapassa 350 escolas.
    * **Existe algum valor muito diferente?** Sim, Porto Alegre destaca-se fortemente como um valor discrepante positivo (outlier), com um número de escolas muito superior aos demais.
    * **Existe aumento ou diminuição?** As barras estão ordenadas em ordem decrescente, mostrando a queda progressiva do primeiro ao décimo colocado.
    * **Existem diferenças entre categorias?** Sim, a concentração escolar é desigual: a capital e as maiores cidades concentram um volume expressivo de escolas comparado ao interior.
    * **Existe algum padrão aparente?** Sim, o padrão de concentração urbana nos principais polos populacionais e económicos do estado.
    """)

    # --- INFORMAÇÕES DE MÁXIMO E MÍNIMO ---
    mun_max = df.loc[df[col_2024].idxmax()]
    mun_min = df.loc[df[col_2024].idxmin()]

    st.markdown(f"""
    ### Destaques Municipais (2024)
    * **Município com mais escolas:** **{mun_max['Município']}** (com {mun_max[col_2024]} escolas)
    * **Município com menos escolas:** **{mun_min['Município']}** (com {mun_min[col_2024]} escolas)
    """)

    # --- PASSO 4: Procure problemas ---
    st.markdown("---")
    st.subheader("Procure problemas")
    
    nomes_limpos = []
    for c in df.columns:
        if 'Total' in c:
            ano_encontrado = re.search(r'(\d{4})', c)
            nomes_limpos.append(ano_encontrado.group(1) if ano_encontrado else c)
        else:
            nomes_limpos.append(c)

    df_nulos = pd.DataFrame({
        'Coluna': nomes_limpos,
        'Valores Nulos': df.isnull().sum().values
    })

    df_tipos = pd.DataFrame({
        'Coluna': nomes_limpos,
        'Tipo de Dado': df.dtypes.astype(str).values
    })

    st.markdown("**1. Verificação de Valores Nulos por Coluna:**")
    st.dataframe(df_nulos, use_container_width=True)

    st.markdown("**2. Verificação de Registros Duplicados:**")
    st.write(f"Total de linhas duplicadas encontradas: **{df.duplicated().sum()}**")

    st.markdown("**3. Verificação de Tipos de Dados:**")
    st.dataframe(df_tipos, use_container_width=True)
    
    # --- RELATÓRIO E JUSTIFICATIVA DOS TRATAMENTOS ---
    st.markdown("---")
    st.subheader("Relatório e Justificativa dos Tratamentos")

    st.markdown("""
    ### 1. Valores Ausentes (Dados Nulos)
    * **Qual é o problema:** Células ou campos vazios na tabela que não possuem nenhuma informação registrada.
    * **Por que pode prejudicar a análise:** Pode gerar erros em cálculos matemáticos ou fazer bibliotecas de gráficos falharem.
    * **Código Pandas necessário:** df.dropna(inplace=True)
    * **O que o código faz:** Remove da base de dados todas as linhas que contenham pelo menos um valor nulo. 
      > *Nota para a apresentação:* Como a nossa verificação resultou em 0 valores nulos, não removemos nenhum dado.

    ### 2. Registros Duplicados
    * **Qual é o problema:** Linhas inteiras repetidas exatamente iguais dentro da base de dados.
    * **Por que pode prejudicar a análise:** Conta a mesma informação mais de uma vez, duplicando artificialmente os totais.
    * **Código Pandas necessário:** df.drop_duplicates(inplace=True)
    * **O que o código faz:** Procura por linhas idênticas e remove as repetições.
      > *Nota para a apresentação:* Como o resultado foi 0 duplicadas, a base não possui registos duplicados, logo a remoção não foi necessária.

    ### 3. Tipos de Dados Incorretos
    * **Qual é o problema:** Colunas numéricas ou coordenadas estarem mal classificadas.
    * **Por que pode prejudicar a análise:** Impede cálculos numéricos avançados ou mapas interativos.
    * **Código Pandas necessário:** df['latitude'] = df['latitude'].str.replace(',', '.').astype(float)
    * **O que o código faz:** Corrige o formato decimal e converte o tipo de dado para numérico.
    """)

    # --- FONTE DOS DADOS E EXEMPLO DE IA ---
    st.markdown("---")
    st.subheader("Fonte dos Dados e Exemplo de Utilização da IA")

    st.markdown("""
    ### Fonte:
    * **Fonte:** Departamento de Economia e Estatística (DEE) / Governo do Estado do Rio Grande do Sul.

    ### Exemplo de Utilização da Inteligência Artificial (IA):
    * **Uso da IA no Projeto:** A inteligência artificial foi utilizada como uma assistente de programação ao longo do projeto. Ela ajudou a criar a estrutura do código em Python, a montar os gráficos interativos, a organizar a visualização das tabelas no Streamlit e a resolver dúvidas de formatação de forma rápida e intuitiva.
    """)