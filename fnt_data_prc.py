#!/usr/bin/python3

import numpy as np
import ioutls as io
import re


def read_datafile(filename, datatype):
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
    datadict = read_datafile(filename, datatype)
    datadict['r'] = re.search(r'(?<=-r)(.*)(?=\.out)',filename).group(1)    
    return datadict

if __name__=="__main__":
    import sys

    datadict = read_datafile(sys.argv[1], complex)
    print(sys.argv[1]) 
    print('here')
    datadict = read_corr_data_file(sys.argv[1],complex)
    print(datadict['ZZCorr'])
