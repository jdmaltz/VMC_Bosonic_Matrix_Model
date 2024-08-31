#########################################################################
#### Based on Xizhi Han's code.  ########################################
### See https://github.com/hanxzh94/minimal_BMN_MQM for the original. ###
#########################################################################
### "xmat" is X_{ij}, i,j = 1,...,nmat       ############################
### "xvec" is X_a, a = 1,...,nmat*nmat-1     ############################
###  X_{ij} = \sum_a X_a T^a_{ij}            ############################
###  SU(N) generators T^a are normalized as Tr(T^a*T^b) = \delta^{ab} ###
######################################################################### 
import torch
class SU():
    def __init__(self, nmat, batch_size):
        ############################
        ### SU(N) generators T^a ###
        ############################        
        self.generator = []
        #########################
        ### off-diagonal part ###
        #########################
        for imat in range(1, nmat):#imat=1,2,...,nmat-1
            # real and symmetric
            for jmat in range(0, nmat - imat):#jmat=0,1,...,nmat-imat-1
                tau = torch.zeros((nmat, nmat), dtype=torch.complex64)
                tau[jmat, jmat + imat] = 1.0 / torch.sqrt(torch.tensor(2.0))
                tau[jmat + imat, jmat] = 1.0 / torch.sqrt(torch.tensor(2.0))
                self.generator.append(tau)
            # imaginary and anti-symmetric
            for jmat in range(0, nmat - imat):#jmat=0,1,...,nmat-imat-1
                tau = torch.zeros((nmat, nmat), dtype=torch.complex64)
                tau[jmat, jmat + imat] = 1.0 * 1j / torch.sqrt(torch.tensor(2.0))
                tau[jmat + imat, jmat] = -1.0 * 1j / torch.sqrt(torch.tensor(2.0))
                self.generator.append(tau)
        #####################
        ### diagonal part ###
        #####################
        for imat in range(1, nmat):#imat=1,2,...,nmat-1
            tau = torch.zeros((nmat, nmat), dtype=torch.complex64)
            for jmat in range(0,imat):#jmat=0,1,...,imat-1
                tau[jmat, jmat] = 1.0 / torch.sqrt(torch.tensor(imat * imat + imat))
            tau[imat, imat] = -imat / torch.sqrt(torch.tensor(imat * imat + imat))
            self.generator.append(tau)

        self.generator_array = torch.stack(self.generator)
     #    super().__init__(self.generator)
    #####################
    ### X_a -> X_{ij} ###
    #####################
    def vector_to_matrix(self, xvec, ndim, nmat, batch_size):
        # for each ibatch, xvec is d*(N^2-1)-dim real vector; xvec(ibatch,idim,ivec)
        # xmat(idim,imat,jmat) is nmat*nmat traceless Hermitian; xmat(ibatch,idim,imat,jmat)
        # idim = 1,..,dim
        # imat, jmat = 1,...,nmat
        xvec = xvec.to(torch.complex64)
        xtemp = xvec.reshape(batch_size,ndim,nmat*nmat-1)
        xmat = torch.einsum("abc,cij->abji",xtemp,self.generator_array)
        return xmat
    #####################
    ### X_{ij} -> X_a ###
    #####################
    def matrix_to_vector(self, xmat, ndim, nmat, batch_size):
        # xvec is d*(N^2-1)-dim real vector; xvec(ibatch,idim,ivec)
        # xmat(idim,imat,jmat) is nmat*nmat traceless Hermitian; xmat(ibatch,idim,imat,jmat)
        # idim = 1,..,dim
        # imat, jmat = 1,...,nmat

        xvec = []
        for ibatch in range(batch_size):
            for idim in range(ndim):
                #########################
                ### off-diagonal part ###
                #########################
                for imat in range(1, nmat):#imat=1,2,...,nmat-1
                # real and symmetric
                    for jmat in range(0, nmat - imat):#jmat=0,1,...,nmat-imat-1
                        xtemp =  xmat[ibatch, idim, jmat, jmat + imat].real * torch.sqrt(torch.tensor(2.0))
                        xvec.append(xtemp)
                        # imaginary and anti-symmetric
                        for jmat in range(0, nmat - imat):#jmat=0,1,...,nmat-imat-1
                            xtemp =  xmat[ibatch, idim, jmat + imat, jmat].imag * torch.sqrt(torch.tensor(2.0))
                            xvec.append(xtemp)
                #####################
                ### diagonal part ###
                #####################
                for imat in range(1, nmat):#imat=1,2,...,nmat-1
                    xtemp =  xmat[ibatch, idim, 0, 0].real * torch.sqrt(torch.tensor(imat * imat + imat))
                    xvec.append(xtemp)
        xvec = torch.tensor(xvec)
        xvec = xvec.reshape(batch_size,ndim*(nmat*nmat-1))
        return xvec



    
