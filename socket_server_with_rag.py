import socket
import threading

from langchain import hub
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama


def process_input(data, llm, embed_model):
    text = '''
        Tom is a cat. He is friends with Jerry the mouse.
        They love to play pranks on each other.
        Tom has gray fur while Jerry is golden orange.
        Tom likes drinking milk and Jerry perfers cheese.
        '''

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=512,
        chunk_overlap=128
    )
    chunks = text_splitter.split_text(text)
    vector_store = Chroma.from_texts(chunks, embed_model)
    retriever = vector_store.as_retriever()
    create_retrieval_chain(combine_docs_chain=llm, retriever=retriever)

    retrieval_qa_chat_prompt = hub.pull('langchain-ai/retrieval-qa-chat')

    combine_docs_chain = create_stuff_documents_chain(
        llm,
        retrieval_qa_chat_prompt
    )

    retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)
    response = retrieval_chain.invoke({'input': data})
    if 'answer' in response:
        return response['answer']
    else:
        return 'Could not complete your request. Please try again later.'


def handle_client(client_socket, client_address, llm, embed_model):
    print(f'[NEW CONNECTION] {client_address} connected.')

    while True:
        try:
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                print(f'[DISCONNECTED] {client_address}')
                break

            breakpoint()
            print(f'[RECEIVED from {client_address}]: {data}')
            result = process_input(data, llm, embed_model)
            client_socket.sendall(result.encode('utf-8'))
        except ConnectionResetError:
            print(f'[ERROR] Connection with {client_address} was lost.')
            break

    client_socket.close()


def start_server(host='0.0.0.0', port=9999):
    llm = Ollama(model='tinyllama', base_url='http://localhost:11434')

    embed_model = OllamaEmbeddings(
        model='tinyllama',
        base_url='http://localhost:11434'
    )

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))

    server.listen(5)  # simultaneous connections
    print(f'[LISTENING] Server is listening on {host}:{port}')

    while True:
        client_socket, client_address = server.accept()
        client_handler = threading.Thread(
            target=handle_client,
            args=(client_socket, client_address, llm, embed_model)
        )
        client_handler.start()

        print(f'[ACTIVE CONNECTIONS] {threading.active_count() - 1}')


if __name__ == '__main__':
    start_server()
