import functions
import numpy as np

def solve(frame,z,t,N, Sol, Om_s_bc, Om_c_bc, dt, i_t, c, Gam_eg, Gam_re, gam_gr, gs, gc, Del_s, Del_c, chebDiffMatrix_norm):

	SampleOm_s = np.zeros((frame,z.shape[0]), dtype=np.complex)
	SampleOm_c = np.zeros((frame,z.shape[0]), dtype=np.complex)
	SamplePg = np.zeros((frame,z.shape[0]))
	SamplePe = np.zeros((frame,z.shape[0]))
	SamplePr = np.zeros((frame,z.shape[0]))
	SampleSge = np.zeros((frame,z.shape[0]), dtype=np.complex)
	SampleSer = np.zeros((frame,z.shape[0]), dtype=np.complex)
	SampleSgr = np.zeros((frame,z.shape[0]), dtype=np.complex)

	tFrame = np.zeros(frame)

	## Equations--------------------------
	j = 0
	for i in np.arange(t.shape[0]):
		Y = Sol # electric fields and coherences at last time step

		### RK4 method (time integration)
		k1 = functions.ladderMemEOMs(Y, c, Gam_eg, Gam_re, gam_gr, gs, gc, N, Del_s, Del_c, chebDiffMatrix_norm)
		k2 = functions.ladderMemEOMs(Y+k1*dt/2.0, c, Gam_eg, Gam_re, gam_gr, gs, gc, N, Del_s, Del_c, chebDiffMatrix_norm)
		k3 = functions.ladderMemEOMs(Y+k2*dt/2.0, c, Gam_eg, Gam_re, gam_gr, gs, gc, N, Del_s, Del_c, chebDiffMatrix_norm)
		k4 = functions.ladderMemEOMs(Y+k3*dt, c, Gam_eg, Gam_re, gam_gr, gs, gc, N, Del_s, Del_c, chebDiffMatrix_norm)

		Sol = Y + (1.0/6)*(k1 + 2.0*k2 + 2.0*k3 + k4)*dt # Solution at position j
		###############

		#### (spatial) boundary condition
		Sol[0,0] = Om_s_bc[i]
		Sol[1,-1] = Om_c_bc[i]

		Sol[2,0] = 1
		Sol[3:Sol.shape[0],0] = 0

		# [Es Ec Pg, Pe, Pr, Sge, Ser, Sgr]
		if i == i_t[j]:
			SampleOm_s[j] = Sol[0]
			SampleOm_c[j] = Sol[1]
			SamplePg[j] = Sol[2] * N
			SamplePe[j] = Sol[3] * N
			SamplePr[j] = Sol[4] * N
			SampleSge[j] = Sol[5] * N
			SampleSer[j] = Sol[6] * N
			SampleSgr[j] = Sol[7] * N
			tFrame[j] = t[i]
			j += 1
	
	return SampleOm_s, SampleOm_c, SamplePg, SamplePe, SamplePr, SampleSge, SampleSer, SampleSgr, tFrame