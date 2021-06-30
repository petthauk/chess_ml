class Node:
    def __init__(self, prediction, activation, fen, bw, promote, sort_prediction):
        self.prediction = prediction
        self.activation = activation
        self.fen = fen
        self.children = []
        self.fr = None
        self.to = None
        self.bw = bw
        self.promote = promote
        self.sort_prediction = sort_prediction

    def get_sort_prediction(self):
        """
        Gets prediction for sorting on moves (previous_move * 10 + current_move)
        :return: sort prediction
        """
        return self.sort_prediction

    def get_promote(self):
        """
        Gets which piece to promote to. None if not promoting
        :return: (String) Which piece to promote to
        """
        return self.promote

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

    def get_children(self):
        """
        Gets list of children
        :return:
        """
        return self.children

    def add_move(self, move):
        """
        Adds move
        :param move: (List) [from, to]
        :return:
        """
        self.fr = move[0]
        self.to = move[1]

    def get_move(self):
        """
        Gets move
        :return: (Tuple) from, to
        """
        return self.fr, self.to

    def get_bw(self):
        """
        Get who is moving after this position
        :return: (String) "w" if white is moving, "b" if black is moving
        """
        return self.bw
