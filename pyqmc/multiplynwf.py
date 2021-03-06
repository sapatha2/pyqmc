import numpy as np


class Parameters:
    def __init__(self, dicts):
        self.data = {}
        self.wf_count = len(dicts)
        for (i, d) in enumerate(dicts):
            self.data["wf" + str(i + 1)] = d

    def __setitem__(self, idx, value):
        k1 = idx[0:3]
        k2 = idx[3:]
        self.data[k1][k2] = value

    def __getitem__(self, idx):
        k1 = idx[0:3]
        k2 = idx[3:]
        return self.data[k1][k2]

    def __delitem__(self, idx):
        k1 = idx[0:3]
        k2 = idx[3:]
        del self.data[k1][k2]

    def __iter__(self):
        for i in range(self.wf_count):
            k1 = "wf" + str(i + 1)
            for k2 in self.data[k1].keys():
                yield k1 + k2

    def __len__(self):
        length = 0
        for i in self.data:
            length += len(i)
        return length

    def items(self):
        for i in range(self.wf_count):
            k1 = "wf" + str(i + 1)
            for k2 in self.data[k1].keys():
                yield k1 + k2, self.data[k1][k2]

    def __repr__(self):
        return "WFmerger: " + self.data.__repr__()

    def keys(self):
        for i in range(self.wf_count):
            k1 = "wf" + str(i + 1)
            for k2 in self.data[k1].keys():
                yield k1 + k2


class MultiplyNWF:
    """
    A general representation of a wavefunction as a product of multiple wf_factors 
    """

    def __init__(self, wf_factors):
        self.wf_factors = wf_factors
        self.parameters = Parameters([wf.parameters for wf in wf_factors])

    def recompute(self, configs):
        signs = np.ones(len(configs.configs))
        vals = np.zeros(len(configs.configs))
        for wf in self.wf_factors:
            results = wf.recompute(configs)
            signs *= results[0]
            vals += results[1]
        return signs, vals

    def updateinternals(self, e, epos, mask=None):
        for wf in self.wf_factors:
            wf.updateinternals(e, epos, mask=mask)

    def value(self):
        results = [wf.value() for wf in self.wf_factors]
        results = np.array([*results])
        return np.prod(results[:, 0, :], axis=0), np.sum(results[:, 1, :], axis=0)

    def gradient(self, e, epos):
        grads = [wf.gradient(e, epos) for wf in self.wf_factors]
        return np.sum(grads, axis=0)

    def testvalue(self, e, epos, mask=None):
        testvalues = [wf.testvalue(e, epos, mask=mask) for wf in self.wf_factors]
        return np.prod(testvalues, axis=0)

    def laplacian(self, e, epos):
        grad_laps = [wf.gradient_laplacian(e, epos) for wf in self.wf_factors]
        grad_laps = np.array(grad_laps)
        # print(grad_laps[1,1].shape)
        grads = grad_laps[:, 0]
        laps = grad_laps[:, 1]
        corss_term = np.zeros(laps[0].shape)
        nwf = len(self.wf_factors)
        for i in range(nwf):
            for j in range(i + 1, nwf):
                corss_term += np.sum(grads[i] * grads[j], axis=0)
        return np.sum(laps, axis=0) + corss_term * 2

    def gradient_laplacian(self, e, epos):
        return self.gradient(e, epos), self.laplacian(e, epos)

    def pgradient(self):
        return Parameters([wf.pgradient() for wf in self.wf_factors])


def test_parameters():
    import numpy as np

    dicts = []
    for i in range(10):
        dicts.append({"coeff" + str(i): np.random.rand(3)})
    p = Parameters(dicts)
    # test len
    assert len(p) == 30
    print("len test passed")
    # test getitem
    assert p["wf2coeff2"].all() == dicts[2]["coeff2"].all()
    print("getitem test passed")
    new_coeff = np.random.rand(5)
    # test setitem
    p["wf2coeff2"] = new_coeff
    assert p["wf2coeff2"].all() == new_coeff.all()
    print("setitem test passed")
