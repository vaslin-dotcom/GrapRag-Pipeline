graph_extraction_cypher="""
            MATCH path = (n {{name: $name}})-[*1..{k}]-(m)

            WITH n, m, path, relationships(path) AS rels

            UNWIND rels AS rel

            WITH
                n,
                collect(DISTINCT {{
                    neighbor : m.name,
                    type     : labels(m)[0],
                    hops     : length(path)
                }})[..30]                    AS neighbors,
                collect(DISTINCT {{
                    source   : startNode(rel).name,
                    relation : type(rel),
                    target   : endNode(rel).name,
                    hops     : length(path)
                }})[..30]                    AS relationships

            RETURN
                n.name          AS entity,
                labels(n)       AS types,
                properties(n)   AS props,
                neighbors,
                relationships
            """