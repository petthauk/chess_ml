from chess_ml import util
import numpy as np
import math


def sigmoid(x):
    try:
        return 1 / (1 + math.exp(-x))
    except OverflowError:
        if x < -50.0:
            return 1.0
        return 0.0


class Perceptron:
    def __init__(self, fen, file):
        self.fen = fen
        self.weights = []
        self.init_weights(file)
        # Update weights in accordance to start position

    def init_weights(self, file):
        ret = None
        if file == "data/weights.npy":
            length = len(util.get_data(self.fen))
            ret = util.get_weights(
                file,
                layer_sizes=np.array([
                    length,
                    128,
                    64,
                    1
                ], dtype=object)
            )
            for w in ret:
                self.weights.append(w)

        elif file == "data/promote_weights.npy":
            length = len(util.get_promote_data(self.fen, "n"))
            ret = util.get_weights(
                file,
                layer_sizes=np.array([
                    length,
                    128,
                    64,
                    1
                ], dtype=object)
            )
            for w in ret:
                self.weights.append(w)

    def predict(self, data):
        """
        Predicts chance of winning from fen-string and move
        :param data: a list with all the data
        :return: chance of winning
        """
        output = 0.5
        activation = data.copy()
        activations = [activation]
        for lr in range(len(self.weights)):
            biased_data = util.add_bias(activation)
            layer = np.zeros(len(self.weights[lr].T))
            for to_node in range(len(layer)):
                for w in range(len(self.weights[lr])):
                    b_data = biased_data[w]
                    if b_data != 0:
                        weight = self.weights[lr][w, to_node]
                        layer[to_node] += b_data * weight
                layer[to_node] = sigmoid(layer[to_node])
            if lr == len(self.weights) - 1:
                output = layer[0]
            else:
                activation = layer.copy()
                activations.append(activation)
        return output, activations

    def back_prop(self, data, predict, target, eta=0.1):
        ret_weights = []
        full_data = data.copy()
        full_data.append([predict])
        delta = [(predict - target) * predict * (1 - predict)]
        for lr in range(-1, -len(self.weights)-1, -1):
            new_weights = np.array([self.weights[lr][i] for i in range(len(self.weights[lr]))])
            current_data = full_data[lr]
            biased_activation = util.add_bias(full_data[lr - 1])
            delta.append([])
            for i in range(len(new_weights)):
                if lr != abs(len(self.weights)):
                    delta[abs(lr)].append(
                        biased_activation[i] * (1 - biased_activation[i])
                    )
                if lr == -1:
                    new_weights[i] = new_weights[i] - eta * delta[0] * current_data[0]
                    delta[abs(lr)][i] += delta[0] * self.weights[lr][i]
                elif lr != -len(self.weights):
                    delta_times = 0.0
                    for j in range(len(new_weights[i])):
                        new_weights[i][j] = self.weights[lr][i][j] - eta * delta[abs(lr+1)][j+1] * biased_activation[i]
                        delta_times += delta[abs(lr+1)][j+1] * self.weights[lr][i][j]
                    delta[abs(lr)][i] = delta[abs(lr)][i] * delta_times
                else:
                    if biased_activation[i] != 0:
                        for j in range(len(new_weights[i])):
                            new_weights[i][j] = self.weights[lr][i][j] - eta \
                                                * delta[abs(lr+1)][j+1] * biased_activation[i]
            ret_weights.append(new_weights)
        ret_weights.reverse()
        return ret_weights
