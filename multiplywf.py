import numpy as np
from collections import ChainMap


class MultiplyWF:
    """Multiplies two wave functions """

    def __init__(self,nconfig,wf1,wf2):
        self.wf1=wf1
        self.wf2=wf2
        #Using a ChainMap here since it makes things easy.
        #But there is a possibility that names collide here. 
        #one option is to use some name-mangling scheme for parameters
        #within each wave function
        self.parameters=ChainMap(self.wf1.parameters,self.wf2.parameters)

        
    def recompute(self,epos):
        v1=self.wf1.recompute(epos)
        v2=self.wf2.recompute(epos)
        return v1[0]*v2[0],v1[1]+v2[1]

    def updateinternals(self,epos,mask=None):
        self.wf1.updateinternals(epos,mask)
        self.wf2.updateinternals(epos,mask)


    def value(self):
        v1=self.wf1.value()
        v2=self.wf2.value()
        return v1[0]*v2[0],v1[1]+v2[1]
    
    def gradient(self,e,epos):
        return self.wf1.gradient(e,epos)+self.wf2.gradient(e,epos)

    def testvalue(self,e,epos):
        return self.wf1.testvalue(e,epos)*self.wf2.testvalue(e,epos)

    def laplacian(self,e,epos):
        # This is a place where we might want to specialize a vgl function 
        # which can save some time if we want both gradient and laplacians
        # Should check to see if that's a limiting factor or not.
        # We typically need the laplacian only for the energy, which is uncommonly 
        # evaluated.
        g1=self.wf1.gradient(e,epos)
        g2=self.wf2.gradient(e,epos)
        l1=self.wf1.laplacian(e,epos)
        l2=self.wf2.laplacian(e,epos)
        return l1+l2+2*np.sum(g1*g2,axis=0)

    def pgradient(self):
        """Here we need to combine the results"""
        return ChainMap(self.wf1.pgradient(),self.wf2.pgradient())





def test():
    from pyscf import lib,gto,scf
    from jastrow import Jastrow2B
    from slater import PySCFSlaterRHF
    nconf=10
    
    mol = gto.M(atom='Li 0. 0. 0.; H 0. 0. 1.5', basis='cc-pvtz',unit='bohr')
    mf = scf.RHF(mol).run()
    slater=PySCFSlaterRHF(nconf,mol,mf)
    jastrow=Jastrow2B(nconf,mol)
    jastrow.parameters['coeff']=np.random.random(jastrow.parameters['coeff'].shape)
    epos=np.random.randn(nconf,4,3)
    wf=MultiplyWF(nconf,slater,jastrow)
    import testwf
    for delta in [1e-3,1e-4,1e-5,1e-6,1e-7]:
        print('delta', delta, "Testing gradient",testwf.test_wf_gradient(wf,epos,delta=delta))
        print('delta', delta, "Testing laplacian", testwf.test_wf_laplacian(wf,epos,delta=delta))
        print('delta', delta, "Testing pgradient", testwf.test_wf_pgradient(wf,epos,delta=delta))
    
if __name__=="__main__":
    test()