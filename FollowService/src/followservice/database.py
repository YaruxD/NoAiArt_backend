from neo4j import GraphDatabase
from typing import Generator

URI = "bolt://neo4j:7687"
USER = "neo4j"
PASSWORD = "97121104"

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))


def get_session() -> Generator:
    with driver.session() as session:
        yield session