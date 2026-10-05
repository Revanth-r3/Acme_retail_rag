import os

import streamlit as st

from pipeline.embeddings import EmbeddingModel
from pipeline.vectorstore import VectorStore
from pipeline.document_tracker import DocumentTracker
from pipeline.indexer import index_document
from services.rag_service import RAGService


DATA_DIR = "data"


st.set_page_config(
    page_title="Acme Retail RAG Assistant",
    page_icon="📚",
    layout="wide"
)


st.title("📚 Retail RAG Assistant")

st.write(
    "Upload Retail documents and ask questions across them."
)


# ---------------------------------------------------------
# Load shared components
# ---------------------------------------------------------

@st.cache_resource
def load_indexing_components():

    embedding_model = EmbeddingModel()
    vector_store = VectorStore()
    tracker = DocumentTracker()

    return embedding_model, vector_store, tracker


@st.cache_resource
def load_rag_service(_embedding_model):
    return RAGService(
        top_k=3,
        embedding_model=_embedding_model
    )


embedding_model, vector_store, tracker = load_indexing_components()

# rag = load_rag_service()
rag = load_rag_service(embedding_model)


# ---------------------------------------------------------
# File Upload
# ---------------------------------------------------------

st.subheader("Upload Documents")

uploaded_files = st.file_uploader(
    "Upload Excel, CSV, or PowerPoint (.pptx) files",
    type=["xlsx", "xls", "csv", "pptx"],
    accept_multiple_files=True
)


if uploaded_files:
    if st.button("Index Uploaded Documents"):

        os.makedirs(DATA_DIR, exist_ok=True)

        for uploaded_file in uploaded_files:
            safe_filename = os.path.basename(
                uploaded_file.name.replace("\\", "/")
            )

            file_path = os.path.join(DATA_DIR, safe_filename)

            # Save uploaded file
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            st.write(
                f"📄 Processing: `{uploaded_file.name}`"
            )

            # Index document
            index_document(
                file_path=file_path,
                embedding_model=embedding_model,
                vector_store=vector_store,
                tracker=tracker
            )

        st.success(
            "Document processing completed."
        )


# ---------------------------------------------------------
# Question Answering
# ---------------------------------------------------------

st.subheader("Ask a Question")

question = st.text_input(
    "Ask a question",
    placeholder="e.g. What was the revenue of the South region?"
)


if st.button("Ask"):

    if not question.strip():

        st.warning(
            "Please enter a question."
        )

    else:

        with st.spinner(
            "Searching documents and generating answer..."
        ):

            result = rag.answer(question)

        st.subheader("Answer")

        st.write(
            result["answer"]
        )

        # -------------------------------------------------
        # Sources
        # -------------------------------------------------

        if result["sources"]:

            st.subheader("Sources")

            for source in result["sources"]:

                source_text = source.get(
                    "source",
                    "Unknown"
                )

                source_text = source_text.replace("\\", "/")

                if source.get("slide"):

                    source_text += (
                        f" — Slide {source['slide']}"
                    )

                if source.get("sheet"):

                    source_text += (
                        f" — Sheet: {source['sheet']}"
                    )

                if source.get("row"):

                    source_text += (
                        f" — Row: {source['row']}"
                    )

                if source.get("title"):

                    source_text += (
                        f" — {source['title']}"
                    )

                st.write(
                    f"📄 {source_text}"
                )