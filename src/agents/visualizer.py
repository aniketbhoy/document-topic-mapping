"""Visualizer Agent - Generate visual representations of topic relationships."""

from typing import List, Dict
from loguru import logger
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages
import networkx as nx
from ..models import Topic, Anomaly
from ..utils import GraphBuilder


class VisualizerAgent:
    """Agent responsible for generating visualizations."""

    def __init__(self):
        """Initialize the visualizer agent."""
        self.color_map = {
            "hierarchical": "#4CAF50",  # Green
            "cross_reference": "#2196F3",  # Blue
            "forward_reference": "#FF9800",  # Orange
            "backward_reference": "#9C27B0",  # Purple
            "broken": "#F44336",  # Red
            "anomaly": "#FFD700"  # Gold
        }

    def visualize(
        self,
        graph_builder: GraphBuilder,
        anomalies: List[Anomaly],
        output_path: str
    ):
        """
        Generate visualization of topic relationships.

        Args:
            graph_builder: Graph builder with relationships
            anomalies: List of detected anomalies
            output_path: Output PDF path
        """
        logger.info("Generating visualization")

        try:
            # Create figure
            fig, ax = plt.subplots(figsize=(16, 12))

            # Get graph
            G = graph_builder.graph

            # Create layout
            pos = self._create_layout(G)

            # Draw nodes
            self._draw_nodes(G, pos, anomalies, ax)

            # Draw edges
            self._draw_edges(G, pos, ax)

            # Add legend
            self._add_legend(ax)

            # Add title and metadata
            self._add_metadata(G, anomalies, ax)

            # Save to PDF
            plt.tight_layout()
            plt.savefig(output_path, format='pdf', bbox_inches='tight', dpi=300)
            plt.close()

            logger.info(f"Visualization saved to {output_path}")
        except Exception as e:
            logger.error(f"Visualization failed: {e}")
            raise

    def _create_layout(self, G: nx.DiGraph) -> Dict:
        """
        Create layout for graph visualization.

        Args:
            G: NetworkX graph

        Returns:
            Dictionary of node positions
        """
        try:
            # Try hierarchical layout first
            pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
        except Exception as e:
            logger.warning(f"Spring layout failed, using shell layout: {e}")
            pos = nx.shell_layout(G)

        return pos

    def _draw_nodes(
        self,
        G: nx.DiGraph,
        pos: Dict,
        anomalies: List[Anomaly],
        ax
    ):
        """
        Draw nodes with color coding for anomalies.

        Args:
            G: NetworkX graph
            pos: Node positions
            anomalies: List of anomalies
            ax: Matplotlib axis
        """
        # Identify anomalous nodes
        anomaly_nodes = set()
        for anomaly in anomalies:
            anomaly_nodes.update(anomaly.affected_topics)

        # Separate normal and anomalous nodes
        normal_nodes = [n for n in G.nodes() if n not in anomaly_nodes]
        anomalous_nodes = [n for n in G.nodes() if n in anomaly_nodes]

        # Draw normal nodes
        nx.draw_networkx_nodes(
            G, pos,
            nodelist=normal_nodes,
            node_color='lightblue',
            node_size=800,
            alpha=0.7,
            ax=ax
        )

        # Draw anomalous nodes
        if anomalous_nodes:
            nx.draw_networkx_nodes(
                G, pos,
                nodelist=anomalous_nodes,
                node_color=self.color_map["anomaly"],
                node_size=1000,
                alpha=0.9,
                ax=ax
            )

        # Draw labels
        nx.draw_networkx_labels(
            G, pos,
            font_size=8,
            font_weight='bold',
            ax=ax
        )

    def _draw_edges(self, G: nx.DiGraph, pos: Dict, ax):
        """
        Draw edges with color coding by type.

        Args:
            G: NetworkX graph
            pos: Node positions
            ax: Matplotlib axis
        """
        # Group edges by type
        edge_types = {}
        for u, v, data in G.edges(data=True):
            edge_type = data.get('type', 'unknown')
            status = data.get('status', 'valid')

            # Use status if broken
            if status == 'broken':
                edge_type = 'broken'

            if edge_type not in edge_types:
                edge_types[edge_type] = []
            edge_types[edge_type].append((u, v))

        # Draw each type with different color
        for edge_type, edges in edge_types.items():
            color = self.color_map.get(edge_type, '#888888')
            style = 'dashed' if edge_type == 'broken' else 'solid'
            width = 2.0 if edge_type == 'hierarchical' else 1.0

            nx.draw_networkx_edges(
                G, pos,
                edgelist=edges,
                edge_color=color,
                style=style,
                width=width,
                alpha=0.6,
                arrows=True,
                arrowsize=15,
                ax=ax,
                connectionstyle="arc3,rad=0.1"
            )

    def _add_legend(self, ax):
        """
        Add legend explaining colors and styles.

        Args:
            ax: Matplotlib axis
        """
        legend_elements = [
            mpatches.Patch(color=self.color_map["hierarchical"], label='Hierarchical'),
            mpatches.Patch(color=self.color_map["cross_reference"], label='Cross Reference'),
            mpatches.Patch(color=self.color_map["forward_reference"], label='Forward Reference'),
            mpatches.Patch(color=self.color_map["backward_reference"], label='Backward Reference'),
            mpatches.Patch(color=self.color_map["broken"], label='Broken Reference'),
            mpatches.Patch(color=self.color_map["anomaly"], label='Anomalous Topic')
        ]

        ax.legend(
            handles=legend_elements,
            loc='upper right',
            fontsize=10,
            framealpha=0.9
        )

    def _add_metadata(self, G: nx.DiGraph, anomalies: List[Anomaly], ax):
        """
        Add title and metadata to visualization.

        Args:
            G: NetworkX graph
            anomalies: List of anomalies
            ax: Matplotlib axis
        """
        # Title
        ax.set_title(
            "Document Topic Relationship Map",
            fontsize=16,
            fontweight='bold',
            pad=20
        )

        # Statistics text
        stats_text = f"""
Statistics:
• Topics: {G.number_of_nodes()}
• Relationships: {G.number_of_edges()}
• Anomalies: {len(anomalies)}
"""

        # Add text box
        ax.text(
            0.02, 0.98,
            stats_text,
            transform=ax.transAxes,
            fontsize=10,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        )

        ax.axis('off')

    def generate_multiple_views(
        self,
        graph_builder: GraphBuilder,
        anomalies: List[Anomaly],
        output_path: str
    ):
        """
        Generate multiple visualization views in a single PDF.

        Args:
            graph_builder: Graph builder
            anomalies: List of anomalies
            output_path: Output PDF path
        """
        logger.info("Generating multiple visualization views")

        try:
            with PdfPages(output_path) as pdf:
                # View 1: Full graph
                self._create_full_view(graph_builder, anomalies, pdf)

                # View 2: Hierarchical view
                self._create_hierarchical_view(graph_builder, pdf)

                # View 3: Cross-references only
                self._create_cross_reference_view(graph_builder, pdf)

                # View 4: Anomalies focus
                if anomalies:
                    self._create_anomaly_view(graph_builder, anomalies, pdf)

            logger.info(f"Multi-view visualization saved to {output_path}")
        except Exception as e:
            logger.error(f"Multi-view visualization failed: {e}")
            raise

    def _create_full_view(self, graph_builder: GraphBuilder, anomalies: List[Anomaly], pdf):
        """Create full graph view."""
        fig, ax = plt.subplots(figsize=(16, 12))
        G = graph_builder.graph
        pos = self._create_layout(G)
        self._draw_nodes(G, pos, anomalies, ax)
        self._draw_edges(G, pos, ax)
        self._add_legend(ax)
        ax.set_title("Full Topic Relationship Map", fontsize=16, fontweight='bold')
        ax.axis('off')
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

    def _create_hierarchical_view(self, graph_builder: GraphBuilder, pdf):
        """Create hierarchical relationships view."""
        fig, ax = plt.subplots(figsize=(16, 12))
        G = graph_builder.graph

        # Filter to hierarchical edges only
        H = nx.DiGraph()
        for u, v, data in G.edges(data=True):
            if data.get('type') == 'hierarchical':
                H.add_edge(u, v, **data)

        # Add all nodes
        for node in G.nodes(data=True):
            H.add_node(node[0], **node[1])

        if H.number_of_edges() > 0:
            try:
                pos = nx.spring_layout(H, k=3, iterations=50)
            except:
                pos = nx.shell_layout(H)

            nx.draw_networkx_nodes(H, pos, node_color='lightgreen', node_size=1000, ax=ax)
            nx.draw_networkx_labels(H, pos, font_size=8, font_weight='bold', ax=ax)
            nx.draw_networkx_edges(
                H, pos,
                edge_color=self.color_map["hierarchical"],
                width=2.0,
                arrows=True,
                arrowsize=20,
                ax=ax
            )

        ax.set_title("Hierarchical Structure", fontsize=16, fontweight='bold')
        ax.axis('off')
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

    def _create_cross_reference_view(self, graph_builder: GraphBuilder, pdf):
        """Create cross-references view."""
        fig, ax = plt.subplots(figsize=(16, 12))
        G = graph_builder.graph

        # Filter to cross-reference edges only
        C = nx.DiGraph()
        for u, v, data in G.edges(data=True):
            if 'reference' in data.get('type', ''):
                C.add_edge(u, v, **data)

        # Add all nodes
        for node in G.nodes(data=True):
            C.add_node(node[0], **node[1])

        if C.number_of_edges() > 0:
            try:
                pos = nx.spring_layout(C, k=3, iterations=50)
            except:
                pos = nx.shell_layout(C)

            nx.draw_networkx_nodes(C, pos, node_color='lightcoral', node_size=1000, ax=ax)
            nx.draw_networkx_labels(C, pos, font_size=8, font_weight='bold', ax=ax)
            nx.draw_networkx_edges(
                C, pos,
                edge_color=self.color_map["cross_reference"],
                width=1.5,
                arrows=True,
                arrowsize=15,
                ax=ax,
                connectionstyle="arc3,rad=0.2"
            )

        ax.set_title("Cross-References", fontsize=16, fontweight='bold')
        ax.axis('off')
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

    def _create_anomaly_view(self, graph_builder: GraphBuilder, anomalies: List[Anomaly], pdf):
        """Create anomalies focus view."""
        fig, ax = plt.subplots(figsize=(16, 12))

        # Create text summary of anomalies
        ax.axis('off')
        ax.set_title("Anomaly Report", fontsize=16, fontweight='bold')

        # Group anomalies by type
        anomaly_groups = {}
        for anomaly in anomalies:
            if anomaly.type not in anomaly_groups:
                anomaly_groups[anomaly.type] = []
            anomaly_groups[anomaly.type].append(anomaly)

        # Create text
        y_pos = 0.95
        for anom_type, anoms in anomaly_groups.items():
            text = f"\n{anom_type.replace('_', ' ').title()} ({len(anoms)}):\n"
            for i, anom in enumerate(anoms[:10], 1):  # Limit to 10 per type
                text += f"  {i}. {anom.location}: {anom.description}\n"

            ax.text(
                0.05, y_pos,
                text,
                transform=ax.transAxes,
                fontsize=10,
                verticalalignment='top',
                fontfamily='monospace'
            )
            y_pos -= 0.15

        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
