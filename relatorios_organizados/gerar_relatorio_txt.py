#!/usr/bin/env python3
"""
Script para gerar relatório TXT da carteira ideal
"""

import json
import os
from datetime import datetime

def gerar_relatorio_txt(arquivo_json):
    """Converte relatório JSON em formato TXT legível"""
    
    # Carregar dados do JSON
    with open(arquivo_json, 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    # Gerar relatório TXT
    relatorio = f"""
{'='*80}
                    RELATÓRIO DA CARTEIRA IDEAL
{'='*80}

📅 Data de Geração: {datetime.now().strftime("%d/%m/%Y às %H:%M:%S")}
📊 Período de Análise: Últimos 24 meses
💰 Valor Total da Carteira: R$ {dados['carteira']['valor_total']:,.2f}

{'='*80}

📋 RESUMO EXECUTIVO
{'-'*40}

🎯 Estratégia: {dados['carteira']['metadados']['estrategia']}
⚠️ Perfil de Risco: {dados['carteira']['metadados']['perfil_risco']}
⏰ Horizonte de Tempo: {dados['carteira']['metadados']['horizonte_tempo']}
🔄 Rebalanceamento: {dados['carteira']['metadados']['rebalanceamento']}

📊 Alocação por Classe de Ativo:
"""
    
    # Adicionar alocação por classe
    for classe, percentual in dados['resumo']['alocacao_por_classe'].items():
        relatorio += f"   • {classe}: {percentual}\n"
    
    relatorio += f"""
{'='*80}

📊 ANÁLISE DETALHADA POR ATIVO
{'-'*40}
"""
    
    # Adicionar tabela de ativos
    for ativo in dados['ativos']:
        relatorio += f"""
{ativo['classe']}: {ativo['nome']}
   💰 Valor Investido: R$ {ativo['valor']:,.2f}
   📈 Percentual da Carteira: {ativo['percentual']:.2f}%
"""
        
        if ativo.get('preco_atual'):
            relatorio += f"   💵 Preço Atual: R$ {ativo['preco_atual']:,.2f}\n"
        
        if ativo.get('rentabilidade'):
            relatorio += f"   📊 Rentabilidade: {ativo['rentabilidade']}\n"
        
        if ativo.get('anos_dados'):
            relatorio += f"   📅 Anos de Dados: {ativo['anos_dados']}\n"
    
    relatorio += f"""
{'='*80}

📈 MÉTRICAS DE RISCO E RETORNO
{'-'*40}

📊 Métricas Básicas:
   • Retorno Esperado: {dados['metricas_risco']['retorno_esperado']:.2%}
   • Volatilidade: {dados['metricas_risco']['volatilidade']:.2%}
   • Sharpe Ratio: {dados['metricas_risco']['sharpe_ratio']:.2f}

📊 Métricas Avançadas:
   • Retorno Médio Mensal: {dados['metricas_avancadas']['retorno_medio_mensal']:.4%}
   • Volatilidade Mensal: {dados['metricas_avancadas']['volatilidade_mensal']:.4%}
   • Sharpe Ratio (Avançado): {dados['metricas_avancadas']['sharpe_ratio']:.2f}
   • Sortino Ratio: {dados['metricas_avancadas']['sortino_ratio']:.2f}
   • Máximo Drawdown: {dados['metricas_avancadas']['max_drawdown']:.2%}
   • CAGR (Retorno Anualizado): {dados['metricas_avancadas']['cagr']:.2%}

{'='*80}

📈 EVOLUÇÃO MENAL DA CARTEIRA
{'-'*40}

"""
    
    # Adicionar evolução mensal
    for i, (data, valor) in enumerate(zip(dados['evolucao_mensal']['datas'], dados['evolucao_mensal']['valores'])):
        if i % 3 == 0:  # Mostrar a cada 3 meses para não ficar muito longo
            relatorio += f"   {data}: R$ {valor:,.2f}\n"
    
    relatorio += f"""
{'='*80}

🎯 OBJETIVOS DA CARTEIRA
{'-'*40}
"""
    
    for objetivo in dados['carteira']['metadados']['objetivos']:
        relatorio += f"   • {objetivo}\n"
    
    relatorio += f"""
{'='*80}

💡 RECOMENDAÇÕES
{'-'*40}

1. DIVERSIFICAÇÃO:
   - A carteira está bem diversificada com 4 classes de ativos
   - Renda fixa (40%) oferece estabilidade
   - Ações (30%) proporcionam crescimento
   - Fundos cambiais (15%) protegem contra variação cambial
   - Criptomoedas (15%) oferecem potencial de alta rentabilidade

2. MONITORAMENTO:
   - Revisar alocação trimestralmente conforme estratégia
   - Acompanhar performance vs benchmarks
   - Rebalancear quando necessário

3. GESTÃO DE RISCO:
   - Sharpe Ratio de {dados['metricas_risco']['sharpe_ratio']:.2f} indica boa relação risco-retorno
   - Volatilidade de {dados['metricas_risco']['volatilidade']:.2%} está dentro do esperado
   - Máximo drawdown de {dados['metricas_avancadas']['max_drawdown']:.2%} é aceitável

4. LIQUIDEZ:
   - Ações e criptomoedas oferecem alta liquidez
   - Fundos podem ter prazo de resgate
   - Renda fixa pode ter vencimento específico

{'='*80}

⚠️ DISCLAIMER
{'-'*40}

Este relatório é gerado automaticamente e não constitui recomendação de investimento.
Consulte sempre um profissional qualificado antes de tomar decisões de investimento.
Os valores e rentabilidades podem variar e não garantem resultados futuros.

{'='*80}

📄 Relatório gerado automaticamente pelo Sistema de Análise Financeira
🕐 {datetime.now().strftime("%d/%m/%Y às %H:%M:%S")}
{'='*80}
"""
    
    return relatorio

def main():
    """Função principal"""
    # Procurar o relatório mais recente
    arquivos_json = [f for f in os.listdir('.') if f.startswith('relatorio_carteira_ideal_') and f.endswith('.json')]
    
    if not arquivos_json:
        print("❌ Nenhum relatório JSON encontrado!")
        return
    
    # Pegar o mais recente
    arquivo_mais_recente = max(arquivos_json)
    print(f"📄 Processando: {arquivo_mais_recente}")
    
    # Gerar relatório TXT
    relatorio_txt = gerar_relatorio_txt(arquivo_mais_recente)
    
    # Salvar arquivo TXT
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"relatorio_carteira_ideal_{timestamp}.txt"
    
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        f.write(relatorio_txt)
    
    print(f"✅ Relatório TXT gerado: {nome_arquivo}")
    print(f"📊 Tamanho: {len(relatorio_txt)} caracteres")

if __name__ == "__main__":
    main() 