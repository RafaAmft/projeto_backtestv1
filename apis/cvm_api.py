import streamlit as st
import pandas as pd
import numpy as np
import io

# ⬇️ Carrega os dados
# Dados processados localmente da CVM
df_final = pd.read_excel("transformados/df_final.xlsx")
df_auditoria = pd.read_excel("auditoria_rentabilidades_mensais.xlsx")

# 🔧 Configuração da página
st.set_page_config(layout='wide', page_title="Painel Carteira CVM", page_icon="📊")

st.title("📈 Painel de Rentabilidade da Carteira - Fundos CVM (dados locais + scraping)")
st.markdown("Versão preliminar – dados de fundos processados localmente da CVM e complementados via scraping do Mais Retorno. Atualizada em 29/06/2025")

# 🔘 Navegação lateral
aba = st.sidebar.radio("Selecione a Visão", [
    "Resumo da Carteira",
    "Auditoria e Consistência",
    "Comparativo Público",
    "Download de Dados"
])

# 1️⃣ Resumo da Carteira
if aba == "Resumo da Carteira":
    st.header("📊 Rentabilidade Resumida por Fundo")

    st.dataframe(df_final.style.format({
        "2021": "{:.2%}", "2022": "{:.2%}", "2023": "{:.2%}",
        "2024": "{:.2%}", "JAN_MAI_2025": "{:.2%}",
        "ULT_12_MESES": "{:.2%}", "RET_TOTAL": "{:.2%}"
    }), use_container_width=True)

    chart_data = df_final[["FUNDO", "RET_TOTAL"]].sort_values("RET_TOTAL", ascending=False)
    st.bar_chart(data=chart_data.set_index("FUNDO"))

# 2️⃣ Auditoria e Consistência
elif aba == "Auditoria e Consistência":
    st.header("🔍 Verificação de Rentabilidades Mensais")

    fundos = df_auditoria["FUNDO"].unique()
    fundo_sel = st.selectbox("Selecione um fundo para inspecionar", sorted(fundos))

    audit_filtro = df_auditoria[df_auditoria["FUNDO"] == fundo_sel].copy()
    audit_filtro["DIF_ABS"] = audit_filtro["DIF_ABS"].round(6)

    st.dataframe(audit_filtro.style
        .highlight_between(subset='DIF_ABS', left=0.001, right=0.1, color='orange')
        .format({
            'RENTAB_MENSAL': "{:.2%}",
            'RENT_CALCULADA': "{:.2%}",
            'DIF_ABS': "{:.4%}"
        }),
        use_container_width=True
    )

    df_rank = df_auditoria.groupby("FUNDO")["DIF_ABS"].mean().sort_values()
    st.subheader("📈 Ranking de Consistência (Desvio Médio)")
    st.dataframe(df_rank.round(6).to_frame("Desvio Médio Absoluto"), use_container_width=True)

# 3️⃣ Comparativo com Dados Públicos
elif aba == "Comparativo Público":
    st.header("🌐 Comparativo com Dados Públicos")
    st.markdown("🚧 Essa aba será conectada à base do Mais Retorno ou API externa.")
    st.info("Você poderá ver: Sua base x Pública x Diferença, com semáforo de consistência.")

# 4️⃣ Downloads
elif aba == "Download de Dados":
    st.header("📁 Baixar Tabelas")

    # ⬇️ Excel - df_final
    buffer_final = io.BytesIO()
    with pd.ExcelWriter(buffer_final, engine='xlsxwriter') as writer:
        df_final.to_excel(writer, index=False, sheet_name='Resumo')
    st.download_button(
        label="⬇️ Baixar df_final.xlsx",
        data=buffer_final.getvalue(),
        file_name="df_final.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # ⬇️ Excel - auditoria
    buffer_aud = io.BytesIO()
    with pd.ExcelWriter(buffer_aud, engine='xlsxwriter') as writer:
        df_auditoria.to_excel(writer, index=False, sheet_name='Auditoria')
    st.download_button(
        label="⬇️ Baixar auditoria_rentabilidades_mensais.xlsx",
        data=buffer_aud.getvalue(),
        file_name="auditoria_rentabilidades_mensais.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )