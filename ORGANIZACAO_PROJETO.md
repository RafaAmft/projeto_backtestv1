# Organização do Projeto Final

## Estrutura de Pastas

### 📁 Pastas Principais
- **`core/`** - Módulos principais do sistema (market indices, etc.)
- **`dashboard/`** - Interface Streamlit e coletor de dados
- **`examples/`** - Exemplos de uso e análise de portfólio
- **`scripts/`** - Scripts utilitários
- **`config/`** - Arquivos de configuração
- **`docs/`** - Documentação do projeto
- **`data/`** - Dados históricos e cache
- **`apis/`** - Integrações com APIs externas

### 📁 Pastas de Organização
- **`relatorios_antigos/`** - Relatórios gerados anteriormente
- **`testes_antigos/`** - Scripts de teste antigos
- **`dados_debug/`** - Arquivos de debug e dados temporários
- **`cache_temp/`** - Cache temporário

### 📁 Integrações Externas
- **`BInance/`** - Integração com Binance
- **`YahooFInance/`** - Integração com Yahoo Finance
- **`CNPJ VALIDADO/`** - Validação de CNPJs

## Arquivos Principais

### 🎯 Arquivos de Configuração
- `carteira_ideal.json` - Configuração da carteira modelo
- `mapeamento_fundos.json` - Mapeamento de fundos
- `config/config.yaml` - Configurações gerais

### 📊 Arquivos de Resultados
- `resultados_*.json` - Resultados de buscas e análises
- `grafico_evolucao_carteira.png` - Gráfico da evolução da carteira

### 📋 Documentação
- `README.md` - Documentação principal
- `RESUMO_EXECUTIVO.md` - Resumo do projeto
- `ROADMAP.md` - Roadmap de desenvolvimento
- `CHECKPOINT_PROJETO.md` - Checkpoints do projeto
- `COMMIT_MESSAGE.md` - Mensagens de commit

### 🚀 Scripts Principais
- `run_dashboard.py` - Executar dashboard Streamlit
- `get_market_prices.py` - Obter preços de mercado
- `cvm_data_processor.py` - Processador de dados CVM

## Arquivos Ignorados pelo Git

O `.gitignore` foi configurado para ignorar:
- Arquivos de cache Python (`__pycache__/`, `.pytest_cache/`)
- Pastas temporárias (`cache_temp/`, `dados_debug/`, etc.)
- Relatórios antigos (`relatorios_antigos/`, `testes_antigos/`)
- Arquivos de debug (`debug_*.html`, `*.log`)
- Dados temporários (`dados_*.json`, `relatorio_*.json`, etc.)
- Gráficos gerados (`*.png`, `*.jpg`)
- Arquivos de IDE (`.vscode/`, `.idea/`)

## Como Usar

1. **Executar Dashboard**: `python run_dashboard.py`
2. **Testar Carteira Ideal**: `python test_carteira_ideal.py`
3. **Obter Preços**: `python get_market_prices.py`

## Limpeza Automática

Para manter o projeto organizado:
- Relatórios antigos são movidos para `relatorios_antigos/`
- Dados de debug são movidos para `dados_debug/`
- Testes antigos são movidos para `testes_antigos/`

## Próximos Passos

1. Commit das mudanças organizacionais
2. Teste da nova estrutura
3. Documentação adicional se necessário 