from llm import get_llm
from langchain_core.messages import HumanMessage,SystemMessage
from schemas import KnowledgeGraph
from prompts import *
from time import sleep

llm=get_llm(output_schema=KnowledgeGraph)

def extract_from_chunk(chunk):
    try:
        response=llm.invoke([
            SystemMessage(content=graph_builder_system_promptsystem_prompt),
            HumanMessage(content=extraction_prompt.format(chunk=chunk))
        ])
        return response
    except Exception as E:
        print(f"Error Occured{E}")
        return KnowledgeGraph(nodes=[], relationships=[])

def extract_ER(chunks: list) -> list[KnowledgeGraph]:
    extracted_entities = []
    total = len(chunks)

    for i, chunk in enumerate(chunks):
        print(f"Extracting from chunk {i+1}/{total}")
        entity = extract_from_chunk(chunk)       # ← always KnowledgeGraph now, never None

        # ── Skip empty results ─────────────────────────────
        if not entity.nodes and not entity.relationships:
            print(f"  ⏭️  Chunk {i+1} — nothing extracted, skipped")
            continue

        print(f"  ✅ Nodes: {len(entity.nodes)}  Relationships: {len(entity.relationships)}")
        extracted_entities.append(entity)
        sleep(2.1)

    return extracted_entities

if __name__=='__main__':
    from loading_txt import extract_txt
    from chunker import chunk_txt
    txt=extract_txt('Game+of+Thrones.pdf')
    chunks=chunk_txt(txt)
    knowledge_graphs=extract_ER(chunks[:5])
    for graph in knowledge_graphs:
        print('=================================================')
        print(graph)
        print('=================================================')
