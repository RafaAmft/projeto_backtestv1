"""
🔒 Gerenciador de Segurança - Sistema de Análise Financeira
Versão: 1.0
Data: 08/07/2025

Módulo opcional para implementar medidas de segurança sem interferir
no funcionamento atual do sistema.
"""

import os
import re
import hashlib
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class SecurityManager:
    """
    Gerenciador de segurança opcional para o sistema.
    Pode ser ativado/desativado sem afetar o funcionamento.
    """
    
    def __init__(self, enabled: bool = False):
        """
        Inicializa o gerenciador de segurança.
        
        Args:
            enabled: Se True, ativa as verificações de segurança
        """
        self.enabled = enabled
        self.security_log = []
        self.suspicious_patterns = [
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'api_secret\s*=\s*["\'][^"\']+["\']',
            r'password\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'private_key\s*=\s*["\'][^"\']+["\']',
        ]
        
        if self.enabled:
            logger.info("🔒 Gerenciador de Segurança ativado")
        else:
            logger.info("🔓 Gerenciador de Segurança desativado (modo seguro)")
    
    def validate_input(self, data: Any, input_type: str = "generic") -> Dict[str, Any]:
        """
        Valida entrada de dados para prevenir injeções.
        
        Args:
            data: Dados a serem validados
            input_type: Tipo de entrada (api_key, symbol, etc.)
            
        Returns:
            Dict com resultado da validação
        """
        if not self.enabled:
            return {"valid": True, "warnings": []}
        
        result = {"valid": True, "warnings": [], "errors": []}
        
        try:
            if input_type == "api_key":
                result = self._validate_api_key(data)
            elif input_type == "symbol":
                result = self._validate_symbol(data)
            elif input_type == "url":
                result = self._validate_url(data)
            elif input_type == "numeric":
                result = self._validate_numeric(data)
            else:
                result = self._validate_generic(data)
                
        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"Erro na validação: {str(e)}")
            logger.warning(f"Erro na validação de {input_type}: {e}")
        
        return result
    
    def _validate_api_key(self, api_key: str) -> Dict[str, Any]:
        """Valida formato de chave de API"""
        result = {"valid": True, "warnings": [], "errors": []}
        
        if not api_key:
            result["warnings"].append("Chave de API vazia")
            return result
        
        # Verificar se não está hardcoded
        if len(api_key) > 50:
            result["warnings"].append("Chave de API muito longa - verificar se não está hardcoded")
        
        # Verificar se contém caracteres suspeitos
        if re.search(r'[<>"\']', api_key):
            result["errors"].append("Chave de API contém caracteres suspeitos")
            result["valid"] = False
        
        return result
    
    def _validate_symbol(self, symbol: str) -> Dict[str, Any]:
        """Valida símbolo de ativo"""
        result = {"valid": True, "warnings": [], "errors": []}
        
        if not symbol:
            result["errors"].append("Símbolo vazio")
            result["valid"] = False
            return result
        
        # Verificar caracteres permitidos
        if not re.match(r'^[A-Z0-9.=^]+$', symbol):
            result["errors"].append("Símbolo contém caracteres inválidos")
            result["valid"] = False
        
        # Verificar tamanho
        if len(symbol) > 20:
            result["warnings"].append("Símbolo muito longo")
        
        return result
    
    def _validate_url(self, url: str) -> Dict[str, Any]:
        """Valida URL"""
        result = {"valid": True, "warnings": [], "errors": []}
        
        if not url:
            result["errors"].append("URL vazia")
            result["valid"] = False
            return result
        
        # Verificar protocolo
        if not url.startswith(('http://', 'https://')):
            result["errors"].append("URL deve usar HTTP ou HTTPS")
            result["valid"] = False
        
        # Verificar caracteres suspeitos
        if re.search(r'[<>"\']', url):
            result["errors"].append("URL contém caracteres suspeitos")
            result["valid"] = False
        
        return result
    
    def _validate_numeric(self, value: Any) -> Dict[str, Any]:
        """Valida valores numéricos"""
        result = {"valid": True, "warnings": [], "errors": []}
        
        try:
            float_val = float(value)
            
            # Verificar se é um número razoável
            if float_val < 0:
                result["warnings"].append("Valor negativo")
            
            if float_val > 1e12:  # 1 trilhão
                result["warnings"].append("Valor muito alto")
                
        except (ValueError, TypeError):
            result["errors"].append("Valor não é numérico")
            result["valid"] = False
        
        return result
    
    def _validate_generic(self, data: Any) -> Dict[str, Any]:
        """Validação genérica"""
        result = {"valid": True, "warnings": [], "errors": []}
        
        if isinstance(data, str):
            # Verificar por padrões suspeitos
            for pattern in self.suspicious_patterns:
                if re.search(pattern, data, re.IGNORECASE):
                    result["warnings"].append(f"Padrão suspeito encontrado: {pattern}")
        
        return result
    
    def sanitize_data(self, data: Any) -> Any:
        """
        Sanitiza dados para remover conteúdo perigoso.
        
        Args:
            data: Dados a serem sanitizados
            
        Returns:
            Dados sanitizados
        """
        if not self.enabled:
            return data
        
        try:
            if isinstance(data, str):
                return self._sanitize_string(data)
            elif isinstance(data, dict):
                return self._sanitize_dict(data)
            elif isinstance(data, list):
                return self._sanitize_list(data)
            else:
                return data
                
        except Exception as e:
            logger.warning(f"Erro na sanitização: {e}")
            return data
    
    def _sanitize_string(self, text: str) -> str:
        """Sanitiza string"""
        # Remover caracteres perigosos
        text = re.sub(r'[<>"\']', '', text)
        
        # Remover scripts
        text = re.sub(r'<script.*?</script>', '', text, flags=re.IGNORECASE)
        
        # Remover comandos SQL
        sql_patterns = [
            r'SELECT.*FROM',
            r'INSERT.*INTO',
            r'UPDATE.*SET',
            r'DELETE.*FROM',
            r'DROP.*TABLE',
            r'CREATE.*TABLE'
        ]
        
        for pattern in sql_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def _sanitize_dict(self, data: Dict) -> Dict:
        """Sanitiza dicionário"""
        sanitized = {}
        for key, value in data.items():
            sanitized_key = self._sanitize_string(str(key))
            sanitized[sanitized_key] = self.sanitize_data(value)
        return sanitized
    
    def _sanitize_list(self, data: List) -> List:
        """Sanitiza lista"""
        return [self.sanitize_data(item) for item in data]
    
    def check_file_security(self, file_path: str) -> Dict[str, Any]:
        """
        Verifica segurança de um arquivo.
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Resultado da verificação
        """
        if not self.enabled:
            return {"secure": True, "issues": []}
        
        result = {"secure": True, "issues": []}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar por padrões suspeitos
            for pattern in self.suspicious_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    result["issues"].append(f"Padrão suspeito encontrado: {pattern}")
                    result["secure"] = False
            
            # Verificar por chaves de API hardcoded
            if re.search(r'api_key\s*=\s*["\'][^"\']{20,}["\']', content):
                result["issues"].append("Possível chave de API hardcoded")
                result["secure"] = False
            
            # Verificar por senhas
            if re.search(r'password\s*=\s*["\'][^"\']+["\']', content):
                result["issues"].append("Possível senha hardcoded")
                result["secure"] = False
                
        except Exception as e:
            result["issues"].append(f"Erro ao verificar arquivo: {e}")
            result["secure"] = False
        
        return result
    
    def audit_project_security(self, project_path: str = ".") -> Dict[str, Any]:
        """
        Realiza auditoria de segurança do projeto.
        
        Args:
            project_path: Caminho do projeto
            
        Returns:
            Resultado da auditoria
        """
        if not self.enabled:
            return {"secure": True, "files_checked": 0, "issues": []}
        
        result = {
            "secure": True,
            "files_checked": 0,
            "issues": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Extensões de arquivo para verificar
        extensions = ['.py', '.yaml', '.yml', '.json', '.txt', '.md']
        
        try:
            for root, dirs, files in os.walk(project_path):
                # Pular diretórios que não devem ser verificados
                dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'venv', 'env', 'node_modules']]
                
                for file in files:
                    if any(file.endswith(ext) for ext in extensions):
                        file_path = os.path.join(root, file)
                        file_result = self.check_file_security(file_path)
                        
                        result["files_checked"] += 1
                        
                        if not file_result["secure"]:
                            result["secure"] = False
                            result["issues"].append({
                                "file": file_path,
                                "issues": file_result["issues"]
                            })
                            
        except Exception as e:
            result["issues"].append(f"Erro na auditoria: {e}")
            result["secure"] = False
        
        return result
    
    def log_security_event(self, event_type: str, details: str, severity: str = "INFO"):
        """
        Registra evento de segurança.
        
        Args:
            event_type: Tipo do evento
            details: Detalhes do evento
            severity: Severidade (INFO, WARNING, ERROR)
        """
        if not self.enabled:
            return
        
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "details": details,
            "severity": severity
        }
        
        self.security_log.append(event)
        
        # Log no sistema
        if severity == "ERROR":
            logger.error(f"🔒 SECURITY ERROR: {event_type} - {details}")
        elif severity == "WARNING":
            logger.warning(f"🔒 SECURITY WARNING: {event_type} - {details}")
        else:
            logger.info(f"🔒 SECURITY INFO: {event_type} - {details}")
    
    def get_security_report(self) -> Dict[str, Any]:
        """
        Gera relatório de segurança.
        
        Returns:
            Relatório de segurança
        """
        return {
            "enabled": self.enabled,
            "events_count": len(self.security_log),
            "recent_events": self.security_log[-10:] if self.security_log else [],
            "timestamp": datetime.now().isoformat()
        }
    
    def export_security_log(self, file_path: str = "security_log.json"):
        """
        Exporta log de segurança para arquivo.
        
        Args:
            file_path: Caminho do arquivo de saída
        """
        if not self.enabled or not self.security_log:
            return
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.security_log, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Log de segurança exportado para {file_path}")
            
        except Exception as e:
            logger.error(f"Erro ao exportar log de segurança: {e}")

# Instância global (opcional)
security_manager = SecurityManager(enabled=False)

def enable_security():
    """Ativa o gerenciador de segurança"""
    global security_manager
    security_manager.enabled = True
    logger.info("🔒 Gerenciador de Segurança ativado")

def disable_security():
    """Desativa o gerenciador de segurança"""
    global security_manager
    security_manager.enabled = False
    logger.info("🔓 Gerenciador de Segurança desativado")

def get_security_manager() -> SecurityManager:
    """Retorna a instância do gerenciador de segurança"""
    return security_manager 