import network_tfl.graph as graph
import networkx as nx
import matplotlib.pyplot as plt

g = graph.main()

degrees = dict(g.degree())
node_sizes = [v * 100 for v in degrees.values()] # Scale size by degree

# 2. Advanced Layout
# 'iterations' helps the nodes find better spacing in large graphs
pos = nx.spring_layout(g, k=0.70, iterations=50) 

plt.figure(figsize=(15, 15))

# 3. Draw with transparency
nx.draw_networkx_edges(g, pos, alpha=0.4, edge_color="gray")
nx.draw_networkx_nodes(g, pos, node_size=node_sizes, 
                       node_color=node_sizes, cmap=plt.cm.viridis)

# 4. Label only the 'VIP' nodes (e.g., degree > 10)
labels = {node: node for node, degree in g.degree() if degree > 5}
nx.draw_networkx_labels(g, pos, labels=labels, font_size=10, font_weight='bold')

plt.axis('off')
plt.savefig("./imgs/large_network.jpeg", bbox_inches='tight')