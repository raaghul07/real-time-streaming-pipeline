from neo4j import GraphDatabase

class Interface:
    def __init__(self, uri, user, password):
        # Establish connection to the Neo4j database
        self._driver = GraphDatabase.driver(uri, auth=(user, password), encrypted=False)
        self._driver.verify_connectivity()

    def close(self):
        # Cleanly shut down the database connection
        self._driver.close()

    def bfs(self, start_node, last_node):
        """
        Execute a BFS from 'start_node' to 'last_node' in an in-memory GDS graph.
        Returns a single-item list containing a dict with the BFS path.
        """

        # Remove 'bfsGraph' if it already exists
        with self._driver.session() as session:
            session.run(
                "CALL gds.graph.exists('bfsGraph') YIELD exists "
                "WITH exists WHERE exists "
                "CALL gds.graph.drop('bfsGraph') YIELD graphName RETURN graphName"
            )

        # Create an in-memory graph projection for BFS
        with self._driver.session() as session:
            session.run("""
                CALL gds.graph.project(
                    'bfsGraph',
                    'Location',
                    {
                        TRIP: {
                            type: 'TRIP',
                            orientation: 'NATURAL'
                        }
                    }
                )
            """)

        # Define the Cypher to run BFS
        bfs_query = """
            MATCH (start:Location {name: $start}), (end:Location {name: $end})
            CALL gds.bfs.stream('bfsGraph', {
                sourceNode: id(start),
                targetNodes: [id(end)]
            })
            YIELD path
            RETURN [node IN nodes(path) | node.name] AS bfsPath
        """

        # Run the BFS and capture the path
        with self._driver.session() as session:
            result = session.run(
                bfs_query, 
                {"start": int(start_node), "end": int(last_node)}
            )
            record = result.single()
            bfs_path = record['bfsPath'] if record else []

        # Release 'bfsGraph' from memory
        with self._driver.session() as session:
            session.run("CALL gds.graph.drop('bfsGraph') YIELD graphName")

        # Return a list whose single element contains the BFS path in the requested format
        return [{"path": [{"name": name} for name in bfs_path]}]

    def pagerank(self, max_iterations, weight_property):
        """
        Runs PageRank on an in-memory GDS graph using 'weight_property' as the
        relationship weight. Returns a 2-element list: 
        [highest_score_node, lowest_score_node]
        """

        with self._driver.session() as session:
            # Create a new GDS graph for PageRank
            session.run(f"""
                CALL gds.graph.project(
                    'pageRankGraph',
                    'Location',
                    {{
                        TRIP: {{
                            orientation: 'NATURAL',
                            properties: ['{weight_property}']
                        }}
                    }}
                )
            """)

            # Perform the PageRank algorithm
            result = session.run(
                """
                CALL gds.pageRank.stream('pageRankGraph', {
                    maxIterations: $max_iter,
                    relationshipWeightProperty: $weight
                })
                YIELD nodeId, score
                RETURN gds.util.asNode(nodeId).name AS name, score
                ORDER BY score DESC
                """,
                {"max_iter": max_iterations, "weight": weight_property}
            )
            output = result.data()

            # Drop the PageRank graph to free memory
            session.run("CALL gds.graph.drop('pageRankGraph')")

        # Return the first (highest) and last (lowest) items in the result list
        return [output[0], output[-1]]
