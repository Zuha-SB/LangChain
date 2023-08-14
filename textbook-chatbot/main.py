from dotenv import load_dotenv
import os
import streamlit as st
import PyPDF2
from pathlib import Path
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.llms import OpenAI
import pickle

load_dotenv()

st.title("This is the title")
st.subheader("This is the subheader")

OPENAI_KEY = os.getenv('OPENAI_KEY')
pageDocs = []

def remove_extra(line):
    line = line.replace('\n', ' ')
    line = line.replace('\n\n', ' ')
    line = line.replace('  ', ' ')
    return line

def pdfToTxt():
    pages_text = []
    print("Starting pdf to text transcription")
    with open("file.pdf", 'rb') as pdfFileObject:
        pdfReader = PyPDF2.PdfReader(pdfFileObject)
        print("No. Of Pages: ", len(pdfReader.pages))
        for i, page in enumerate(pdfReader.pages):
            pageObject = pdfReader.pages[i]
            pages_text.append((pageObject.extract_text(), i + 2)) # Why 2?
            if i == 544: # pages past 544 trash
                break

    for pageText, pageNum in pages_text:
        pageClean = remove_extra(pageText)
        print("ONE PAGE: ", pageClean)
        doc = Document(page_content=pageClean, metadata={"source": f"Page Number: {pageNum}"})
        pageDocs.append(doc)
    print("Done with pdf to txt!")

uploaded_file = st.file_uploader("Choose a pdf file")

if uploaded_file is not None:
    pdfBytes = uploaded_file.getvalue()
    with open("file.pdf", 'wb') as handler:
        handler.write(pdfBytes)
    with st.spinner(text="In progress"):
        pdfToTxt()
        st.success("PDF uploaded!")

    text_splitter = CharacterTextSplitter(separator=" ", chunk_size=75, chunk_overlap=0)
    out_chunks = []
    for page in pageDocs:
        for smaller_chunk in text_splitter.split_text(page.page_content):
            out_chunks.append(Document(page_content=smaller_chunk, metadata=page.metadata))

    vectorStorePkl = Path("vectorstore.pkl")
    vectorStore = None
    if vectorStorePkl.is_file():
        print("Vector index found...")
        with open('vectorstore.pkl', 'rb') as f:
            vectorStore = pickle.load(f)
    else:
        print("Regenerating search index vector store...")
        vectorStore = FAISS.from_documents(out_chunks, OpenAIEmbeddings(openai_api_key = OPENAI_KEY))
        with open("vectorstore.pkl", 'wb') as f:
            pickle.dump(vectorStore, f)

    chain = load_qa_with_sources_chain(OpenAI(temperature=0, openai_api_key=OPENAI_KEY))

    userInput = st.text_input(label="input_text", placeholder="Enter query")

    result = chain(
        {
            "input_documents": vectorStore.similarity_search(userInput, k=4),
            "question": userInput,
        },
        return_only_outputs=True,
    )["output_text"]

    st.balloons()
    st.subheader(result)

# streamlit run main.py
