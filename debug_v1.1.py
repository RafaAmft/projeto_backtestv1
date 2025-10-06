#!/usr/bin/env python3
"""
Script de Debug e Validação - Sistema de Análise de Portfólios v1.1.0

Este script verifica se todas as funcionalidades da v1.1.0 estão funcionando.

Uso:
    python debug_v1.1.py
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Cores para output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_section(title):
    """Imprime título de seção"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{title.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")


def test_result(name, passed, details=""):
    """Imprime resultado do teste"""
    if passed:
        status = f"{Colors.OKGREEN}✓ PASS{Colors.ENDC}"
    else:
        status = f"{Colors.FAIL}✗ FAIL{Colors.ENDC}"
    
    print(f"{status} | {name}")
    if details:
        print(f"       └─ {Colors.OKCYAN}{details}{Colors.ENDC}")


def check_python_version():
    """Verifica versão do Python"""
    print_section("1. VERIFICANDO PYTHON")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    passed = version.major == 3 and version.minor >= 10
    test_result(
        "Versão do Python >= 3.10",
        passed,
        f"Detectado: Python {version_str}"
    )
    
    return passed


def check_version_system():
    """Verifica sistema de versionamento"""
    print_section("2. VERIFICANDO SISTEMA DE VERSIONAMENTO")
    
    results = []
    
    # Verificar se __version__.py existe
    version_file = Path("__version__.py")
    test_result(
        "Arquivo __version__.py existe",
        version_file.exists(),
        str(version_file.absolute()) if version_file.exists() else "Não encontrado"
    )
    results.append(version_file.exists())
    
    # Tentar importar
    try:
        from __version__ import __version__, __title__, __author__
        test_result(
            "Importação de __version__",
            True,
            f"v{__version__} - {__title__}"
        )
        test_result(
            "Informações do autor",
            bool(__author__),
            __author__
        )
        results.extend([True, True])
    except ImportError as e:
        test_result("Importação de __version__", False, str(e))
        results.extend([False, False])
    
    # Verificar core/__init__.py
    try:
        import core
        has_version = hasattr(core, '__version__')
        test_result(
            "core.__version__ disponível",
            has_version,
            f"v{core.__version__}" if has_version else "Não encontrado"
        )
        results.append(has_version)
    except Exception as e:
        test_result("core.__version__", False, str(e))
        results.append(False)
    
    return all(results)


def check_config_files():
    """Verifica arquivos de configuração"""
    print_section("3. VERIFICANDO ARQUIVOS DE CONFIGURAÇÃO")
    
    files_to_check = {
        "pytest.ini": "Configuração de testes",
        "pyproject.toml": "Metadados do projeto",
        ".pre-commit-config.yaml": "Hooks de pré-commit",
        "env.example.txt": "Template de variáveis",
        "requirements.txt": "Dependências",
    }
    
    results = []
    for file, description in files_to_check.items():
        file_path = Path(file)
        exists = file_path.exists()
        size = file_path.stat().st_size if exists else 0
        
        test_result(
            f"{file}",
            exists,
            f"{description} - {size} bytes" if exists else "Não encontrado"
        )
        results.append(exists)
    
    return all(results)


def check_documentation():
    """Verifica documentação"""
    print_section("4. VERIFICANDO DOCUMENTAÇÃO")
    
    docs = {
        "CHANGELOG.md": "Histórico de versões",
        "CHANGELOG_BOASPRATICAS.md": "Histórico do guia",
        "boaspraticas.md": "Guia de boas práticas",
        "GUIA_RAPIDO_V1.1.md": "Guia rápido v1.1",
        "MIGRAÇÃO_V1.1.md": "Relatório de migração",
        "README.md": "Documentação principal",
    }
    
    results = []
    total_lines = 0
    
    for doc, description in docs.items():
        doc_path = Path(doc)
        exists = doc_path.exists()
        
        if exists:
            with open(doc_path, 'r', encoding='utf-8') as f:
                lines = len(f.readlines())
            total_lines += lines
            test_result(f"{doc}", True, f"{description} - {lines} linhas")
        else:
            test_result(f"{doc}", False, "Não encontrado")
        
        results.append(exists)
    
    print(f"\n{Colors.OKGREEN}Total de linhas de documentação: {total_lines:,}{Colors.ENDC}")
    
    return all(results)


def check_directory_structure():
    """Verifica estrutura de diretórios"""
    print_section("5. VERIFICANDO ESTRUTURA DE DIRETÓRIOS")
    
    required_dirs = [
        "core",
        "apis",
        "dashboard",
        "data",
        "data/cache",
        "data/raw",
        "data/processed",
        "logs",
        "relatorios",
        "examples",
        "config",
        "docs",
        "scripts",
    ]
    
    results = []
    for directory in required_dirs:
        dir_path = Path(directory)
        exists = dir_path.exists() and dir_path.is_dir()
        
        if exists:
            # Contar arquivos no diretório
            try:
                files = list(dir_path.iterdir())
                count = len(files)
                details = f"{count} item(s)"
            except:
                details = "Permissão negada"
        else:
            details = "Não encontrado"
        
        test_result(f"{directory}/", exists, details)
        results.append(exists)
    
    return all(results)


def check_dependencies():
    """Verifica dependências principais"""
    print_section("6. VERIFICANDO DEPENDÊNCIAS")
    
    dependencies = {
        "pandas": "Manipulação de dados",
        "numpy": "Computação numérica",
        "requests": "Requisições HTTP",
        "yfinance": "Dados financeiros",
        "matplotlib": "Visualização",
        "streamlit": "Dashboard",
        "yaml": "Configuração YAML",
        "dotenv": "Variáveis de ambiente",
    }
    
    results = []
    for module, description in dependencies.items():
        try:
            if module == "yaml":
                import yaml
            elif module == "dotenv":
                from dotenv import load_dotenv
            else:
                __import__(module)
            
            test_result(f"{module}", True, description)
            results.append(True)
        except ImportError:
            test_result(f"{module}", False, f"{description} - NÃO INSTALADO")
            results.append(False)
    
    return all(results)


def check_dev_tools():
    """Verifica ferramentas de desenvolvimento (opcional)"""
    print_section("7. VERIFICANDO FERRAMENTAS DE DESENVOLVIMENTO (Opcional)")
    
    dev_tools = {
        "pytest": "Framework de testes",
        "black": "Formatador de código",
        "flake8": "Linter",
        "mypy": "Type checker",
        "isort": "Organizador de imports",
    }
    
    installed = []
    for tool, description in dev_tools.items():
        try:
            __import__(tool)
            test_result(f"{tool}", True, description)
            installed.append(tool)
        except ImportError:
            test_result(f"{tool}", False, f"{description} - não instalado")
    
    print(f"\n{Colors.OKBLUE}Ferramentas instaladas: {len(installed)}/{len(dev_tools)}{Colors.ENDC}")
    
    return len(installed) > 0  # Pelo menos uma ferramenta


def check_imports():
    """Verifica imports principais do projeto"""
    print_section("8. VERIFICANDO IMPORTS DO PROJETO")
    
    results = []
    
    # Core
    try:
        from core.market_indices import MarketIndicesManager
        test_result("core.market_indices", True, "MarketIndicesManager importado")
        results.append(True)
    except Exception as e:
        test_result("core.market_indices", False, str(e))
        results.append(False)
    
    # APIs
    try:
        from apis import yahoo_api, binance_api
        test_result("apis.*", True, "Módulos de API importados")
        results.append(True)
    except Exception as e:
        test_result("apis.*", False, str(e))
        results.append(False)
    
    # Examples
    try:
        from examples import portfolio_analysis_example
        test_result("examples.portfolio_analysis_example", True, "Exemplo importado")
        results.append(True)
    except Exception as e:
        test_result("examples.portfolio_analysis_example", False, str(e))
        results.append(False)
    
    return all(results)


def check_scripts():
    """Verifica scripts auxiliares"""
    print_section("9. VERIFICANDO SCRIPTS AUXILIARES")
    
    scripts = {
        "setup_v1.1.py": "Script de setup",
        "__version__.py": "Sistema de versão",
        "test_carteira_ideal.py": "Teste de carteira",
        "run_dashboard.py": "Executar dashboard",
    }
    
    results = []
    for script, description in scripts.items():
        script_path = Path(script)
        exists = script_path.exists()
        
        if exists:
            # Tentar compilar
            try:
                import py_compile
                py_compile.compile(str(script_path), doraise=True)
                test_result(f"{script}", True, f"{description} - sintaxe OK")
                results.append(True)
            except Exception as e:
                test_result(f"{script}", False, f"Erro de sintaxe: {e}")
                results.append(False)
        else:
            test_result(f"{script}", False, "Não encontrado")
            results.append(False)
    
    return all(results)


def print_summary(results):
    """Imprime resumo dos testes"""
    print_section("RESUMO DA VALIDAÇÃO")
    
    total = len(results)
    passed = sum(results.values())
    failed = total - passed
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"Total de verificações: {total}")
    print(f"{Colors.OKGREEN}✓ Passou: {passed}{Colors.ENDC}")
    print(f"{Colors.FAIL}✗ Falhou: {failed}{Colors.ENDC}")
    print(f"Percentual de sucesso: {percentage:.1f}%")
    
    if percentage == 100:
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}SISTEMA 100% VALIDADO!{Colors.ENDC}")
        print(f"{Colors.OKGREEN}Versao 1.1.0 esta funcionando perfeitamente!{Colors.ENDC}")
    elif percentage >= 80:
        print(f"\n{Colors.WARNING}{Colors.BOLD}SISTEMA QUASE PRONTO{Colors.ENDC}")
        print(f"{Colors.WARNING}Algumas verificacoes falharam, mas o sistema deve funcionar.{Colors.ENDC}")
    else:
        print(f"\n{Colors.FAIL}{Colors.BOLD}PROBLEMAS DETECTADOS{Colors.ENDC}")
        print(f"{Colors.FAIL}Varias verificacoes falharam. Revise a instalacao.{Colors.ENDC}")
    
    print(f"\n{Colors.HEADER}{'='*70}{Colors.ENDC}")
    
    return percentage == 100


def main():
    """Função principal"""
    # Garantir encoding UTF-8 no Windows
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except (AttributeError, OSError):
            pass
    
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("=" + "="*68 + "=")
    print("DEBUG E VALIDAÇÃO - SISTEMA DE ANÁLISE DE PORTFÓLIOS v1.1.0".center(70))
    print("=" + "="*68 + "=")
    print(f"{Colors.ENDC}")
    
    print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Diretório: {Path.cwd()}")
    
    # Executar verificações
    results = {}
    
    try:
        results["Python"] = check_python_version()
        results["Versionamento"] = check_version_system()
        results["Configuração"] = check_config_files()
        results["Documentação"] = check_documentation()
        results["Diretórios"] = check_directory_structure()
        results["Dependências"] = check_dependencies()
        results["Dev Tools"] = check_dev_tools()
        results["Imports"] = check_imports()
        results["Scripts"] = check_scripts()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Validação interrompida pelo usuário{Colors.ENDC}")
        return 1
    except Exception as e:
        print(f"\n{Colors.FAIL}Erro durante validação: {e}{Colors.ENDC}")
        return 1
    
    # Imprimir resumo
    success = print_summary(results)
    
    return 0 if success else 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"{Colors.FAIL}Erro fatal: {e}{Colors.ENDC}")
        sys.exit(1)

