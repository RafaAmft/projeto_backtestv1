# 📁 Organização de Arquivos do Projeto

## 🎯 Objetivo

Este documento descreve a organização dos arquivos do projeto para manter a área comum limpa e organizada.

## 📊 Problema Identificado

A área comum (diretório raiz) estava poluída com:
- **Relatórios JSON** (test_report_*.json, relatorio_carteira_ideal_*.json)
- **Arquivos de teste** (test_cotacoes_reais_fundos.py)
- **Gráficos** (*.png, *.jpg)
- **Arquivos de resultado** (resultados_*.json, audit_report.json)
- **Arquivos de debug** (README_SISTEMA_NOVO.md, resultado_data_manager.txt)

## 🧹 Solução Implementada

### Script de Organização
- **Arquivo**: `scripts/organizar_projeto.py`
- **Função**: Move automaticamente arquivos para diretórios apropriados
- **Segurança**: Confirma antes de mover arquivos

### Estrutura de Diretórios

```
📁 Projeto/
├── 📄 Arquivos Principais (Raiz)
│   ├── README.md
│   ├── requirements.txt
│   ├── run_dashboard.py
│   ├── carteira_ideal.json
│   ├── mapeamento_fundos.json
│   ├── ROADMAP.md
│   ├── RESUMO_EXECUTIVO.md
│   └── CHECKPOINT_PROJETO.md
│
├── 📁 relatorios_organizados/
│   ├── relatorio_carteira_ideal_*.json
│   ├── gerar_relatorio_*.py
│   └── relatorio_*.py
│
├── 📁 relatorios_cache/
│   ├── 📁 graficos/
│   │   ├── *.png
│   │   └── *.jpg
│   ├── 📁 test_reports/
│   │   └── test_report_*.json
│   └── 📁 yahoo_tests/
│       └── yahoo_connection_test.json
│
├── 📁 testes_organizados/
│   ├── test_cotacoes_reais_fundos.py
│   ├── teste_*.py
│   └── test_*.py
│
├── 📁 data/
│   ├── resultados_*.json
│   ├── audit_report.json
│   └── resultado_data_manager.txt
│
└── 📁 arquivos_debug/
    └── README_SISTEMA_NOVO.md
```

## 🚀 Como Usar

### Organização Automática
```bash
# Executar script de organização
python scripts/organizar_projeto.py
```

### Organização Manual
```bash
# Mover relatórios
mv relatorio_carteira_ideal_*.json relatorios_organizados/

# Mover testes
mv test_cotacoes_reais_fundos.py testes_organizados/

# Mover gráficos
mv *.png relatorios_cache/graficos/

# Mover resultados
mv resultados_*.json data/
```

## 📋 Regras de Organização

### ✅ Arquivos que FICAM na Raiz
- **Documentação principal**: README.md, ROADMAP.md, etc.
- **Configuração**: requirements.txt, config.yaml
- **Scripts principais**: run_dashboard.py, test_carteira_ideal.py
- **Dados essenciais**: carteira_ideal.json, mapeamento_fundos.json

### 📁 Arquivos que VÃO para Diretórios

| Tipo | Destino | Exemplos |
|------|---------|----------|
| **Relatórios JSON** | `relatorios_organizados/` | `relatorio_carteira_ideal_*.json` |
| **Test Reports** | `relatorios_cache/test_reports/` | `test_report_*.json` |
| **Gráficos** | `relatorios_cache/graficos/` | `*.png`, `*.jpg` |
| **Arquivos de Teste** | `testes_organizados/` | `test_*.py` |
| **Resultados** | `data/` | `resultados_*.json` |
| **Debug** | `arquivos_debug/` | `README_SISTEMA_NOVO.md` |

## 🔧 Configuração do .gitignore

O `.gitignore` foi atualizado para ignorar automaticamente:
```gitignore
# Arquivos de teste e relatórios temporários
test_report_*.json
relatorio_carteira_ideal_*.json
yahoo_connection_test.json
resultado_data_manager.txt

# Arquivos de debug e desenvolvimento
README_SISTEMA_NOVO.md
debug_*.html
debug_*.txt
```

## 📊 Benefícios

### ✅ Antes da Organização
- 50+ arquivos na raiz
- Difícil encontrar arquivos importantes
- Poluição visual
- Confusão na navegação

### ✅ Depois da Organização
- ~15 arquivos essenciais na raiz
- Estrutura clara e lógica
- Fácil navegação
- Manutenção simplificada

## 🎯 Próximos Passos

1. **Executar organização**: `python scripts/organizar_projeto.py`
2. **Verificar estrutura**: Confirmar se todos os arquivos estão nos lugares corretos
3. **Atualizar documentação**: Manter este guia atualizado
4. **Automatizar**: Configurar organização automática no CI/CD

## 📞 Suporte

Para dúvidas sobre organização:
1. Consulte este documento
2. Execute o script de organização
3. Verifique a estrutura de diretórios
4. Abra uma issue se necessário

---

**Resultado**: Área comum limpa e organizada! 🎉 