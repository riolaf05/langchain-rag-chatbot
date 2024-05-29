from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain.memory.buffer import ConversationBufferMemory
import chainlit as cl
from utils import database_managers, embedding
import os
from dotenv import load_dotenv
load_dotenv(override=True)

# RAG Setup
def llmama3_llm(question, context):
    chat = ChatGroq(temperature=0, model_name="Llama3-8b-8192")
    system = """
        Sei un assistente nella ricerca di ristoranti o locali o eventi. Date le informazioni di contesto restituisci una lista di ristoranti, locali, eventi richiesti,
        che soddisfano i requisiti di ricerca.
        Per ogni elemento indica:
          + nome del ristorante, locale, evento
          + indirizzo
          + descrizione
          """
    
    formatted_prompt = f"Domanda: {question}\n\nContesto: {context}"
    prompt = ChatPromptTemplate.from_messages([("system", system), ("user", formatted_prompt)])

    chain = prompt | chat
    return chain.invoke({"text": question})
def combine_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)
def rag_chain(question):
    retrieved_docs = retriever.invoke(question)
    formatted_context = combine_docs(retrieved_docs)
    return llmama3_llm(question, formatted_context)


COLLECTION_NAME = "web-places"
embedding = embedding.EmbeddingFunction('fast-bgeEmbedding').embedder
vectore_store=qdrantClient = database_managers.QDrantDBManager(
    url=os.getenv('QDRANT_URL'),
    port=6333,
    collection_name=COLLECTION_NAME,
    vector_size=768,
    embedding=embedding,
    record_manager_url=r"sqlite:///record_manager_cache.sql"
)
vectore_store_client=vectore_store.vector_store
retriever = vectore_store_client.as_retriever()

#aggiungere memoria!!

@cl.on_chat_start
async def on_chat_start():

    # Sending an image with the local file path
    elements = [
        cl.Image(name="image1", display="inline", path="./assets/bot.png")
    ]
    await cl.Message(content="Ciao 👋, ti darò consigli su luoghi ed eventi!", elements=elements).send()

@cl.on_message
async def main(message: str):

    try:
        res = rag_chain(message.content)
        await cl.Message(
            content=res.content,
        ).send()
        
        # await cl.Message(content=answer['result']).send()
    except Exception as e:
        print(e)
        return
    