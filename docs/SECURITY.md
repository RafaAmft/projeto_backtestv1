# 🔒 Guia de Segurança - Sistema de Análise Financeira

**Versão:** 1.0 | **Data:** 08/07/2025 | **Status:** Ativo

Este documento descreve as medidas de segurança implementadas no sistema e como mantê-las atualizadas.

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Medidas Implementadas](#medidas-implementadas)
3. [Configuração de Segurança](#configuração-de-segurança)
4. [Auditoria de Segurança](#auditoria-de-segurança)
5. [Boas Práticas](#boas-práticas)
6. [Checklist de Segurança](#checklist-de-segurança)
7. [Troubleshooting](#troubleshooting)

## 🎯 Visão Geral

O sistema implementa múltiplas camadas de segurança para proteger dados sensíveis e prevenir vulnerabilidades comuns.

### 🔐 Princípios de Segurança

- **Defesa em Profundidade**: Múltiplas camadas de proteção
- **Princípio do Menor Privilégio**: Acesso mínimo necessário
- **Segurança por Padrão**: Configurações seguras por padrão
- **Transparência**: Logs detalhados de eventos de segurança

## 🛡️ Medidas Implementadas

### 1. Gerenciamento de Segredos

#### ✅ Arquivo .env
- Chaves de API armazenadas em variáveis de ambiente
- Template `.env.template` fornecido
- Arquivo `.env` no `.gitignore`

#### ✅ Configuração Segura
- `config.yaml` sem chaves hardcoded
- Comentários explicativos sobre segurança
- Configurações de segurança avançadas

### 2. Validação e Sanitização

#### ✅ Gerenciador de Segurança
- Validação de entrada de dados
- Sanitização automática
- Prevenção de injeções
- Logs de eventos de segurança

#### ✅ Validações Implementadas
- Chaves de API
- Símbolos de ativos
- URLs
- Valores numéricos
- Dados genéricos

### 3. Proteção de Dados

#### ✅ Criptografia
- Dependências atualizadas com criptografia
- Suporte a SSL/TLS
- Hash seguro de senhas

#### ✅ Auditoria
- Verificação de arquivos por padrões suspeitos
- Análise de histórico Git
- Relatórios de segurança

## ⚙️ Configuração de Segurança

### Ativando o Gerenciador de Segurança

```python
from core.security_manager import enable_security, get_security_manager

# Ativar segurança
enable_security()

# Usar o gerenciador
security_manager = get_security_manager()

# Validar entrada
result = security_manager.validate_input("BTCUSDT", "symbol")
```

### Configuração via Variáveis de Ambiente

```bash
# Copiar template
cp .env.template .env

# Configurar chaves (opcional)
BINANCE_API_KEY=your_key_here
BINANCE_API_SECRET=your_secret_here

# Configurações de segurança
VALIDATE_INPUT=true
SANITIZE_DATA=true
LOG_SENSITIVE_OPERATIONS=false
SSL_VERIFY=true
RATE_LIMIT=1200
```

### Configuração no config.yaml

```yaml
security:
  validate_input: true
  sanitize_data: true
  log_sensitive_operations: false
  api_key_rotation: false
  encryption_enabled: false
  ssl_verify: true
  rate_limiting: true
  input_validation: true
  sql_injection_protection: true
  xss_protection: true
```

## 🔍 Auditoria de Segurança

### Script de Auditoria

```bash
# Execução completa
python scripts/security_audit.py

# Execução rápida
python scripts/security_audit.py --quick

# Gerar relatório
python scripts/security_audit.py --report
```

### Verificações Automáticas

1. **Dependências de Segurança**
   - Verifica se todas as dependências estão instaladas
   - Identifica versões vulneráveis

2. **Arquivo .env**
   - Verifica se existe e está configurado
   - Confirma que está no .gitignore

3. **Configuração**
   - Verifica por chaves hardcoded
   - Valida configurações de segurança

4. **Histórico Git**
   - Procura por informações sensíveis nos commits
   - Identifica possíveis vazamentos

5. **Auditoria de Código**
   - Verifica padrões suspeitos
   - Analisa vulnerabilidades conhecidas

### Relatório de Segurança

O script gera um relatório JSON com:

```json
{
  "timestamp": "2025-07-08T20:30:00",
  "security_score": 85.0,
  "total_checks": 5,
  "passed_checks": 4,
  "checks": {
    "dependencies": true,
    "env_file": true,
    "config_security": true,
    "git_history": true,
    "security_audit": false
  }
}
```

## 📚 Boas Práticas

### 🔑 Gerenciamento de Chaves

1. **Nunca commite chaves de API**
   ```bash
   # ❌ ERRADO
   api_key = "sk-1234567890abcdef"
   
   # ✅ CORRETO
   api_key = os.getenv("BINANCE_API_KEY")
   ```

2. **Use variáveis de ambiente**
   ```bash
   # .env
   BINANCE_API_KEY=your_actual_key_here
   ```

3. **Rotacione chaves regularmente**
   - Troque chaves a cada 90 dias
   - Monitore uso anormal

### 🔒 Validação de Dados

1. **Sempre valide entrada**
   ```python
   # Validar símbolo
   result = security_manager.validate_input(symbol, "symbol")
   if not result["valid"]:
       raise ValueError("Símbolo inválido")
   ```

2. **Sanitize dados externos**
   ```python
   # Sanitizar dados
   clean_data = security_manager.sanitize_data(raw_data)
   ```

3. **Use HTTPS sempre**
   ```python
   # Configurar SSL
   requests.get(url, verify=True)
   ```

### 📝 Logging Seguro

1. **Não logue dados sensíveis**
   ```python
   # ❌ ERRADO
   logger.info(f"API Key: {api_key}")
   
   # ✅ CORRETO
   logger.info("API Key configurada")
   ```

2. **Use níveis apropriados**
   ```python
   logger.debug("Detalhes internos")
   logger.info("Informações gerais")
   logger.warning("Avisos de segurança")
   logger.error("Erros críticos")
   ```

## ✅ Checklist de Segurança

### Antes de Cada Commit

- [ ] Verificar se não há chaves hardcoded
- [ ] Confirmar que .env está no .gitignore
- [ ] Executar auditoria de segurança
- [ ] Verificar dependências atualizadas
- [ ] Testar validações de entrada

### Semanalmente

- [ ] Executar `python scripts/security_audit.py --report`
- [ ] Verificar logs de segurança
- [ ] Atualizar dependências se necessário
- [ ] Revisar configurações de segurança

### Mensalmente

- [ ] Rotacionar chaves de API
- [ ] Revisar permissões de arquivos
- [ ] Atualizar documentação de segurança
- [ ] Treinar equipe em boas práticas

## 🔧 Troubleshooting

### Problemas Comuns

#### 1. "Chave de API não encontrada"

```bash
# Verificar se .env existe
ls -la .env

# Verificar variável de ambiente
echo $BINANCE_API_KEY

# Recarregar variáveis
source .env
```

#### 2. "Erro de validação"

```python
# Verificar se segurança está ativada
from core.security_manager import get_security_manager
security_manager = get_security_manager()
print(f"Segurança ativada: {security_manager.enabled}")

# Verificar validação específica
result = security_manager.validate_input(data, "symbol")
print(result)
```

#### 3. "Dependência vulnerável"

```bash
# Verificar dependências
pip list | grep cryptography

# Atualizar dependência
pip install --upgrade cryptography

# Verificar vulnerabilidades
safety check
```

### Logs de Segurança

Os logs de segurança são salvos em:

```python
# Verificar logs
tail -f logs/app.log | grep "SECURITY"

# Exportar log de segurança
security_manager.export_security_log("security_log.json")
```

### Contatos de Emergência

Em caso de incidente de segurança:

1. **Imediatamente**: Desative chaves comprometidas
2. **Dentro de 1 hora**: Notifique a equipe
3. **Dentro de 24 horas**: Documente o incidente
4. **Dentro de 1 semana**: Implemente correções

## 📞 Suporte

Para questões de segurança:

- **Email**: security@projeto.com
- **Issues**: GitHub Security Issues
- **Documentação**: Este arquivo

---

**Última Atualização:** 08/07/2025  
**Próxima Revisão:** 08/08/2025  
**Responsável:** Equipe de Segurança 