# Educ360_Atividade_BD_Analise_Produto_Vendas
Instruções da Atividade Analise de dados produtos e vendas

Etapas sugeridas:
Explore os dados das tabelas produtos e vendas.
Observe os relacionamentos entre as tabelas.
Analise a consulta SQL que faz o JOIN e cria a coluna valor_total.
Trate os valores nulos de forma adequada.
Gere novas análises e gráficos, como:
Faturamento médio por categoria.
Produto com maior número de vendas.
Dias de pico de faturamento.
Elabore conclusões sobre os padrões identificados nos dados.
💡 Desafio extra: adicione novos filtros (por data ou categoria) e exporte o DataFrame final em CSV.
===================================================================================================================
📊 Relatório Analítico de Vendas e Faturamento — Painel Streamlit (Supabase)
1. Introdução
Este relatório apresenta uma análise detalhada dos dados de vendas provenientes da base armazenada no Supabase, integrados ao aplicativo Streamlit. 
A análise tem como objetivo identificar tendências de faturamento, padrões de comportamento de compra, e produtos de destaque em termos de lucratividade e volume de vendas, considerando o período de janeiro a junho de 2025.

Os dados analisados foram tratados quanto a valores nulos e inconsistências, com a opção de imputação de data pela mediana, assegurando consistência temporal e qualidade da informação.

2. Estrutura do Dashboard
O painel interativo desenvolvido no Streamlit exibe os seguintes elementos:

1. Faturamento Médio e Total por Categoria — Gráfico de barras e pizza.
2. Evolução do Faturamento Diário — Gráficos de linha e barras.
3. Top 10 Produtos Mais Lucrativos e Mais Vendidos — Gráficos de barras e pizza.
4. Filtros de Data — Seleção de data inicial e final para análises dinâmicas.

3. Faturamento por Categoria
A análise revelou padrões distintos:

- Categoria Informática: Alto faturamento médio devido a produtos de maior valor unitário, como Notebook Dell e Monitor LG 24".
- Categoria Acessórios: Maior volume de unidades vendidas, destacando Mouse Logitech e Cabo HDMI 2m.
- Categoria Armazenamento: Desempenho estável com preços moderados (SSD Kingston, HD Externo 1TB).
- Categorias Periféricos e Redes: Menor participação, mas contribuem para a diversificação.

Conclusão parcial: Informática e Acessórios são as categorias mais relevantes, recomendando otimização em campanhas e estoque.

4. Evolução do Faturamento Diário e Dias de Pico
O comportamento das vendas mostra crescimento gradual entre janeiro e junho de 2025, com picos em 10/01, 10/03 e 25/06. 
Esses períodos podem estar relacionados a promoções sazonais e datas estratégicas.

Conclusão parcial: Planejar campanhas promocionais em meses de pico e reforçar ações nos períodos de baixa pode equilibrar o fluxo de vendas.

5. Top 10 Produtos Mais Lucrativos e Mais Vendidos
Mais Lucrativos: Notebook Dell, Monitor LG 24", Smartphone Samsung, Tablet Lenovo.
Mais Vendidos: Cabo HDMI 2m, Mouse Logitech, Headset Gamer, Caixa de Som JBL.

Conclusão parcial: Produtos mais vendidos não são necessariamente os mais lucrativos — há equilíbrio entre giro e margem de lucro. 
Manter um mix equilibrado é essencial para sustentabilidade financeira.

6. Impacto dos Descontos
Descontos variaram de 10% a 200 reais, aplicados em produtos de maior valor agregado.
Promoções moderadas influenciaram positivamente as vendas, principalmente em Headset Gamer e Smartphone Samsung.

Conclusão parcial: A política de descontos deve ser estratégica e seletiva, priorizando produtos com boa margem.

7. Conclusões Gerais e Recomendações
1. Categorias-Chave: Informática e Acessórios concentram o maior potencial de crescimento.
2. Gestão de Estoque: Manter alto giro e disponibilidade de produtos premium.
3. Sazonalidade: Reforçar campanhas em janeiro, março e junho.
4. Descontos: Aplicar com estratégia para preservar margens.
5. Qualidade dos Dados: Imputação pela mediana manteve consistência e confiabilidade.

8. Considerações Finais
O painel Streamlit demonstra a eficácia da integração entre Supabase e Python para análises de vendas em tempo real.
Com filtragem dinâmica, visualizações interativas e tratamento inteligente de dados nulos, o sistema gera insights acionáveis para decisões estratégicas.

