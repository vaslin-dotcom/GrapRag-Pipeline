from query_processing_for_graphDB import *
from query_processing_for_vectorDB import *

def format_vector_context(chunks: list[str]) -> str:
    """Format retrieved chunks into readable context."""
    if not chunks:
        return "No relevant text passages found."

    formatted = "=== RELEVANT TEXT PASSAGES ===\n"
    for i, chunk in enumerate(chunks):
        formatted += f"\n[Passage {i+1}]\n{chunk}\n"
    return formatted


def format_graph_context(graph_results: list[dict]) -> str:
    """Format graph relationships into readable context."""
    if not graph_results:
        return "No graph relationships found."

    formatted = "=== KNOWLEDGE GRAPH RELATIONSHIPS ===\n"

    for result in graph_results:
        entity = result.get("entity", "Unknown")
        types  = result.get("types",  [])
        props  = result.get("props",  {})

        formatted += f"\n[Entity: {entity}]"
        formatted += f"\n  Type: {', '.join(types)}"

        # ── Properties ────────────────────────────────────
        if props:
            formatted += f"\n  Properties:"
            for k, v in props.items():
                if k != "name":
                    formatted += f"\n    - {k}: {v}"

        # ── Relationships ──────────────────────────────────
        if result.get("relationships"):
            formatted += f"\n  Relationships:"
            for rel in result["relationships"]:
                source   = rel['source']
                relation = rel['relation']
                target   = rel['target']

                # ── Mark direction clearly ─────────────────
                if source == entity:
                    formatted += f"\n    {source} --[{relation}]--> {target}  (outgoing)"
                else:
                    formatted += f"\n    {source} --[{relation}]--> {target}  (incoming — {source} does this TO/WITH {entity})"

        formatted += "\n"

    return formatted


def combine_context(vector_context: str, graph_context: str) -> str:
    """Combine both contexts into one string for LLM."""
    return f"{graph_context}\n\n{vector_context}"


# ── Test ───────────────────────────────────────────────────
if __name__ == "__main__":
    query = "Who is Eddard Stark?"
    print(f"Query: {query}\n")

    # ── Graph context ──────────────────────────────────────
    entities      = extract_entity_from_query(query)
    k             = select_k(query).k
    graph_results = graph_retrieve_entities(entities, k=k)
    graph_context = format_graph_context(graph_results)

    # ── Vector context ─────────────────────────────────────
    chunks        = vector_retrieve(query, k=3)
    vector_context = format_vector_context(chunks)

    # ── Combined ───────────────────────────────────────────
    combined = combine_context(vector_context, graph_context)
    print('=============COMBINED=============')
    print(combined)