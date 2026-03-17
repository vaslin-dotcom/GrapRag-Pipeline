from loading_txt import extract_txt
from chunker import chunk_txt
from entity_relation_extracter import extract_ER
from graph_builder import store_in_graphDB, close_driver

PDF_PATH = "Game+of+Thrones.pdf"

def build_knowledge_graph(pdf_path: str) -> None:
    print("🚀 Starting Knowledge Graph build...\n")

    text   = extract_txt(pdf_path)
    chunks = chunk_txt(text)

    # ✅ pass full list to extract_ER — it handles looping internally
    knowledge_graphs = extract_ER(chunks)

    for i, kg in enumerate(knowledge_graphs):
        try:
            store_in_graphDB(kg)
            print(f"  ✅ Graph {i+1} — {len(kg.nodes)} nodes, {len(kg.relationships)} relationships written")
        except Exception as e:
            print(f"  ⚠️  Skipped graph {i+1} — {e}")

    close_driver()
    print("\n✅ Knowledge Graph built successfully!")

if __name__ == "__main__":
    build_knowledge_graph(PDF_PATH)
