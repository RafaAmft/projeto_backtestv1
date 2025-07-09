#!/usr/bin/env python3
"""
🔒 Script de Auditoria de Segurança - Sistema de Análise Financeira
Versão: 1.0
Data: 08/07/2025

Script opcional para realizar auditoria de segurança do projeto.
Pode ser executado independentemente sem afetar o funcionamento.
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))

from core.security_manager import SecurityManager, enable_security, disable_security

def print_header():
    """Imprime cabeçalho do script"""
    print("=" * 80)
    print("🔒 AUDITORIA DE SEGURANÇA - SISTEMA DE ANÁLISE FINANCEIRA")
    print("=" * 80)
    print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"Versão: 1.0")
    print("=" * 80)

def check_dependencies():
    """Verifica dependências de segurança"""
    print("\n📦 VERIFICANDO DEPENDÊNCIAS DE SEGURANÇA")
    print("-" * 50)
    
    security_deps = [
        'cryptography',
        'requests',
        'urllib3',
        'certifi'
    ]
    
    missing_deps = []
    
    for dep in security_deps:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} - NÃO INSTALADO")
            missing_deps.append(dep)
    
    if missing_deps:
        print(f"\n⚠️  Dependências de segurança faltando: {', '.join(missing_deps)}")
        print("💡 Execute: pip install " + " ".join(missing_deps))
    else:
        print("\n✅ Todas as dependências de segurança estão instaladas")
    
    return len(missing_deps) == 0

def check_env_file():
    """Verifica arquivo .env"""
    print("\n🔐 VERIFICANDO ARQUIVO .ENV")
    print("-" * 50)
    
    env_file = Path(".env")
    env_template = Path(".env.template")
    
    if env_file.exists():
        print("✅ Arquivo .env encontrado")
        
        # Verificar se está no .gitignore
        gitignore = Path(".gitignore")
        if gitignore.exists():
            with open(gitignore, 'r', encoding='utf-8') as f:
                content = f.read()
                if '.env' in content:
                    print("✅ .env está no .gitignore")
                else:
                    print("❌ .env NÃO está no .gitignore")
        else:
            print("❌ Arquivo .gitignore não encontrado")
    else:
        print("⚠️  Arquivo .env não encontrado")
        if env_template.exists():
            print("💡 Copie .env.template para .env e configure suas chaves")
        else:
            print("❌ Template .env.template não encontrado")
    
    return env_file.exists()

def check_config_security():
    """Verifica segurança do arquivo de configuração"""
    print("\n⚙️  VERIFICANDO CONFIGURAÇÃO")
    print("-" * 50)
    
    config_file = Path("config/config.yaml")
    
    if not config_file.exists():
        print("❌ Arquivo config.yaml não encontrado")
        return False
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar por chaves hardcoded
        issues = []
        
        if 'api_key: "' in content and 'api_key: ""' not in content:
            issues.append("Possível chave de API hardcoded")
        
        if 'api_secret: "' in content and 'api_secret: ""' not in content:
            issues.append("Possível secret de API hardcoded")
        
        if 'password: "' in content and 'password: ""' not in content:
            issues.append("Possível senha hardcoded")
        
        if issues:
            print("❌ Problemas encontrados:")
            for issue in issues:
                print(f"   - {issue}")
            return False
        else:
            print("✅ Configuração segura")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao verificar configuração: {e}")
        return False

def run_security_audit():
    """Executa auditoria completa de segurança"""
    print("\n🔍 EXECUTANDO AUDITORIA DE SEGURANÇA")
    print("-" * 50)
    
    # Ativar gerenciador de segurança
    enable_security()
    security_manager = SecurityManager(enabled=True)
    
    # Executar auditoria
    audit_result = security_manager.audit_project_security()
    
    print(f"📁 Arquivos verificados: {audit_result['files_checked']}")
    
    if audit_result['secure']:
        print("✅ Projeto seguro")
    else:
        print("❌ Problemas de segurança encontrados:")
        for issue in audit_result['issues']:
            print(f"   📄 {issue['file']}")
            for problem in issue['issues']:
                print(f"      - {problem}")
    
    # Desativar gerenciador
    disable_security()
    
    return audit_result['secure']

def check_git_history():
    """Verifica histórico do Git por informações sensíveis"""
    print("\n📜 VERIFICANDO HISTÓRICO DO GIT")
    print("-" * 50)
    
    try:
        import subprocess
        
        # Verificar se é um repositório Git
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        
        if result.returncode != 0:
            print("⚠️  Não é um repositório Git")
            return True
        
        # Verificar por commits com palavras-chave sensíveis
        sensitive_keywords = ['api_key', 'api_secret', 'password', 'token', 'secret']
        
        for keyword in sensitive_keywords:
            result = subprocess.run(
                ['git', 'log', '--all', '--grep', keyword, '--oneline'],
                capture_output=True, text=True
            )
            
            if result.stdout.strip():
                print(f"⚠️  Possível informação sensível no histórico: {keyword}")
                print(f"   Commits: {result.stdout.strip()}")
            else:
                print(f"✅ Nenhum commit com '{keyword}' encontrado")
        
        return True
        
    except Exception as e:
        print(f"⚠️  Erro ao verificar Git: {e}")
        return True

def generate_security_report():
    """Gera relatório de segurança"""
    print("\n📋 GERANDO RELATÓRIO DE SEGURANÇA")
    print("-" * 50)
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "checks": {}
    }
    
    # Executar verificações
    report["checks"]["dependencies"] = check_dependencies()
    report["checks"]["env_file"] = check_env_file()
    report["checks"]["config_security"] = check_config_security()
    report["checks"]["git_history"] = check_git_history()
    report["checks"]["security_audit"] = run_security_audit()
    
    # Calcular score de segurança
    total_checks = len(report["checks"])
    passed_checks = sum(report["checks"].values())
    security_score = (passed_checks / total_checks) * 100
    
    report["security_score"] = security_score
    report["total_checks"] = total_checks
    report["passed_checks"] = passed_checks
    
    # Salvar relatório
    report_file = f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Relatório salvo em: {report_file}")
        
    except Exception as e:
        print(f"❌ Erro ao salvar relatório: {e}")
    
    # Exibir resumo
    print(f"\n📊 RESUMO DA AUDITORIA")
    print("-" * 50)
    print(f"Score de Segurança: {security_score:.1f}%")
    print(f"Verificações Passadas: {passed_checks}/{total_checks}")
    
    if security_score >= 80:
        print("🎉 Excelente! Seu projeto está seguro")
    elif security_score >= 60:
        print("⚠️  Bom, mas há melhorias a fazer")
    else:
        print("🚨 Atenção! Há problemas de segurança importantes")
    
    return report

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Auditoria de Segurança")
    parser.add_argument("--quick", action="store_true", help="Execução rápida")
    parser.add_argument("--report", action="store_true", help="Gerar relatório")
    parser.add_argument("--fix", action="store_true", help="Tentar corrigir problemas")
    
    args = parser.parse_args()
    
    print_header()
    
    if args.quick:
        print("\n⚡ EXECUÇÃO RÁPIDA")
        check_dependencies()
        check_env_file()
        check_config_security()
    elif args.report:
        generate_security_report()
    elif args.fix:
        print("\n🔧 MODO CORREÇÃO")
        print("⚠️  Este modo ainda não está implementado")
        print("💡 Use --report para ver os problemas")
    else:
        # Execução completa
        generate_security_report()
    
    print("\n" + "=" * 80)
    print("🔒 AUDITORIA CONCLUÍDA")
    print("=" * 80)

if __name__ == "__main__":
    main() 