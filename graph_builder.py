from neo4j import GraphDatabase
from schemas import KnowledgeGraph
from config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))  # ✅ fix typo

def property_to_dict(properties):
    return {p.key: p.value for p in properties} if properties else {}

def _sanitize_label(text: str) -> str:
    return text.strip().upper().replace(" ", "_").replace("-", "_")

def store_in_graphDB(kg: KnowledgeGraph):
    with driver.session() as session:

        for node in kg.nodes:
            props = property_to_dict(node.properties)
            label = _sanitize_label(node.type)
            session.run(
                f"""
                MERGE (n {{name: $name}})
                SET n:{label}
                SET n += $props
                """,
                name=node.name,
                props=props
            )

        for relation in kg.relationships:
            props    = property_to_dict(relation.properties)  
            rel_type = _sanitize_label(relation.type)
            session.run(
                f"""
                MERGE (a {{name: $source}})
                MERGE (b {{name: $target}})
                MERGE (a)-[r:{rel_type}]->(b)
                SET r += $props
                """,
                source=relation.source,
                target=relation.target,
                props=props
            )

def close_driver():
    driver.close()
    print("Terminating connection with DB")