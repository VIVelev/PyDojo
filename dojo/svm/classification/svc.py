from ..utils import (
    Classifier,
    MethodNotSupportedError,

    set_kernel,
    svm_problem,
    svm_parameter,
    svm_train,
    svm_predict,

    accuracy_score,
)

__all__ = [
    "SVC",
]


class SVC(Classifier):
    """C-Support Vector Machine Classifier
    
    Parameters:
    -----------
    C : float, optional
    kernel : string, optional
    degree : integer, optional
    gamma : "auto" or float, optional
    verbose : boolean, optional
    
    """

    def __init__(self, C=1.0, kernel="rbf", degree=3, gamma="auto", verbose=False):
        self._estimator = None
        self.C = C
        self.kernel = set_kernel(kernel)
        self.degree = degree
        self.gamma = gamma
        self.verbose = verbose

    def fit(self, X, y):
        X, y = super().fit(X, y)

        if type(self.gamma) is str and self.gamma.upper() == "AUTO":
            self.gamma = 1.0/X.shape[0]

        problem = svm_problem(y, X)
        param_str = f"""
            -s 0
            -c {self.C}
            -t {self.kernel}
            -d {self.degree}
            -g {self.gamma}
        """
        if not self.verbose:
            param_str += " -q"
        parameter = svm_parameter(param_str)

        self._estimator = svm_train(problem, parameter)
        return self

    def predict(self, X):
        X = super().predict(X)
        predictions, *_ = svm_predict([0 for _ in X], X, self._estimator, options="-q")
        return predictions

    def predict_proba(self, X):
        raise MethodNotSupportedError("Probability prediction are not supported for Support Vector Machine.")

    def decision_function(self, X):
        X = super().decision_function(X)
        *_, decision_values = svm_predict([0 for _ in X], X, self._estimator, options="-q")
        return decision_values

    def evaluate(self, X, y):
        return accuracy_score(y, self.predict(X))
