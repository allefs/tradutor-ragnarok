import streamlit as st
import google.generativeai as genai
import os

# 1. Configuração da Página Web
st.set_page_config(page_title="Tradutor bRO Pre-Renewal", page_icon="🗡️", layout="centered")

st.title("Agente de Tradução: bRO / Pre-Renewal")
st.write("""
Faça o upload do seu arquivo de Ragnarok (ex: `item_db.conf`, `mob_db.txt`, scripts de NPC). 
A IA vai traduzir o conteúdo para o Português (padrão bRO) mantendo a estrutura do código intacta.
""")

st.markdown("---")

# 2. Configuração de Segurança (Chave da API)
api_key = st.text_input("Insira sua API Key do Google Gemini:", type="password")
st.caption("Você pode gerar uma chave gratuita em: https://aistudio.google.com/")

# 3. Área de Upload de Arquivo
uploaded_file = st.file_uploader("Suba seu arquivo (.txt, .conf, .csv)", type=["txt", "conf", "csv"])


if st.button("Traduzir e Formatar", type="primary"):
    if not api_key:
        st.error("Por favor, insira sua chave de API para continuar.")
    elif uploaded_file is None:
        st.error("Por favor, faça o upload de um arquivo.")
    else:
        try:
            # --- MUDANÇA AQUI: Tratamento de Codificação ---
            raw_data = uploaded_file.getvalue()
            try:
                # Tenta ler como UTF-8 primeiro
                conteudo = raw_data.decode("utf-8")
            except UnicodeDecodeError:
                # Se falhar, tenta como ISO-8859-1 (comum em arquivos ANSI/Windows)
                conteudo = raw_data.decode("iso-8859-1")
            # ----------------------------------------------

            # Configurar a IA
            genai.configure(api_key=api_key)
            
            # Mudamos para o modelo Flash (mais rápido e com maior disponibilidade)
            model = genai.GenerativeModel('gemini-1.5-flash') 

            with st.spinner('Traduzindo banco de dados do Ragnarok...'):
                
                # 4. O "Cérebro" do Agente (Prompt Engineering)
                prompt = f"""
                Você é um Desenvolvedor Especialista em Ragnarok Online, focado em emuladores (rAthena/eAthena) e bancos de dados Pre-Renewal (como Ragnaplace).
                
                Sua tarefa:
                Receber o arquivo de script/database abaixo e traduzir o conteúdo voltado para o jogador (descrições de itens, nomes de monstros, falas de NPCs) para o Português do Brasil, utilizando os termos oficiais do bRO (Level Up! / WarpPortal Brasil).
                
                Regras Absolutas:
                1. MANTENHA A SINTAXE INTACTA: Não altere chaves, variáveis numéricas, IDs de itens/monstros, lógicas de script (if, else, bonus, etc).
                2. PADRÃO PRE-RENEWAL: Respeite os status e o meta do Pre-Renewal (ex: ignorar atributos Renewal como MATK fixo na fórmula nova, caso existam comentários sobre isso).
                3. Não adicione saudações, explicações ou markdown no começo. Retorne APENAS o código pronto para ser salvo no arquivo.

                Arquivo original:
                {conteudo}
                """

                # Executar a IA
                response = model.generate_content(prompt)
                resultado = response.text

            st.success("✅ Tradução concluída com sucesso!")

            # 5. Mostrar o resultado na tela
            st.text_area("Pré-visualização do Arquivo Traduzido:", resultado, height=300)

            # 6. Botão para baixar o novo arquivo
            st.download_button(
                label="Baixar Arquivo Traduzido",
                data=resultado,
                file_name=f"bRO_{uploaded_file.name}",
                mime="text/plain"
            )

        except Exception as e:
            st.error(f"Ocorreu um erro durante o processamento: {e}")
