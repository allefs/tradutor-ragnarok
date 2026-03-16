import streamlit as st
import google.generativeai as genai
import chardet

st.set_page_config(page_title="Tradutor bRO Pro-Renewal", page_icon="🗡️")

st.title("🤖 Agente de Tradução: bRO / Pre-Renewal")

api_key = st.text_input("Insira sua API Key do Google Gemini:", type="password")

uploaded_file = st.file_uploader("Suba seu arquivo (.txt, .conf, .csv)", type=["txt", "conf", "csv"])

if st.button("Traduzir e Formatar", type="primary"):
    if not api_key:
        st.error("⚠️ Insira a API Key.")
    elif uploaded_file is None:
        st.error("⚠️ Suba um arquivo.")
    else:
        try:
            # 1. Detectar Codificação automaticamente
            raw_data = uploaded_file.getvalue()
            detected = chardet.detect(raw_data)
            encoding = detected['encoding'] if detected['encoding'] else 'utf-8'
            conteudo = raw_data.decode(encoding)

            # 2. Configurar API
            genai.configure(api_key=api_key)
            
            # 3. AUTO-DETECÇÃO DE MODELO (O "Pulo do Gato")
            # Vamos procurar um modelo que funcione na sua conta gratuita
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            
            if not available_models:
                st.error("Nenhum modelo disponível encontrado para esta chave.")
            else:
                # Tenta priorizar o 1.5-flash, se não tiver, pega o primeiro da lista
                model_to_use = next((m for m in available_models if "1.5-flash" in m), available_models[0])
                
                model = genai.GenerativeModel(model_to_use)
                
                with st.spinner(f'Traduzindo com o modelo: {model_to_use}...'):
                    prompt = f"""
                    Você é um Especialista em Ragnarok Online (bRO). 
                    Traduza o conteúdo abaixo para o Português padrão bRO (Pre-Renewal).
                    Mantenha IDs, Chaves e Sintaxe intactos. Traduza apenas as strings de texto.
                    
                    Conteúdo:
                    {conteudo}
                    """
                    
                    response = model.generate_content(prompt)
                    
                    st.success("✅ Concluído!")
                    st.text_area("Resultado:", response.text, height=300)
                    st.download_button("📥 Baixar Traduzido", response.text, file_name=f"bRO_{uploaded_file.name}")

        except Exception as e:
            st.error(f"Erro detalhado: {e}")
            st.info("Dica: Se o erro persistir, verifique se sua API Key foi criada recentemente no Google AI Studio.")
