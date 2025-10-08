# Changelog - Boas Práticas de Código

Todas as mudanças notáveis no guia de boas práticas serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

---

## [1.1.0] - 2025-10-06

### ✨ Adicionado

#### Git Workflow
- Exemplos práticos de Conventional Commits (feat, fix, docs, refactor, test, perf, chore, style)
- Visualização da estratégia de branches (GitFlow)
- Comandos para criar e gerenciar tags de versionamento

#### Estrutura de Projeto
- Estrutura de diretórios completa e corrigida
- Exemplo detalhado incluindo pastas de testes, dados, documentação e relatórios
- Princípios de organização de código

#### Python
- Seção expandida sobre convenções de nomenclatura (PascalCase, snake_case, UPPER_SNAKE_CASE)
- Exemplos completos de type hints com documentação
- Configuração de logging estruturado
- Exemplos de tratamento de erros com exceções customizadas
- Context managers e sua importância
- Boas práticas para configurações (variáveis de ambiente)
- Técnicas de performance e profiling
- Gerenciamento de dependências com ranges de versão

#### Testes
- Estrutura AAA (Arrange, Act, Assert) com exemplos
- Fixtures do pytest com casos de uso reais
- Mocking de APIs externas (monkeypatch e @patch)
- Testes parametrizados para múltiplos casos
- Testando exceções com pytest.raises
- Markers customizados para categorização de testes
- Configuração completa do pytest.ini
- Comandos para cobertura de código

#### Análise de Dados
- Boas práticas para manipulação de DataFrames
- Seção completa sobre séries temporais financeiras
- Cálculos financeiros essenciais (Sharpe Ratio, CAGR, Max Drawdown, Volatilidade)
- Validação de dados financeiros
- Sistema de cache para dados de mercado (decorator)
- Visualização de dados financeiros (preço/volume, distribuição de retornos)
- Reprodutibilidade com fixação de seeds
- Segurança de dados e conformidade com LGPD
- Performance para grandes datasets (Polars, Dask, chunking)

#### Deploy / CI-CD
- Definição clara de ambientes (Development, Staging, Production)
- Pipeline CI/CD completo com GitHub Actions
- Exemplos práticos de jobs: lint, test, security, deploy
- Configuração de pre-commit hooks
- Dockerfile completo para containerização
- docker-compose.yml com exemplo de multi-serviços
- Template de variáveis de ambiente (.env.example)
- Classe Settings para gerenciamento de configurações
- Logging estruturado em JSON
- Branch strategy (GitFlow) detalhada
- Checklist completo de deploy (pre, during, post)

#### Recursos Adicionais
- Lista de ferramentas recomendadas por categoria
- Links úteis para documentação oficial
- Seção de notas finais com informações de manutenção

### 🔧 Corrigido
- Formatação da estrutura de projeto (estava quebrada)
- Sintaxe de código nos exemplos
- Organização visual do documento

### 📝 Melhorado
- Clareza e detalhamento em todas as seções
- Exemplos práticos e aplicáveis ao projeto
- Navegação e estrutura do documento
- Consistência na formatação

---

## [1.0.0] - 2025-07-08

### ✨ Inicial
- Versão inicial do guia de boas práticas
- Seções básicas:
  - Git Workflow
  - Estrutura de Projeto
  - Python
  - Testes
  - Análise de Dados
  - Deploy / CI-CD

---

## Comparação de Versões

### Estatísticas
| Métrica | v1.0.0 | v1.1.0 | Diferença |
|---------|--------|--------|-----------|
| Linhas de código | ~101 | ~1348 | +1247 (+1234%) |
| Seções principais | 6 | 6 | 0 |
| Subseções | 0 | 45+ | +45 |
| Exemplos de código | ~5 | ~50+ | +45 |
| Ferramentas mencionadas | ~10 | ~30+ | +20 |

### O que mudou?
- **v1.0.0**: Guia básico com diretrizes gerais
- **v1.1.0**: Guia completo com exemplos práticos, configurações reais e aplicações específicas para análise financeira

---

## Próximas Versões (Planejado)

### [1.2.0] - Planejado para 2025-12
- Seção sobre documentação (Sphinx, MkDocs)
- Boas práticas para notebooks Jupyter
- Guidelines de code review
- Métricas de qualidade de código

### [1.3.0] - Planejado para 2026-03
- Padrões de design (Factory, Singleton, Observer)
- Arquitetura de microsserviços
- Event-driven architecture
- API design best practices

### [2.0.0] - Planejado para 2026-06
- Reestruturação completa com foco em escalabilidade
- Seção sobre MLOps e modelos de machine learning
- Kubernetes e orquestração de containers
- Observabilidade e telemetria

---

**Mantenedores:** Equipe de Desenvolvimento  
**Contato:** [Adicionar email/canal de comunicação]


