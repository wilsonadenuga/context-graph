"""Tool definitions shared between Claude and Bedrock adapters."""

import json
from dataclasses import dataclass
from typing import Any, Callable

from ..context_graph_client import context_graph_client
from ..gds_client import gds_client
from ..vector_client import vector_client


@dataclass
class ToolDefinition:
    name: str
    description: str
    parameters: dict
    fn: Callable


# ============================================
# SYSTEM PROMPT
# ============================================

CONTEXT_GRAPH_SYSTEM_PROMPT = """You are an AI assistant for a financial institution with access to a Context Graph.

The Context Graph stores decision traces - the reasoning, context, and causal relationships behind every significant decision made in the organization. This enables you to:

1. **Find Precedents**: Search for similar past decisions to inform current recommendations
2. **Trace Causality**: Understand how past decisions influenced subsequent outcomes
3. **Record Decisions**: Create new decision traces with full reasoning context
4. **Detect Patterns**: Identify fraud patterns and entity duplicates using graph structure

## Key Concepts

**Event Clock vs State Clock**:
- Traditional systems store the "state clock" - what is true right now
- The Context Graph stores the "event clock" - what happened, when, and with what reasoning

**Decision Traces**:
- Every significant decision is recorded with full reasoning
- Risk factors, confidence scores, and applied policies are captured
- Causal chains show how decisions influenced each other

## Guidelines

When helping users:
1. **Always search for precedents** before making recommendations
2. **Explain your reasoning thoroughly** - this becomes part of the decision trace
3. **Cite specific past decisions** when they inform your recommendation
4. **Flag exceptions or escalations** that may be needed
5. **Consider both structural and semantic similarity** when finding related cases

You have access to tools that leverage both:
- **Semantic similarity** (text embeddings) - for matching by meaning
- **Structural similarity** (FastRP graph embeddings) - for matching by relationship patterns

This combination provides insights that are impossible with traditional databases."""


# ============================================
# HELPER FUNCTIONS
# ============================================


def build_agent_message(message: str, conversation_history: list[dict[str, str]] | None) -> str:
    """Format a message with optional conversation history for the agent."""
    if conversation_history:
        history_text = "\n".join(
            [f"{msg['role'].upper()}: {msg['content']}" for msg in conversation_history[-6:]]
        )
        return (
            f"Previous conversation:\n{history_text}\n\n"
            f"Current message from USER: {message}\n\n"
            "Please respond to the current message, taking the conversation history into account."
        )
    return message


def slim_properties(props: dict) -> dict:
    """Remove large properties to reduce response size."""
    slim = {}
    for key, value in props.items():
        if key in ("fast_rp_embedding", "reasoning_embedding", "embedding"):
            continue
        if isinstance(value, str) and len(value) > 200:
            slim[key] = value[:200] + "..."
        elif isinstance(value, list) and len(value) > 10:
            slim[key] = value[:10]
        else:
            slim[key] = value
    return slim


def get_graph_data_for_entity(entity_id: str, depth: int = 2, limit: int = 30) -> dict:
    """Get graph visualization data centered on an entity."""
    try:
        graph_data = context_graph_client.get_graph_data(
            center_node_id=entity_id, depth=depth, limit=limit
        )
        nodes = [
            {
                "id": node.id,
                "labels": node.labels,
                "properties": slim_properties(node.properties),
            }
            for node in graph_data.nodes
        ]
        node_ids = {node["id"] for node in nodes}
        relationships = [
            {
                "id": rel.id,
                "type": rel.type,
                "startNodeId": rel.start_node_id,
                "endNodeId": rel.end_node_id,
                "properties": slim_properties(rel.properties),
            }
            for rel in graph_data.relationships
            if rel.start_node_id in node_ids and rel.end_node_id in node_ids
        ]
        return {"nodes": nodes, "relationships": relationships}
    except Exception as e:
        print(f"Error getting graph data for entity {entity_id}: {e}")
        return {"nodes": [], "relationships": []}


def merge_graph_data(graphs: list[dict], max_nodes: int = 50, max_rels: int = 75) -> dict:
    """Merge multiple graph data objects, removing duplicates and limiting size."""
    all_nodes = {}
    all_relationships = {}
    for graph in graphs:
        if not graph:
            continue
        for node in graph.get("nodes", []):
            if len(all_nodes) < max_nodes:
                all_nodes[node["id"]] = node
        for rel in graph.get("relationships", []):
            if rel.get("startNodeId") in all_nodes and rel.get("endNodeId") in all_nodes:
                if len(all_relationships) < max_rels:
                    all_relationships[rel["id"]] = rel
    return {
        "nodes": list(all_nodes.values()),
        "relationships": list(all_relationships.values()),
    }


# ============================================
# TOOL FUNCTIONS
# ============================================


async def search_customer(args: dict[str, Any]) -> dict[str, Any]:
    try:
        results = context_graph_client.search_customers(
            query=args["query"], limit=args.get("limit", 10)
        )
        graphs = []
        for customer in results[:3]:
            customer_id = customer.get("id")
            if customer_id:
                graphs.append(get_graph_data_for_entity(customer_id, depth=1))
        graph_data = merge_graph_data(graphs) if graphs else {"nodes": [], "relationships": []}
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(
                        {"customers": results, "graph_data": graph_data}, indent=2, default=str
                    ),
                }
            ]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error searching customers: {str(e)}"}],
            "is_error": True,
        }


async def get_customer_decisions(args: dict[str, Any]) -> dict[str, Any]:
    try:
        results = context_graph_client.get_customer_decisions(
            customer_id=args["customer_id"],
            decision_type=args.get("decision_type"),
            limit=args.get("limit", 20),
        )
        graph_data = get_graph_data_for_entity(args["customer_id"], depth=2)
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(
                        {"decisions": results, "graph_data": graph_data}, indent=2, default=str
                    ),
                }
            ]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error getting decisions: {str(e)}"}],
            "is_error": True,
        }


async def find_similar_decisions(args: dict[str, Any]) -> dict[str, Any]:
    try:
        decision_id = args["decision_id"]
        limit = int(args.get("limit", 10))
        similar_decisions = gds_client.find_similar_decisions(decision_id, limit=limit)
        graph_data = get_graph_data_for_entity(decision_id, depth=2)
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(
                        {"similar_decisions": similar_decisions, "graph_data": graph_data},
                        indent=2,
                        default=str,
                    ),
                }
            ]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error finding similar decisions: {str(e)}"}],
            "is_error": True,
        }


async def find_precedents(args: dict[str, Any]) -> dict[str, Any]:
    try:
        results = vector_client.find_precedents_hybrid(
            scenario=args["scenario"], category=args.get("category"), limit=args.get("limit", 5)
        )
        graph_data = None
        if results:
            first_id = results[0].get("id") if isinstance(results[0], dict) else None
            if first_id:
                graph_data = get_graph_data_for_entity(first_id, depth=2)
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(
                        {"precedents": results, "graph_data": graph_data}, indent=2, default=str
                    ),
                }
            ]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error finding precedents: {str(e)}"}],
            "is_error": True,
        }


async def get_causal_chain(args: dict[str, Any]) -> dict[str, Any]:
    try:
        results = context_graph_client.get_causal_chain(
            decision_id=args["decision_id"],
            direction=args.get("direction", "both"),
            depth=args.get("depth", 3),
        )
        graph_data = get_graph_data_for_entity(args["decision_id"], depth=3)
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(
                        {"causal_chain": results, "graph_data": graph_data}, indent=2, default=str
                    ),
                }
            ]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error getting causal chain: {str(e)}"}],
            "is_error": True,
        }


async def record_decision(args: dict[str, Any]) -> dict[str, Any]:
    try:
        reasoning_embedding = None
        try:
            reasoning_embedding = vector_client.generate_embedding(args["reasoning"])
        except Exception:
            pass
        decision_id = context_graph_client.record_decision(
            decision_type=args["decision_type"],
            category=args["category"],
            reasoning=args["reasoning"],
            customer_id=args.get("customer_id"),
            account_id=args.get("account_id"),
            risk_factors=args.get("risk_factors", []),
            precedent_ids=args.get("precedent_ids", []),
            confidence_score=args.get("confidence_score", 0.8),
            reasoning_embedding=reasoning_embedding,
        )
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(
                        {
                            "success": True,
                            "decision_id": decision_id,
                            "message": f"Decision recorded successfully with ID {decision_id}",
                        },
                        indent=2,
                    ),
                }
            ]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error recording decision: {str(e)}"}],
            "is_error": True,
        }


async def detect_fraud_patterns(args: dict[str, Any]) -> dict[str, Any]:
    try:
        neighbor_count = int(args.get("neighbor_count", 5))
        results = gds_client.detect_fraud_patterns(
            account_id=args.get("account_id"),
            neighbor_count=neighbor_count,
        )
        return {"content": [{"type": "text", "text": json.dumps(results, indent=2, default=str)}]}
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error detecting fraud patterns: {str(e)}"}],
            "is_error": True,
        }


async def find_decision_community(args: dict[str, Any]) -> dict[str, Any]:
    decision_id = args["decision_id"]
    try:
        example_count = int(args.get("example_count", 5))
        results = gds_client.get_decision_community(
            decision_id=decision_id, example_count=example_count
        )
        graph_data = get_graph_data_for_entity(decision_id, depth=2)
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(
                        {"community_decisions": results, "graph_data": graph_data},
                        indent=2,
                        default=str,
                    ),
                }
            ]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error finding community: {str(e)}"}],
            "is_error": True,
        }


async def find_accounts_with_high_shared_transaction_volume(args: dict[str, Any]) -> dict[str, Any]:
    try:
        results = gds_client.find_accounts_with_high_shared_transaction_volume(
            account_id=args.get("account_id")
        )
        return {"content": [{"type": "text", "text": json.dumps(results, indent=2, default=str)}]}
    except Exception as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Error finding accounts with high shared transaction volume: {str(e)}",
                }
            ],
            "is_error": True,
        }


async def get_policy(args: dict[str, Any]) -> dict[str, Any]:
    try:
        policies = context_graph_client.get_policies(category=args.get("category"))
        if args.get("policy_name"):
            stop_words = {"the", "a", "an", "for", "and", "or", "of", "in", "to", "with"}
            search_words = [
                word.lower()
                for word in args["policy_name"].split()
                if word.lower() not in stop_words and len(word) > 2
            ]
            scored_policies = []
            for policy in policies:
                policy_name_lower = policy.get("name", "").lower()
                matches = sum(1 for word in search_words if word in policy_name_lower)
                if matches > 0:
                    scored_policies.append({"policy": policy, "relevance_score": matches})
            scored_policies.sort(key=lambda x: x["relevance_score"], reverse=True)
            if scored_policies:
                results = {
                    "matching_policies": [
                        {**sp["policy"], "relevance_score": sp["relevance_score"]}
                        for sp in scored_policies
                    ],
                    "search_terms": search_words,
                    "total_matches": len(scored_policies),
                }
            else:
                results = {
                    "matching_policies": [],
                    "search_terms": search_words,
                    "total_matches": 0,
                    "all_policies_in_category": policies,
                    "note": f"No policies matched '{args['policy_name']}'. Showing all policies in category.",
                }
        else:
            results = policies
        return {"content": [{"type": "text", "text": json.dumps(results, indent=2, default=str)}]}
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error getting policy: {str(e)}"}],
            "is_error": True,
        }


async def execute_cypher(args: dict[str, Any]) -> dict[str, Any]:
    try:
        results = context_graph_client.execute_cypher(cypher=args["cypher"])
        return {"content": [{"type": "text", "text": json.dumps(results, indent=2, default=str)}]}
    except ValueError as e:
        return {
            "content": [{"type": "text", "text": f"Query not allowed: {str(e)}"}],
            "is_error": True,
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error executing query: {str(e)}"}],
            "is_error": True,
        }


async def get_schema(args: dict[str, Any]) -> dict[str, Any]:
    try:
        schema = context_graph_client.get_schema()
        return {"content": [{"type": "text", "text": json.dumps(schema, indent=2, default=str)}]}
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Error getting schema: {str(e)}"}],
            "is_error": True,
        }


# ============================================
# TOOL REGISTRY
# ============================================

TOOL_DEFINITIONS: list[ToolDefinition] = [
    ToolDefinition(
        name="search_customer",
        description="Search for customers by name, email, or account number. Returns customer profiles with risk scores and related account counts.",
        parameters={"query": str, "limit": int},
        fn=search_customer,
    ),
    ToolDefinition(
        name="get_customer_decisions",
        description="Get all decisions made about a specific customer, including approvals, rejections, escalations, and exceptions.",
        parameters={"customer_id": str, "decision_type": str, "limit": int},
        fn=get_customer_decisions,
    ),
    ToolDefinition(
        name="find_similar_decisions",
        description="Find structurally similar past decisions using FastRP graph embeddings. Returns decisions with similar influences, causes, and precedents as well as decisions about related accounts.",
        parameters={
            "decision_id": {"type": str, "description": "The internal decision ID (decision.id)"},
            "limit": {
                "type": int,
                "description": "Number of similar decisions to return",
                "default": 5,
            },
        },
        fn=find_similar_decisions,
    ),
    ToolDefinition(
        name="find_precedents",
        description="Find precedent decisions that could inform the current decision. Uses both semantic similarity (meaning) and structural similarity (graph patterns).",
        parameters={"scenario": str, "category": str, "limit": int},
        fn=find_precedents,
    ),
    ToolDefinition(
        name="get_causal_chain",
        description="Trace the causal chain of a decision - what caused it and what it led to. Useful for understanding decision impact and history.",
        parameters={"decision_id": str, "direction": str, "depth": int},
        fn=get_causal_chain,
    ),
    ToolDefinition(
        name="record_decision",
        description="Record a new decision with full reasoning context. Creates a decision trace in the context graph that can be referenced by future decisions.",
        parameters={
            "decision_type": str,
            "category": str,
            "reasoning": str,
            "customer_id": str,
            "account_id": str,
            "risk_factors": list,
            "precedent_ids": list,
            "confidence_score": float,
        },
        fn=record_decision,
    ),
    ToolDefinition(
        name="detect_fraud_patterns",
        description="Analyze accounts or transactions for potential fraud patterns using graph structure analysis. Checks an account's proximity to flagged transactions as well as the prevalence of flagged transactions in the community of related accounts.",
        parameters={
            "account_id": {
                "type": str,
                "description": "The internal account ID (account.id), not the customer-facing account number (account.account_number)",
            },
            "neighbor_count": {
                "type": int,
                "description": "Number of example decisions to return from the community",
                "default": 5,
            },
        },
        fn=detect_fraud_patterns,
    ),
    ToolDefinition(
        name="find_decision_community",
        description="Find decisions in the same community using Leiden community detection. Returns decisions that are structurally related through causal chains and precedent relationships.",
        parameters={
            "decision_id": {"type": str, "description": "The internal decision ID (decision.id)"},
            "example_count": {
                "type": int,
                "description": "Number of example decisions to return from the community",
                "default": 5,
            },
        },
        fn=find_decision_community,
    ),
    ToolDefinition(
        name="find_accounts_with_high_shared_transaction_volume",
        description="Find accounts that share high transaction volumes with a given account.",
        parameters={
            "account_id": {
                "type": str,
                "description": "The internal account ID (account.id), not the customer-facing account number (account.account_number)",
            },
        },
        fn=find_accounts_with_high_shared_transaction_volume,
    ),
    ToolDefinition(
        name="get_policy",
        description="Get the current policy rules for a specific category. Returns policy details including thresholds and requirements. If policy_name is provided, returns policies matching any words in the name.",
        parameters={"category": str, "policy_name": str},
        fn=get_policy,
    ),
    ToolDefinition(
        name="execute_cypher",
        description="Execute a read-only Cypher query against the context graph for custom analysis. Only SELECT/MATCH queries are allowed.",
        parameters={"cypher": str},
        fn=execute_cypher,
    ),
    ToolDefinition(
        name="get_schema",
        description="Get the graph database schema including node labels, relationship types, property keys, indexes, and constraints. Also returns counts for each node label and relationship type.",
        parameters={},
        fn=get_schema,
    ),
]

TOOL_REGISTRY: dict[str, ToolDefinition] = {td.name: td for td in TOOL_DEFINITIONS}
AVAILABLE_TOOLS: list[str] = [td.name for td in TOOL_DEFINITIONS]
