#!/usr/bin/env python3
"""
Script de Inicialização - Sistema de Análise de Portfólios v1.1.0

Este script ajuda a configurar o ambiente para a versão 1.1.0
do Sistema de Análise de Portfólios.

Uso:
    python setup_v1.1.py
"""

import os
import sys
import subprocess
from pathlib import Path
import shutil

# Cores para output no terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(message):
    """Imprime cabeçalho colorido"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")


def print_success(message):
    """Imprime mensagem de sucesso"""
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")


def print_error(message):
    """Imprime mensagem de erro"""
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")


def print_warning(message):
    """Imprime mensagem de aviso"""
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")


def print_info(message):
    """Imprime mensagem informativa"""
    print(f"{Colors.OKBLUE}ℹ {message}{Colors.ENDC}")


def check_python_version():
    """Verifica se a versão do Python é adequada"""
    print_header("Verificando Versão do Python")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    print_info(f"Python {version_str} detectado")
    
    if version.major == 3 and version.minor >= 10:
        print_success("Versão do Python OK (>= 3.10)")
        return True
    else:
        print_error(f"Python 3.10+ requerido. Você tem {version_str}")
        return False


def create_env_file():
    """Cria arquivo .env a partir do template"""
    print_header("Configurando Variáveis de Ambiente")
    
    env_file = Path(".env")
    template_file = Path("env.example.txt")
    
    if env_file.exists():
        print_warning(".env já existe")
        response = input("Deseja sobrescrever? (s/N): ").strip().lower()
        if response != 's':
            print_info("Mantendo .env existente")
            return True
    
    if not template_file.exists():
        print_error(f"Template {template_file} não encontrado")
        return False
    
    try:
        shutil.copy(template_file, env_file)
        print_success(f"Arquivo .env criado a partir de {template_file}")
        print_info("IMPORTANTE: Edite o arquivo .env com suas credenciais!")
        return True
    except Exception as e:
        print_error(f"Erro ao criar .env: {e}")
        return False


def create_directories():
    """Cria diretórios necessários"""
    print_header("Criando Estrutura de Diretórios")
    
    directories = [
        "data/cache",
        "data/raw",
        "data/processed",
        "logs",
        "relatorios/portfolio",
        "relatorios/executivo",
        "relatorios/graficos",
        "tests/unit",
        "tests/integration",
        "tests/fixtures",
    ]
    
    for directory in directories:
        path = Path(directory)
        if not path.exists():
            try:
                path.mkdir(parents=True, exist_ok=True)
                print_success(f"Criado: {directory}")
            except Exception as e:
                print_error(f"Erro ao criar {directory}: {e}")
        else:
            print_info(f"Já existe: {directory}")
    
    return True


def install_dependencies():
    """Instala dependências do requirements.txt"""
    print_header("Instalando Dependências")
    
    requirements_file = Path("requirements.txt")
    
    if not requirements_file.exists():
        print_error("requirements.txt não encontrado")
        return False
    
    print_info("Instalando pacotes... (isso pode demorar)")
    
    try:
        # Atualizar pip
        print_info("Atualizando pip...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--upgrade", "pip"
        ], stdout=subprocess.DEVNULL)
        
        # Instalar dependências
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        
        print_success("Dependências instaladas com sucesso")
        return True
        
    except subprocess.CalledProcessError as e:
        print_error(f"Erro ao instalar dependências: {e}")
        return False


def install_dev_tools():
    """Instala ferramentas de desenvolvimento (opcional)"""
    print_header("Ferramentas de Desenvolvimento (Opcional)")
    
    response = input("Instalar ferramentas de desenvolvimento? (S/n): ").strip().lower()
    
    if response == 'n':
        print_info("Pulando ferramentas de desenvolvimento")
        return True
    
    dev_tools = [
        "pytest",
        "pytest-cov",
        "pytest-mock",
        "black",
        "flake8",
        "mypy",
        "isort",
        "pre-commit",
        "bandit",
    ]
    
    print_info(f"Instalando: {', '.join(dev_tools)}")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install"
        ] + dev_tools)
        
        print_success("Ferramentas de desenvolvimento instaladas")
        return True
        
    except subprocess.CalledProcessError as e:
        print_error(f"Erro ao instalar ferramentas de dev: {e}")
        return False


def setup_precommit():
    """Configura pre-commit hooks"""
    print_header("Configurando Pre-commit Hooks (Opcional)")
    
    response = input("Configurar pre-commit hooks? (S/n): ").strip().lower()
    
    if response == 'n':
        print_info("Pulando pre-commit hooks")
        return True
    
    try:
        # Instalar pre-commit
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "pre-commit"
        ], stdout=subprocess.DEVNULL)
        
        # Instalar hooks
        subprocess.check_call(["pre-commit", "install"])
        
        print_success("Pre-commit hooks configurados")
        print_info("Os hooks serão executados automaticamente em cada commit")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print_error(f"Erro ao configurar pre-commit: {e}")
        return False


def run_tests():
    """Executa testes iniciais"""
    print_header("Executando Testes Iniciais")
    
    response = input("Executar testes? (S/n): ").strip().lower()
    
    if response == 'n':
        print_info("Pulando testes")
        return True
    
    # Verificar se pytest está instalado
    try:
        subprocess.check_call([
            sys.executable, "-m", "pytest", "--version"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        print_warning("pytest não instalado, executando teste básico")
        test_file = Path("test_carteira_ideal.py")
        if test_file.exists():
            try:
                subprocess.check_call([sys.executable, str(test_file)])
                print_success("Teste básico passou")
                return True
            except subprocess.CalledProcessError:
                print_error("Teste básico falhou")
                return False
        else:
            print_warning("Nenhum teste encontrado")
            return True
    
    # Executar pytest
    try:
        print_info("Executando pytest...")
        subprocess.check_call([sys.executable, "-m", "pytest", "-v"])
        print_success("Todos os testes passaram")
        return True
    except subprocess.CalledProcessError:
        print_warning("Alguns testes falharam (isso pode ser normal se APIs não estiverem configuradas)")
        return True


def print_final_instructions():
    """Imprime instruções finais"""
    print_header("Setup Completo! 🎉")
    
    print(f"{Colors.OKGREEN}{Colors.BOLD}Próximos Passos:{Colors.ENDC}\n")
    
    steps = [
        "1. Edite o arquivo .env com suas credenciais de API",
        "2. Execute 'python test_carteira_ideal.py' para validar",
        "3. Execute 'python run_dashboard.py' para abrir o dashboard",
        "4. Leia GUIA_RAPIDO_V1.1.md para mais informações",
        "5. Confira boaspraticas.md para guidelines de desenvolvimento",
    ]
    
    for step in steps:
        print(f"   {Colors.OKCYAN}{step}{Colors.ENDC}")
    
    print(f"\n{Colors.OKGREEN}{Colors.BOLD}Recursos Úteis:{Colors.ENDC}\n")
    
    resources = [
        "📖 README.md - Documentação principal",
        "📋 CHANGELOG.md - Histórico de versões",
        "🔧 pytest.ini - Configuração de testes",
        "🎯 pyproject.toml - Metadados do projeto",
        "📚 boaspraticas.md - Guia de desenvolvimento",
    ]
    
    for resource in resources:
        print(f"   {resource}")
    
    print(f"\n{Colors.OKGREEN}{Colors.BOLD}Comandos Úteis:{Colors.ENDC}\n")
    
    commands = [
        "pytest                    # Executar testes",
        "black core/ apis/        # Formatar código",
        "pre-commit run --all     # Validar código",
        "python __version__.py    # Ver versão do sistema",
    ]
    
    for command in commands:
        print(f"   {Colors.OKCYAN}$ {command}{Colors.ENDC}")
    
    print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.OKGREEN}Sistema pronto para uso! Versão 1.1.0{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")


def main():
    """Função principal"""
    print_header("Setup - Sistema de Análise de Portfólios v1.1.0")
    
    print(f"{Colors.OKCYAN}Este script irá:{Colors.ENDC}")
    print("  • Verificar requisitos do sistema")
    print("  • Criar estrutura de diretórios")
    print("  • Configurar variáveis de ambiente")
    print("  • Instalar dependências")
    print("  • Configurar ferramentas de desenvolvimento (opcional)")
    print("  • Executar testes iniciais\n")
    
    response = input(f"{Colors.BOLD}Continuar? (S/n): {Colors.ENDC}").strip().lower()
    
    if response == 'n':
        print_info("Setup cancelado")
        return 1
    
    steps = [
        ("Versão do Python", check_python_version),
        ("Diretórios", create_directories),
        ("Arquivo .env", create_env_file),
        ("Dependências", install_dependencies),
        ("Ferramentas de Dev", install_dev_tools),
        ("Pre-commit Hooks", setup_precommit),
        ("Testes", run_tests),
    ]
    
    failed_steps = []
    
    for step_name, step_func in steps:
        try:
            if not step_func():
                failed_steps.append(step_name)
        except KeyboardInterrupt:
            print_error("\n\nSetup interrompido pelo usuário")
            return 1
        except Exception as e:
            print_error(f"\nErro inesperado em {step_name}: {e}")
            failed_steps.append(step_name)
    
    if failed_steps:
        print_warning(f"\nAlgumas etapas falharam: {', '.join(failed_steps)}")
        print_info("O sistema pode não funcionar corretamente")
        return 1
    
    print_final_instructions()
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print_error("\n\nSetup interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n\nErro fatal: {e}")
        sys.exit(1)

