from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma 
from langchain_core.documents import Document

embeddings=HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-mpnet-base-v2"
)

chroma_path='chroma_db'

def build_vector_store(chunks):

    documents=[
        Document(
            page_content=chunk,
            metadata={"chunk_id":i}
        )
        for i,chunk in enumerate(chunks)
    ]

    vector_store=Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=chroma_path
    )

def load_vector_store():
    print(f"Loading vector store from {chroma_path}")
    return Chroma(
        persist_directory=chroma_path,
        embedding_function=embeddings
    )

def vector_retrieve(query,k=3):
    vector_store=load_vector_store()
    results      = vector_store.max_marginal_relevance_search(
        query,
        k=k,
        fetch_k=20    # fetch 20, pick k most diverse
    )
    chunks = [doc.page_content for doc in results]
    return chunks

if __name__ == "__main__":
    # from loading_txt import extract_txt
    # from chunker import chunk_txt

    # txt    = extract_txt("Game+of+Thrones.pdf")
    # chunks = chunk_txt(txt)

    # # ── Build ──────────────────────────────────────────────
    # build_vector_store(chunks)

    #── Test search ────────────────────────────────────────
    test_queries = [
        "Who is Eddard Stark?",
        "What are the alliances of House Stark?",
        "How did Robert's Rebellion affect the Targaryens?",
        "Tell me about Jaime Lannister"
    ]

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"  Query: {query}")
        print(f"{'='*60}")

        chunks = vector_retrieve(query, k=3)

        for i, chunk in enumerate(chunks):
            print(f"\n  Result {i+1}:")
            print(f"  {chunk[:200]}...")
