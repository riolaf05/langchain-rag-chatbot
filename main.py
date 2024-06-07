from langchain_groq import ChatGroq
from langchain.memory.buffer import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
import chainlit as cl
from utils import database_managers, embedding
import os
from dotenv import load_dotenv
load_dotenv(override=True)

# RAG Setup
def llmama3_chain(question):
    system_message_prompt = SystemMessagePromptTemplate.from_template(
        """
        Sei un chatbot incaricato di rispondere alle domande sulla ricerca di ristoranti o di locali o di eventi.

        Non dovresti mai rispondere a una domanda con un'altra domanda e dovresti sempre rispondere con la pagina della documentazione più pertinente.

        Non rispondere a domande che non riguardano ristoranti o locali o eventi.

        Data una domanda, dovresti rispondere con un elenco dei ristoranti, eventi o locali più pertinenti, seguento il contesto rilevante qui sotto:
        {context}

        Per ogni elemento dell'elenco, indica:
          + nome del ristorante, locale, evento
          + indirizzo (ove disponibile)
          + descrizione
        """
    )
    human_message_prompt = HumanMessagePromptTemplate.from_template("{question}")

    llm = ChatGroq(temperature=0.1, model_name="Llama3-8b-8192")
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        combine_docs_chain_kwargs={
            "prompt": ChatPromptTemplate.from_messages(
                [
                    system_message_prompt,
                    human_message_prompt,
                ]
            ),
        },
    )
    return conversation_chain({"question": question})


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
        res = llmama3_chain(message.content)
        await cl.Message(
            content=res['answer'],
        ).send()
        
        # await cl.Message(content=answer['result']).send()
    except Exception as e:
        print(e)
        return
    