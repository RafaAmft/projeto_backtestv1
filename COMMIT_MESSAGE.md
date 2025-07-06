feat: Implementar melhorias no painel Streamlit e sistema de cache

## 🚀 Principais Melhorias Implementadas:

### 📊 Painel Streamlit Melhorado:
- **portfolio_collector_fixed.py**: Versão com campo de renda fixa corrigido (% do CDI)
- **portfolio_collector_auto.py**: Versão com busca automática de preços para ações e criptos
- **portfolio_collector.py**: Versão original mantida para compatibilidade

### 💰 Correção do Campo Renda Fixa:
- Alterado de "Taxa Anual (%)" para "% do CDI"
- Adicionado box explicativo sobre como funciona a % do CDI
- Cálculo automático da taxa efetiva baseada no CDI atual (10.5%)
- Valor padrão mais realista (95% do CDI)
- Limite máximo de 200% para casos especiais

### 🔍 Busca Automática de Preços:
- **Para Ações**: Botão "🔍 Buscar Preço" que preenche automaticamente o preço de fechamento
- **Para Criptos**: Botão "🔍 Buscar Preço" que preenche o preço de abertura em USD
- Integração com Yahoo Finance para dados em tempo real
- Conversão automática USD/BRL para criptomoedas
- Indicadores visuais de variação (📈 alta, 📉 baixa)
- Informações detalhadas: abertura, fechamento, variação do dia

### 💾 Sistema de Cache Melhorado:
- **fund_cache_manager.py**: Gerenciador de cache para dados de fundos
- Validade de 30 dias para dados em cache
- Normalização automática de CNPJ
- Estatísticas de cache na sidebar
- Botões para limpar cache expirado ou todo o cache
- Persistência de dados entre sessões do Streamlit

### 🛠️ Scripts Utilitários:
- **get_market_prices.py**: Script para buscar preços de mercado em tempo real
- **test_cache_system.py**: Testes para o sistema de cache
- **test_real_portfolio.py**: Teste com portfólio real
- **run_dashboard.py**: Script para executar o painel

### 📈 Funcionalidades Adicionais:
- Busca automática de slug para fundos via DuckDuckGo
- Extração de dados de fundos via Selenium
- Geração de relatórios em TXT com timestamp
- Download automático de relatórios
- Interface responsiva com CSS personalizado
- Sidebar com estatísticas e controles

### 🔧 Melhorias Técnicas:
- Tratamento de erros robusto
- Timeouts configuráveis para APIs
- Fallbacks para cotação USD/BRL
- Validação de dados de entrada
- Logs detalhados para debugging

## 🎯 Benefícios:
- ✅ Facilita a entrada de dados do usuário
- ✅ Reduz erros de digitação
- ✅ Preços sempre atualizados
- ✅ Interface mais intuitiva
- ✅ Performance melhorada com cache
- ✅ Relatórios mais completos

## 📝 Arquivos Modificados/Criados:
- dashboard/portfolio_collector_fixed.py (novo)
- dashboard/portfolio_collector_auto.py (novo)
- dashboard/fund_cache_manager.py (novo)
- get_market_prices.py (novo)
- test_cache_system.py (novo)
- test_real_portfolio.py (novo)
- run_dashboard.py (novo)
- requirements.txt (atualizado)

## 🚀 Como Usar:
1. Painel básico: `streamlit run dashboard/portfolio_collector.py`
2. Painel com renda fixa corrigida: `streamlit run dashboard/portfolio_collector_fixed.py`
3. Painel com busca automática: `streamlit run dashboard/portfolio_collector_auto.py`
4. Buscar preços: `python get_market_prices.py` 