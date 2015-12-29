import numpy as np


class KNearestNeighbor:
    """ a kNN classifier with L2 distance """
    def __init__(self):
        pass

    def train(self, X, y):
        self.X_train = X
        self.y_train = y

    def predict(self, X, k=1, num_loops=0):
        if num_loops == 0:
            dists = self.compute_distances_no_loops(X)
        elif num_loops == 1:
            dists = self.compute_distances_one_loop(X)
        elif num_loops == 2:
            dists = self.compute_distances_two_loops(X)
        else:
            raise ValueError('Invalid value %d for num_loops' % num_loops)

        return self.predict_labels(dists, k=k)

    def compute_distances_two_loops(self, X):
        """Compute L2 distance matrix for the test vectors X.

        Each vector in X is a test sample. We compute its L2 distance from each
        training vector in X_train and put it in the matrix.

        The returned matrix at [i, j] has the L2 distance between test i and
        training sample j.

        Note: this is a very slow version using Python-level loops.
        """
        num_test = X.shape[0]
        num_train = self.X_train.shape[0]
        dists = np.zeros((num_test, num_train))
        for i in xrange(num_test):
            for j in xrange(num_train):
                dists[i, j] = np.sqrt(
                        np.sum(np.square(X[i, :] - self.X_train[j, :])))
        return dists

    def compute_distances_one_loop(self, X):
        """Partially-vectorized distance matrix computation."""
        num_test = X.shape[0]
        num_train = self.X_train.shape[0]
        dists = np.zeros((num_test, num_train))
        for i in xrange(num_test):
            # X_train is (num_train, imgsize)
            # X[i] is (imgsize,)
            # X_train - X[i] broadcasts X[i] over each row of X_train.
            # np.square is elementwise; sum over axis=1 sums up all the columns
            # into a single number per row.
            dists[i, :] = np.sqrt(np.square(self.X_train - X[i]).sum(axis=1))
        return dists

    def compute_distances_no_loops(self, X):
        """Fully-vectorized distance matrix computation."""
        X_norm = np.sum(X ** 2, axis=1, keepdims=True)
        print 'X_norm', X_norm.shape
        X_train_norm = np.sum(self.X_train ** 2, axis=1)
        print 'X_train_norm', X_train_norm.shape
        cross = -2.0 * X.dot(self.X_train.T)
        print 'cross', cross.shape
        dists = np.sqrt(X_norm + cross + X_train_norm)
        return dists

    def predict_labels(self, dists, k=1):
        """Predict labels, given a distances matrix.

        dists - (num_test, num_train) array; dists[i, j] is the distance between
                the ith test point and the jth trainin point.

        k - how many neighbors to use.

        Output: a vector of length num_test where each element is the predicted
                label for the test point.
        """
        num_tests = dists.shape[0]
        y_pred = np.zeros(num_tests, dtype='int64')
        for i in xrange(num_tests):
            # dists[i] has the ith test distance from each training example.
            # argsort will produce sorted indices of training examples, from
            # smallest distance (closes) to largest distance. We can use this
            # to index into y_train to find the labels that are closest.
            closest_y = self.y_train[np.argsort(dists[i])]
            k_closest_y = closest_y[:k]

            # k_closest_y is a list of k labels that were the closest among
            # the training samples. Find the most common label among these.
            values, counts = np.unique(k_closest_y, return_counts=True)
            y_pred[i] = values[np.argmax(counts)]

        return y_pred