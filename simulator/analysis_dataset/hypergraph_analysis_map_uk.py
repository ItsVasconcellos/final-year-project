import hypernetx as hnx
import hypernetx.classes.hypergraph as hch
import simulator.network_uk_railway.network as nt
import simulator.network_uk_railway.routes as rt
import plotly.graph_objects as go

def main():
    stations = nt.get_station_with_latitude()
    stations_name_dict = nt.station_code_to_name()
    routes = rt.get_all_routes()
    routes_list = []
    for route in routes.values():
        routes_list.append(route["path"])
    hypergraph: hch.Hypergraph  = hnx.Hypergraph(routes_list)
    node_list = hypergraph.nodes
    centrality = hnx.algorithms.s_betweenness_centrality(hypergraph, edges=False)
    # --- Step 1: Extract data into flat Python lists ---
    lats = []
    lons = []
    names = []
    scores = []
    sorted_centrality = sorted(centrality.items(),key=lambda item:item[1],reverse=True)
    top_10 = sorted_centrality[:10]
    top_10_with_names = []
    for item in top_10:
        station_name = stations_name_dict.get(item[0])
        top_10_with_names.append([station_name,item[1]])
    print(top_10_with_names)
    for station_code, score in centrality.items():
        if station_code in stations:
            coords, name = stations[station_code]
            lats.append(coords[0])
            lons.append(coords[1])
            names.append(name)
            # Scaling: Multiply score by a factor (e.g., 50) so dots are visible
            scores.append(score * 50 + 5) 

    # --- Step 2: Create the plot using Graph Objects ---
    fig = go.Figure(go.Scattermap(
        lat=lats,
        lon=lons,
        mode='markers',
        marker=go.scattermap.Marker(
            size=scores,
            colorscale='Viridis',
            showscale=True
        ),
        text=names,
        hoverinfo='text'
    ))

    # --- Step 3: Configure Layout ---
    fig.update_layout(
        height=1600,
        width=2000,
        map_style="open-street-map",
        map=dict(
            center=dict(lat=54.5057, lon=-1.7274),
            zoom=6
        ),
        margin={"r":0,"t":0,"l":0,"b":0}
    )

    # --- Step 4: Save the image instead of showing ---
    print("Saving map to station_centrality.png...")
    fig.write_image("station_centrality.png", scale=3) # scale=2 improves resolution
    print("Done!")


if __name__ == "__main__":
    main()