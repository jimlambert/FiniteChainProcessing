import time
import sys
import numpy as np


def progressBar(CURR_PROG, TOT_PROG, BAR_WIDTH=15, PROMPT="Progress: ") :
    """
    MODULE: ioutls
    ==============
    progressBar(CURR_PROG, TOT_PROG, BAR_WIDTH=15, PROMPT="Progess: ")

    ARGUMENTS
    ---------

        CURR_PROG:              Current progress completed.
        TOT_PROG:               Total progress to be completed.
        BAR_WIDTH (Optional):   Width of progress bar. Default is 15.
        PROPMT (Optional):      Prompt appearing to the left of bar.   

    RETURNS
    -------

        Pass

    """
    CURR_PROG = int((CURR_PROG*BAR_WIDTH) / TOT_PROG)
    barString= ("#"*int(CURR_PROG)) + ("-"*int(BAR_WIDTH-CURR_PROG))
    sys.stdout.write(PROMPT+"[%s]" % (barString))
    sys.stdout.flush()
    sys.stdout.write("\r")
    pass


def readOutFile(FILE_NAME, COL_LEN=0, VERBOSE=False, COL_FIXED=False,
                DEBUG=False, HEADER_SIZE=0) :
    """
    MODULE: ioutls
    ==============
    readOutFile(FILE_NAME, COL_LEN=0, VERBOSE=0, COL_FIXED=0, DEBUG=0, 
                HEADER_SIZE=0)

    Extracts the contents of an output file, FILE_NAME. If FILE_NAME has a 
    header then the number of lines in the header may be specified and the 
    header is returned separately. 

    ARGUMENTS
    ---------

        FILE_NAME:          Name of target file to be read in.
        COL_LEN (0):        Number of columns in target file.
        VERBOSE (False):    Controls verbose output,
        COL_FIXED (False):  Fixed number of columns.
        DEBUG(False):       Turns on debugging. 
        HEADER_SIZE(0):        Number of lines in Header
       
    RETURNS
    -------

        Returns list of header lines and list of data as a two element python
        list.

    """
    
    HEADER = False
    
    if DEBUG : 
        assert COL_LEN >= 0, "Please specify positive column length."
        assert HEADER_SIZE >= 0, "Please specifiy positive number of lines in header."
    if VERBOSE : print("Reading file: ", FILE_NAME)
    if (COL_LEN > 0) : COL_FIXED=True 
    
    if HEADER_SIZE > 0 : HEADER = True
        
    infil = open(FILE_NAME, "r")
    lines = infil.readlines()
    nLines = len(lines)
    
    if VERBOSE : print(nLines, " lines detected.")
    
    # empty list for lines from the header
    headLines = []
    
    # empty list for data contents
    datLines = []
    
    # extract data from lines
    for (i,line) in enumerate(lines) :
    
        # add progress bar here 
        colst=line.split() 
        lencolst=len(colst)
     
        if VERBOSE : 
            if i == 0 : print(lencolst, " columns detected on line 0.")
            progressBar(i, nLines)
    
        if COL_FIXED : 
            assert lencolst==COL_LEN, "Column %i has lencolst=%i" % (i, lencolst)  
    
        if i < HEADER_SIZE : headLines.append(line.split())
        else : datLines.append(line.split())
            
    return headLines, datLines


def readInFile(inFileName):
    
    inFile = open(inFileName, "r")
    lines = inFile.readlines()
    
    parameters = {}
    
    for line in lines:
        

        line = line.strip().split('=')
        if line[0] == "sweepfile" : continue
        if line[0] == "bc" : continue

        parameters[line[0]] = float(line[1])
        
    return parameters


def readOutBatch(FNAME_ARR, COL_ARR=[], VERBOSE_B=False, VERBOSE_F=False,
                 COL_FIXED=False, DEBUG=False, HEADER_SIZE_ARR=[]) : 
    """
    MODULE: ioutls
    ==============

    readOutBatch(FNAME_ARR, COL_ARR=[], VERBOSE_B=False, VERBOSE_F=False,
                 COL_FIXED=False, DEBUG=False, HEADER_SIZE_ARR=[])

    Extracts data from a batch of data files specified by FNAME_ARR. These files 
    may be of different lengths and each file may or may not have an associated header. 

    ARGUMENTS
    ---------

      FNAME_ARR:            List of files names to be read in.
      COL_ARR([]):          List of column lengths for each file in FNAME. Default is 
                            empty which evaluates to all zeros
      VERBOSE_B(False):     Optional output while processing the batch.
      VERBOSE_F(False):     Optional output while processing each file. 
      COL_FIXED(False):     Fixed number of columns in each file.
      DEBUG(False):         Turn on debugging mode
      HEADER_SIZE_ARR([]):  List of header sizes (default is zero)

    RETURNS
    -------

      batch: Each element corresponds to one input file. 
             If the input files have headers the elements are formatted as [header, data].
             If the input files do not have a header then the batch array elements contain 
             the data sets at index 1 and an empty header list at index 0 
    """
   
    # If the header size and column length are not set, take default values to
    # be zero.
    if not HEADER_SIZE_ARR : HEADER_SIZE_ARR = [0] * len(FNAME_ARR)
    if not COL_ARR : COL_ARR = [0] * len(FNAME_ARR)

    # empty list to contain data
    batch = []

    nFiles = len(FNAME_ARR)

    if VERBOSE_B : print(nFiles, " files detected.")

    for i, (fName, nCols, nHead) in enumerate(zip(FNAME_ARR, COL_ARR, 
                                                  HEADER_SIZE_ARR)) :

        if VERBOSE_B : progressBar(i, nFiles, PROMPT="Reading files:")
        header, data = readOutFile(fName, nCols, VERBOSE_F, COL_FIXED, 
                                   DEBUG, nHead)
        batch.append([header, data])

    return batch


def typeSetData(DATA, TYPLST) :
    """
    MODULE: ioutls
    ==============
    typeSetData(TYPLST, DATA)

    ARGUMENTS
    ---------
        
        TYPLST      -       List of types that the each data column should be
                            set to.

        DATA        -       multidimensional python list with same number of
                            columns as elements in TYPLST.

    RETURNS
    -------
    
        Returns a numpy array with the same shape as DATA.
    """
    
    procData = []

    for line in DATA:
        
        procLine = []

        for (colel,type) in zip(line, TYPLST):
            # If type is complex, process appropriately. This script assumes
            # that complex numbers are given by strings of the form (real,imag)
            if(type==complex):
                
                colel = colel.split('(')
                colel = colel[1].split(')')
                colel = colel[0].split(',')
                num = complex(float(colel[0]),float(colel[1]))    
                procLine.append(num)
            
            else:
                procLine.append(type(colel))

        procData.append(np.array(procLine))

    return np.array(procData)


def typeSetBatch(BATCH, DTYP_ARR, HTYP_ARR=[]) : 
    """
    MODULE: ioutls
    ==============
    typeSetBatch()

    DTYP_ARR and HTYP_ARR should have as many entries as BATCH. If they do 
    not, it is assumed that each element of BATCH has an indentical type 
    structure.

    """
  
    tBatch = []

    datypExt = DTYP_ARR
    hetypExt = HTYP_ARR

    print(DTYP_ARR)

    if (type(DTYP_ARR[0]) != np.ndarray) and (type(DTYP_ARR[0]) != list) : 
        print("Extrapolating data types.")
        datypExt = [DTYP_ARR for i in range(len(BATCH))]
    
    if HTYP_ARR and (type(HTYP_ARR[0]) != np.ndarray) and (type(HTYP_ARR[0]) != list): 
        print("Extrapolating header data types.")
        hetypExt = [HTYP_ARR for i in range(len(BATCH))]

    if not HTYP_ARR : hetypExt = [[] for i in range(len(BATCH))]

    assert len(datypExt) == len(BATCH), "Insufficient number of data type arrays." 
    assert len(hetypExt) == len(BATCH), "Insufficient number of header type arrays."

    for (dataTypes, headerTypes, dataSet) in zip(datypExt, hetypExt, BATCH) : 
        
        tHeader = typeSetData(dataSet[0], headerTypes)
        tData = typeSetData(dataSet[1], dataTypes)
    
        tBatch.append([tHeader, tData])

    return tBatch


def procFile(FILE_NAME, DTYPLST, HTYPLST=[], COL_LEN=0, VERBOSE=False, COL_FIXED=False,
             DEBUG=False, HEADER_SIZE=0) :
    """
    Reads and type sets the data in FILE_NAME according to the types contained
    in DTYPLST and HTYPLST.
    """
  
    header, data = readOutFile(FILE_NAME, COL_LEN, VERBOSE, COL_FIXED, DEBUG, HEADER_SIZE)

    if(HTYPLST): tHeader = typeSetData(HTYPLST, header)
    else: tHeader = []

    tData = typeSetData(DTYPLST, data)

    return tHeader, tData
    

def procBatch(FNAME_ARR, DTYP_ARR, HTYP_ARR=[], COL_ARR=[], VERBOSE_B=False, 
              VERBOSE_F=False, COL_FIXED=False, DEBUG=False, 
              HEADER_SIZE_ARR=[]) : 
    """
    MODULE: ioutls
    ==============

    """

    batch = readOutBatch(FNAME_ARR, COL_ARR, VERBOSE_B, VERBOSE_F, COL_FIXED, DEBUG,
                      HEADER_SIZE_ARR)
    tBatch = typeSetBatch(batch, DTYP_ARR, HTYP_ARR)

    return tBatch

