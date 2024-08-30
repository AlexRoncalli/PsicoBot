import streamlit as st
import replicate
import os

# Titulo
st.set_page_config(page_title="PsicoBot")

# Autentificar as credenciais
with st.sidebar:
    st.title('💬 PsicoBot')
    st.write('Esse chatbot foi criado sando Llama 2 LLM.')
    if 'REPLICATE_API_TOKEN' in st.secrets:
        st.success('API key funcionou!', icon='✅')
        replicate_api = st.secrets['REPLICATE_API_TOKEN']
    else:
        replicate_api = st.text_input('Replicate API token:', type='password')
        if not (replicate_api.startswith('r8_') and len(replicate_api)==40):
            st.warning('Por favor coloque suas credenciais!', icon='⚠️')
        else:
            st.success('Pode falar com o PsicoBot!', icon='👉')
    os.environ['REPLICATE_API_TOKEN'] = replicate_api

    llm = 'a16z-infra/llama7b-v2-chat:4f0a4744c7295c024a1de15e1a63c880d3da035fa1f49bfd344fe076074c8eea'

# Guarda o historico do chat LLM
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistente", "content": "Como você está se sentindo hoje??"}]

# Mostrar ou limpar as a conversa
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistente", "content": "Como você está se sentindo hoje??"}]
st.sidebar.button('Limpar chat', on_click=clear_chat_history)

# Fução para gerar a resposta
def generate_llama2_response(prompt_input):
    string_dialogue = "Você é um psicólogo que tenta ajudar os usuários com problemas ou sentimentos que os incomodam com conselhos. Você não responde como 'User' nem finge ser 'User'. Você responde apenas uma vez como 'assistente'. É muito importante que você sempre responda em português brasileiro."
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            string_dialogue += "User: " + dict_message["content"] + "\n\n"
        else:
            string_dialogue += "assistente: " + dict_message["content"] + "\n\n"
    output = replicate.run('a16z-infra/llama7b-v2-chat:4f0a4744c7295c024a1de15e1a63c880d3da035fa1f49bfd344fe076074c8eea',
                            #'a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5', 
                           input={"prompt": f"{string_dialogue} {prompt_input} assistente: ",
                                  "temperature":0.2, "top_p":0.7, "max_length":250, "repetition_penalty":1})# temperatura bem baixa para o modelo nao correr riscos e dar uma resposta menos criativa
    return output

# Prompt do usuario
if prompt := st.chat_input(disabled=not replicate_api):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Gera a resposta se a ultima msg nao for do assistente
if st.session_state.messages[-1]["role"] != "assistente":
    with st.chat_message("assistente"):
        with st.spinner("Pensando..."):
            response = generate_llama2_response(prompt)
            placeholder = st.empty()
            full_response = ''
            for item in response:
                full_response += item
                placeholder.markdown(full_response)
            placeholder.markdown(full_response)
    message = {"role": "assistente", "content": full_response}
    st.session_state.messages.append(message)
