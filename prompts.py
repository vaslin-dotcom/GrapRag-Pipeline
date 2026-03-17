system_prompt = """You are a knowledge graph builder.
You MUST always respond by calling the KnowledgeGraph function.
Never respond with plain text or markdown. Always use the function call."""

extraction_prompt="""
Extract all nodes and relationships from the text below.

Rules:
- Node `type` and relationship `type` must be UPPER_SNAKE_CASE e.g. PERSON, WORKS_AT
- Use meaningful, specific relationship types — not just RELATES_TO
- Node `name` should be the canonical name of the entity
- Do NOT escape apostrophes or special characters in entity names
  ✅ correct  : "Storm's End", "King Robert's Rebellion"
  ❌ incorrect : "Storm\\'s End", "King Robert\\'s Rebellion"
- `properties` are optional — only include if clearly stated in the text


IMPORTANT — Be consistent with node types. Always use the same type for the same category:
  PERSON       → for all human characters
  HOUSE        → for all noble houses e.g. House Stark, House Targaryen
  LOCATION     → for all places, cities, regions, castles
  EVENT        → for all wars, rebellions, battles
  ORGANIZATION → for all groups, councils, orders
  OBJECT       → for all physical items, weapons, artifacts
  DYNASTY      → for all ruling dynasties
  TITLE        → for all titles and roles

Only create a new type if none of the above fit.

Text:
{chunk}

"""