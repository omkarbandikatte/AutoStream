from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


def build_vectorstore():
    loader = TextLoader("data/knowledge_base.md", encoding="utf-8")
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunk = splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings(
        model_name = "sentence-transformers/all-MiniLM-L6-v2"
    )

    vectorestore = FAISS.from_documents(chunk, embeddings)
    return vectorestore

VECTORSTORE = build_vectorstore()

def retrieve_context(query: str) -> dict:
    """Retrieve context with relevance scoring to prevent hallucination"""
    docs_with_scores = VECTORSTORE.similarity_search_with_score(query, k=3)
    
    if not docs_with_scores:
        return {
            "context": "No relevant information found.",
            "relevance_score": 0.0
        }
    
    avg_score = sum(score for _, score in docs_with_scores) / len(docs_with_scores)
    relevance_score = max(0, 1 - (avg_score / 2))
    
    context = "\n\n".join([doc.page_content for doc, _ in docs_with_scores])
    
    return {
        "context": context,
        "relevance_score": relevance_score,
        "num_results": len(docs_with_scores)
    }