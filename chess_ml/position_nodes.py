import copy


def sort_children_func(e):
    return e.get_prediction()


class Node:
    def __init__(self, prediction, activation, fen):
        self.prediction = prediction
        self.activation = activation
        self.fen = fen
        self.children = []
        self.visited = False
        self.fr = None
        self.to = None

    def set_prediction(self, prediction):
        """
        Sets prediction of node
        :param prediction:
        :return:
        """
        self.prediction = prediction

    def get_prediction(self):
        """
        Gets prediction of node
        :return:
        """
        return self.prediction

    def get_activation(self):
        """
        Gets activation of node
        :return:
        """
        return self.activation

    def get_fen(self):
        """
        Gets fen-string of node
        :return:
        """
        return self.fen

    def add_child(self, child, move, bw):
        """
        Adds child to child-list
        :param child: the child-node
        :param move: Move to get to child
        :param bw: Black or White to move
        :return:
        """
        self.children.append(child)
        child.add_move(move)

    def sort_children(self, rev):
        """
        Sorts children based on prediction
        :param rev: If sorting should be reversed
        :return:
        """
        self.children.sort(key=sort_children_func, reverse=rev)

    def get_children(self):
        """
        Gets list of children
        :return:
        """
        return self.children

    def visit(self):
        self.visited = True

    def unvisit(self):
        self.visited = False

    def is_visited(self):
        return self.visited

    def add_move(self, move):
        self.fr = move[0]
        self.to = move[1]

    def get_move(self):
        return self.fr, self.to
