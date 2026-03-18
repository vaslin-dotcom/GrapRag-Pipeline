from schemas import *
from llm import get_llm
from langchain_core.messages import HumanMessage,SystemMessage
from prompts import *
from neo4j import GraphDatabase
from cypher import graph_extraction_cypher
from config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

entity_llm=get_llm(output_schema=ExtractEntities)
khop_llm=get_llm(output_schema=KHopDecision)

def extract_entity_from_query(query):
    result=entity_llm.invoke([
        SystemMessage(content=entity_extracter_system_prompt),
        HumanMessage(content=f'Query:{query}')
    ])
    return result.entities

def select_k(query):
    result=khop_llm.invoke([
        SystemMessage(content=KHop_system_prompt),
        HumanMessage(content=f'Querry:{query}')
    ])
    return result

def fuzzy_find_node(session, entity: str) -> str | None:
    # 1. Exact
    result = session.run(
        "MATCH (n {name: $name}) RETURN n.name AS name LIMIT 1",
        name=entity
    ).single()
    if result:
        return result["name"]

    # 2. Case insensitive
    result = session.run(
        "MATCH (n) WHERE toLower(n.name) = toLower($name) RETURN n.name AS name LIMIT 1",
        name=entity
    ).single()
    if result:
        return result["name"]

    # 3. Contains
    result = session.run(
        "MATCH (n) WHERE toLower(n.name) CONTAINS toLower($name) RETURN n.name AS name LIMIT 1",
        name=entity
    ).single()
    if result:
        return result["name"]

    return None

def graph_retrieve_entity(entity: str, k: int = 1) -> dict | None:
    with driver.session() as session:

        # ── Fuzzy find the node ────────────────────────────
        matched_name = fuzzy_find_node(session, entity)
        if not matched_name:
            print(f"    ⚠️  Node not found for '{entity}'")
            return None

        if matched_name != entity:
            print(f"    🔄 Fuzzy matched '{entity}' → '{matched_name}'")

        # ── Retrieve k-hop subgraph ────────────────────────
        result = session.run(
            graph_extraction_cypher.format(k=k),
            name=matched_name
        ).single()

        if not result:
            return None

        return dict(result)

def graph_retrieve_entities(entities: list[str], k: int = 1) -> list[dict]:
    results = []
    for entity in entities:
        print(f"    🕸️  Retrieving '{entity}' at k={k}...")
        result = graph_retrieve_entity(entity, k=k)
        if result:
            results.append(result)
    return results

def close_driver():
    driver.close()

if __name__=='__main__':
    test_queries = [
        "Who is Eddard Stark?",
        "What are the alliances of House Stark?",
        "How did Robert's Rebellion affect the Targaryens?",
        "Tell me about Jaime Lannister"
    ]

    for query in test_queries:
        print("Query:",query)
        entities=extract_entity_from_query(query)
        print("Entities:",entities)
        decision = select_k(query)
        k=decision.k
        print("K=",k)
        retrieved_connections=graph_retrieve_entities(entities,k)
        for result in retrieved_connections:
            if result:
                print(f"  ✅ Found : {result['entity']}")
                print(f"  Types   : {result['types']}")
                print(f"  Props   : {result['props']}")
                print(f"  Neighbors ({len(result['neighbors'])}):")
                for n in result['neighbors'][:5]:
                    print(f"    [{n['hops']} hop] {n['neighbor']} ({n['type']})")
                print(f"  Relationships ({len(result['relationships'])}):")
                for r in result['relationships'][:5]:
                    print(f"    {r['source']} --[{r['relation']}]--> {r['target']}")
            else:
                print(f"  ❌ Not found")

        
       