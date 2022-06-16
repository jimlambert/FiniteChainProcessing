#!/usr/bin/python3

import numpy as np
import ioutls as io
import re
import glob

def read_data_file(filename, datatype):
    """
    ARGUMENTS
    ---------
        
        filename    -   name of date file ending in out and formatted with
                        columns delineated by whitespace containing a header
                        for each column (excluding the first column which is
                        assumed to contain indexs)

                name 1.       name2.        name3.      ...
        1       <data>11      <data>12      <data>13      
        2       <data>21      <data>22      <data>23      
        3       <data>31      <data>32      <data>33      
        .          .             .             .
        .          .             .             . 
        .          .             .             .

        dataype     -   datatype assumed for <data>, supports complex numbers if
                        formatted as (a,b) for a=Re(z), b=Im(z)

    RETURNS
    -------

        A dictionary type formatted as,

        { "name1" : np.array([<data>11, <data>12, <data>[13]]),
          "name2" : np.array([<data>21, <data>22, <data>[23]]),
          "name2" : np.array([<data>31, <data>32, <data>[33]]),
             .
             .
             .
        }

    """ 
    header,data=io.readOutFile(filename, HEADER_SIZE=1)
    data = [row[1:] for row in data]
    header = header[0]
    header = [(header[n]+header[n+1]).strip('.') for n in range(0,len(header)-1,2)] 
    ncol = len(header)
    typelst = [datatype]*ncol
    tpdata = io.typeSetData(data,typelst)
    return dict(zip(header,np.transpose(tpdata)))
   

def read_corr_data_file(filename, datatype):
    datadict = read_data_file(filename, datatype)
    datadict['r'] = re.search(r'(?<=-r)(.*)(?=\.out)',filename).group(1)    
    return datadict


def connected_correlations(r, corrsAB, magsA, magsB):
    concorrsAB = [] 
    for (j, corrAB) in enumerate(corrsAB):
        concorrsAB.append(corrAB-(magsA[r]*magsB[j]))
    return np.array(concorrsAB)


def ccs_from_data_dir(dirname):
    """
    ARUGMENTS
    ---------
        
        dirname     -   name of directory containing correlation and
                        magnetization data. The correlation files should start
                        with 'corr' and should end with '-r<pos>.out' where
                        <pos> is the position of the correlation function in the
                        file. The magnetization files should start with mag

        tarname     -   target file where columns contain (1/N \sum_<ij> cos(k
                        r_i) cos(k r_j) <S_{r_i}^aS_{r_j}^b>). Each row contains
                        a value of k from 0 to (N-1) and a,b \in {x,y,z}

    RETURNS
    -------

        A numpy array of the connected correlations
    """

    corr_file_names = glob.glob(dirname+"/"+"corr*")
    mag_file_name = glob.glob(dirname+"/"+"mag*")

    mag_dict = read_data_file(mag_file_name[0], complex)
    mag_keys = list(mag_dict.keys())

    conn_corrs_set = np.empty([len(mag_dict[mag_keys[0]])], dtype=list)

    # get correlations as dictionaries
    for corr_file_name in corr_file_names:
        corr_dict = read_corr_data_file(corr_file_name, complex)
        corr_keys = list(corr_dict.keys())
        r = int(corr_dict['r'])-1
        
        conn_corrs = []
        for (i,corr_key) in enumerate(corr_keys):
            if corr_key == 'r': continue
            a = i//3
            b = i%3 
            Ma = mag_dict[mag_keys[a]]
            Mb = mag_dict[mag_keys[b]]
            corrsAB = corr_dict[corr_key]
            conn_corrs.append(connected_correlations(r,corrsAB,Ma,Mb))
        
        conn_corrs_set[r] = conn_corrs
        
    return conn_corrs_set
    

def qfi_from_ccs(corr_sets,k):

    Fxx = 0.0
    Fyy = 0.0
    Fzz = 0.0

    Fxy = 0.0
    Fyz = 0.0
    Fzx = 0.0

    N = len(corr_sets)

    pf = 2*np.pi/N

    for (r,corr_set) in enumerate(corr_sets):
        XX = corr_set[0] 
        XY = corr_set[1]
        XZ = corr_set[2]
        YX = corr_set[3]
        YY = corr_set[4]
        YZ = corr_set[5]
        ZX = corr_set[6]
        ZY = corr_set[7]
        ZZ = corr_set[8]
        
        for i in range(N):
            chi = np.cos(pf*k*r)*np.cos(pf*k*i)
            
            Fxx += XX[i]*chi
            Fyy += YY[i]*chi
            Fzz += ZZ[i]*chi

            Fxy += (XY[i]+YX[i])*chi
            Fyz += (YZ[i]+ZY[i])*chi
            Fzx += (ZX[i]+XZ[i])*chi
    
    return np.array([Fxx, Fyy, Fzz, Fxy, Fyz, Fzx]).real/(3*N)
             

if __name__=="__main__":
    import sys 

    inputdir = sys.argv[1]

    ccs = ccs_from_data_dir(inputdir)

    prcfile = inputdir+".prc"

    print(f"{prcfile=}")

    f = open(prcfile,'w')

    rowlabels = ["k", "fxx", "fyy", "fzz", "fxy", "fyz", "fzx"]
    
    fmtstr = "{:>10}{:>20}{:>20}{:>20}{:>20}{:>20}{:>20}\n"

    f.write(fmtstr.format(*rowlabels))
    
    fmtstr = "{:10.0f}{:20.9f}{:20.9f}{:20.9f}{:20.9f}{:20.9f}{:20.9f}\n"

    for k in range(len(ccs)):
        qfi = qfi_from_ccs(ccs, k)
        qfi = np.insert(qfi,0,k)
        print(qfi)
        f.write(fmtstr.format(*qfi))
        
    f.close() 


    #datadict = read_data_file(sys.argv[1], complex)
    #print(sys.argv[1]) 
    #print('here')
    #datadict = read_corr_data_file(sys.argv[1],complex)
    
