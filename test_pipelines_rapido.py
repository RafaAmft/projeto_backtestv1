#!/usr/bin/env python3
"""
Teste Rápido de Validação dos Pipelines (sem web scraping)
==========================================================

Versão rápida que pula o teste de fundos para resultados imediatos.
"""

import sys
import os

# Adicionar ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import do validador principal
from test_pipelines_validacao import ValidadorPipelines, QualidadeDados
import json
from datetime import datetime
import numpy as np

def main():
    """Função principal - versão rápida"""
    print()
    print("=" * 70)
    print("VALIDACAO RAPIDA DOS PIPELINES (sem web scraping)")
    print("=" * 70)
    print()
    
    validador = ValidadorPipelines()
    
    # Executar apenas testes rápidos
    print("[*] Executando validacoes rapidas...\n")
    
    # 1. Pipeline de Índices de Mercado
    print("[1] Validando Pipeline de Indices de Mercado...")
    resultado_mercado = validador._validar_pipeline_mercado()
    validador.resultados.append(resultado_mercado)
    validador._imprimir_resultado(resultado_mercado)
    print()
    
    # 2. Pipeline de Criptomoedas
    print("[2] Validando Pipeline de Criptomoedas...")
    resultado_crypto = validador._validar_pipeline_crypto()
    validador.resultados.append(resultado_crypto)
    validador._imprimir_resultado(resultado_crypto)
    print()
    
    # 3. Pipeline de Ações
    print("[3] Validando Pipeline de Acoes...")
    resultado_acoes = validador._validar_pipeline_acoes()
    validador.resultados.append(resultado_acoes)
    validador._imprimir_resultado(resultado_acoes)
    print()
    
    # PULAR Pipeline de Fundos (demora muito)
    print("[4] Pipeline de Fundos - PULADO (muito lento)")
    print("   Use test_pipelines_validacao.py para teste completo")
    print()
    
    # 5. Pipeline de Câmbio
    print("[5] Validando Pipeline de Cambio...")
    resultado_cambio = validador._validar_pipeline_cambio()
    validador.resultados.append(resultado_cambio)
    validador._imprimir_resultado(resultado_cambio)
    print()
    
    # 6. Pipeline de Dados Históricos
    print("[6] Validando Pipeline de Dados Historicos...")
    resultado_historico = validador._validar_pipeline_historico()
    validador.resultados.append(resultado_historico)
    validador._imprimir_resultado(resultado_historico)
    print()
    
    # Gerar relatório consolidado
    print("\n" + "="*70)
    print("RELATORIO CONSOLIDADO (RAPIDO)")
    print("="*70)
    print()
    
    total_pipelines = len(validador.resultados)
    pipelines_funcionais = sum(1 for r in validador.resultados if r.qualidade != QualidadeDados.FALHOU)
    pipelines_com_dados_reais = sum(1 for r in validador.resultados if r.dados_reais)
    pipelines_excelentes = sum(1 for r in validador.resultados if r.qualidade == QualidadeDados.EXCELENTE)
    pipelines_simulados = sum(1 for r in validador.resultados if r.qualidade == QualidadeDados.SIMULADO)
    
    print(f"[T] Total de Pipelines Testados: {total_pipelines} (pulado 1)")
    print(f"[OK] Pipelines Funcionais: {pipelines_funcionais}/{total_pipelines}")
    print(f"[R] Pipelines com Dados REAIS: {pipelines_com_dados_reais}/{total_pipelines}")
    print(f"[E] Pipelines Excelentes: {pipelines_excelentes}/{total_pipelines}")
    print(f"[S] Pipelines com Dados Simulados: {pipelines_simulados}/{total_pipelines}")
    print()
    
    # Tabela resumo
    print("RESUMO POR PIPELINE:")
    print("-" * 70)
    print(f"{'Pipeline':<25} {'Qualidade':<12} {'Reais':<8} {'Completo':<10}")
    print("-" * 70)
    
    for resultado in validador.resultados:
        nome = resultado.pipeline.replace("Pipeline ", "")
        qualidade = resultado.qualidade.value[:10]
        reais = "SIM" if resultado.dados_reais else "NAO"
        completude = f"{resultado.completude:.1%}"
        
        print(f"{nome:<25} {qualidade:<12} {reais:<8} {completude:<10}")
    
    print("-" * 70)
    print()
    
    # Avaliação final
    print("AVALIACAO FINAL:")
    print("-" * 70)
    
    if pipelines_simulados > 0:
        print(f"[X] CRITICO: {pipelines_simulados} pipeline(s) usando dados SIMULADOS!")
        print("   Os calculos da carteira NAO sao confiaveis.")
        print()
    
    if pipelines_com_dados_reais == total_pipelines:
        print("[OK] EXCELENTE: Todos os pipelines testados usam dados REAIS!")
    elif pipelines_com_dados_reais >= total_pipelines * 0.7:
        print("[+] BOM: Maioria dos pipelines usa dados reais.")
    else:
        print("[-] RUIM: Muitos pipelines NAO usam dados reais!")
    
    print()
    
    completude_media = sum(r.completude for r in validador.resultados) / len(validador.resultados)
    print(f"[C] Completude Media: {completude_media:.1%}")
    
    latencia_media = sum(r.latencia_ms for r in validador.resultados) / len(validador.resultados)
    print(f"[T] Latencia Media: {latencia_media:.0f}ms")
    
    print()
    print("="*70)
    
    # Salvar relatório JSON
    relatorio = {
        'timestamp': datetime.now().isoformat(),
        'versao': '1.0.0-rapido',
        'nota': 'Pipeline de fundos foi pulado nesta versao rapida',
        'estatisticas': {
            'total_pipelines': total_pipelines,
            'pipelines_funcionais': pipelines_funcionais,
            'pipelines_com_dados_reais': pipelines_com_dados_reais,
            'pipelines_excelentes': pipelines_excelentes,
            'pipelines_simulados': pipelines_simulados,
            'completude_media': completude_media,
            'latencia_media_ms': latencia_media
        },
        'resultados': [
            {
                'pipeline': r.pipeline,
                'qualidade': r.qualidade.value,
                'dados_reais': bool(r.dados_reais),
                'dados_atualizados': bool(r.dados_atualizados),
                'completude': float(r.completude),
                'latencia_ms': float(r.latencia_ms),
                'erros': r.erros,
                'avisos': r.avisos,
                'metricas': {k: float(v) if isinstance(v, (int, float, np.number)) else v for k, v in r.metricas.items()},
                'timestamp': r.timestamp
            } for r in validador.resultados
        ]
    }
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"relatorio_validacao_rapido_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False)
    
    print(f"[SAVE] Relatorio salvo em: {filename}")
    print()
    
    # Conclusão
    print("CONCLUSAO:")
    print("="*70)
    
    if pipelines_simulados == 0 and pipelines_com_dados_reais == total_pipelines:
        print("[OK] Pipelines testados estao usando dados REAIS!")
        print("   Execute test_pipelines_validacao.py para teste completo.")
        return 0
    elif pipelines_simulados > 0:
        print("[X] ATENCAO: Foram detectados pipelines com DADOS SIMULADOS!")
        print(f"   {pipelines_simulados}/{total_pipelines} pipeline(s) com problemas.")
        print()
        print("RECOMENDACAO:")
        print("   1. Verifique as configuracoes das APIs")
        print("   2. Confirme que as credenciais estao corretas no .env")
        print("   3. Teste conectividade com as APIs externas")
        print("   4. Revise o codigo de test_carteira_ideal.py")
        return 1
    else:
        print("[~] PARCIAL: Alguns pipelines com problemas.")
        print(f"   {pipelines_com_dados_reais}/{total_pipelines} pipeline(s) com dados reais.")
        return 1


if __name__ == "__main__":
    # Forçar UTF-8 no Windows
    import sys
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n[X] Validacao interrompida pelo usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[X] Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

