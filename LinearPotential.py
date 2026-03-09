import networkx as nx
import matplotlib.pyplot as plt
import itertools
import random
from IPython.display import clear_output

# ======================
# Utility functions
# ======================

def target_edges(n, target):
    """Return all edge sets that form the target cycle."""
    nodes = list(range(n))
    k = int(target[1])
    subgraphs = []

    for combo in itertools.combinations(nodes, k):
        cycle_edges = [(combo[i], combo[(i+1)%k]) for i in range(k)]
        subgraphs.append(set(tuple(sorted(e)) for e in cycle_edges))

    return subgraphs


def check_maker_win(maker_edges, target_subgraphs):

    maker_set = set(tuple(sorted(e)) for e in maker_edges)

    for sub in target_subgraphs:
        if sub.issubset(maker_set):
            return True

    return False


# ======================
# Potential Function
# ======================

def game_potential(maker_edges, breaker_edges, target_subgraphs):

    maker_set = set(tuple(sorted(e)) for e in maker_edges)
    breaker_set = set(tuple(sorted(e)) for e in breaker_edges)

    # Maker win
    for sub in target_subgraphs:
        if sub.issubset(maker_set):
            return 1.0

    total = 0
    active = 0

    for sub in target_subgraphs:

        # If breaker blocks this subgraph → potential 0
        if any(e in breaker_set for e in sub):
            continue

        active += 1

        maker_count = len(sub & maker_set)
        total += maker_count / len(sub)

    # Breaker has blocked all targets
    if active == 0:
        return 0.0

    return total / len(target_subgraphs)


# ======================
# Graph drawing
# ======================

def draw_graph(G, maker_edges, breaker_edges, pos):

    plt.clf()

    nx.draw_networkx_nodes(G, pos,
                           node_color="lightgrey",
                           node_size=500)

    remaining_edges = [
        e for e in G.edges()
        if e not in maker_edges and e not in breaker_edges
    ]

    nx.draw_networkx_edges(G, pos,
                           edgelist=remaining_edges,
                           edge_color="grey",
                           style="dotted",
                           width=1.5)

    nx.draw_networkx_edges(G, pos,
                           edgelist=maker_edges,
                           edge_color="red",
                           width=2)

    nx.draw_networkx_edges(G, pos,
                           edgelist=breaker_edges,
                           edge_color="blue",
                           width=2)

    nx.draw_networkx_labels(G, pos)

    plt.axis("off")
    plt.title("Maker (Red) vs Breaker (Blue)")
    plt.show(block=False)
    plt.pause(0.1)


# ======================
# Game Setup
# ======================

n = int(input("Enter number of nodes (n) for complete graph K_n: "))
q = int(input("Enter bias q (Breaker claims q edges per turn): "))
target_choice = input("Enter target subgraph (C3, C4, or C5): ").upper()

G = nx.complete_graph(n)
pos = nx.spring_layout(G, seed=42)

target_subgraphs = target_edges(n, target_choice)

maker_edges = []
breaker_edges = []

available_edges = list(G.edges())
random.shuffle(available_edges)

clear_output(wait=True)

print(f"Game started: Maker–Breaker on K{n} with bias q={q} and target={target_choice}\n")

draw_graph(G, maker_edges, breaker_edges, pos)

print("Initial Potential:", round(game_potential(maker_edges, breaker_edges, target_subgraphs),4))


# ======================
# Gameplay Loop
# ======================

turn = 1

while available_edges:

    print(f"\n--- Turn {turn} ---")

    # Maker move
    maker_move = input("Maker move (u v): ")

    try:
        u, v = map(int, maker_move.split())
        edge = tuple(sorted((u,v)))

        if edge not in available_edges:
            print("Invalid edge")
            continue

    except:
        print("Invalid input")
        continue

    maker_edges.append(edge)
    available_edges.remove(edge)

    draw_graph(G, maker_edges, breaker_edges, pos)

    pot = game_potential(maker_edges, breaker_edges, target_subgraphs)
    print("Potential after Maker move:", round(pot,4))

    if pot == 1:
        print(" Maker wins!")
        break


    # Breaker moves
    for i in range(q):

        if not available_edges:
            break

        breaker_move = input(f"Breaker move {i+1}/{q} (u v): ")

        try:
            u, v = map(int, breaker_move.split())
            edge = tuple(sorted((u,v)))

            if edge not in available_edges:
                print("Invalid edge")
                continue

        except:
            print("Invalid input")
            continue

        breaker_edges.append(edge)
        available_edges.remove(edge)

        draw_graph(G, maker_edges, breaker_edges, pos)

        pot = game_potential(maker_edges, breaker_edges, target_subgraphs)
        print("Potential after Breaker move:", round(pot,4))

        if pot == 0:
            print(" Breaker has blocked all targets!")
            break

    if pot == 0:
        break

    turn += 1


print("\nFinal Board:")
draw_graph(G, maker_edges, breaker_edges, pos)
