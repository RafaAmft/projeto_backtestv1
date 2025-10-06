# Changelog - Sistema de Análise de Portfólios

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

---

## [1.1.0] - 2025-10-06

### ✨ Adicionado

#### Qualidade de Código
- Sistema de versionamento semântico implementado
- Arquivo `.env.example` com template de variáveis de ambiente
- Configuração `pytest.ini` para padronização de testes
- Pre-commit hooks (`.pre-commit-config.yaml`) para validação automática
- `pyproject.toml` com metadados e configurações do projeto
- CHANGELOG.md para rastreamento de mudanças

#### Documentação
- Guia completo de boas práticas (`boaspraticas.md` v1.1.0)
- CHANGELOG dedicado para boas práticas
- Documentação expandida no README

#### Infraestrutura
- Template de variáveis de ambiente para segurança
- Configurações centralizadas para ferramentas de desenvolvimento
- Sistema de versionamento no código (`__version__.py`)

### 🔧 Melhorado
- `requirements.txt` com ranges de versão apropriados
- Estrutura de testes mais robusta
- Documentação do README atualizada
- Segurança: variáveis sensíveis movidas para .env

### 📝 Documentação
- README.md atualizado para v1.1.0
- Adicionados badges de status
- Melhorias na seção de instalação
- Guia de contribuição expandido

### 🔒 Segurança
- Template `.env.example` para proteger credenciais
- Validação de configurações obrigatórias
- Hooks de segurança (bandit, safety) configurados

---

## [1.0.0] - 2025-07-08

### 🎉 Lançamento Inicial

#### Core System
- `MarketIndicesManager` - Classe central (1.123 linhas)
- Sistema de cache inteligente (5 minutos)
- Tratamento de erros com fallbacks automáticos
- Logging detalhado
- Conversão automática USD ↔ BRL

#### APIs Integradas
- **Binance API** - 8 criptomoedas em tempo real
- **Yahoo Finance** - 15+ símbolos (ações, índices, commodities)
- **Fundos CVM** - Dados processados localmente + scraping
- **Exchange Rate API** - Cotações com fallback
- **IBGE API** - Dados econômicos brasileiros

#### Análise Avançada
- Análise de portfólios (crypto, ações, fundos, renda fixa)
- Métricas de risco (Sharpe, Sortino, VaR, Max Drawdown, CAGR)
- Comparação com benchmarks
- Análise de correlações
- Evolução temporal (1, 3, 5 anos)
- Carteira ideal otimizada (13 ativos)

#### Funcionalidades
- Dashboard Streamlit interativo
- Auditoria automática de fundos
- Relatórios automatizados (JSON e TXT)
- 15+ testes automatizados
- Sistema de cache para performance

#### Estrutura do Projeto
```
ProjetoFinal/
├── core/           # Núcleo do sistema
├── apis/           # Integrações
├── dashboard/      # Interface web
├── examples/       # Exemplos de uso
├── config/         # Configurações
├── docs/           # Documentação
├── scripts/        # Scripts auxiliares
├── tests/          # Testes (implementação inicial)
└── relatorios/     # Relatórios gerados
```

#### Carteira Ideal
- **Renda Fixa (40%)**: CDB, LCI
- **Ações (30%)**: PETR4, VALE3, BBAS3
- **Criptomoedas (15%)**: BTC, ETH, USDT, BNB
- **Fundos Cambiais (15%)**: 5 fundos especializados

**Métricas:**
- Sharpe Ratio: 0.53
- CAGR: 6.71%
- Volatilidade: 11.80%
- Valor Total: R$ 300.000,00

#### Testes
- 15+ testes automatizados
- Cobertura básica das funcionalidades principais

---

## [Unreleased]

### 🚀 Planejado para v1.2.0

#### Melhorias de Código
- [ ] Type hints completos em todo o código
- [ ] Cobertura de testes >= 80%
- [ ] Refatoração do MarketIndicesManager em módulos menores
- [ ] Logging estruturado (JSON)
- [ ] Documentação com Sphinx ou MkDocs

#### Novas Funcionalidades
- [ ] Análise técnica (RSI, MACD, Bollinger Bands)
- [ ] Suporte para Tesouro Direto
- [ ] Relatórios em PDF
- [ ] API REST para acesso programático
- [ ] Alertas por email/telegram

#### Infraestrutura
- [ ] Docker e docker-compose
- [ ] CI/CD com GitHub Actions
- [ ] Monitoramento com Prometheus
- [ ] Deploy automático

### 🤖 Planejado para v2.0.0

#### Machine Learning
- [ ] Previsão de preços com ML
- [ ] Otimização automática de carteiras
- [ ] Detecção de anomalias
- [ ] Análise de sentimento

#### Plataforma Web
- [ ] Web App completo (React/Vue)
- [ ] Autenticação de usuários
- [ ] Múltiplas carteiras por usuário
- [ ] Histórico de operações
- [ ] Simulador de investimentos

---

## Comparação de Versões

| Funcionalidade | v1.0.0 | v1.1.0 |
|----------------|--------|--------|
| APIs Integradas | 6 | 6 |
| Versionamento | ❌ | ✅ |
| Pre-commit Hooks | ❌ | ✅ |
| Pytest Configurado | Básico | ✅ Completo |
| .env Template | ❌ | ✅ |
| CHANGELOG | ❌ | ✅ |
| Boas Práticas Doc | ❌ | ✅ |
| Type Hints | Parcial | Parcial* |
| Cobertura Testes | ~30% | ~30%* |
| Docker | ❌ | ❌ |

*\* Marcado para v1.2.0*

---

## Tipos de Mudanças

- `✨ Adicionado` - Novas funcionalidades
- `🔧 Melhorado` - Melhorias em funcionalidades existentes
- `🐛 Corrigido` - Correções de bugs
- `🔒 Segurança` - Correções de vulnerabilidades
- `📝 Documentação` - Mudanças apenas na documentação
- `🗑️ Removido` - Funcionalidades removidas
- `⚠️ Deprecated` - Funcionalidades que serão removidas

---

## Como Atualizar

### De v1.0.0 para v1.1.0

1. **Backup dos dados:**
   ```bash
   cp -r data/ data_backup/
   cp -r relatorios/ relatorios_backup/
   ```

2. **Atualizar código:**
   ```bash
   git pull origin main
   git checkout v1.1.0
   ```

3. **Instalar novas dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variáveis de ambiente:**
   ```bash
   cp .env.example .env
   # Editar .env com suas credenciais
   ```

5. **Instalar pre-commit hooks (opcional):**
   ```bash
   pip install pre-commit
   pre-commit install
   ```

6. **Executar testes:**
   ```bash
   pytest
   ```

---

## Links Úteis

- [README](README.md) - Documentação principal
- [CONTRIBUTING](CONTRIBUTING.md) - Guia de contribuição
- [ROADMAP](ROADMAP.md) - Planejamento futuro
- [Boas Práticas](boaspraticas.md) - Guia de desenvolvimento

---

**Mantenedor:** Rafael Augusto Masson Fontes  
**GitHub:** [@RafaAmft](https://github.com/RafaAmft/projeto_backtestv1)

