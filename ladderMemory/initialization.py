## Quantization of Time and Space-----
def init():
	import functions
	import numpy as np

	c = 2.99792458e8
	eps0 = 8.854187817e-12
	h = 6.62606896e-34
	hbar = h /2/np.pi

	dpl = 3.58425e-29 # J=1.0/2 -> J=3/2
	dpl_s = np.power(1.0/2,1.0/2) * dpl # F=3,mf=3 -> F=4,mf=4
	dpl_c = np.power(0.1,1.0/2) * dpl_s # 
	wavelength = 780.241368271e-9
	om0 = 2*np.pi*c/wavelength #

	nLvls = 3 # num atomic levels involved in the simulation

	photonEnergy = hbar * om0 # energy per photon

	### interaction parameters
	Gam_eg = 2*np.pi * 6.0666e6 # sp em rate e to g
	Gam_re = 1.0/250e-9 # sp em rate r to e, 250ns lifetime
	gam_gr = 1e-5 * Gam_eg
	gs = om0 * dpl_s**2 / eps0 / hbar # coupling constant
	gc = om0 * dpl_c**2 / eps0 / hbar # coupling constant
	CrossSection_s = 2 * gs / c / Gam_eg # 3->4: 1.2457e-13 m**2, F=3,mf=3 -> F=4,mf=4: 2.9067e-13
	CrossSection_c = 2 * gc / c / Gam_re # 

	w2 = np.pi*50e-6**2 # beam cross section
	En_s = 1e-19
	En_c = 0.7e-9

	### signal (pump) pulse parameters
	Del_s = - 2*np.pi*30e9 # (1.67Gam for 10 MHz detuning) om_34 - om_L: detuning
	sig_s = 2*np.pi*(0.44/267e-12) # TETS (0.4Gam for 100ns FWHM pulses)
	sig_fwhm_s = sig_s * (2*np.power(2*np.log(2),1.0/2)) # (field) FWHM freq span of the pulse- intensity FWHM = np.power(2) x field FWHM
	Om0_s =dpl_s*np.power(2**(1.5)*En_s*sig_s/(0.44*w2*eps0*c*np.power(np.pi,1.0/2)),1.0/2)/hbar #
	# Om0_s = 0e-1*Gam_eg #TEST
	T_s=0.44/(sig_s/(2*np.pi))	

	### coupling beam parameters
	Del_c = -Del_s # om_34 - om_L: detuning
	sig_cW = 2.5*sig_s # 1 / rise time of the coupling, write pulse # different pulse durations have different efficiencies, 5x sig_FWHM seems to be the best (for medium 2x sig_FWHM), and it falls with smaller/larger, only slightly better than current case though -> Josh's modes?
	sig_cR = 2.5*sig_s # 1 / rise time of the coupling, Read pulse
	Om0_c =dpl_c*np.power(2**(1.5)*En_c*sig_cW/(0.44*w2*eps0*c*np.power(np.pi,1.0/2)),1.0/2)/hbar #
	# Om0_c = 0 # TEST

	### atom cloud parameters
	D = 5 * c/sig_s # FWHM of atomic cloud (gaussian dist)
	OD0 = 5e4 # optical density
	N0 = OD0*eps0*hbar*c*Gam_eg/dpl_s**2/om0 / D # peak atomic density (agrees with Josh's code)

	Energy=(hbar*Om0_c/dpl_c)**2*(w2*eps0*c*np.power(np.pi,1.0/2)*2**(-1.5)*0.44/sig_cW)*1e9

	ramMemCoupling = (OD0/D*2*c/sig_s) * (np.power(2*np.pi,1.0/2)*Om0_c**2) / Del_c**2

	#################

	L = 1.05*D # spatial extent of the simulation
	zL = -L/2 
	zR = L/2 # left and right bounds of the simulation
	NzSteps = 50 # Number of z Steps
	chebDiffMatrix, chebMesh = functions.cheb(NzSteps) # checyshev mesh is defined between -1 and 1
	z = zL*chebMesh # space
	chebDiffMatrix_norm = chebDiffMatrix / zL # to compensate the change of variable
	dz = np.mean(np.diff(z))

	# N = N0 * ones(1,length(z)-1) # atomic density
	N = N0 * np.piecewise(z, [z < -D/2, z > D/2], [0, 0, 1]) # atomic density

	#### read and write timings and amplitudes
	t0signal = -(L/2/c + 5/sig_s) 
	t0write =  +(L/2/c + 5/sig_s)
	t0readR = t0write + 12/sig_s
	t0readL = t0signal - 8/sig_s
	alpha1 = 1 # amp of read pulse

	T = 30/sig_s #1 * (abs(t0read) + abs(t0signal))  # Simulation time 
	StepSize = 0.4 # simulation step size
	NtSteps = round(c * T / L * NzSteps**2 / StepSize)
	t = np.linspace(0,T,NtSteps) # time
	dt = np.mean(np.diff(t)) # time step

	print 'step size (cdt/dz): {0:.2f}'.format(c*dt/dz)
	print 'number of spatial steps over the cloud: {}'.format(np.round(D/dz))
	print 'number of temporal steps over the signal pulse: {}'.format(np.round(1.0/2/sig_s/dt))
	print '(total) number of temporal steps: {}'.format(NtSteps)
	print '(total) number of spatial steps: {}'.format(z.shape[0])
	print 'c**2: {0:.2f}'.format(ramMemCoupling)
	print 'theoretical linear absorption {0:.4f}'.format(1 - np.exp(- 2*OD0 / (1 + (2*Del_s/Gam_eg)**2)))
	print 'coupling pulse energy (nJ): {}, {}'.format(En_c*1e9,Energy)

	frame = long(4*2**(np.round(np.log2(sig_s*T))+1)/1+1) # number of snapshots to display
	
	## initial condition (t=0)
	S = np.zeros((nLvls*(nLvls-1)/2,z.shape[0])) # coherences at t=0

	Om_s_0 = Om0_s *  np.exp(-(sig_s)**2/4 * (z/c - t0signal)**2) # gaussian- signal field initial 
	Om_c_0 = Om0_c *  np.exp(-(sig_cW)**2/4 * (z/c - t0write)**2) + alpha1 * Om0_c *  np.exp(-(sig_cR)**2 * (z/c - t0readR)**2) # gaussian- pump field initial value
	
	Om_s_bc = Om0_s *  np.exp(-(sig_s)**2/4 * (zL/c - t0signal - t)**2) # gaussian- signal field BC 
	Om_c_bc = Om0_c *  np.exp(-(sig_cW)**2/4 * (zR/c - t0write + t)**2) + alpha1 * Om0_c * np.exp(-(sig_cR)**2/4 * (zR/c - t0readR + t)**2) # gaussian- pump field BC value

	P = np.append([np.ones(z.shape[0])], np.zeros((nLvls-1,z.shape[0])), axis=0) # initial populations

	## initialization
	# [Es Ec Pg, Pe, Pr, Sge, Ser, Sgr]
	Sol = np.append(np.append([Om_s_0], [Om_c_0], axis=0), np.append(P, S, axis=0), axis=0) # pde solution

	i_ti = np.argmin(np.absolute(t-(t0signal-4/sig_s))) # frames start time marker
	i_t = np.round(np.linspace(i_ti,t.shape[0],frame))
	
	return frame,z,t,N, Sol, Om_s_bc, Om_c_bc, dt, i_t, c, Gam_eg, Gam_re, gam_gr, gs, gc, Del_s, Del_c, chebDiffMatrix_norm, Om0_s, Om0_c