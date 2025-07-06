# 📊 Painel Coletor de Portfólio Financeiro

## 🎯 Objetivo

Este painel Streamlit permite coletar dados de diferentes tipos de ativos e gerar relatórios completos em formato TXT para auditoria.

## 🚀 Como Usar

### 1. Instalação

```bash
# Instalar dependências
pip install -r requirements.txt

# Ou instalar manualmente
pip install streamlit selenium beautifulsoup4 pandas numpy requests
```

### 2. Execução

```bash
# Opção 1: Usar o script de execução
python run_dashboard.py

# Opção 2: Executar diretamente
streamlit run dashboard/portfolio_collector.py
```

### 3. Acesso

Abra o navegador e acesse: `http://localhost:8501`

## 📋 Funcionalidades

### 🏦 Fundos de Investimento (5 fundos)
- **Busca automática por CNPJ**: O sistema busca automaticamente o slug no Mais Retorno
- **Extração de dados**: Rentabilidades históricas e informações do fundo
- **Validação**: Verifica se o fundo existe e tem dados disponíveis

### 📈 Ações (5 ações)
- **Código da ação**: Ex: PETR4, VALE3, etc.
- **Quantidade**: Número de ações
- **Preço de entrada**: Preço médio de compra

### 🪙 Criptomoedas (5 criptos)
- **Seleção**: Lista das principais criptomoedas
- **Quantidade**: Quantidade em cripto
- **Preço de entrada**: Preço em dólares

### 💰 Renda Fixa (2 ativos)
- **Tipos**: CDB, LCI, LCA, Tesouro Direto, Debêntures
- **Valor investido**: Valor em reais
- **Taxa anual**: Taxa de juros anual

## 📄 Relatório Gerado

O sistema gera um relatório completo em formato TXT com:

1. **Resumo Executivo**: Visão geral do portfólio
2. **Análise por Classe**: Detalhamento de cada tipo de ativo
3. **Métricas de Performance**: Retornos e riscos
4. **Recomendações**: Insights e sugestões
5. **Próximos Passos**: Orientações para gestão

## ⚙️ Configurações

### Período de Análise
- 1 Ano
- 3 Anos  
- 5 Anos

### Data de Referência
- Data personalizada para cálculos

## 📁 Estrutura de Arquivos

```
dashboard/
├── portfolio_collector.py    # Painel principal
├── requirements.txt          # Dependências
├── README.md                # Documentação
└── run_dashboard.py         # Script de execução
```

## ⚠️ Requisitos do Sistema

- **Python 3.8+**
- **Chrome/Chromium**: Para web scraping dos fundos
- **Conexão com internet**: Para buscar dados em tempo real

## 🐛 Solução de Problemas

### Erro de WebDriver
```bash
# Instalar webdriver-manager
pip install webdriver-manager

# Ou baixar ChromeDriver manualmente
```

### Erro de Importação
```bash
# Verificar se todos os módulos estão instalados
pip install -r requirements.txt
```

### Fundo não encontrado
- Verificar se o CNPJ está correto
- Alguns fundos podem não estar no Mais Retorno
- Tentar buscar manualmente no site

## 📞 Suporte

Para dúvidas ou problemas, consulte a documentação do projeto principal ou abra uma issue no repositório. 