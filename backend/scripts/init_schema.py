"""
Run schema.cypher against Neo4j to set up constraints and indexes.
Safe to run on every startup — all statements use IF NOT EXISTS.
"""

import os
import sys
import time

from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")
SCHEMA_PATH = os.getenv("SCHEMA_PATH", "/app/cypher/schema.cypher")


def wait_for_neo4j(driver, retries=30, delay=2):
    for i in range(1, retries + 1):
        try:
            driver.verify_connectivity()
            print("Neo4j is ready.")
            return
        except ServiceUnavailable:
            print(f"Waiting for Neo4j... ({i}/{retries})")
            time.sleep(delay)
    print("Neo4j not ready after retries, exiting.")
    sys.exit(1)


def parse_statements(cypher_text):
    statements = []
    for raw in cypher_text.split(";"):
        # Strip comments and whitespace
        lines = [l for l in raw.splitlines() if not l.strip().startswith("//")]
        stmt = " ".join(lines).strip()
        if stmt:
            statements.append(stmt)
    return statements


def run_schema(driver):
    with open(SCHEMA_PATH, "r") as f:
        cypher_text = f.read()

    statements = parse_statements(cypher_text)

    with driver.session(database=NEO4J_DATABASE) as session:
        for stmt in statements:
            try:
                session.run(stmt)
            except Exception as e:
                print(f"Warning: {e} — statement: {stmt[:80]}...")

    print(f"Schema applied ({len(statements)} statements).")


if __name__ == "__main__":
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    try:
        wait_for_neo4j(driver)
        run_schema(driver)
    finally:
        driver.close()
