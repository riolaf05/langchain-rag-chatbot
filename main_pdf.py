#See https://medium.com/@cleancoder/build-a-chatbot-in-minutes-with-chainlit-gpt-4-and-langchain-7690968578f0

from langchain_groq import ChatGroq
from langchain.memory.buffer import ConversationBufferMemory
import chainlit as cl
from langchain.document_loaders import pdf
from langchain.document_loaders import PyPDFLoader, TextLoader
from langchain.memory import ChatMessageHistory, ConversationBufferMemory
from utils import database_managers, embedding
import os
from langchain.chains import (
    ConversationalRetrievalChain,
)
from dotenv import load_dotenv
import platform
load_dotenv(override=True)
from langchain.text_splitter import RecursiveCharacterTextSplitter

UPLOAD_FOLDER = r"C:\Users\ELAFACRB1\Codice\GitHub\riassume\riassume\uploads" if platform.system()=='Windows' else '/tmp'

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
vectore_store = database_managers.QDrantDBManager(
        url=os.getenv('QDRANT_URL'),
        port=6333,
        vector_size=768,
        collection_name="pdf",
        embedding=embedding.EmbeddingFunction('fast-bgeEmbedding').embedder,
        record_manager_url="sqlite:///record_manager_cache.sql"
    )

@cl.on_chat_start
async def on_chat_start():

    files = None

    # Wait for the user to upload a file
    while files == None:
        files = await cl.AskFileMessage(
            content="Carica un pdf o fai una domanda!",
            accept=["application/pdf"],
            max_size_mb=20,
            timeout=180,
        ).send()

    file = files[0]

    msg = cl.Message(
        content=f"Creazione chunks per `{file.name}`..."
    )
    await msg.send()

    Loader = PyPDFLoader
    loader = Loader(file.path)

    # Split the text into chunks
    docs = loader.load()
    splitted_docs = text_splitter.split_documents(docs)

    # Create a metadata for each chunk
    metadatas = [{"source": f"{i}-pl"} for i in range(len(splitted_docs))]

    vectore_store.index_documents(splitted_docs)

    msg.content = f"Creazione embeddings for `{file.name}`. . ."
    await msg.update()

    message_history = ChatMessageHistory()

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        output_key="answer",
        chat_memory=message_history,
        return_messages=True,
    )
    
    # Create a chain that uses the Chroma vector store
    chain = ConversationalRetrievalChain.from_llm(
        llm = ChatGroq(temperature=0, model_name="Llama3-8b-8192"),
        chain_type="stuff",
        retriever=vectore_store.vector_store.as_retriever(),
        memory=memory,
        return_source_documents=True,
    )

    # Let the user know that the system is ready
    msg.content = f"File `{file.name}` processato. Puoi fare domande!"
    await msg.update()

    cl.user_session.set("chain", chain)

@cl.on_message
async def main(message: str):

    chain = cl.user_session.get("chain")
    cb = cl.AsyncLangchainCallbackHandler()
    res = await chain.acall(message, callbacks=[cb])
    answer = res["answer"]
    source_documents = res["source_documents"]

    text_elements = []

    if source_documents:
        for source_idx, source_doc in enumerate(source_documents):
            source_name = f"source_{source_idx}"
            text_elements.append(
                cl.Text(content=source_doc.page_content, name=source_name)
            )
        source_names = [text_el.name for text_el in text_elements]

        if source_names:
            answer += f"\nSources: {', '.join(source_names)}"
        else:
            answer += "\nNo sources found"

    await cl.Message(content=answer, elements=text_elements).send()