import numpy as np

from ..base import BaseModel

__all__ = [
    "sigmoid",
    "LogisticRegression",
]

def sigmoid(x):
    z = lambda k: 1.0/(1 + np.exp(-k))

    if type(x) in [list, np.ndarray]:
        for i in range(len(x)):
            x[i] = z(x[i])
        return x

    else:
        return z(x)

class LogisticRegression(BaseModel):
    def __init__(self, intercept=0, coefs=[], C=1.0, lr=0.001, verbose=False):
        self.intercept = intercept
        self.coefs = coefs
        self.C = C
        self.lr = lr
        self.verbose = verbose

        self._X, self._y = [], []

    def _loss(self):
        y_pred = np.array([0.99 if self.predict([x])[0] == 1 else 0.01 for x in self._X])
        m, _ = self._X.shape

        return -1/m * np.sum(
            self._y * np.log(y_pred) + (np.ones(m)-self._y) * np.log(np.ones(m)-y_pred)
        ) + 1/self.C * 1/2*m * np.sum(self.coefs**2)

    def _gradient(self):
        y_pred = np.array([self.predict([x])[0] for x in self._X])
        m, n = self._X.shape

        grad = np.zeros(n+1, dtype=np.float32)
        grad[0] = 1/m * np.sum(y_pred - self._y)
        grad[1:] = (self._X.T @ (y_pred - self._y)).T * 1/m + 1/self.C * 1/m * self.coefs
        
        return grad

    def fit(self, X, y):
        self._X, self._y = super().fit(X, y)
        self.intercept = 0
        self.coefs = np.zeros(self._X.shape[1], dtype=np.float32)
        
        best_loss = 1e9
        grad = None

        n = 0
        while n < self._X.shape[0] or best_loss > self._loss():
            best_loss = self._loss()
            grad = self._gradient()

            self.intercept -= self.lr * grad[0]
            self.coefs -= self.lr * grad[1:]
            n+=1

        self.intercept += self.lr * grad[0]
        self.coefs += self.lr * grad[1:]
        self.coefs = list(self.coefs)
        return self

    def predict(self, X):
        return list(
            np.round(self.predict_proba(X))
        )

    def predict_proba(self, X):
        return list(
            sigmoid(self.decision_function(X))
        )

    def decision_function(self, X):
        X = super().decision_function(X)
        return [self.intercept + np.array(self.coefs).T @ x for x in X]

    def evaluate(self, X, y):
        X, y = super().evaluate(X, y)
        # TODO: implement
        raise NotImplementedError("This method is not yet implemented.")
