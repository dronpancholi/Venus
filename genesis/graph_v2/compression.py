from __future__ import annotations

import gzip
import json
from typing import Any

from genesis.graph_v2.core import GraphLayer, GraphNode, GraphEdge


class GraphCompression:
    """Compression and serialization for graph layers."""

    @staticmethod
    def serialize_layer(layer: GraphLayer) -> bytes:
        data = {
            "name": layer.name,
            "layer_type": layer.layer_type.value,
            "nodes": [
                {"id": n.id, "name": n.name, "type": n.node_type,
                 "properties": n.properties, "labels": n.labels, "weight": n.weight}
                for n in layer._nodes.values()
            ],
            "edges": [
                {"id": e.id, "source": e.source_id, "target": e.target_id,
                 "type": e.edge_type, "properties": e.properties, "weight": e.weight}
                for e in layer._edges.values()
            ],
        }
        raw = json.dumps(data, default=str, sort_keys=True).encode()
        return gzip.compress(raw, compresslevel=6)

    @staticmethod
    def deserialize_layer(data: bytes) -> GraphLayer:
        from genesis.graph_v2.core import LayerType
        raw = gzip.decompress(data)
        parsed = json.loads(raw.decode())
        layer = GraphLayer(parsed["name"], LayerType(parsed["layer_type"]))
        for nd in parsed.get("nodes", []):
            layer.add_node(GraphNode(
                id=nd["id"], name=nd.get("name", ""), node_type=nd.get("type", "entity"),
                properties=nd.get("properties", {}), labels=nd.get("labels", []),
                weight=nd.get("weight", 1.0),
            ))
        for ed in parsed.get("edges", []):
            layer.add_edge(GraphEdge(
                id=ed["id"], source_id=ed["source"], target_id=ed["target"],
                edge_type=ed.get("type", "related"),
                properties=ed.get("properties", {}), weight=ed.get("weight", 1.0),
            ))
        return layer

    @staticmethod
    def compression_ratio(layer: GraphLayer) -> float:
        raw = sum(len(json.dumps(n.__dict__, default=str)) for n in layer._nodes.values())
        raw += sum(len(json.dumps(e.__dict__, default=str)) for e in layer._edges.values())
        compressed = len(GraphCompression.serialize_layer(layer))
        return raw / max(compressed, 1)

    @staticmethod
    def strip_properties(layer: GraphLayer) -> GraphLayer:
        from genesis.graph_v2.core import LayerType
        stripped = GraphLayer(f"{layer.name}_stripped", layer.layer_type)
        for node in layer._nodes.values():
            stripped.add_node(GraphNode(
                id=node.id, name=node.name, node_type=node.node_type,
                properties={}, labels=list(node.labels), weight=node.weight,
            ))
        for edge in layer._edges.values():
            stripped.add_edge(GraphEdge(
                id=edge.id, source_id=edge.source_id, target_id=edge.target_id,
                edge_type=edge.edge_type, properties={}, weight=edge.weight,
            ))
        return stripped
