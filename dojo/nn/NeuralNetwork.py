import numpy as np

from ..base import BaseModel
from ..losses import CrossEntropy
from ..metrics.classification import accuracy_score

__all__ = [
    "NeuralNetwork",
]


class NeuralNetwork(BaseModel):
    # TODO: add __doc__

    def __init__(self, alpha=0.01, n_iterations=5_000, loss=CrossEntropy(), verbose=False):
        self.alpha = alpha
        self.n_iterations = n_iterations
        self.loss = loss
        self.verbose = verbose

        self._loss_values = []
        self._layers = []

    def add(self, layer):
        if len(self._layers) > 0:
            layer.n_inputs = self._layers[-1].n_neurons
        layer.init_weights()
        self._layers.append(layer)

    def forwardprop(self, X):
        AL = X
        for layer in self._layers:
            AL = layer.forward(AL)

        return AL

    def backprop(self, Y, AL):
        dA = self.loss.gradient(Y, AL)

        for layer in reversed(self._layers):
            layer.backward(dA)
            dA = layer.grads["dA_prev"]

    def fit(self, X, y):
        X, y = super().fit(X, y)
        m = X.shape[0]
        X = X.T
        y = y.reshape(1, -1)

        for i in range(1, self.n_iterations + 1):
            # Forward-propagation
            AL = self.forwardprop(X)

            # Computing the cost
            self._loss_values.append(np.mean(self.loss(y, AL)))
            penalty = 0
            for layer in self._layers:
                penalty += layer.regularizer(layer.W)
            self._loss_values[-1] += 1/m * penalty

            # Printing
            if i % 100 == 0 and self.verbose:
                print(f"Iteration {i}, Cost: {self._loss_values[-1]}")

            # Back-propagation
            self.backprop(y, AL)

            # Updating the weights
            for layer in self._layers:
                layer.update(self.alpha)

        return self

    def predict(self, X):
        return np.round(self.predict_proba(X))

    def predict_proba(self, X):
        X = super().predict_proba(X).T
        return self.forwardprop(X)

    def decision_function(self, X):
        pass

    def evaluate(self, X, y):
        return accuracy_score(y, self.predict(X))
