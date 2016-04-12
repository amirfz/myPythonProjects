# CHEB  compute D = differentiation matrix, x = Chebyshev grid
#
# See chap. 6 of Trefethen, Spectral Methods in MATLAB, SIAM, 2000.
# import numpy as np
import numpy as np

def cheb(N):
	
	if N==0:
		D=0
		x=1
	x = np.cos(np.pi*(np.arange(N+1))/N).reshape(N+1,1)
	c = np.multiply(np.concatenate(([2], np.ones(N-1), [2])),np.power(-1,np.arange(N+1))).reshape(N+1,1)
	X = np.tile(x,(1,N+1))
	dX = X-np.transpose(X)                  
	D  = (c*np.transpose(1.0/c))/(dX+(np.identity(N+1))) # off-diagonal entries
	D  = D - np.diag(np.sum(D,axis=1)) # diagonal entries
	
	return np.transpose(D), x.flatten()
	
def ladderMemEOMs(y, c, Gam_eg, Gam_re, gam_gr, gs, gc, N, Del_s, Del_c, chebDiffMatrix_norm):

	# [Es Ec Pg, Pe, Pr, Sge, Ser, Sgr]
	Es = y[0]
	Ec = y[1]
	Pg = y[2] # pop gnd state 
	Pe = y[3] # pop excited state 
	Pr = y[4] # pop ry state
	Sge = y[5] # ge
	Ser = y[6] # er
	Sgr = y[7] # gr

	# the very first column is forcing all solutions to be zero at z=start,
	# which is only valid if every thing is moving to right
	dydt = np.array([-c*Es.dot(chebDiffMatrix_norm) + 1j * gs * N * Sge, # Es - on the lhs of this relation there is E/2.0 e^i om0 t NOT E e^i om0 t
		+c*Ec.dot(chebDiffMatrix_norm) + 1j * gc * N * Ser, # Ec
		+Gam_eg * Pe + 1j * np.conj(Es)/2.0 * Sge - 1j * Es/2.0 * np.conj(Sge), # Pg
		+Gam_re * Pr - Gam_eg * Pe - 1j * np.conj(Es)/2.0 * Sge + 1j * Es/2.0 * np.conj(Sge) + 1j * np.conj(Ec)/2.0 * Ser - 1j * Ec/2.0 * np.conj(Ser), # Pe
		-Gam_re * Pr - 1j * np.conj(Ec)/2.0 * Ser + 1j * Ec/2.0 * np.conj(Ser), # Pr
		(1j * Del_s - Gam_eg/2.0) * Sge + 1j * np.conj(Ec)/2.0 * Sgr - 1j * Es/2.0 * (Pe - Pg), # Sge
		(1j * Del_c - Gam_re/2.0) * Ser - 1j * np.conj(Es)/2.0 * Sgr - 1j * Ec/2.0 * (Pr - Pe), # Ser
		(1j * (Del_s + Del_c) - gam_gr) * Sgr + 1j * Ec/2.0 * Sge - 1j * Es/2.0 * Ser]) # Sgr
	
	return dydt