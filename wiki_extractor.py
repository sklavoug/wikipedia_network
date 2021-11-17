# -*- coding: utf-8 -*-
"""
Created on Tue Nov 16 17:24:10 2021

@author: Arden Morbe
"""

import networkx as nx
from urllib.request import urlopen
import pandas as pd
from bs4 import *
import plotly.graph_objs as go
import plotly
import random

def wiki_graph(link, breadth=2):
    
    # Extract links from a given Wikipedia page, add to an expanding dataframe,
    # and return in graph form.
    
    # breadth is how many pages to return, set to two by default (i.e., three
    # total pages).
    
    # Get only the 'a' tags in the page which start with '/wiki'
    def extract(url_suffix):
        with urlopen(f'https://en.wikipedia.org/wiki/{url_suffix}') as response:
            soup = BeautifulSoup(response, 'html.parser')
            
            links = []
            
            for anchor in soup.find_all('a'):
                ref = anchor.get('href', '/')
                if ref[:5] == '/wiki' and ':' not in ref and ref[6:] != url_suffix:
                    links.append(ref[6:])
            
            return links
    
    # Create a dataframe from the initial extract, and set 'Origin' to the
    # page the links were found in.
    text = link
    links = extract(text)
    
    df = pd.DataFrame(links)
    
    df = df.rename(columns={0: 'Link'})
    df['Origin'] = text
    
    # Then for each link in that page, up to breadth, get links from those pages.
    for idx, i in enumerate(list(df['Link'])):
        if idx < breadth:
            links = extract(i)
            temp = pd.DataFrame(links)
            temp = temp.rename(columns={0: 'Link'})
            temp['Origin'] = i
            df = df.append(temp)
    
    print('Dataframe created')
    
    # Generate graph
    G = nx.from_pandas_edgelist(df, 'Origin', 'Link')
    
    return df, G


def visualise_network(pos, df, G, origin):
    
    # Visualise the network diagram as a Plotly scatterplot.
    edge_x = []
    edge_y = []
    
    # Create line for each edge
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)
    
    # Generate scatterplot of the lines
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')
    
    node_x = []
    node_y = []
    
    # Create marker for each node
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
    
    # Generate scatterplot of nodes
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        # hovertext=df['Link'],
        marker=dict(
            showscale=True,
            # colorscale options
            #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
            #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
            #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
            colorscale='RdBu',
            reversescale=True,
            color=[],
            size=10,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            )))
    
    # Colour nodes based on number of adjacencies
    node_adjacencies = []
    node_text = []
    for node, adjacencies in enumerate(G.adjacency()):
        node_adjacencies.append(len(adjacencies[1]))
        node_text.append(f'Page: {adjacencies[0]}<br># of connections: '+str(len(adjacencies[1])))
    
    node_trace.marker.color = node_adjacencies
    node_trace.text = node_text
    
    # Generate plot
    fig = go.Figure(data=[edge_trace, node_trace],
                 layout=go.Layout(
                    title=f'<br>Links between Wikipedia Pages (starting with {origin})',
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    annotations=[ dict(
                        text="Visualisation code sourced from Plotly: <a href='https://plotly.com/ipython-notebooks/network-graphs/'> https://plotly.com/ipython-notebooks/network-graphs/</a>",
                        showarrow=False,
                        xref="paper", yref="paper",
                        x=0.005, y=-0.002 ) ],
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    
    print('Graph created')
    # Change background colour
    fig.layout.plot_bgcolor = 'lightsteelblue'
    
    plotly.offline.plot(fig, filename='file.html')
    print('File saved')

origin = 'Beautiful_Soup_(HTML_parser)'

# Create dataframe and graph
df, G = wiki_graph(origin, 3)

# Generate a count of each page (currently unused)
df['Count'] = 1
df = df.groupby(by=['Link','Origin']).count()
df = df.reset_index(drop=False)

# Generate positions for each node
pos = {}
for node in G.nodes():
    pos[node] = (random.randrange(0,10000) / 10000, random.randrange(0,10000) / 10000)

# Visualise and save to html
visualise_network(pos, df, G, origin)

