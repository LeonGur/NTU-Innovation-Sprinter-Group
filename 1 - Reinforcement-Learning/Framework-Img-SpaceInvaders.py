# Leon Gurtler
import gym, time, cv2
import numpy as np

import keras
from keras.models import Sequential
from keras.layers import Dense, Dropout, BatchNormalization
from keras.layers import Conv2D, MaxPooling2D, Flatten


env = gym.make("SpaceInvaders-v0")
n = np.shape(env.observation_space.sample())
num_labels = env.action_space.n

# To save the training data
X_train = []
y_train = []

# variables and CONSTANTS
epsilon = .5
EPSILON_DECAY = 1
TOTAL_GAMES = 100_000

score_list = []



# probably a good idea to initialize your model somewhere here


def preprocess(obs):
    """ Basic pre-process to grayscale and re-shape for (84,84,1) or (84,84) """
    obs = cv2.cvtColor(obs, cv2.COLOR_BGR2GRAY) # grayscale
    obs = cv2.resize(obs, (84,84))/255.0 # resize
    return obs[...,np.newaxis] # necessary for Conv2D Layers


# training loop
for game_nr in range(TOTAL_GAMES):
    done = score = 0
    obs = env.reset()

    # initialize local game_based memory
    game_obs = []
    game_action = []

    while not done:
        obs = preprocess(obs)

        if np.random.uniform() < epsilon: # basic epsilon-decreasing/-greedy strategy
            action = env.action_space.sample()
        else:
            # this is where your action should be executed
            action = env.action_space.sample() # please change this eh

        obs, reward, done, info = env.step(action)
        score+= reward

    score_list.append(score)
    """
    For DQN and similar:
    for obs, a in zip(game_obs, game_action):
        label = np.zeros((num_labels,))
        label[a] = score
        y_train.append(label)
        X_train.append(obs)
    """

    """
    For strict Epsilon-first & iterative Epsilon-first strategies:
    if score >= score_threshold:
        for obs, a in zip(game_obs, game_action):
            label = np.zeros((num_labels,))
            label[a] = score
            y_train.append(label)
            X_train.append(obs)
    """

    if not (game_nr%50):
        print(f"{game_nr} / {TOTAL_GAMES}"+\
              f"Most recent score: {score}"+\
              f"Inter-training score-avg: {np.mean(score_list)}")


    """
    Train the Network/tree on some condition

    model.fit(
        np.asarray(X_train),
        np.asarray(y_train),
        epochs=5
    )
    X_train = []
    y_train = []
    score_list = []
    epsilon *= EPSILON_DECAY
    model.save("myAwesomeModelLah.model")
    """
