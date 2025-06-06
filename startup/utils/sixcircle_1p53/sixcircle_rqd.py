# sixcircle_rqd: codes for diffractometer at BL35XU, BL43LXU, SPring-8
# Required additional documents: 1- sixcircle.py, 2- scbasic.py, 3- ini.conf, 4- BL43XU_CONST.mac, 5- BL35XU_CONST.mac

# Developed with Python 3.7.3, numpy 1.16.4, scipy 1.3.0
# Materials Dynamics Laboratory, RIKEN SPring-8 Center
# Ver 1.53, Jun 2021

# Authors: Wenyang Zhao & Alfred Q. R. Baron
# Contact: baron@spring8.or.jp

# If this code is used independently of work at BL43, please reference the writeup ("Open-source Python software for six-circle diffraction with an inelastic x-ray scattering (IXS) spectrometer" by Wenyang ZHAO and Alfred Q.R. BARON, unpublished, available at https://beamline.harima.riken.jp/bl43lxu)

# In typical use related to experimental work at BL43LXU, it is enough to reference a BL publication.  However, if this code is used extensively, then please include a separate reference as above.

import sixcircle
from sixcircle import *

import numpy as np
import math

import subprocess

print ('Loading sixcircle_rqd.py - for IXS users at SPring-8 - W. Zhao and A. Baron')

sixcircle.wdesc('ini_rqd()','Initialize (for BL43 IXS Spectrometer)')
def ini_rqd():
    global agaph, agapv
    agaph = 80.0 ;  agapv = 80.0
    # Default: incident beam is not set
    # Incident beam setup
    global incident_beam_is_setup
    incident_beam_is_setup = False
    setincident(1)
    # Default set bl43
    global flag_bl
    flag_bl = 43
    setbl(43)

# Set wavelength with silicon backreflection order
# Usage:  setorder()  or  setorder(n)
sixcircle.wdesc('setorder(n)','Sets wavelength for Si(nnn) reflection near RT')
def setorder(*args):
    if len(args) == 0:
        n = int(input('Order: '))
    elif len(args) == 1:
        n = int(args[0])
    else:
        print ('\nUsage:  setorder()  or  setorder(n)')
    if int(n) <= 0:
        print ('\nInvalid argument: {0}\n'.format(n))
        return
    # Silicon lattice constant
    asi = 5.431
    sixcircle.LAMBDA = 2*asi / (n*3**0.5)
    print ('\nWavelength set to {0:.{1}f}'.format(sixcircle.LAMBDA, sixcircle.PRE+2))
    print ('')

# Set beamline
# Usage:  setbl()  or setbl(43)
sixcircle.wdesc('setbl(n)','Sets diffraction calcs for either BL43LXU (n=43) or BL35(n=35)')
def setbl(*args):
    global flag_bl
    # x_n, z_n: columns and rows of analyzers; x_cen, z_cen: location of center analyzer
    global x_n, z_n, x_cen, z_cen
    # x_spac, z_spac: spacing of analyzers in x and z direction
    # x_off, z_off: offset of analyzers in x and z direction, +x -> larger tth, +z -> downward (+gam)
    # ah_size, av_size: analyzer size
    # a_radi: arm radius of analyzers
    # ah_size, av_size: horizontal and vertical size of analyzers, for bl35, ah_size = av_size = dia.
    # sh_radi, sv_radi: arm radius of horizontal and vertical slits, for bl35, sh_radi = sv_radi
    global x_spac, z_spac, x_off, z_off, ah_size, av_size, a_radi, sh_radi, sv_radi
    if len(args) == 0:
        flag_loop = True
        while flag_loop == True:
            flag_bl_input = input('Set beamline (35 or 43, currently {0})? '.format(flag_bl))
            if len(flag_bl_input) == 0:
                flag_bl_input = str(flag_bl)
            if (flag_bl_input in ['35','43']) == False:
                print ('Invalid argument for setbl: {0}\n'.format(flag_bl_input))
                continue
            flag_loop = False
            flag_bl = int(flag_bl_input)
    elif len(args) == 1:
        flag_bl_input = str(args[0])
        if (flag_bl_input in ['35','43']) == False:
            print ('Invalid argument for setbl: {0}\n'.format(flag_bl_input))
            return
        flag_bl = int(flag_bl_input)
    else:
        print ('\nUsage:  setbl()  or  setbl(43)\n')
        return
    print ('Beamline set to {0}'.format(flag_bl))
    # Read constants in BL43LXU
    if flag_bl == 43:
        try:
            with open('BL43XU_CONST.mac', 'r') as f:
                lines = f.read().split('\n')
        except:
            print ('')
            print ('Error! Cannot read BL43XU_CONST.mac')
            print ('Please run  setbl()  again after fixing this problem')
            print ('')
            return
        dic = {}
        for line in lines:
            if line.startswith('constant') == True:
                constantstr = line.split()[1]
                constantvalue = float(line.split()[2])
                dic.update({constantstr:constantvalue})
        x_spac = dic['ANALYZ42_X_SPAC_MM']
        z_spac = dic['ANALYZ42_Z_SPAC_MM']
        a_radi = dic['ANALYZ42_RADIUS_MM']
        x_off = dic['OFFSET42X_MM']
        z_off =  - dic['OFFSET42Z_MM']
        sh_radi = dic['SLIT42H_RADIUS_MM']
        sv_radi = dic['SLIT42V_RADIUS_MM']
        ah_size = dic['ANALYZ42_WIDTH_MM']
        av_size = dic['ANALYZ42_HEIGHT_MM']
        x_n = 7
        z_n = 4
        x_cen = 3
        z_cen = 0
    # Read constants in BL35
    if flag_bl == 35:
        try:
            with open('BL35XU_CONST.mac', 'r') as f:
                lines = f.read().split('\n')
        except:
            print ('')
            print ('Error! Cannot read BL35XU_CONST.mac')
            print ('Please run  setbl()  again after fixing this problem')
            print ('')
            return
        dic = {}
        for line in lines:
            if line.startswith('constant') == True:
                constantstr = line.split()[1]
                constantvalue = float(line.split()[2])
                dic.update({constantstr:constantvalue})
        x_spac = dic['ANALYZ12_X_SPAC_MM']
        z_spac = dic['ANALYZ12_Z_SPAC_MM']
        a_radi = dic['ANALYZ12_RADIUS_MM']
        x_off = dic['OFFSET12_X_MM']
        z_off = dic['OFFSET12_Z_MM']
        sh_radi = dic['SLIT12_RADIUS_MM']
        sv_radi = dic['SLIT12_RADIUS_MM']
        ah_size = dic['ANALYZ12_DIAM_MM']
        av_size = dic['ANALYZ12_DIAM_MM']
        x_n = 4
        z_n = 3
        x_cen = 1.5
        z_cen = 1

# Incident beam setup
# Usage:  setinci  or  setincident(itype)
sixcircle.wdesc('setincident(n),showincident()','Sets/shows incident beam characterisitcs - divergence and mu.')
def setincident(*args):
    showincident()
    # ALPHA_V > 0    incident beam moves upward
    # ALPHA_H > 0    incident beam moves toward the experimental hall
    global ALPHA_V, ALPHA_H, SAM_cz, BEAM_IN_DIV_H, BEAM_IN_DIV_V
    global INCIDENT_BEAM_SETUP_STRING, RF_DWELL_TIME, RF_SPV_STEP_SIZE
    global INCIDENT_BEAM_SETUP_TYPE, incident_beam_is_setup
    dic_DES = {}
    dic_ALPHA_V = {}
    dic_ALPHA_H = {}
    dic_SAM_cz = {}
    dic_BEAM_IN_DIV_H = {}
    dic_BEAM_IN_DIV_V = {}
    dic_INCIDENT_BEAM_SETUP_STRING = {}
    dic_RF_DWELL_TIME = {}
    dic_RF_SPV_STEP_SIZE = {}
    # Preset values of incident beam setup type
    # Type 1
    dic_DES[1] = 'BL43LXU usual operation with M3'
    dic_ALPHA_V[1] = 3.0/1000;  dic_ALPHA_H[1] = 0.0
    dic_SAM_cz[1] = 0.0
    dic_BEAM_IN_DIV_H[1] = 3.0/5000;  dic_BEAM_IN_DIV_V[1] = 1.0/5000
    dic_INCIDENT_BEAM_SETUP_STRING[1] = 'STDM3'
    dic_RF_DWELL_TIME[1] = 300.0;  dic_RF_SPV_STEP_SIZE[1] = 0.05
    # Type 2
    dic_DES[2] = 'BL43LXU prsim lens + KBv'
    dic_ALPHA_V[2] = -3.0/1000;  dic_ALPHA_H[2] = 0.0
    dic_SAM_cz[2] = 0.0 
    dic_BEAM_IN_DIV_H[2] = 0.00125;  dic_BEAM_IN_DIV_V[2] = 0.001
    dic_INCIDENT_BEAM_SETUP_STRING[2] = 'PLKBV'
    dic_RF_DWELL_TIME[2] = 100.0;  dic_RF_SPV_STEP_SIZE[2] = 0.015 
    # Type 3
    dic_DES[3] = 'BL43LXU Multilayer KB'
    dic_ALPHA_V[3] = 0.0275;  dic_ALPHA_H[3] = math.radians(1.5388) 
    dic_SAM_cz[3] = -20.0
    dic_BEAM_IN_DIV_H[3] = 2.5/400;  dic_BEAM_IN_DIV_V[3] = 1.0/200 
    dic_INCIDENT_BEAM_SETUP_STRING[3] = 'MLKB'
    dic_RF_DWELL_TIME[3] = 10.0;  dic_RF_SPV_STEP_SIZE[3] = 0.006
    # Type 4
    dic_DES[4] = 'BL43LXU Multilayer KB with limited horizontal acceptance (1.5 mm at 400 mm)'
    dic_ALPHA_V[4] = 0.0275;  dic_ALPHA_H[4] = 0.0279 
    dic_SAM_cz[4] = -20.0 
    dic_BEAM_IN_DIV_H[4] = -1.5/400;  dic_BEAM_IN_DIV_V[4] = -1.0/200 
    dic_INCIDENT_BEAM_SETUP_STRING[4] = 'L-MLKB'
    dic_RF_DWELL_TIME[4] = 10.0;  dic_RF_SPV_STEP_SIZE[4] = 0.006
    # Type 9
    dic_DES[9] = '(manual input)'
    dic_ALPHA_V[9] = 0;  dic_ALPHA_H[9] = 0
    dic_SAM_cz[9] = -240.0
    dic_BEAM_IN_DIV_H[9] = 3.0/400;  dic_BEAM_IN_DIV_V[9] = 1.0/200 
    dic_INCIDENT_BEAM_SETUP_STRING[9] = 'MANUAL/MLKB'
    dic_RF_DWELL_TIME[9] = 20.0;  dic_RF_SPV_STEP_SIZE[9] = 0.006
    if len(args) == 1:
        itype_input = args[0]
        if (itype_input in [1,2,3,4,9]) == False:
            print ('Error! Incident beam setup type {0} not defined!'.format(itype_input))
            return
    elif len(args) == 0:
        print ('')
        print ('Incident beam type (1, 2, 3, 4, 9):')
        print ('')
        print (' 1. Usual operation at BL43: M3 with 50 um beam')
        print (' 2. Prism lens + KBv:  BL43, no longer used')
        print (' 3. Multilayer KB:  BL43 small sample setup, 5 um beam')
        print (' 4. Multilayer KB with limited horizontal acceptance (1.5 mm at 40 mm) - as 3, but reduced H divergence.')
        print (' 9. Manual setting')
        flag_loop = True
        while flag_loop == True:
            print ('')
            try:
                itype_input = int(input('Please select: '))
            except:
                print ('Invalid input! Retry...')
                continue
            if (itype_input in [1,2,3,4,9]) == False:
                print ('Incident beam setup type {0} not defined! Retry...'.format(itype_input))
                continue
            flag_loop = False
    else:
        print ('Usage:  setincident()  or  setincident(itype)')
        return
    itype = itype_input
    print ('Setting incident beam parameters for {0}'.format(dic_DES[itype]))
    ALPHA_V = dic_ALPHA_V[itype];  ALPHA_H = dic_ALPHA_H[itype]
    SAM_cz = dic_SAM_cz[itype]
    BEAM_IN_DIV_H = dic_BEAM_IN_DIV_H[itype];  BEAM_IN_DIV_V = dic_BEAM_IN_DIV_V[itype]
    INCIDENT_BEAM_SETUP_STRING = dic_INCIDENT_BEAM_SETUP_STRING[itype]
    RF_DWELL_TIME = dic_RF_DWELL_TIME[itype];  RF_SPV_STEP_SIZE = dic_RF_SPV_STEP_SIZE[itype]
    # Manual setting for type 9
    if itype == 9:
        print ('')
        #  ALPHA_V
        flag_loop = True
        while flag_loop == True:
            try:
                t = float(input(' Vertical beam angle (mrad)? '))
            except:
                print (' Error! Invalid input. Retry...\n')
                continue
            ALPHA_V = 1000 * t / 1000.0
            flag_loop = False
        # ALPHA_H
        flag_loop = True
        while flag_loop == True:
            try:
                t = float(input(' Horizontal beam angle (mrad)? '))
            except:
                print (' Error! Invalid input! Retry...\n')
                continue
            ALPHA_H = 1000 * t / 1000
            flag_loop = False
    INCIDENT_BEAM_SETUP_TYPE = itype
    incident_beam_is_setup = True
    # Move mu (and set frozen mu) based on ALPHA_V
    # Impact of ALPHA_H not considered
    sixcircle.MU = - math.degrees(ALPHA_V)
    sixcircle.F_MU = sixcircle.MU
    print (' -> mu set to {0:.{1}f} degrees'.format(sixcircle.MU, sixcircle.PRE))
    print ('')

# Show incident beam setup
# Useage:  showincident()
def showincident():
    print ('')
    if incident_beam_is_setup == False:
        print ('Incident beam has not been set up')
        return
    print ('Present incident beam type is {0} ({1})'.format(INCIDENT_BEAM_SETUP_TYPE, INCIDENT_BEAM_SETUP_STRING))
    print (' Beam Vertical Angle (+ is moving upward):       ALPHA_V = {0:<.2f} mrad = {1:<5.3f} deg    V Divergence = {2:<5.2f} mrad'.format(ALPHA_V*1000,math.degrees(ALPHA_V),1000*BEAM_IN_DIV_V))
    print (' Beam Horizontal Angle (effective zero of tth):  ALPHA_H = {0:<.2f} mrad = {1:<5.3f} deg    H Divergence = {2:<5.2f} mrad'.format(ALPHA_H*1000,math.degrees(ALPHA_H),1000*BEAM_IN_DIV_H))
    print (' Sample height relative to first analyzer row:   SAM_cz  = {0:<.1f} mm'.format(SAM_cz))
    print ('')

# Move slits of analyzers
# Usage:  mvgap()  or  mvgap(agaph=?,agapv=?)
sixcircle.wdesc('mvgap(agaph=?,agapv=?)  also setgap','Sets analyzer slit gap size (control Q resolution)')
def mvgap(**args):
    global agaph, agapv
    agaph_old = agaph; agapv_old = agapv
    if len(args) == 0:
        print ('')
        print ('Current position:')
        print ('')
        print ('{0:>10}{1:>10}'.format('agaph','agapv'))
        print ('{0:>10.1f}{1:>10.1f}'.format(agaph,agapv))
        print ('')
        print ('Usage:  mvgap(agaph=?,agapv=?)')
        return
    for key in args.keys():
        if (key in ['agaph','agapv']) == False:
            print ('Invalid motor mnemonic for mvgap: {0}\n'.format(key))
    for value in args.values():
        if (type(value) in [int,float]) == False:
            print ('Invalid motor position for mvgap: {0}\n'.format(value))
            return
    if 'agaph' in args.keys():
        agaph = args['agaph']
    if 'agapv' in args.keys():
        agapv = args['agapv']
    print("  agapv: %.1f -> %.1f    agaph: %.1f -> %.1f  " %(agapv_old,agapv,agaph_old,agaph))

def setgap(**kwargs): mvgap(**kwargs)


# Print out ca6 to default printer
def pca6(*args):
    ca6(*args)
    if len(args) == 6:
        cmd=['a2ps', '-d', '-R', '-B', '--columns=1', '--font-size=8', 'hkl_pos']
        subprocess.call(cmd)
    if len(args) == 3:
        cmd=['a2ps', '-d', '-R', '-B', '--columns=1', '--font-size=8', 'hkl_pos']
        subprocess.call(cmd)

# Calculate H, K, L of every analyzer
# Usage:  ca6(H,K,L)  or  ca6(H,K,L,Href,Kref,Lref)
# Reference vector (Href, Kref, Lref), usually is a nearby gamma point
sixcircle.wdesc('ca6(H,K,L)','Finds analyzer Q vectors for arm center at (H,K,L)')
sixcircle.wdesc('ca6(H,K,L,Href,Kref,Lref)','Finds analyzer q = (H,K,L)-(Href,Kref,Lref) for arm center at (H,K,L)')
def ca6(*args):
    # make some global variables available for other routines such as plotting packages
    global A_str, A_Q, A_q, A_ABSQ, A_absq, A_dQH, A_dQV, A_dQ
    for value in args:
        if (type(value) in [int,float]) == False:
            print ('\nInvalid argument: {0}\n'.format(value))
    if len(args) == 3:
        caH, caK, caL = args
    elif len(args) == 6:
        caH, caK, caL, Href, Kref, Lref = args
    else:
        print ('\nUsage:  ca6(H,K,L)  or  ca6(H,K,L,Href,Kref,Lref)\n')
        return
    # Calculate positions
    flagca, pos = ca_s(caH,caK,caL)
    if flagca == False:
        print ('Error: Impossible reflection for present frozen!')
        return
    # Record current positions for ease of coming back after calculation
    o_tth, o_th, o_chi, o_phi, o_mu, o_gam = (sixcircle.TTH, sixcircle.TH, sixcircle.CHI, sixcircle.PHI, sixcircle.MU, sixcircle.GAM)
    # Calculate for the first set of pos
    ca_tth, ca_th, ca_chi, ca_phi, ca_mu, ca_gam, ca_sa, ca_omega, ca_azimuth, ca_alpha, ca_beta = pos[0]
    # Record current condition of wh_on (wh_off); turn off wh() after mv()
    o_FLAG_WH = sixcircle.FLAG_WH
    sixcircle.FLAG_WH = False
    mv(tth=ca_tth,th=ca_th,chi=ca_chi,phi=ca_phi,mu=ca_mu,gam=ca_gam)
    A_str = [['0' for xi in range(0,x_n)] for zi in range(0,z_n)]
    A_Q = [[0 for xi in range(0,x_n)] for zi in range(0,z_n)]
    A_q = [[0 for xi in range(0,x_n)] for zi in range(0,z_n)]
    A_ABSQ = [[0 for xi in range(0,x_n)] for zi in range(0,z_n)]
    A_absq = [[0 for xi in range(0,x_n)] for zi in range(0,z_n)]
    A_dQH = [[0 for xi in range(0,x_n)] for zi in range(0,z_n)]
    A_dQV = [[0 for xi in range(0,x_n)] for zi in range(0,z_n)]
    A_dQ = [[0 for xi in range(0,x_n)] for zi in range(0,z_n)]
    for zi in range(0,z_n):
        for xi in range(0,x_n):
            # Give analyzer name
            if flag_bl == 43:
                if zi <= 2:
                    A_str[zi][xi] = 'a' + str(11*zi+6+(xi-x_cen)).zfill(2)
                elif zi >= 3:
                    A_str[zi][xi] = 'a' + str(11*zi+6+(xi-x_cen)-1).zfill(2)
            if flag_bl == 35:
                if zi == 0:
                    A_str[zi][xi] = 'a' + str(5+xi).zfill(2)
                elif zi == 1:
                    A_str[zi][xi] = 'a' + str(1+xi).zfill(2)
                elif zi == 2:               
                    A_str[zi][xi] = 'a' + str(9+xi).zfill(2)
            # Calculate H, K, L at center of each analyzer (A_gam, A_tth)
            A_z = z_off + z_spac * (z_cen - zi)
            A_x = x_off + x_spac * (xi - x_cen)
            A_tth = ca_tth + math.degrees(math.atan2(A_x, a_radi))
            A_gam = ca_gam + math.degrees(math.atan2(A_z, (a_radi**2 + A_x**2)**0.5))
            mv(tth=A_tth, gam=A_gam)
            A_Q[zi][xi] = [sixcircle.H, sixcircle.K, sixcircle.L]
            # Q length, unit A-1
            A_ABSQ[zi][xi] = np.linalg.norm(np.dot(sixcircle.M_B, np.array([[sixcircle.H],[sixcircle.K],[sixcircle.L]])))
            if len(args)==6:
                A_q[zi][xi] = [sixcircle.H-Href, sixcircle.K-Kref, sixcircle.L-Lref]
                # Q length, unit A-1                
                A_absq[zi][xi] = np.linalg.norm(np.dot(sixcircle.M_B, np.array([[sixcircle.H-Href],[sixcircle.K-Kref],[sixcircle.L-Lref]])))
            # Calculate H, K, L at four edges of each analyzer
            A_x_left = A_x + min(agaph*a_radi/sh_radi,ah_size)/2
            A_x_right = A_x - min(agaph*a_radi/sh_radi,ah_size)/2
            A_z_up = A_z + min(agapv*a_radi/sv_radi,av_size)/2
            A_z_low = A_z - min(agapv*a_radi/sv_radi,av_size)/2
            A_tth_left = ca_tth + math.degrees(math.atan2(A_x_left, a_radi))
            A_tth_right = ca_tth + math.degrees(math.atan2(A_x_right, a_radi))
            A_gam_up = ca_gam + math.degrees(math.atan2(A_z_up, (a_radi**2 + A_x**2)**0.5))
            A_gam_low = ca_gam + math.degrees(math.atan2(A_z_low, (a_radi**2 + A_x**2)**0.5))
            # Upper edge
            mv(tth=A_tth, gam=A_gam_up)
            A_Q_up = np.array([sixcircle.H, sixcircle.K, sixcircle.L])
            # Lower edge
            mv(tth=A_tth, gam=A_gam_low)
            A_Q_low = np.array([sixcircle.H, sixcircle.K, sixcircle.L])
            # Left edge
            mv(tth=A_tth_left, gam=A_gam)
            A_Q_left = np.array([sixcircle.H, sixcircle.K, sixcircle.L])
            # Right edge
            mv(tth=A_tth_right, gam=A_gam)
            A_Q_right = np.array([sixcircle.H, sixcircle.K, sixcircle.L])
            # Horizontal dQ
            A_dQH[zi][xi] = A_Q_left - A_Q_right
            # Vertical dQ
            A_dQV[zi][xi] = A_Q_low - A_Q_up
            # dQ
            A_dQ[zi][xi] = (A_dQH[zi][xi]**2 + A_dQV[zi][xi]**2)**0.5
    # Average horizontal dQ and vertical dQ for 28 positions
    aver_dQH = np.array([0,0,0])
    aver_dQV = np.array([0,0,0])
    for zi in range(0,z_n):
        for xi in range(0,x_n):
            aver_dQH = aver_dQH + A_dQH[zi][xi]
            aver_dQV = aver_dQV + A_dQV[zi][xi]
    aver_dQH = aver_dQH / (z_n*x_n)
    aver_dQV = aver_dQV / (z_n*x_n)
    print('')
    if len(args) == 6:
        print('Q: ({0:.{3}f}  {1:.{3}f}  {2:.{3}f})'.format(caH,caK,caL,sixcircle.PRE), end='')
        print('   Qref: ({0:.{3}f}  {1:.{3}f}  {2:.{3}f})\n'.format(Href,Kref,Lref,sixcircle.PRE), end='') 
    if len(args) == 3:
        print('Q: ({0:.{3}f}  {1:.{3}f}  {2:.{3}f})\n'.format(caH,caK,caL,sixcircle.PRE), end='')
    print('    at tth={0:.{8}f}, th={1:.{8}f}, chi={2:.{8}f}, phi={3:.{8}f}, mu={4:.{8}f}, gam={5:.{8}f}  H={6:.1f}  V={7:.1f}'.format(ca_tth,ca_th,ca_chi,ca_phi,ca_mu,ca_gam,agaph,agapv,sixcircle.PRE+1))
    print('')
    latprt = (sixcircle.g_sample,sixcircle.g_aa,sixcircle.g_bb,sixcircle.g_cc,sixcircle.g_al,sixcircle.g_be,sixcircle.g_ga)
    print('Sample {0}    a/b/c {1:.{7}f}/{2:.{7}f}/{3:.{7}f}    alpha/beta/gamma {4:.{7}f}/{5:.{7}f}/{6:.{7}f}'.format(*latprt,sixcircle.PRE))
    infprt = (sixcircle.LAMBDA,sixcircle.g_frozen,sixcircle.g_haz,sixcircle.g_kaz,sixcircle.g_laz,ca_alpha,ca_beta)
    print('Wavelength {0:.{7}f}    frozen={1}    AZ ({2:.{8}f}, {3:.{8}f}, {4:.{8}f})    ALPHA={5:.{8}f}  BETA={6:.{8}f}'.format(*infprt,sixcircle.PRE+2,sixcircle.PRE))
    print('Or0: ({0:.{3}f}, {1:.{3}f}, {2:.{3}f})'.format(sixcircle.g_h0,sixcircle.g_k0,sixcircle.g_l0,sixcircle.PRE+1), end='')
    or0prt = (sixcircle.g_u00,sixcircle.g_u01,sixcircle.g_u02,sixcircle.g_u03,sixcircle.g_u04,sixcircle.g_u05)
    print('    at tth={0:.{6}f}, th={1:.{6}f}, chi={2:.{6}f}, phi={3:.{6}f}, mu={4:.{6}f}, gam={5:.{6}f}  '.format(*or0prt,sixcircle.PRE))
    print('Or1: ({0:.{3}f}, {1:.{3}f}, {2:.{3}f})'.format(sixcircle.g_h1,sixcircle.g_k1,sixcircle.g_l1,sixcircle.PRE+1), end='')
    or1prt = (sixcircle.g_u10,sixcircle.g_u11,sixcircle.g_u12,sixcircle.g_u13,sixcircle.g_u14,sixcircle.g_u15)
    print('    at tth={0:.{6}f}, th={1:.{6}f}, chi={2:.{6}f}, phi={3:.{6}f}, mu={4:.{6}f}, gam={5:.{6}f}'.format(*or1prt,sixcircle.PRE))
    print('')
    for zi in range(0,z_n):
        for xi in range(0,x_n):
            if len(args) == 6:
                afmt = '{0}: ({1:>{11}.{12}f}, {2:>{11}.{12}f}, {3:>{11}.{12}f})  |q|={4:>6.2f}/nm  dq:({5:>{11}.{12}f}, {6:>{11}.{12}f}, {7:>{11}.{12}f})  Qtot:({8:>{11}.{12}f}, {9:>{11}.{12}f}, {10:>{11}.{12}f})'
                aprt = (A_str[zi][xi],A_q[zi][xi][0],A_q[zi][xi][1],A_q[zi][xi][2],A_absq[zi][xi]*10,A_dQ[zi][xi][0],A_dQ[zi][xi][1],A_dQ[zi][xi][2],A_Q[zi][xi][0],A_Q[zi][xi][1],A_Q[zi][xi][2])
                print(afmt.format(*aprt,sixcircle.PRE+3,sixcircle.PRE))
            if len(args) == 3:
                afmt = '{0}: ({1:>{8}.{9}f}, {2:>{8}.{9}f}, {3:>{8}.{9}f})  |Q|={4:>6.2f}/nm  dq:({5:>{8}.{9}f}, {6:>{8}.{9}f}, {7:>{8}.{9}f})'
                aprt = (A_str[zi][xi],A_Q[zi][xi][0],A_Q[zi][xi][1],A_Q[zi][xi][2],A_ABSQ[zi][xi]*10,A_dQ[zi][xi][0],A_dQ[zi][xi][1],A_dQ[zi][xi][2])
                print(afmt.format(*aprt,sixcircle.PRE+3,sixcircle.PRE))
        print('')
    dqprt = (agaph,aver_dQH[0],aver_dQH[1],aver_dQH[2],agapv,aver_dQV[0],aver_dQV[1],aver_dQV[2])
    print('Av.  dq  H({0:.1f}): ({1:.{8}f},{2:.{8}f},{3:.{8}f})  V({4:.1f}): ({5:.{8}f},{6:.{8}f},{7:.{8}f})'.format(*dqprt,sixcircle.PRE))
    # Come back to original positions
    mv(tth=o_tth, th=o_th, chi=o_chi, phi=o_phi, mu=o_mu, gam=o_gam)
    # Come back to original wh_on (wh_off)
    sixcircle.FLAG_WH = o_FLAG_WH
    # Create document gpi.hkl_pos
    print ('')
    print ('HKL values to:  gpi.hkl_pos')
    try:
        with open('gpi.hkl_pos', 'w') as f:
            for zi in range(0,z_n):
                for xi in range(0,x_n):
                    f.write('hkl_{0} = "({1:.{4}f}, {2:.{4}f}, {3:.{4}f})"\n'.format(A_str[zi][xi],A_Q[zi][xi][0],A_Q[zi][xi][1],A_Q[zi][xi][2],sixcircle.PRE))        
            f.write('\n')
            f.write('dq_Hav({0:.1f}) = "({1:.{4}f}, {2:.{4}f}, {3:.{4}f})"\n'.format(agaph,aver_dQH[0],aver_dQH[1],aver_dQH[2],sixcircle.PRE))
            f.write('dq_Vav({0:.1f}) = "({1:.{4}f}, {2:.{4}f}, {3:.{4}f})"'.format(agapv,aver_dQV[0],aver_dQV[1],aver_dQV[2],sixcircle.PRE))
    except:
        print ('\nError in writing gpi.hkl_pos')
    # Create document hkl_pos
    print ('HKL values to:  hkl_pos')
    try:
        with open('hkl_pos', 'w') as g:
            if len(args) == 6:
                g.write('Q: ({0:.{3}f}  {1:.{3}f}  {2:.{3}f})'.format(caH,caK,caL,sixcircle.PRE))
                g.write('   Qref: ({0:.{3}f}  {1:.{3}f}  {2:.{3}f})\n'.format(Href,Kref,Lref,sixcircle.PRE))
            if len(args) == 3:
                g.write('Q: ({0:.{3}f}  {1:.{3}f}  {2:.{3}f})\n'.format(caH,caK,caL,sixcircle.PRE))
            g.write(' at tth={0:.{8}f}, th={1:.{8}f}, chi={2:.{8}f}, phi={3:.{8}f}, mu={4:.{8}f}, gam={5:.{8}f}  H={6:.1f}  V={7:.1f}\n'.format(ca_tth,ca_th,ca_chi,ca_phi,ca_mu,ca_gam,agaph,agapv,sixcircle.PRE+1))
            g.write('\n')
            g.write('Sample {0}    a/b/c {1:.{7}f}/{2:.{7}f}/{3:.{7}f}    alpha/beta/gamma {4:.{7}f}/{5:.{7}f}/{6:.{7}f}\n'.format(*latprt,sixcircle.PRE))
            g.write('Wavelength {0:.{7}f}    frozen={1}    AZ ({2:.{8}f}, {3:.{8}f}, {4:.{8}f})    ALPHA={5:.{8}f}  BETA={6:.{8}f}\n'.format(*infprt,sixcircle.PRE+2,sixcircle.PRE))
            g.write('Or0: ({0:.{3}f}, {1:.{3}f}, {2:.{3}f})'.format(sixcircle.g_h0,sixcircle.g_k0,sixcircle.g_l0,sixcircle.PRE))
            g.write(' at tth={0:.{6}f}, th={1:.{6}f}, chi={2:.{6}f}, phi={3:.{6}f}, mu={4:.{6}f}, gam={5:.{6}f}\n'.format(*or0prt,sixcircle.PRE+1))
            g.write('Or1: ({0:.{3}f}, {1:.{3}f}, {2:.{3}f})'.format(sixcircle.g_h1,sixcircle.g_k1,sixcircle.g_l1,sixcircle.PRE))
            g.write(' at tth={0:.{6}f}, th={1:.{6}f}, chi={2:.{6}f}, phi={3:.{6}f}, mu={4:.{6}f}, gam={5:.{6}f}\n'.format(*or1prt,sixcircle.PRE+1))
            if len(args) == 6: g.write('-' * 104); g.write('\n') 
            if len(args) == 3: g.write('-' * 73); g.write('\n')
            for zi in range(0,z_n):
                for xi in range(0,x_n):
                    if len(args) == 6:
                        afmt1 = '{0}: ({1:>{11}.{12}f}, {2:>{11}.{12}f}, {3:>{11}.{12}f})  |q|={4:>6.2f}/nm  dq:({5:>{11}.{12}f}, {6:>{11}.{12}f}, {7:>{11}.{12}f})  Qtot:({8:>{11}.{12}f}, {9:>{11}.{12}f}, {10:>{11}.{12}f})\n'
                        aprt1 = (A_str[zi][xi],A_q[zi][xi][0],A_q[zi][xi][1],A_q[zi][xi][2],A_absq[zi][xi]*10,A_dQ[zi][xi][0],A_dQ[zi][xi][1],A_dQ[zi][xi][2],A_Q[zi][xi][0],A_Q[zi][xi][1],A_Q[zi][xi][2])
                        g.write(afmt1.format(*aprt1,sixcircle.PRE+3,sixcircle.PRE))
                    if len(args) == 3:
                        afmt1 = '{0}: ({1:>{8}.{9}f}, {2:>{8}.{9}f}, {3:>{8}.{9}f})  |Q|={4:>6.2f}/nm  dq:({5:>{8}.{9}f}, {6:>{8}.{9}f}, {7:>{8}.{9}f})\n'
                        aprt1 = (A_str[zi][xi],A_Q[zi][xi][0],A_Q[zi][xi][1],A_Q[zi][xi][2],A_ABSQ[zi][xi]*10,A_dQ[zi][xi][0],A_dQ[zi][xi][1],A_dQ[zi][xi][2],)
                        g.write(afmt1.format(*aprt1,sixcircle.PRE+3,sixcircle.PRE))
                if len(args) == 6: g.write('-' * 104); g.write('\n')
                if len(args) == 3: g.write('-' * 73); g.write('\n')
            g.write('\n')
            dqprt1 = (agaph,aver_dQH[0],aver_dQH[1],aver_dQH[2],agapv,aver_dQV[0],aver_dQV[1],aver_dQV[2])
            g.write('Av.  dq  H({0:.1f}): ({1:.{8}f},{2:.{8}f},{3:.{8}f})  V({4:.1f}): ({5:.{8}f},{6:.{8}f},{7:.{8}f})\n'.format(*dqprt1,sixcircle.PRE))
    except:
        print ('\nError in writing hkl_pos')
    print ('')
    print ('Command(BL43LXU):      ', end='')    
    print ('mv tth {0:.{8}f} th {1:.{8}f} chi {2:.{8}f} phi {3:.{8}f} agaph {6:.1f} agapv {7:.1f}'.format(ca_tth,ca_th,ca_chi,ca_phi,ca_mu,ca_gam,agaph,agapv,sixcircle.PRE))
    print ()



# Find |Q| and d|Q| of every analyzer at current TTH, MU, GAMMA
# Usage:  htth_q()
sixcircle.wdesc('htth_q','Determines analyzer |Q| (and resolution including inc. divergence)')
def htth_q():
    if incident_beam_is_setup == False:
        print ('Incident beam has not been set up -> please run  setincident()')
        return
    # Record current positions for ease of coming back after calculation
    o_tth, o_th, o_chi, o_phi, o_mu, o_gam = (sixcircle.TTH, sixcircle.TH, sixcircle.CHI, sixcircle.PHI, sixcircle.MU, sixcircle.GAM)
    # Scattering angle at arm center
    o_sa = sixcircle.SA
    # Nominal |Q| at arm center
    o_absq = sixcircle.ABSQ
    # dq_ash: dq due to BEAM_IN_DIV_H
    # Impact of mu and gam is considered, unlike htthe43 macro
    half_sa_1 = scbasic.thetaD_angle_2(o_tth/2 + math.degrees(BEAM_IN_DIV_H/2), o_mu, o_gam)
    half_sa_2 = scbasic.thetaD_angle_2(o_tth/2 - math.degrees(BEAM_IN_DIV_H/2), o_mu, o_gam)
    dq_ash = scbasic.Q_length(sixcircle.LAMBDA, half_sa_2) - scbasic.Q_length(sixcircle.LAMBDA, half_sa_1)
    # Calculate |Q| at point (x,z) refering to arm center. +x -> larger tth; +z -> downward
    def Get_ABSQ(p_x,p_z):
        p_tth = o_tth + math.degrees(math.atan2(p_x, a_radi))
        p_mu = o_mu
        p_gam = o_gam + math.degrees(math.atan2(p_z, (a_radi**2 + p_x**2)**0.5))
        half_sa = scbasic.thetaD_angle_2(p_tth/2,p_mu,p_gam)
        absq_p = scbasic.Q_length(sixcircle.LAMBDA,half_sa)
        return absq_p
    # Do calculation for each analyzer
    A_str = [['0' for xi in range(0,x_n)] for zi in range(0,z_n)]
    # Average |Q|, not |Q| at crystal center
    A_AVG_ABSQ = [[0 for xi in range(0,x_n)] for zi in range(0,z_n)]
    # Full width of |Q|, |Q|max - |Q|min
    A_FW_ABSQ = [[0 for xi in range(0,x_n)] for zi in range(0,z_n)]
    # RMSE of |Q|
    A_RMSE_ABSQ = [[0 for xi in range(0,x_n)] for zi in range(0,z_n)]
    # Resolution of |Q|, here, sqrt((3.5*rms)^2 + dq_ash^2)
    A_RES_ABSQ = [[0 for xi in range(0,x_n)] for zi in range(0,z_n)]
    # Mesh points 40 x 40
    nmesh = 40
    # Effective x,z on analyzer
    # Note: just an approximation for circular analyzers in bl35
    A_dx = min(agaph*a_radi/sh_radi,ah_size)
    if agaph*a_radi/sh_radi >= ah_size:
        print ('Caution: agaph full open')
    A_dz = min(agapv*a_radi/sv_radi,av_size)
    if agapv*a_radi/sv_radi >= av_size:
        print ('Caution: agapv full open')
    for zi in range(0,z_n):
        for xi in range(0,x_n):
            # Analyzer name
            if flag_bl == 43:
                if zi <= 2:
                    A_str[zi][xi] = 'a' + str(11*zi+6+(xi-x_cen)).zfill(2)
                elif zi >= 3:
                    A_str[zi][xi] = 'a' + str(11*zi+6+(xi-x_cen)-1).zfill(2)
            if flag_bl == 35:
                if zi == 0:
                    A_str[zi][xi] = 'a' + str(5+xi).zfill(2)
                elif zi == 1:
                    A_str[zi][xi] = 'a' + str(1+xi).zfill(2)
                elif zi == 2:
                    A_str[zi][xi] = 'a' + str(9+xi).zfill(2)
            # x, z at the center of each analyzer
            A_z = z_off + z_spac * (z_cen - zi)
            A_x = x_off + x_spac * (xi - x_cen)
            # Calculate nmesh by nmesh meshpoints to get avg., fw., and rmse. of |Q|
            ABSQ_mesh = []
            for zimesh in range(0,nmesh):
                A_zmesh = A_z + (zimesh/nmesh-0.5)*A_dz
                for ximesh in range(0,nmesh):
                    A_xmesh = A_x + (zimesh/nmesh-0.5)*A_dx
                    ABSQ_mesh.append(Get_ABSQ(A_xmesh,A_zmesh))
            A_AVG_ABSQ[zi][xi] = sum(ABSQ_mesh) / len(ABSQ_mesh)
            A_FW_ABSQ[zi][xi] = max(ABSQ_mesh) - min(ABSQ_mesh)
            for imesh in range(0,len(ABSQ_mesh)):
                A_RMSE_ABSQ[zi][xi] = A_RMSE_ABSQ[zi][xi] + (ABSQ_mesh[imesh]-A_AVG_ABSQ[zi][xi])**2
            A_RMSE_ABSQ[zi][xi] = (A_RMSE_ABSQ[zi][xi] / len(ABSQ_mesh)) ** 0.5
            A_RES_ABSQ[zi][xi] = ((A_RMSE_ABSQ[zi][xi]*3.5)**2 + dq_ash**2) ** 0.5
    print ('')
    print ('Qs from 1600 pt mesh. Beam setup {0} = {1}'.format(INCIDENT_BEAM_SETUP_TYPE, INCIDENT_BEAM_SETUP_STRING))
    print ('SA = {0:.{1}f} deg ->  '.format(o_sa, sixcircle.PRE), end='')
    print ('Qnom = {0:.{2}f} nm-1 at {1:.{2}f} keV  '.format(o_absq*10, 12.39854/sixcircle.LAMBDA, sixcircle.PRE), end='')
    print ('tth = {0:.{1}f}'.format(o_tth, sixcircle.PRE))
    # Slit opening is compared with analyzer size
    print ('Slit  H: {0:.1f}/{1:.2f}/{2:.3f}  '.format(agaph, A_dx/a_radi*1000, math.degrees(A_dx/a_radi)), end='')
    print ('V: {0:.1f}/{1:.2f}/{2:.3f}    mm/mrad/deg'.format(agapv, A_dz/a_radi*1000, math.degrees(A_dz/a_radi)))
    print ('mu = {0:.{2}f}  gam = {1:.{2}f}'.format(o_mu, o_gam, sixcircle.PRE))
    print ('Incident Divergence: Div.:  {0:.2f} mrad ({1:.3f} deg  {2:.2f} nm) H    '.format(BEAM_IN_DIV_H*1000, math.degrees(BEAM_IN_DIV_H), dq_ash*10), end='')
    print ('{0:.2f} mrad V'.format(BEAM_IN_DIV_V*1000))
    print ('Qres = sqrt((3.5*rms)^2 + beam_div_in^2)')
    print ('')
    print ((('{:>14}')*4).format('A','Q_Av','SLIT_FW','Qres'))
    for zi in range(0,z_n):
        for xi in range(0,x_n):
            qprt = (A_str[zi][xi], 10.0*A_AVG_ABSQ[zi][xi], 10.0*A_FW_ABSQ[zi][xi], 10.0*A_RES_ABSQ[zi][xi])
            print (('{:>14}'+('{:>14.3f}')*3+'{:>14}').format(*qprt,'nm-1'))
        print ('')
    # Write to gpi.qpos
    print ('    Q values written to: gpi.qpos')
    try:
        with open('gpi.qpos', 'w') as f:
            f.write('A  Q_Av  SLIT_FW  Qres\n')
            f.write('\n')
            for zi in range(0,z_n):
                for xi in range(0,x_n):
                    qwrt = (A_str[zi][xi],10.0*A_AVG_ABSQ[zi][xi],10.0*A_FW_ABSQ[zi][xi],10.0*A_RES_ABSQ[zi][xi])
                    f.write('{0} {1:.3f} {2:.3f} {3:.3f} nm-1\n'.format(*qwrt))
                f.write('\n')
    except:
        print ('\nError in writing gpi.qpos')
    print ('')

# Set some typical specific limit conditions
sixcircle.wdesc('setlm_bl43_*','Sets limits for setups at BL43 - e.g. cradle w or w/o  cryostat, etc')
def setlm_bl43_eulerian_cradle():
    print("\nSetting typical limits for BL43 with the Eulerian cradle installed, but no cryostat.  (note: in general small tth with large th can be a problem - maybe freeze omega=0)")
    setlm(ltth=0.6,utth=52,lth=-20,uth=26,lchi=-180,uchi=180,lphi=-180,uphi=180,lmu=-180,umu=180,lgam=-180,ugam=180,lalpha=-180,ualpha=180,lbeta=-180,ubeta=180)
def setlm_bl43_cryostat():
    print("\nSetting typical limits for BL43 with the cryostat installed on the Eulerian cradle. (note: in general small tth with large th can be a problem - maybe freeze omega=0)")
    setlm(ltth=0.6,utth=52,lth=-20,uth=26,lchi=-30,uchi=30,lphi=-10,uphi=100,lmu=-180,umu=180,lgam=-180,ugam=180,lalpha=-180,ualpha=180,lbeta=-180,ubeta=180)
def setlm_bl43_cryostat_generous():
    print("\nSetting GENEROUS limits for BL43 with the cryostat installed on the Eulerian cradle.  (note: in general small tth with large th can be a problem - maybe freeze omega=0)")
    setlm(ltth=0.6,utth=52,lth=-20,uth=26,lchi=-30,uchi=92,lphi=-100,uphi=100,lmu=-180,umu=180,lgam=-180,ugam=180,lalpha=-180,ualpha=180,lbeta=-180,ubeta=180)


ini_rqd()
