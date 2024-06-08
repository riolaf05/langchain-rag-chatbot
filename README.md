# Setup 

Usare `.env.template` per lanciare il Docker sulla 8000 

# Changelog

## 0.1.0

Using `ChatPromptTemplate` and `Groq`

```python
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
```


## 0.2.0 

Using `ConversationalRetrievalChain` and `Groq`:

```python
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
```

### References

* [Chatbot con Python e Langchain](https://www.diariodiunanalista.it/posts/chatbot-python-langchain-rag/)

## 0.3.0

CSV Ingestion