import numpy as np
from pylops import LinearOperator
from solartom import project_3d, backproject_3d


class TomoOp(LinearOperator):
        def __init__(self, xs, ys, zs, norms, ds, b, delta, model_shape, mask, dtype=None):
            self.xs = xs
            self.ys = ys
            self.zs = zs
            self.norms = norms
            self.ds = ds
            self.b = b
            self.delta = delta
            self.model_shape = model_shape
            self.mask = mask
            super().__init__(dtype=np.dtype(dtype),
                             dims=self.model_shape,
                             dimsd=(len(self.xs), self.xs[0].shape[0], self.xs[0].shape[1]))

        def _matvec(self, densities):
            return np.array([project_3d(x, y, z, densities.reshape(self.model_shape).astype(np.float32),
                                        self.mask, self.b, self.delta, norm, d)
                    for x, y, z, norm, d in zip(self.xs, self.ys, self.zs, self.norms, self.ds)]).flatten()

        def _rmatvec(self, imgs):
            densitiesi = np.zeros(self.model_shape, dtype=np.float32)
            for i, img in enumerate(imgs.reshape(len(self.xs), self.xs[0].shape[0], self.xs[0].shape[1])):
                densitiesi += backproject_3d(self.xs[i], self.ys[i], self.zs[i], img,
                                             np.zeros_like(densitiesi).astype(np.float32),
                                             self.mask, self.b, self.delta, self.norms[i], self.ds[i], True)
            return densitiesi.flatten().astype(np.float32)
