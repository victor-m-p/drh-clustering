import numpy as np
from scipy.stats import spearmanr
import random

"""
setting up a basic simulation
"""
radius = 10
n_features = 3
n_generations = 20
inherit_prob = 0.95
spawn_board = np.array([[0, 100], [0, 100]])


# Function to check if two cultures overlap
def cultures_overlap(culture1, culture2):
    distance = np.sqrt(
        (culture1[0] - culture2[0]) ** 2 + (culture1[1] - culture2[1]) ** 2
    )
    return distance < (2 * radius)


# Function to inherit or mutate a feature
def inherit_or_mutate(feature, prob):
    return feature if random.random() < prob else 1 - feature


cultures_dict = {}

for generation in range(1, n_generations + 1):
    # Culture label
    culture_label = f"culture_{generation}"

    # Randomly spawn a culture within the board
    new_culture_x = random.uniform(spawn_board[0][0], spawn_board[0][1])
    new_culture_y = random.uniform(spawn_board[1][0], spawn_board[1][1])
    new_culture = [new_culture_x, new_culture_y]

    # Check for overlapping cultures
    overlapping_cultures = [
        label
        for label, culture in cultures_dict.items()
        if cultures_overlap(new_culture, culture["centroid"])
    ]

    if overlapping_cultures:
        # Randomly choose one of the overlapping cultures to inherit from
        parent_culture_label = random.choice(overlapping_cultures)
        parent_culture = cultures_dict[parent_culture_label]
        new_features = [
            inherit_or_mutate(feature, inherit_prob)
            for feature in parent_culture["bit_string"]
        ]
        inheritance = parent_culture_label
    else:
        # Randomly generate features if no overlap
        new_features = [random.randint(0, 1) for _ in range(n_features)]
        inheritance = "none"

    # Add the new culture to the dictionary with generation number and inheritance info
    cultures_dict[culture_label] = {
        "generation": generation,
        "centroid": tuple(new_culture),
        "bit_string": tuple(new_features),
        "inheritance": inheritance,
    }


""" 
visualize and animate the simulation
"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
import os


# Function to plot each generation
def plot_generation(gen, cultures_dict):
    fig, ax = plt.subplots()
    ax.set_xlim(-15, 115)
    ax.set_ylim(-15, 115)
    ax.set_title(f"Generation {gen}")

    # Color mapping for bit strings
    color_map = {
        (0, 0, 0): "tab:red",
        (0, 0, 1): "tab:orange",
        (0, 1, 0): "tab:olive",
        (0, 1, 1): "tab:green",
        (1, 0, 0): "tab:blue",
        (1, 0, 1): "tab:purple",
        (1, 1, 0): "tab:brown",
        (1, 1, 1): "tab:pink",
    }

    # Plotting each culture up to the current generation
    for culture_label, culture_info in cultures_dict.items():
        if culture_info["generation"] <= gen:
            circle = patches.Circle(
                culture_info["centroid"],
                radius,
                color=color_map[culture_info["bit_string"]],
                alpha=0.5,
            )
            ax.add_patch(circle)

    # Saving each plot as an image
    plt.savefig(f"png/generation_{gen}.png")
    plt.close()


# Generate and save plots for each generation
for generation in range(1, n_generations + 1):
    plot_generation(generation, cultures_dict)

# Creating GIF from saved images
images = []
for gen in range(1, n_generations + 1):
    images.append(plt.imread(f"png/generation_{gen}.png"))

# Create an animation
fig, ax = plt.subplots()


def update(frame):
    ax.clear()
    ax.imshow(images[frame])
    ax.axis("off")


ani = FuncAnimation(fig, update, frames=n_generations, interval=500)

# Save the animation
gif_path = "gif/cultural_evolution.gif"
ani.save(gif_path, writer="pillow")

# Clean up the generated image files
# for gen in range(1, n_generations + 1):
#    os.remove(f"png/generation_{gen}.png")


""" 
test statistical relationships
"""


# Function to calculate Hamming distance between two bit strings
def hamming_distance(bit_string1, bit_string2):
    return sum(el1 != el2 for el1, el2 in zip(bit_string1, bit_string2))


# Initialize matrices
n_cultures = len(cultures_dict)
hamming_matrix = np.zeros((n_cultures, n_cultures))
overlap_matrix = np.zeros((n_cultures, n_cultures))

# Populate the matrices
for i, (label1, culture1) in enumerate(cultures_dict.items()):
    for j, (label2, culture2) in enumerate(cultures_dict.items()):
        # Calculate Hamming distance
        hamming_matrix[i, j] = hamming_distance(
            culture1["bit_string"], culture2["bit_string"]
        )

        # Determine overlap (only considering cases where culture2 spawned after culture1)
        if culture2["generation"] > culture1["generation"]:
            overlap_matrix[i, j] = cultures_overlap(
                culture2["centroid"], culture1["centroid"]
            )

# one way of testing, perhaps:
upper_tri_hamming = hamming_matrix[np.triu_indices(10, k=1)]
upper_tri_dependence = overlap_matrix[np.triu_indices(10, k=1)]

correlation, p_value = spearmanr(upper_tri_hamming, upper_tri_dependence)

# another way of testing:
import pymc as pm
import arviz as az

with pm.Model() as model:
    alpha = pm.Normal("mu", mu=0, sigma=10)
    beta = pm.Normal("beta", mu=0, sigma=10)
    sigma = pm.HalfNormal("sigma", sigma=10)
    mu = alpha + beta * upper_tri_dependence
    y = pm.Normal("y", mu=mu, sigma=sigma, observed=upper_tri_hamming)
    trace = pm.sample(1000, tune=1000)

az.summary(trace)

""" 
This makes sense; 
We have 
mu=1.35 (mean value)
beta=-1.35 (from 0-1 as expected: significant)
sigma=0.825 (some noise as expected)
"""
