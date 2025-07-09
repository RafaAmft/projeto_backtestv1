#!/usr/bin/env python3
"""
Sistema de Processamento e Validação de Dados Brutos da CVM
==========================================================

Este módulo processa os dados brutos baixados da CVM (não uma API REST), identifica inconsistências
e gera dados limpos e validados para análise local.
"""

import pandas as pd
import numpy as np
import os
import warnings
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
warnings.filterwarnings('ignore')

class CVMDataProcessor:
    """
    Processador de dados brutos da CVM com validação completa
    """
    
    def __init__(self, base_path: str = "CNPJ VALIDADO"):
        self.base_path = base_path
        self.brutos_path = os.path.join(base_path, "brutos")
        self.derivados_path = os.path.join(base_path, "derivados")
        
        # Dados carregados
        self.dados_brutos = {}
        self.dados_processados = {}
        self.inconsistencias = []
        self.fundos_problematicos = set()
        
        # Configurações de validação
        self.config_validacao = {
            'rentabilidade_min': -0.99,  # -99%
            'rentabilidade_max': 10.0,   # 1000%
            'duracao_min_dias': 1,
            'duracao_max_dias': 31,
            'valor_min': 0.01,
            'diferenca_max_rentab': 0.001,  # 0.1%
            'meses_min_fundo': 3
        }
        
        # Níveis de problema
        self.NIVEIS_PROBLEMA = {
            'CRITICO': 'Dados completamente inválidos',
            'ALTO': 'Diferenças significativas (>10%)',
            'MEDIO': 'Inconsistências moderadas (5-10%)',
            'BAIXO': 'Pequenas inconsistências (<5%)',
            'CONFIAVEL': 'Dados consistentes'
        }
        
        logger.info("CVMDataProcessor inicializado")
    
    def carregar_dados_brutos(self) -> Dict[str, pd.DataFrame]:
        """
        Carrega todos os dados brutos da CVM
        """
        logger.info("Carregando dados brutos da CVM...")
        
        dados = {}
        
        try:
            # 1. Dados de rentabilidade anual
            caminho_ano = os.path.join(self.brutos_path, "Lamina_fi_rentab", "lamina_fi_rentab_ano_202505.csv")
            if os.path.exists(caminho_ano):
                dados['rentab_ano'] = pd.read_csv(caminho_ano, sep=";", encoding="latin1", dtype=str)
                logger.info(f"✅ Rentabilidade anual carregada: {dados['rentab_ano'].shape}")
            
            # 2. Dados de rentabilidade mensal
            caminho_mes = os.path.join(self.brutos_path, "Lamina_fi_rentab", "lamina_fi_rentab_mes_202505.csv")
            if os.path.exists(caminho_mes):
                dados['rentab_mes'] = pd.read_csv(caminho_mes, sep=";", encoding="latin1", dtype=str)
                logger.info(f"✅ Rentabilidade mensal carregada: {dados['rentab_mes'].shape}")
            
            # 3. Dados diários (último arquivo disponível)
            caminho_diario = os.path.join(self.brutos_path, "inf_diario_padronizado", "df_diario_completo.parquet")
            if os.path.exists(caminho_diario):
                dados['diario'] = pd.read_parquet(caminho_diario)
                logger.info(f"✅ Dados diários carregados: {dados['diario'].shape}")
            
            # 4. Dados cadastrais importantes
            cadastrais = ['cad_fi_hist_classe', 'cad_fi_hist_rentab', 'cad_fi_hist_sit']
            for cad in cadastrais:
                caminho_cad = os.path.join(self.brutos_path, f"{cad}.csv")
                if os.path.exists(caminho_cad):
                    dados[cad] = pd.read_csv(caminho_cad, sep=";", encoding="latin1", dtype=str)
                    logger.info(f"✅ {cad} carregado: {dados[cad].shape}")
            
            self.dados_brutos = dados
            logger.info(f"✅ Total de {len(dados)} arquivos carregados")
            return dados
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar dados brutos: {e}")
            return {}
    
    def limpar_e_preparar_dados(self) -> Dict[str, pd.DataFrame]:
        """
        Limpa e prepara os dados para análise
        """
        logger.info("Limpando e preparando dados...")
        
        dados_limpos = {}
        
        # 1. Limpar dados de rentabilidade anual
        if 'rentab_ano' in self.dados_brutos:
            df_ano = self.dados_brutos['rentab_ano'].copy()
            df_ano.columns = df_ano.columns.str.strip().str.upper()
            
            # Limpar CNPJ
            df_ano['CNPJ_FUNDO'] = df_ano['CNPJ_FUNDO_CLASSE'].str.replace(r'\D', '', regex=True)
            
            # Converter tipos
            df_ano['ANO_RENTAB'] = pd.to_numeric(df_ano['ANO_RENTAB'], errors='coerce')
            df_ano['PR_RENTAB_ANO'] = pd.to_numeric(
                df_ano['PR_RENTAB_ANO'].str.replace(',', '.'), errors='coerce'
            ) / 100
            
            # Filtrar dados válidos
            df_ano = df_ano[
                (df_ano['CNPJ_FUNDO'].notna()) &
                (df_ano['ANO_RENTAB'].between(2021, 2024)) &
                (df_ano['PR_RENTAB_ANO'].notna())
            ]
            
            dados_limpos['rentab_ano'] = df_ano
            logger.info(f"✅ Rentabilidade anual limpa: {df_ano.shape}")
        
        # 2. Limpar dados de rentabilidade mensal
        if 'rentab_mes' in self.dados_brutos:
            df_mes = self.dados_brutos['rentab_mes'].copy()
            df_mes.columns = df_mes.columns.str.strip().str.upper()
            
            # Limpar CNPJ
            df_mes['CNPJ_FUNDO'] = df_mes['CNPJ_FUNDO_CLASSE'].str.replace(r'\D', '', regex=True)
            
            # Converter tipos
            df_mes['DT_COMPTC'] = pd.to_datetime(df_mes['DT_COMPTC'], errors='coerce')
            df_mes['MES_RENTAB'] = pd.to_numeric(df_mes['MES_RENTAB'], errors='coerce')
            df_mes['PR_RENTAB_MES'] = pd.to_numeric(
                df_mes['PR_RENTAB_MES'].str.replace(',', '.'), errors='coerce'
            ) / 100
            
            # Filtrar dados válidos
            df_mes = df_mes[
                (df_mes['CNPJ_FUNDO'].notna()) &
                (df_mes['DT_COMPTC'].notna()) &
                (df_mes['MES_RENTAB'].between(1, 12)) &
                (df_mes['PR_RENTAB_MES'].notna())
            ]
            
            dados_limpos['rentab_mes'] = df_mes
            logger.info(f"✅ Rentabilidade mensal limpa: {df_mes.shape}")
        
        # 3. Limpar dados diários
        if 'diario' in self.dados_brutos:
            df_diario = self.dados_brutos['diario'].copy()
            
            # Converter tipos
            df_diario['DT_COMPTC'] = pd.to_datetime(df_diario['DT_COMPTC'], errors='coerce')
            df_diario['VL_QUOTA'] = pd.to_numeric(df_diario['VL_QUOTA'], errors='coerce')
            df_diario['VL_PATRIM_LIQ'] = pd.to_numeric(df_diario['VL_PATRIM_LIQ'], errors='coerce')
            
            # Filtrar dados válidos
            df_diario = df_diario[
                (df_diario['DT_COMPTC'].notna()) &
                (df_diario['VL_QUOTA'] > 0) &
                (df_diario['VL_PATRIM_LIQ'] > 0)
            ]
            
            dados_limpos['diario'] = df_diario
            logger.info(f"✅ Dados diários limpos: {df_diario.shape}")
        
        self.dados_processados = dados_limpos
        return dados_limpos
    
    def identificar_inconsistencias_rentabilidade(self) -> List[Dict]:
        """
        Identifica inconsistências nos dados de rentabilidade
        """
        logger.info("Identificando inconsistências de rentabilidade...")
        
        inconsistencias = []
        
        # 1. Inconsistências em rentabilidade anual
        if 'rentab_ano' in self.dados_processados:
            df_ano = self.dados_processados['rentab_ano']
            
            # Valores extremos
            extremos = df_ano[
                (df_ano['PR_RENTAB_ANO'] < self.config_validacao['rentabilidade_min']) |
                (df_ano['PR_RENTAB_ANO'] > self.config_validacao['rentabilidade_max'])
            ]
            
            for _, row in extremos.iterrows():
                inconsistencias.append({
                    'tipo': 'RENTABILIDADE_EXTREMA_ANO',
                    'cnpj': row['CNPJ_FUNDO'],
                    'ano': row['ANO_RENTAB'],
                    'valor': row['PR_RENTAB_ANO'],
                    'nivel': 'ALTO',
                    'descricao': f"Rentabilidade anual {row['PR_RENTAB_ANO']:.2%} fora do range esperado"
                })
        
        # 2. Inconsistências em rentabilidade mensal
        if 'rentab_mes' in self.dados_processados:
            df_mes = self.dados_processados['rentab_mes']
            
            # Valores extremos
            extremos = df_mes[
                (df_mes['PR_RENTAB_MES'] < self.config_validacao['rentabilidade_min']) |
                (df_mes['PR_RENTAB_MES'] > self.config_validacao['rentabilidade_max'])
            ]
            
            for _, row in extremos.iterrows():
                inconsistencias.append({
                    'tipo': 'RENTABILIDADE_EXTREMA_MES',
                    'cnpj': row['CNPJ_FUNDO'],
                    'data': row['DT_COMPTC'],
                    'mes': row['MES_RENTAB'],
                    'valor': row['PR_RENTAB_MES'],
                    'nivel': 'ALTO',
                    'descricao': f"Rentabilidade mensal {row['PR_RENTAB_MES']:.2%} fora do range esperado"
                })
        
        # 3. Inconsistências entre diferentes fontes
        if 'rentab_ano' in self.dados_processados and 'rentab_mes' in self.dados_processados:
            inconsistencias.extend(self._comparar_fontes_rentabilidade())
        
        self.inconsistencias.extend(inconsistencias)
        logger.info(f"✅ {len(inconsistencias)} inconsistências identificadas")
        return inconsistencias
    
    def _comparar_fontes_rentabilidade(self) -> List[Dict]:
        """
        Compara rentabilidades entre diferentes fontes
        """
        inconsistencias = []
        
        df_ano = self.dados_processados['rentab_ano']
        df_mes = self.dados_processados['rentab_mes']
        
        # Agrupar por CNPJ e ano
        rentab_ano_agrupada = df_ano.groupby(['CNPJ_FUNDO', 'ANO_RENTAB'])['PR_RENTAB_ANO'].first().reset_index()
        
        # Calcular rentabilidade mensal acumulada por ano
        df_mes['ANO_RENTAB'] = df_mes['DT_COMPTC'].dt.year
        rentab_mes_acumulada = df_mes.groupby(['CNPJ_FUNDO', 'ANO_RENTAB'])['PR_RENTAB_MES'].apply(
            lambda x: (1 + x).prod() - 1
        ).reset_index()
        
        # Comparar
        comparacao = rentab_ano_agrupada.merge(
            rentab_mes_acumulada, 
            on=['CNPJ_FUNDO', 'ANO_RENTAB'], 
            how='inner',
            suffixes=('_ano', '_mes_calc')
        )
        
        # Calcular diferença
        comparacao['DIFERENCA'] = comparacao['PR_RENTAB_ANO'] - comparacao['PR_RENTAB_MES']
        comparacao['DIFERENCA_ABS'] = abs(comparacao['DIFERENCA'])
        
        # Identificar diferenças significativas
        diferencas_significativas = comparacao[
            comparacao['DIFERENCA_ABS'] > self.config_validacao['diferenca_max_rentab']
        ]
        
        for _, row in diferencas_significativas.iterrows():
            inconsistencias.append({
                'tipo': 'DIFERENCA_FONTES_RENTABILIDADE',
                'cnpj': row['CNPJ_FUNDO'],
                'ano': row['ANO_RENTAB'],
                'rentab_ano': row['PR_RENTAB_ANO'],
                'rentab_mes_calc': row['PR_RENTAB_MES'],
                'diferenca': row['DIFERENCA'],
                'nivel': 'MEDIO' if row['DIFERENCA_ABS'] < 0.1 else 'ALTO',
                'descricao': f"Diferença de {row['DIFERENCA']:.2%} entre fontes"
            })
        
        return inconsistencias
    
    def identificar_fundos_problematicos(self) -> Dict[str, List[str]]:
        """
        Identifica fundos com problemas
        """
        logger.info("Identificando fundos problemáticos...")
        
        fundos_problematicos = {
            'poucos_dados': [],
            'dados_inconsistentes': [],
            'rentabilidades_extremas': [],
            'lacunas_temporais': []
        }
        
        # 1. Fundos com poucos dados
        if 'rentab_mes' in self.dados_processados:
            df_mes = self.dados_processados['rentab_mes']
            contagem_por_fundo = df_mes.groupby('CNPJ_FUNDO').size()
            
            fundos_poucos_dados = contagem_por_fundo[
                contagem_por_fundo < self.config_validacao['meses_min_fundo']
            ].index.tolist()
            
            fundos_problematicos['poucos_dados'] = fundos_poucos_dados
        
        # 2. Fundos com rentabilidades extremas
        if self.inconsistencias:
            cnpjs_extremos = set()
            for inc in self.inconsistencias:
                if 'RENTABILIDADE_EXTREMA' in inc['tipo']:
                    cnpjs_extremos.add(inc['cnpj'])
            
            fundos_problematicos['rentabilidades_extremas'] = list(cnpjs_extremos)
        
        # 3. Fundos com dados inconsistentes
        if 'rentab_mes' in self.dados_processados:
            df_mes = self.dados_processados['rentab_mes']
            
            # Verificar lacunas temporais
            for cnpj in df_mes['CNPJ_FUNDO'].unique():
                dados_fundo = df_mes[df_mes['CNPJ_FUNDO'] == cnpj].sort_values('DT_COMPTC')
                
                if len(dados_fundo) > 1:
                    # Calcular diferenças entre datas consecutivas em meses
                    datas = dados_fundo['DT_COMPTC'].dt.to_period('M')
                    lacunas = datas.diff().dropna()
                    # Converter para número de meses
                    lacunas_meses = lacunas.apply(lambda x: x.n if pd.notnull(x) else 0)
                    # Se há lacunas maiores que 2 meses
                    if (lacunas_meses > 2).any():
                        fundos_problematicos['lacunas_temporais'].append(cnpj)
        
        self.fundos_problematicos = set()
        for lista in fundos_problematicos.values():
            self.fundos_problematicos.update(lista)
        
        logger.info(f"✅ {len(self.fundos_problematicos)} fundos problemáticos identificados")
        return fundos_problematicos
    
    def gerar_relatorio_inconsistencias(self) -> Dict[str, Any]:
        """
        Gera relatório completo de inconsistências
        """
        logger.info("Gerando relatório de inconsistências...")
        
        relatorio = {
            'timestamp': datetime.now().isoformat(),
            'resumo': {
                'total_inconsistencias': len(self.inconsistencias),
                'total_fundos_problematicos': len(self.fundos_problematicos),
                'dados_processados': {k: v.shape for k, v in self.dados_processados.items()}
            },
            'inconsistencias_por_tipo': {},
            'inconsistencias_por_nivel': {},
            'fundos_problematicos': self.identificar_fundos_problematicos(),
            'recomendacoes': []
        }
        
        # Agrupar inconsistências por tipo
        for inc in self.inconsistencias:
            tipo = inc['tipo']
            nivel = inc['nivel']
            
            if tipo not in relatorio['inconsistencias_por_tipo']:
                relatorio['inconsistencias_por_tipo'][tipo] = 0
            relatorio['inconsistencias_por_tipo'][tipo] += 1
            
            if nivel not in relatorio['inconsistencias_por_nivel']:
                relatorio['inconsistencias_por_nivel'][nivel] = 0
            relatorio['inconsistencias_por_nivel'][nivel] += 1
        
        # Gerar recomendações
        relatorio['recomendacoes'] = self._gerar_recomendacoes()
        
        return relatorio
    
    def _gerar_recomendacoes(self) -> List[str]:
        """
        Gera recomendações baseadas nas inconsistências encontradas
        """
        recomendacoes = []
        
        if len(self.inconsistencias) > 1000:
            recomendacoes.append("Implementar filtros mais rigorosos para dados extremos")
        
        if len(self.fundos_problematicos) > 100:
            recomendacoes.append("Considerar exclusão de fundos com dados inconsistentes")
        
        if any('DIFERENCA_FONTES_RENTABILIDADE' in inc['tipo'] for inc in self.inconsistencias):
            recomendacoes.append("Investigar diferenças entre fontes de rentabilidade")
        
        if not recomendacoes:
            recomendacoes.append("Dados estão consistentes - prosseguir com análise")
        
        return recomendacoes
    
    def salvar_relatorio(self, caminho: str = None):
        """
        Salva o relatório de inconsistências
        """
        if caminho is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            caminho = f"relatorio_inconsistencias_cvm_{timestamp}.json"
        
        relatorio = self.gerar_relatorio_inconsistencias()
        
        import json
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(relatorio, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"✅ Relatório salvo em: {caminho}")
        return caminho

def main():
    """
    Função principal para testar o processador
    """
    print("🚀 INICIANDO PROCESSAMENTO DE DADOS BRUTOS CVM")
    print("=" * 60)
    
    # Inicializar processador
    processor = CVMDataProcessor()
    
    # Carregar dados brutos
    dados_brutos = processor.carregar_dados_brutos()
    if not dados_brutos:
        print("❌ Falha ao carregar dados brutos")
        return
    
    # Limpar e preparar dados
    dados_limpos = processor.limpar_e_preparar_dados()
    
    # Identificar inconsistências
    inconsistencias = processor.identificar_inconsistencias_rentabilidade()
    
    # Identificar fundos problemáticos
    fundos_problematicos = processor.identificar_fundos_problematicos()
    
    # Gerar e salvar relatório
    caminho_relatorio = processor.salvar_relatorio()
    
    # Resumo final
    print("\n📊 RESUMO FINAL:")
    print(f"📁 Dados brutos carregados: {len(dados_brutos)} arquivos")
    print(f"🧹 Dados processados: {len(dados_limpos)} arquivos")
    print(f"🚨 Inconsistências encontradas: {len(inconsistencias)}")
    print(f"🏦 Fundos problemáticos: {len(processor.fundos_problematicos)}")
    print(f"📄 Relatório salvo em: {caminho_relatorio}")
    
    print("\n✅ Processamento concluído!")

if __name__ == "__main__":
    main() 