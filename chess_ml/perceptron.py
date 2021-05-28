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
        self.square = [0, 0]
        self.move = [0, 0]
        self.weights = self.init_weights(file)

    def init_weights(self, file):
        ret = None
        if file == "data/weights.npy":
            ret = util.get_weights(
                file,
                layer_sizes=np.array([
                    len(util.get_data(self.fen, self.square, self.move)),
                    30,
                    1
                ], dtype=object)
            )
        elif file == "data/promote_weights.npy":
            ret = util.get_weights(
                file,
                layer_sizes=np.array([
                    len(util.get_promote_data(self.fen, 0)),
                    30,
                    1
                ], dtype=object)
            )
        return ret

    def predict(self, data):
        """
        Predicts chance of winning from fen-string and move
        :param data: a list with all the data
        :return: chance of winning
        """
        output = 0.0
        activation = data
        for lr in range(len(self.weights)):
            biased_data = util.add_bias(activation)
            layer = np.zeros(len(self.weights[lr].T))
            for to_node in range(len(layer)):
                for w in range(len(self.weights[lr])):
                    b_data = biased_data[w]
                    weight = self.weights[lr][w, to_node]
                    layer[to_node] += b_data * weight
                layer[to_node] = sigmoid(layer[to_node])
            if lr == 0:
                activation = layer
            if lr == len(self.weights) - 1:
                output = layer[0]
        return output, activation

    def back_prop(self, data, predict, target, eta=0.1):
        new_weights_output = np.array([self.weights[1][i] for i in range(len(self.weights[1]))])
        new_weights_input = np.array([self.weights[0][i] for i in range(len(self.weights[0]))])
        # Change weight in output layer
        biased_activation = util.add_bias(data[1])
        for i in range(len(new_weights_output)):
            new_weights_output[i] = new_weights_output[i] - eta * 2 * (predict - target) * biased_activation[i]
        biased_data = util.add_bias(data[0])
        for i in range(len(new_weights_input)):
            for j in range(len(new_weights_input[i])):
                new_weights_input[i][j] = (
                        new_weights_input[i][j] - eta * 2 * (predict - target)
                        * self.weights[1][j] * biased_activation[j] * biased_data[i]
                )
        ret_weights = [new_weights_input, new_weights_output]
        return ret_weights


