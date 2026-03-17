from llm import get_llm
from langchain_core.messages import HumanMessage,SystemMessage
from schemas import KnowledgeGraph
from prompts import *

llm=get_llm(output_schema=KnowledgeGraph)

def extract_from_chunk(chunk):
    try:
        response=llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=extraction_prompt.format(chunk=chunk))
        ])
        return response
    except Exception as E:
        print(f"Error Occured{E}")
extracted_entities=[]
def extract_ER(chunks):
    total=len(chunks)
    for i,chunk in enumerate(chunks):
        print(f'Extracting from chunk {i+1}/{total}')
        entity=extract_from_chunk(chunk)
        print(f"Nodes:{len(entity.nodes)}")
        print(f"Relationships:{len(entity.relationships)}")
        extracted_entities.append(entity)
    return extracted_entities

if __name__=='__main__':
    sum=0
    from loading_txt import extract_txt
    from chunker import chunk_txt
    txt=extract_txt('Game+of+Thrones.pdf')
    chunks=chunk_txt(txt)
    knowledge_graphs=extract_ER(chunks[:5])
    for graph in knowledge_graphs:
        sum+=len(graph.nodes)
    print(sum)
