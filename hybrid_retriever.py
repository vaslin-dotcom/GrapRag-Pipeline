from langchain_core.messages import HumanMessage, SystemMessage
from llm                    import get_llm
from query_processing_for_graphDB       import graph_retrieve_entities,select_k,extract_entity_from_query
from query_processing_for_vectorDB       import vector_retrieve
from context_formater      import format_vector_context, format_graph_context, combine_context
from prompts import *

answer_llm = get_llm()

def hybrid_retrieve(query: str) -> str:
    print(f"\n{'='*60}")
    print(f"  Query: {query}")
    print(f"{'='*60}")

    # ── Step 1: Select k ───────────────────────────────────
    print("\n🧠 Step 1: Selecting k...")
    k = select_k(query).k

    # ── Step 2: Extract entities ───────────────────────────
    print("\n🔍 Step 2: Extracting entities...")
    entities = extract_entity_from_query(query)

    # ── Step 3: Graph retrieval ────────────────────────────
    print(f"\n🕸️  Step 3: Graph retrieval (k={k})...")
    graph_results  = graph_retrieve_entities(entities, k=k)
    graph_context  = format_graph_context(graph_results)
    print(f"  ✅ {len(graph_results)} entities retrieved from graph")

    # ── Step 4: Vector retrieval ───────────────────────────
    print("\n📚 Step 4: Vector retrieval...")
    chunks         = vector_retrieve(query, k=3)
    vector_context = format_vector_context(chunks)
    print(f"  ✅ {len(chunks)} chunks retrieved from vector store")

    # ── Step 5: Combine context ────────────────────────────
    print("\n🔗 Step 5: Combining context...")
    combined = combine_context(vector_context, graph_context)

    # ── Step 6: Generate answer ────────────────────────────
    print("\n🤖 Step 6: Generating answer...")
    response = answer_llm.invoke([
        SystemMessage(content=hybrid_retriever_system_prompt),
        HumanMessage(content=hybrid_retriver_search_prompt.format(
            context=combined,
            query=query
        ))
    ])

    return response.content

# ── Test ───────────────────────────────────────────────────
if __name__ == "__main__":
    test_queries = [
        "Who is Eddard Stark?",
        "What are the alliances of House Stark?",
        "How did Roberts Rebellion affect the Targaryens?",
        "Tell me about Jaime Lannister"
    ]

    for query in test_queries:
        answer = hybrid_retrieve(query)
        print(f"\n💬 Answer:\n{answer}")
        print(f"\n{'='*60}\n")