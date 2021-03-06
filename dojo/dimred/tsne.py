import numpy as np

from ..base import Preprocessor
from ..losses import KL_Divergence

__all__ = [
    "TSNE",
]


class TSNE(Preprocessor):
    """t-distributed Stochastic Neighbor Embedding (t-SNE)
    
    t-distributed Stochastic Neighbor Embedding (t-SNE) is a machine learning algorithm for dimensionality reduction
    developed by Geoffrey Hinton and Laurens van der Maaten. It is a nonlinear dimensionality reduction technique
    that is particularly well-suited for embedding high-dimensional data into a space of two or three dimensions,
    which can then be visualized in a scatter plot. Specifically, it models each high-dimensional object by a
    two- or three-dimensional point in such a way that similar objects are modeled by nearby points and dissimilar
    objects are modeled by distant points.

    For a good user guide on `How to Use t-SNE Effectively`: https://distill.pub/2016/misread-tsne/
    Here is the original paper: http://www.cs.toronto.edu/~hinton/absps/tsne.pdf

    Parameters:
    -----------
    n_components : integer
    perplexity : integer
    learning_rate : float
    momentum : float, (0, 1]
    n_iter : integer
    verbose : boolean

    """

    def __init__(self, n_components=2, perplexity=30, learning_rate=200.0, momentum=0.99, n_iter=1000, verbose=False):
        self.n_components = n_components
        self.perplexity = perplexity
        self.learning_rate = learning_rate
        self.momentum = momentum
        self.n_iter = n_iter
        self.verbose = verbose

        self._sigma = []

    def _compute_std_dev(self, X):
        """Computes the standard deviation of a Gaussian Distribution with mean vector X[i]"""

        self._sigma = []
        if X.shape[0] <= 1:
            self._sigma = [0.0]
        else:
            for x_mean in range(X.shape[0]):
                std_dev = np.sqrt(sum([np.linalg.norm(x - x_mean) ** 2 for x in X]) / float(X.shape[0]-1))
                self._sigma.append(std_dev)

        return self._sigma

    def _high_dim_sim(self, v, w, normalize=False, X=None, idx=0):
        """Similarity measurement based on Gaussian Distribution"""

        sim = np.exp((-np.linalg.norm(v - w) ** 2) / (2*self._sigma[idx] ** 2))

        if normalize:
            return sim / sum(map(lambda x: x[1], self._knn(idx, X, high_dim=True)))
        else:
            return sim

    def _low_dim_sim(self, v, w, normalize=False, Y=None, idx=0):
        """Similarity measurement based on (Student) t-Distribution"""

        sim = (1 + np.linalg.norm(v - w) ** 2) ** -1

        if normalize:
            return sim / sum(map(lambda x: x[1], self._knn(idx, Y, high_dim=False)))
        else:
            return sim

    def _knn(self, i, X, high_dim=True):
        """Performs KNN search based on high/low-dimensional similarity/distance measurement"""

        knns = []
        for j in range(X.shape[0]):
            if j != i:
                if high_dim:
                    distance = self._high_dim_sim(X[i], X[j], idx=i)
                else:
                    distance = self._low_dim_sim(X[i], X[j])
                knns.append([j, distance])

        return sorted(knns, key=lambda x: x[1])[:self.perplexity]

    def _get_high_dim_dist(self, X):
        table = np.zeros((X.shape[0], X.shape[0]))

        for i in range(X.shape[0]):
            for j in range(X.shape[0]):
                if i != j:
                    Pij = self._high_dim_sim(X[i], X[j], normalize=True, X=X, idx=i)
                    Pji = self._high_dim_sim(X[i], X[j], normalize=True, X=X, idx=j)
                    table[i, j] = (Pij + Pji) / (2*X.shape[0])

        return table

    def _get_low_dim_dist(self, Y):
        table = np.zeros((Y.shape[0], Y.shape[0]))

        for i in range(Y.shape[0]):
            for j in range(Y.shape[0]):
                if i != j:
                    Pij = self._low_dim_sim(Y[i], Y[j], normalize=True, Y=Y, idx=i)
                    Pji = self._low_dim_sim(Y[i], Y[j], normalize=True, Y=Y, idx=j)
                    table[i, j] = (Pij + Pji) / (2*Y.shape[0])

        return table

    def fit(self, X):
        """Gradient Descent optimization process
        
        Tunes the embeddings (Y) so that their pairwise distance distribution
        matches the input high-dimensional data (X) pairwise distance distribution.
        In other words, minimizes the KL divergence cost.

        """

        # compute the std. deviation with mean vector x in X
        self._compute_std_dev(X)

        # Kullback–Leibler divergence
        kl_cost = KL_Divergence()

        # compute high-dimensional affinities (Gaussian Distribution)
        high_dim_dist = self._get_high_dim_dist(X)
        # sample initial solutions
        Y = np.random.randn(X.shape[0], self.n_components)

        prev_Ys = [Y, Y]

        for iteration in range(1, self.n_iter+1):
            # compute low-dimensional affinities (Student t-Distribution)
            low_dim_dist = self._get_low_dim_dist(Y)
    
            for i in range(Y.shape[0]):
                # compute gradient
                grad = kl_cost.gradient(high_dim_dist, low_dim_dist, Y, i)
                # set new Y[i]
                Y[i] = prev_Ys[1][i] + self.learning_rate * grad + self.momentum * (prev_Ys[1][i] - prev_Ys[0][i])

            prev_Ys = [prev_Ys[1], Y]

            if iteration % 100 == 0 and self.verbose:
                low_dim_dist = self._get_low_dim_dist(Y)
                print(f"ITERATION: {iteration}{3*' '}|||{3*' '}KL divergence: {kl_cost(high_dim_dist, low_dim_dist)}")

        self.embeddings = Y
        return self

    def transform(self, X):
        """Returns the learned low-dimensional embeddings of the high-dimensional data"""
        return self.embeddings
