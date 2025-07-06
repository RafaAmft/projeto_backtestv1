#!/usr/bin/env python3
"""
Teste de Comparação: Fundo CAIXA INDEXA OURO
============================================

Este script compara os dados de rentabilidade do fundo CAIXA INDEXA OURO
entre o Mais Retorno e os dados brutos da CVM.
"""

import pandas as pd
import numpy as np
import requests
from datetime import datetime
import json
import re
from typing import Dict, List, Optional
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FundoCaixaOuroTester:
    """
    Testador específico para o fundo CAIXA INDEXA OURO
    """
    
    def __init__(self):
        self.cnpj_fundo = "16916060000199"  # CNPJ do CAIXA INDEXA OURO
        self.nome_fundo = "CAIXA INDEXA OURO FI FINANCEIRO MULTIMERCADO LP RL"
        self.url_mais_retorno = "https://maisretorno.com/fundo/caixa-indexa-ouro-fi-financeiro-multimercado-lp-rl"
        
        # Dados carregados
        self.dados_cvm = {}
        self.dados_mais_retorno = {}
        
    def carregar_dados_cvm(self) -> Dict:
        """
        Carrega dados do fundo nos dados brutos da CVM
        """
        logger.info(f"Carregando dados CVM para CNPJ: {self.cnpj_fundo}")
        
        dados_fundo = {
            'rentab_ano': None,
            'rentab_mes': None,
            'dados_diarios': None,
            'cadastral': None
        }
        
        try:
            # 1. Dados de rentabilidade anual
            caminho_ano = "CNPJ VALIDADO/brutos/Lamina_fi_rentab/lamina_fi_rentab_ano_202505.csv"
            df_ano = pd.read_csv(caminho_ano, sep=";", encoding="latin1", dtype=str)
            df_ano.columns = df_ano.columns.str.strip().str.upper()
            df_ano['CNPJ_FUNDO'] = df_ano['CNPJ_FUNDO_CLASSE'].str.replace(r'\D', '', regex=True)
            
            # Filtrar pelo CNPJ
            dados_ano = df_ano[df_ano['CNPJ_FUNDO'] == self.cnpj_fundo].copy()
            if not dados_ano.empty:
                dados_ano['ANO_RENTAB'] = pd.to_numeric(dados_ano['ANO_RENTAB'], errors='coerce')
                dados_ano['PR_RENTAB_ANO'] = pd.to_numeric(
                    dados_ano['PR_RENTAB_ANO'].str.replace(',', '.'), errors='coerce'
                ) / 100
                dados_fundo['rentab_ano'] = dados_ano
                logger.info(f"✅ Dados anuais CVM: {len(dados_ano)} registros")
            
            # 2. Dados de rentabilidade mensal
            caminho_mes = "CNPJ VALIDADO/brutos/Lamina_fi_rentab/lamina_fi_rentab_mes_202505.csv"
            df_mes = pd.read_csv(caminho_mes, sep=";", encoding="latin1", dtype=str)
            df_mes.columns = df_mes.columns.str.strip().str.upper()
            df_mes['CNPJ_FUNDO'] = df_mes['CNPJ_FUNDO_CLASSE'].str.replace(r'\D', '', regex=True)
            
            # Filtrar pelo CNPJ
            dados_mes = df_mes[df_mes['CNPJ_FUNDO'] == self.cnpj_fundo].copy()
            if not dados_mes.empty:
                dados_mes['DT_COMPTC'] = pd.to_datetime(dados_mes['DT_COMPTC'], errors='coerce')
                dados_mes['MES_RENTAB'] = pd.to_numeric(dados_mes['MES_RENTAB'], errors='coerce')
                dados_mes['PR_RENTAB_MES'] = pd.to_numeric(
                    dados_mes['PR_RENTAB_MES'].str.replace(',', '.'), errors='coerce'
                ) / 100
                dados_fundo['rentab_mes'] = dados_mes
                logger.info(f"✅ Dados mensais CVM: {len(dados_mes)} registros")
            
            # 3. Dados diários (últimos 12 meses)
            caminho_diario = "CNPJ VALIDADO/brutos/inf_diario_padronizado/df_diario_completo.parquet"
            df_diario = pd.read_parquet(caminho_diario)
            
            # Filtrar pelo CNPJ e últimos 12 meses
            dados_diario = df_diario[df_diario['CNPJ_FUNDO'] == self.cnpj_fundo].copy()
            if not dados_diario.empty:
                dados_diario['DT_COMPTC'] = pd.to_datetime(dados_diario['DT_COMPTC'])
                dados_diario = dados_diario.sort_values('DT_COMPTC')
                
                # Últimos 12 meses
                data_limite = dados_diario['DT_COMPTC'].max() - pd.DateOffset(months=12)
                dados_diario = dados_diario[dados_diario['DT_COMPTC'] >= data_limite]
                
                dados_fundo['dados_diarios'] = dados_diario
                logger.info(f"✅ Dados diários CVM: {len(dados_diario)} registros")
            
            # 4. Dados cadastrais
            caminho_cadastral = "CNPJ VALIDADO/brutos/cad_fi_hist_classe.csv"
            df_cad = pd.read_csv(caminho_cadastral, sep=";", encoding="latin1", dtype=str)
            df_cad.columns = df_cad.columns.str.strip().str.upper()
            df_cad['CNPJ_FUNDO'] = df_cad['CNPJ_FUNDO'].str.replace(r'\D', '', regex=True)
            
            dados_cad = df_cad[df_cad['CNPJ_FUNDO'] == self.cnpj_fundo].copy()
            if not dados_cad.empty:
                dados_fundo['cadastral'] = dados_cad
                logger.info(f"✅ Dados cadastrais CVM: {len(dados_cad)} registros")
            
            self.dados_cvm = dados_fundo
            return dados_fundo
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar dados CVM: {e}")
            return {}
    
    def extrair_dados_mais_retorno(self) -> Dict:
        """
        Extrai dados do Mais Retorno (simulação - em produção seria via API ou web scraping)
        """
        logger.info("Extraindo dados do Mais Retorno...")
        
        # Dados simulados baseados na página do Mais Retorno
        # Em produção, isso seria feito via API ou web scraping
        dados_mr = {
            'nome': 'CAIXA INDEXA OURO FI FINANCEIRO MULTIMERCADO LP RL',
            'cnpj': '16.916.060/0001-99',
            'administrador': 'CAIXA ECONOMICA FEDERAL',
            'gestor': 'CAIXA',
            'classe': 'Multimercado',
            'data_inicial': '15/02/2013',
            'rentabilidades': {
                '2024': {
                    'jan': 0.0234,  # 2.34%
                    'fev': 0.0187,  # 1.87%
                    'mar': 0.0312,  # 3.12%
                    'abr': 0.0156,  # 1.56%
                    'mai': 0.0289,  # 2.89%
                    'jun': 0.0221,  # 2.21%
                    'jul': 0.0198,  # 1.98%
                    'ago': 0.0245,  # 2.45%
                    'set': 0.0167,  # 1.67%
                    'out': 0.0298,  # 2.98%
                    'nov': 0.0213,  # 2.13%
                    'dez': 0.0256,  # 2.56%
                    'ano': 0.3123   # 31.23%
                },
                '2023': {
                    'ano': 0.2845   # 28.45%
                },
                '2022': {
                    'ano': 0.1567   # 15.67%
                },
                '2021': {
                    'ano': 0.2234   # 22.34%
                }
            }
        }
        
        self.dados_mais_retorno = dados_mr
        logger.info("✅ Dados Mais Retorno extraídos (simulados)")
        return dados_mr
    
    def calcular_rentabilidades_cvm(self) -> Dict:
        """
        Calcula rentabilidades a partir dos dados CVM
        """
        logger.info("Calculando rentabilidades CVM...")
        
        resultados = {
            'rentab_anual': {},
            'rentab_mensal': {},
            'rentab_acumulada': {}
        }
        
        # 1. Rentabilidade anual
        if self.dados_cvm.get('rentab_ano') is not None:
            df_ano = self.dados_cvm['rentab_ano']
            for _, row in df_ano.iterrows():
                ano = int(row['ANO_RENTAB'])
                rentab = row['PR_RENTAB_ANO']
                resultados['rentab_anual'][ano] = rentab
        
        # 2. Rentabilidade mensal (2024)
        if self.dados_cvm.get('rentab_mes') is not None:
            df_mes = self.dados_cvm['rentab_mes']
            df_2024 = df_mes[df_mes['DT_COMPTC'].dt.year == 2024]
            
            for _, row in df_2024.iterrows():
                mes = int(row['MES_RENTAB'])
                rentab = row['PR_RENTAB_MES']
                resultados['rentab_mensal'][mes] = rentab
            
            # Calcular acumulada 2024
            if resultados['rentab_mensal']:
                rentabs_mensais = list(resultados['rentab_mensal'].values())
                rentab_acumulada = (1 + pd.Series(rentabs_mensais)).prod() - 1
                resultados['rentab_acumulada']['2024'] = rentab_acumulada
        
        # 3. Calcular rentabilidade diária (últimos 12 meses)
        if self.dados_cvm.get('dados_diarios') is not None:
            df_diario = self.dados_cvm['dados_diarios']
            if len(df_diario) > 1:
                # Calcular rentabilidade diária
                df_diario['VL_QUOTA'] = pd.to_numeric(df_diario['VL_QUOTA'], errors='coerce')
                df_diario = df_diario.sort_values('DT_COMPTC')
                
                # Calcular retornos diários
                df_diario['RET_DIARIO'] = df_diario['VL_QUOTA'].pct_change()
                
                # Rentabilidade dos últimos 12 meses
                rentab_12m = (1 + df_diario['RET_DIARIO'].dropna()).prod() - 1
                resultados['rentab_acumulada']['ultimos_12m'] = rentab_12m
        
        return resultados
    
    def comparar_rentabilidades(self) -> Dict:
        """
        Compara rentabilidades entre CVM e Mais Retorno
        """
        logger.info("Comparando rentabilidades...")
        
        rentab_cvm = self.calcular_rentabilidades_cvm()
        rentab_mr = self.dados_mais_retorno.get('rentabilidades', {})
        
        comparacao = {
            'anos_comuns': [],
            'diferencas': {},
            'resumo': {}
        }
        
        # Comparar anos
        anos_cvm = set(rentab_cvm['rentab_anual'].keys())
        anos_mr = set(rentab_mr.keys())
        anos_comuns = anos_cvm.intersection(anos_mr)
        
        for ano in anos_comuns:
            rentab_cvm_ano = rentab_cvm['rentab_anual'].get(ano, 0)
            rentab_mr_ano = rentab_mr[ano].get('ano', 0)
            
            diferenca = rentab_cvm_ano - rentab_mr_ano
            diferenca_pct = (diferenca / rentab_mr_ano) * 100 if rentab_mr_ano != 0 else 0
            
            comparacao['diferencas'][ano] = {
                'cvm': rentab_cvm_ano,
                'mais_retorno': rentab_mr_ano,
                'diferenca_abs': diferenca,
                'diferenca_pct': diferenca_pct
            }
        
        # Resumo
        if comparacao['diferencas']:
            diferencas_pct = [v['diferenca_pct'] for v in comparacao['diferencas'].values()]
            comparacao['resumo'] = {
                'media_diferenca_pct': np.mean(diferencas_pct),
                'max_diferenca_pct': max(diferencas_pct),
                'min_diferenca_pct': min(diferencas_pct),
                'total_anos_comparados': len(anos_comuns)
            }
        
        return comparacao
    
    def gerar_relatorio_comparativo(self) -> Dict:
        """
        Gera relatório completo de comparação
        """
        logger.info("Gerando relatório comparativo...")
        
        comparacao = self.comparar_rentabilidades()
        
        relatorio = {
            'timestamp': datetime.now().isoformat(),
            'fundo': {
                'nome': self.nome_fundo,
                'cnpj': self.cnpj_fundo,
                'url_mais_retorno': self.url_mais_retorno
            },
            'dados_cvm': {
                'rentab_anual': self.calcular_rentabilidades_cvm()['rentab_anual'],
                'rentab_mensal_2024': self.calcular_rentabilidades_cvm()['rentab_mensal'],
                'rentab_acumulada': self.calcular_rentabilidades_cvm()['rentab_acumulada']
            },
            'dados_mais_retorno': self.dados_mais_retorno,
            'comparacao': comparacao,
            'conclusoes': []
        }
        
        # Gerar conclusões
        if comparacao['resumo']:
            media_diff = comparacao['resumo']['media_diferenca_pct']
            if abs(media_diff) < 1:
                relatorio['conclusoes'].append("✅ Dados muito consistentes entre as fontes")
            elif abs(media_diff) < 5:
                relatorio['conclusoes'].append("⚠️ Pequenas diferenças detectadas")
            else:
                relatorio['conclusoes'].append("🚨 Diferenças significativas encontradas")
        
        return relatorio
    
    def executar_teste_completo(self):
        """
        Executa o teste completo
        """
        print(f"🧪 TESTE: {self.nome_fundo}")
        print(f"📋 CNPJ: {self.cnpj_fundo}")
        print("=" * 60)
        
        # 1. Carregar dados CVM
        self.carregar_dados_cvm()
        
        # 2. Extrair dados Mais Retorno
        self.extrair_dados_mais_retorno()
        
        # 3. Gerar relatório
        relatorio = self.gerar_relatorio_comparativo()
        
        # 4. Salvar relatório
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        caminho_relatorio = f"teste_caixa_ouro_{timestamp}.json"
        
        with open(caminho_relatorio, 'w', encoding='utf-8') as f:
            json.dump(relatorio, f, indent=2, ensure_ascii=False, default=str)
        
        # 5. Mostrar resumo
        print("\n📊 RESUMO DO TESTE:")
        print(f"📁 Dados CVM carregados: {len([k for k, v in self.dados_cvm.items() if v is not None])} fontes")
        print(f"🌐 Dados Mais Retorno: {'Sim' if self.dados_mais_retorno else 'Não'}")
        
        if relatorio['comparacao']['resumo']:
            resumo = relatorio['comparacao']['resumo']
            print(f"📈 Anos comparados: {resumo['total_anos_comparados']}")
            print(f"📊 Diferença média: {resumo['media_diferenca_pct']:.2f}%")
            print(f"📊 Diferença máxima: {resumo['max_diferenca_pct']:.2f}%")
        
        print(f"\n📄 Relatório salvo em: {caminho_relatorio}")
        
        # 6. Mostrar conclusões
        print("\n🎯 CONCLUSÕES:")
        for conclusao in relatorio['conclusoes']:
            print(f"  {conclusao}")
        
        return relatorio

def main():
    """
    Função principal
    """
    tester = FundoCaixaOuroTester()
    relatorio = tester.executar_teste_completo()
    
    print("\n✅ Teste concluído!")

if __name__ == "__main__":
    main() 