# Leon Gurtler
import numpy as np
import gym, time, random

# for visualization
import matplotlib.pyplot as plt
from tabulate import tabulate
plt.style.use("seaborn")


env = gym.make("CartPole-v0")
n = len(env.observation_space.sample()) # n = number of features
num_labels = env.action_space.n


# GA CONSTANTS
GENERATION_SIZE = 48
EPOCHS = 35
KEEP_BEST_N = 8
ASSESS_N_GAMES = 3

MUTATION_RATE = .7
MUTATION_PROB = .7



def initialize_rndom_weights_matrix(weight_size):
    """
    Initialize the first generation with random weights between
    -0.12 and 0.12 (The range is not super important for a GA).
    """
    global GENERATION_SIZE
    return np.random.uniform(-.12,.12,size=(GENERATION_SIZE, weight_size))

def ReLU(x):
    """ Basic Rectified Linear Unit implementation (self-explanatory) """
    return x * (x>0)

def predict(X, theta_1, theta_2, theta_3):
    """
    Forward porpagate through the network.
    """
    # Layer 1
    a_1 = np.dot([[1, *X]], theta_1.T) #add the bias term
    z_1 = np.c_[np.ones(np.shape(a_1)[0],),ReLU(a_1) ]

    # Layer 2
    a_2 = np.dot(z_1, theta_2.T)
    z_2 = np.c_[np.ones(np.shape(a_2)[0],),ReLU(a_2) ]

    # Layer 3 - output
    a_3 = np.dot(z_2, theta_3.T) # linear activation (since we argmax anyway)
    return a_3


def unflatten_thetas(theta_flat):
    """
    To simplify the evolution process each theta (weight) is appended accross the
    same dimension. For the forward-pass however, we need to unflatten (for a lack
    of better term) it back to the common theta-weight layout (e.g. layer-wise).
    """
    theta_1_range = 25 * 5
    theta_2_range = 25 * 26
    theta_3_range = 2 * 26

    theta_1 = theta_flat[0:theta_1_range].reshape(25,5)
    theta_2 = theta_flat[theta_1_range:theta_1_range+theta_2_range].reshape(25,26)
    theta_3 = theta_flat[theta_1_range+theta_2_range:theta_1_range+theta_2_range+theta_3_range].reshape(2,26)
    return theta_1, theta_2, theta_3



def evaluate_fitness(gene):
    """
    Evaluate the average score achieved of the current combination of thetas on
    a fixed number of attempts.
    """
    global ASSESS_N_GAMES
    theta_1, theta_2, theta_3 = unflatten_thetas(theta_flat=gene)
    total_score = 0
    for _ in range(ASSESS_N_GAMES):
        done = 0 # in python 0 == False
        obs = env.reset()
        while not done:
            # choose the action with the highest expected score
            action = np.argmax(predict(obs, theta_1, theta_2, theta_3))
            obs, reward, done, info = env.step(action)
            total_score += reward
    return total_score/ASSESS_N_GAMES


def repopulate(fittest_n_genes):
    """
    After the performance of all genes has been assessed, we take the best n genes
    and use them to re-populate our generation.
    """
    global MUTATION_RATE, MUTATION_PROB, GENERATION_SIZE

    theta_flat_shape = np.shape(fittest_n_genes[0])
    new_generation_shape = (GENERATION_SIZE, *list(theta_flat_shape))
    new_generation = np.zeros((new_generation_shape))

    # keep the fittest_n_genes in the next generation (for robustness)
    new_generation[:len(fittest_n_genes)] = fittest_n_genes.copy()

    # For all other genes required to fill-up the new generation, pick two random
    # ones from the fittest_n_genes, and combine them by choosing about 50% of all
    # values from each. Broaded the exploration space by introductin the mutation-mask
    # (as common for darwian evolution). It basically introduces random small changes.
    for x in range(len(fittest_n_genes), GENERATION_SIZE):
        parent_mask = np.random.uniform(size=theta_flat_shape)>.5
        mutation_mask = np.random.uniform(1-MUTATION_RATE, 1+MUTATION_RATE, size=(theta_flat_shape)) * \
                        (np.random.uniform(size=(theta_flat_shape))<MUTATION_PROB)

        new_generation[x] = (random.choice(fittest_n_genes) * parent_mask + \
                            random.choice(fittest_n_genes) * (~parent_mask)) * \
                            mutation_mask
    return new_generation



# initialize first batch
genes_theta_matrix = initialize_rndom_weights_matrix(weight_size=5*25+25*26+2*26)


tabulated_list = [] # used to tabulate the final results


score_matrix = np.zeros((EPOCHS, GENERATION_SIZE))
for epoch in range(EPOCHS):
    assessment_vector = np.zeros((len(genes_theta_matrix)))
    for x in range(len(genes_theta_matrix)):
        assessment_vector[x] = evaluate_fitness(gene=genes_theta_matrix[x])

    # this is used to keep track of results for post-training analysis
    score_matrix[epoch] = assessment_vector[:GENERATION_SIZE].copy()
    tabulated_list.append(
        [f"epoch_{epoch}",
         f"{np.max(assessment_vector):.0f}",
         f"{np.mean(assessment_vector):.0f}",
         f"{np.max(score_matrix):.0f}",
         f"{np.mean(score_matrix[:epoch]):.0f}",
         epoch*GENERATION_SIZE*ASSESS_N_GAMES]
    )
    print(f"{epoch} / {EPOCHS}\t"+\
          f"\tepoch_max: {np.max(assessment_vector):.0f}\t"+\
          f"\tepoch_mean: {np.mean(assessment_vector):.0f}\t"+\
          f"\tgames_played: {epoch*GENERATION_SIZE*ASSESS_N_GAMES}")#, end="\r")


    # pick the cut-off point for score and pass all genes with a greater or equal
    # score into the re-population function.
    best_nth_value = np.sort(assessment_vector)[-KEEP_BEST_N]
    genes_theta_matrix = repopulate(
        fittest_n_genes=genes_theta_matrix[np.where(assessment_vector>=best_nth_value)[:KEEP_BEST_N]]
        )

# pretty print summary of training
print(
tabulate(tabulated_list, headers=["", "epoch-Max", "epoch-Mean", "total-Max", "total-Mean", "total-Games"])
)


# create a pretty plot eh
plt.title("Amazing GA")
plt.plot(np.max(score_matrix,axis=1), label="max")
plt.plot(np.mean(score_matrix,axis=1), label="mean")
plt.plot(np.median(score_matrix,axis=1), label="median")
plt.plot(np.min(score_matrix,axis=1), label="min")
plt.legend()
plt.show()



# choose the best gene of the last epoch to render a few games
best_gene = genes_theta_matrix[np.argmax(assessment_vector)]
theta_1, theta_2, theta_3 = unflatten_thetas(theta_flat=best_gene)

for _ in range(25):
    done = score = 0
    obs = env.reset()
    while not done:
        action = np.argmax(predict(obs, theta_1, theta_2, theta_3))
        obs, reward, done, info = env.step(action)
        env.render()    # actually render the games
        score += reward
        print(score, end="\r")
    print("") # necessary since we use end="\r" above but don't want to overwrite
