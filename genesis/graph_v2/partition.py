from __future__ import annotations

from typing import Any

from genesis.graph_v2.core import GraphNode, GraphEdge, GraphLayer, UnifiedGraph


class GraphPartition:
    """Graph partitioning and sharding strategies."""

    @staticmethod
    def by_label(layer: GraphLayer) -> dict[str, GraphLayer]:
        from genesis.graph_v2.core import LayerType
        partitions: dict[str, GraphLayer] = {}
        for node in layer._nodes.values():
            primary_label = node.labels[0] if node.labels else "default"
            if primary_label not in partitions:
                sub_layer = GraphLayer(f"{layer.name}_{primary_label}", layer.layer_type)
                sub_layer.add_node(GraphNode(
                    id=node.id, name=node.name, node_type=node.node_type,
                    properties=dict(node.properties), labels=list(node.labels),
                    weight=node.weight,
                ))
                partitions[primary_label] = sub_layer
            else:
                partitions[primary_label]._nodes[node.id] = node
        return partitions

    @staticmethod
    def by_type(layer: GraphLayer) -> dict[str, GraphLayer]:
        from genesis.graph_v2.core import LayerType
        partitions: dict[str, GraphLayer] = {}
        for node in layer._nodes.values():
            t = node.node_type
            if t not in partitions:
                sub_layer = GraphLayer(f"{layer.name}_{t}", layer.layer_type)
                sub_layer._nodes = {}
                sub_layer._edges = {}
                partitions[t] = sub_layer
            partitions[t]._nodes[node.id] = node
        for edge in layer._edges.values():
            src_layer = None
            tgt_layer = None
            for t, sub in partitions.items():
                if edge.source_id in sub._nodes:
                    src_layer = sub
                if edge.target_id in sub._nodes:
                    tgt_layer = sub
            if src_layer and src_layer is tgt_layer:
                src_layer._edges[edge.id] = edge
        return partitions

    @staticmethod
    def random_shard(layer: GraphLayer, num_shards: int) -> list[GraphLayer]:
        from genesis.graph_v2.core import LayerType
        if num_shards < 1:
            num_shards = 1
        shards = [GraphLayer(f"{layer.name}_shard_{i}", layer.layer_type)
                 for i in range(num_shards)]
        for i, node in enumerate(layer._nodes.values()):
            shard_idx = i % num_shards
            shards[shard_idx]._nodes[node.id] = node
        for edge in layer._edges.values():
            for shard in shards:
                if edge.source_id in shard._nodes and edge.target_id in shard._nodes:
                    shard._edges[edge.id] = edge
                    break
        return shards

    @staticmethod
    def summary(partitions: dict[str, GraphLayer]) -> dict[str, Any]:
        return {
            "partitions": len(partitions),
            "by_partition": {k: {"nodes": v.node_count(), "edges": v.edge_count()}
                            for k, v in partitions.items()},
        }
