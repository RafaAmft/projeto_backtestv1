#!/usr/bin/env python3
"""
Script de Setup - Sistema de Análise Financeira
===============================================

Este script configura o ambiente de desenvolvimento e valida a instalação
do sistema de análise financeira.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

def print_header(title):
    """Imprime cabeçalho formatado"""
    print("\n" + "="*60)
    print(f"🚀 {title}")
    print("="*60)

def print_step(step, description):
    """Imprime passo do setup"""
    print(f"\n📋 {step}. {description}")

def run_command(command, description, check=True):
    """Executa comando e retorna sucesso"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            print(f"✅ {description} - Sucesso")
            return True
        else:
            print(f"❌ {description} - Falha")
            if result.stderr:
                print(f"   Erro: {result.stderr[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ {description} - Erro: {e}")
        return False

def check_python_version():
    """Verifica versão do Python"""
    print_step(1, "Verificando versão do Python")
    
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Versão mínima: 3.8")
        return False

def create_directories():
    """Cria diretórios necessários"""
    print_step(2, "Criando estrutura de diretórios")
    
    directories = [
        "logs",
        "reports",
        "data/cache",
        "data/historical",
        "tests/data",
        "config"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Diretório criado: {directory}")
    
    return True

def install_dependencies():
    """Instala dependências do projeto"""
    print_step(3, "Instalando dependências")
    
    # Verificar se requirements.txt existe
    if not Path("requirements.txt").exists():
        print("❌ Arquivo requirements.txt não encontrado")
        return False
    
    # Instalar dependências
    success = run_command(
        "pip install -r requirements.txt",
        "Instalando dependências do requirements.txt"
    )
    
    return success

def validate_imports():
    """Valida imports principais"""
    print_step(4, "Validando imports principais")
    
    modules_to_test = [
        ("pandas", "pd"),
        ("numpy", "np"),
        ("yfinance", "yf"),
        ("requests", "requests"),
        ("matplotlib", "plt"),
        ("streamlit", "st")
    ]
    
    failed_imports = []
    
    for module_name, alias in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {module_name}")
        except ImportError as e:
            print(f"❌ {module_name}: {e}")
            failed_imports.append(module_name)
    
    if failed_imports:
        print(f"\n⚠️ Módulos com falha: {', '.join(failed_imports)}")
        return False
    
    return True

def test_core_functionality():
    """Testa funcionalidade básica do core"""
    print_step(5, "Testando funcionalidade do core")
    
    try:
        # Testar import do core
        sys.path.append(os.getcwd())
        from core.market_indices import market_indices
        
        # Teste básico de câmbio
        rates = market_indices.get_exchange_rate()
        if rates and 'USD_BRL' in rates:
            print(f"✅ Core funcionando - Dólar: R$ {rates['USD_BRL']:.4f}")
            return True
        else:
            print("❌ Core não retornou dados válidos")
            return False
            
    except Exception as e:
        print(f"❌ Erro no core: {e}")
        return False

def create_config_files():
    """Cria arquivos de configuração"""
    print_step(6, "Criando arquivos de configuração")
    
    # Verificar se config.yaml já existe
    if Path("config/config.yaml").exists():
        print("✅ config.yaml já existe")
    else:
        print("⚠️ config.yaml não encontrado - será criado pelo usuário")
    
    # Criar .env template com configurações de segurança
    env_template = """# 🔒 CONFIGURAÇÕES DE AMBIENTE - SISTEMA DE ANÁLISE FINANCEIRA
# ⚠️ IMPORTANTE: Copie este arquivo para .env e configure suas chaves
# ⚠️ NUNCA commite o arquivo .env no repositório

# ============================================================================
# 🔑 CHAVES DE API (OPCIONAIS)
# ============================================================================

# Binance API (para dados privados e trading)
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_API_SECRET=your_binance_api_secret_here

# Yahoo Finance API (se necessário)
YAHOO_API_KEY=your_yahoo_api_key_here

# Exchange Rate API (se necessário)
EXCHANGE_RATE_API_KEY=your_exchange_rate_api_key_here

# ============================================================================
# 📧 CONFIGURAÇÕES DE EMAIL (OPCIONAIS)
# ============================================================================

# Servidor SMTP
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password_here

# Destinatários para notificações
EMAIL_RECIPIENTS=user1@example.com,user2@example.com

# ============================================================================
# 🔧 CONFIGURAÇÕES DO SISTEMA
# ============================================================================

# Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Arquivo de log
LOG_FILE=logs/app.log

# Configurações de cache
CACHE_DURATION=300
CACHE_STORAGE=memory

# ============================================================================
# 🌐 CONFIGURAÇÕES DE REDE
# ============================================================================

# Timeout para requisições HTTP (segundos)
REQUEST_TIMEOUT=30

# Número máximo de tentativas de reconexão
MAX_RETRY_ATTEMPTS=3

# Delay entre tentativas (segundos)
RETRY_DELAY=1

# ============================================================================
# 🔒 CONFIGURAÇÕES DE SEGURANÇA
# ============================================================================

# Habilitar validação de entrada
VALIDATE_INPUT=true

# Habilitar sanitização de dados
SANITIZE_DATA=true

# Log de operações sensíveis (false em produção)
LOG_SENSITIVE_OPERATIONS=false

# Verificação SSL
SSL_VERIFY=true

# Rate limiting (requisições por minuto)
RATE_LIMIT=1200

# ============================================================================
# 📊 CONFIGURAÇÕES DE ANÁLISE
# ============================================================================

# Taxa livre de risco (CDI anual)
RISK_FREE_RATE=0.12

# Nível de confiança para VaR
CONFIDENCE_LEVEL=0.95

# Janela de volatilidade (dias)
VOLATILITY_WINDOW=30

# ============================================================================
# 🎯 CONFIGURAÇÕES DE PORTFÓLIO
# ============================================================================

# Moedas padrão
DEFAULT_CURRENCIES=USD,BRL

# Calcular métricas de risco
CALCULATE_SHARPE=true
CALCULATE_VAR=true
CALCULATE_MAX_DRAWDOWN=true
CALCULATE_BETA=true

# ============================================================================
# 📈 CONFIGURAÇÕES DE RELATÓRIOS
# ============================================================================

# Diretório de saída
REPORTS_OUTPUT_DIR=reports/

# Formatos de saída
REPORTS_FORMATS=json,csv,xlsx

# Salvar automaticamente
AUTO_SAVE_REPORTS=true

# Incluir gráficos
INCLUDE_CHARTS=true

# Incluir métricas
INCLUDE_METRICS=true

# ============================================================================
# 🖥️ CONFIGURAÇÕES DO DASHBOARD
# ============================================================================

# Porta do Streamlit
STREAMLIT_PORT=8501

# Host do Streamlit
STREAMLIT_HOST=localhost

# Tema do Streamlit
STREAMLIT_THEME=light

# ============================================================================
# 🧪 CONFIGURAÇÕES DE TESTES
# ============================================================================

# Usar APIs mock para testes
MOCK_APIS=false

# Diretório de dados de teste
TEST_DATA_DIR=tests/data/

# Threshold de cobertura de testes
COVERAGE_THRESHOLD=80

# Timeout para testes
TEST_TIMEOUT=30

# ============================================================================
# 📊 CONFIGURAÇÕES DE MONITORAMENTO
# ============================================================================

# Habilitar monitoramento
MONITORING_ENABLED=true

# Intervalo de métricas (segundos)
METRICS_INTERVAL=60

# Thresholds de alerta
ERROR_RATE_THRESHOLD=0.05
RESPONSE_TIME_THRESHOLD=5.0
CACHE_HIT_RATE_THRESHOLD=0.8

# ============================================================================
# 💾 CONFIGURAÇÕES DE BACKUP
# ============================================================================

# Habilitar backup
BACKUP_ENABLED=true

# Frequência de backup
BACKUP_FREQUENCY=daily

# Retenção de backups (dias)
BACKUP_RETENTION_DAYS=30

# Incluir relatórios no backup
BACKUP_INCLUDE_REPORTS=true

# Incluir logs no backup
BACKUP_INCLUDE_LOGS=true

# ============================================================================
# 🔔 CONFIGURAÇÕES DE NOTIFICAÇÕES
# ============================================================================

# Habilitar notificações por email
EMAIL_NOTIFICATIONS_ENABLED=false

# Habilitar webhooks
WEBHOOK_ENABLED=false

# URL do webhook
WEBHOOK_URL=

# Eventos para notificação
WEBHOOK_EVENTS=error,warning,success

# ============================================================================
# 🌍 CONFIGURAÇÕES DE AMBIENTE
# ============================================================================

# Ambiente (development, staging, production)
ENVIRONMENT=development

# Debug mode
DEBUG=true

# Timezone
TIMEZONE=America/Sao_Paulo

# ============================================================================
# 📝 INSTRUÇÕES DE USO
# ============================================================================

# 1. Copie este arquivo para .env
# 2. Configure as variáveis necessárias
# 3. Mantenha as chaves de API seguras
# 4. Nunca commite o arquivo .env
# 5. Use diferentes configurações para cada ambiente
"""
    
    with open(".env.template", "w", encoding="utf-8") as f:
        f.write(env_template)
    
    print("✅ .env.template criado com configurações de segurança")
    return True

def run_quick_tests():
    """Executa testes rápidos"""
    print_step(7, "Executando testes rápidos")
    
    # Teste do script de testes
    if Path("scripts/run_tests.py").exists():
        success = run_command(
            "python scripts/run_tests.py",
            "Executando testes automatizados",
            check=False  # Não falhar se testes falharem
        )
        return success
    else:
        print("⚠️ Script de testes não encontrado")
        return True

def generate_setup_report(results):
    """Gera relatório do setup"""
    print_header("RELATÓRIO DO SETUP")
    
    total_steps = len(results)
    successful_steps = sum(1 for success in results.values() if success)
    success_rate = (successful_steps / total_steps) * 100
    
    print(f"\n📊 RESUMO:")
    print(f"  Passos: {successful_steps}/{total_steps}")
    print(f"  Taxa de Sucesso: {success_rate:.1f}%")
    
    print(f"\n📋 DETALHES:")
    for step, success in results.items():
        status = "✅" if success else "❌"
        print(f"  {status} {step}")
    
    # Salvar relatório
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_steps': total_steps,
        'successful_steps': successful_steps,
        'success_rate': success_rate,
        'results': results
    }
    
    report_file = f"setup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Relatório salvo em: {report_file}")
    
    return success_rate >= 80

def print_next_steps():
    """Imprime próximos passos"""
    print_header("PRÓXIMOS PASSOS")
    
    print("""
🎯 Para começar a usar o sistema:

1. 📝 Configure suas APIs (opcional):
   - Copie .env.template para .env
   - Adicione suas chaves de API

2. 🚀 Execute o exemplo básico:
   python examples/portfolio_analysis_example.py

3. 📊 Teste o dashboard:
   streamlit run "CNPJ VALIDADO/app.py"

4. 🧪 Execute todos os testes:
   python scripts/run_tests.py

5. 📚 Leia a documentação:
   - README.md
   - docs/MarketIndicesManager_README.md
   - ROADMAP.md

🔗 Links úteis:
   - GitHub: https://github.com/seu-usuario/projeto-final
   - Documentação: docs/
   - Exemplos: examples/
""")

def main():
    """Função principal"""
    print_header("SETUP DO SISTEMA DE ANÁLISE FINANCEIRA")
    print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"Diretório: {os.getcwd()}")
    
    # Executar todos os passos
    results = {
        'Python Version': check_python_version(),
        'Directories': create_directories(),
        'Dependencies': install_dependencies(),
        'Imports': validate_imports(),
        'Core Functionality': test_core_functionality(),
        'Config Files': create_config_files(),
        'Quick Tests': run_quick_tests()
    }
    
    # Gerar relatório
    success = generate_setup_report(results)
    
    if success:
        print("\n🎉 SETUP CONCLUÍDO COM SUCESSO!")
        print_next_steps()
        sys.exit(0)
    else:
        print("\n⚠️ SETUP CONCLUÍDO COM PROBLEMAS!")
        print("Verifique os erros acima e tente novamente.")
        sys.exit(1)

if __name__ == "__main__":
    main() 