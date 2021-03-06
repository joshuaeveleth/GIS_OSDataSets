
def funNDVI(tif):

    import struct,os,string,re,binascii,glob
    from osgeo import gdal
    import numpy as np

    print tif,"\n"
    #create an array with two elements from the name of the .tif file separated by the period
    tifarr=tif.split('.')
    #create the output filename by appending _ndvi.tif to the text to the left of the period in the original filename
    newtiff=tifarr[0]+'_ndvi.tif'
    print newtiff,"\n"
    #create an empty array to load the bands of the tiff file
    tifbands=[]
    #open the tiff file for reading
    g = gdal.Open(tif)
    #for all bands load each band into an array
    for i in xrange(1,g.RasterCount+1):
        tifbands.append(g.GetRasterBand(i).ReadAsArray())
    #select the red and near infrared bands
    red=np.array(tifbands[0],dtype= float)
    nir=np.array(tifbands[3],dtype= float)
    #make sure the arrays selected are not empty
    check = np.logical_and ( red > 1, nir > 1 )
    #do the ndvi calculation and scale the output of 1 to -1  to values between 250 and 0 
    #clipping values less than -0.25.  This is the same proceedure as the MODIS NDVI 
    #analysis , see
    #http://www.glcf.umd.edu/data/ndvi/ 
    #http://staff.glcf.umd.edu/sns/branch/htdocs.sns/library/guide/techguide_ndvi.pdf. This gives an effective 
    ndvi = np.where ( check,  (200*((nir - red ) / ( nir + red )))+50,253) 
    nullnum=253
    #get projection and datum info from original file
    geo = g.GetGeoTransform()  
    proj = g.GetProjection()  
    #get extent of original file
    shape = red.shape 
    #use the Geotiff driver for output
    driver = gdal.GetDriverByName("GTiff")
    #create the  output file settings
    # changed the output data type to integer byte format deflate compressed with predictor 2 
    dst_ds = driver.Create( "newtiff", shape[1], shape[0], 1, gdal.GDT_Byte, options=['COMPRESS=DEFLATE','PREDICTOR=2'])
    #set the output datum and projection
    dst_ds.SetGeoTransform( geo )
    dst_ds.SetProjection( proj )
    #Start write of temp output file
    dst_ds.GetRasterBand(1).WriteArray(ndvi)
    dst_ds = None;g=None  # save, close of output file and input file
    #after testing the text below this line can be removed
    #create command line string to create an intermediate temporary virtual file
    #sysCall = "gdalbuildvrt -srcnodata -9  test.vrt temptiff"
    #os.system(sysCall)
    #create command line string to create the losslessly compressed final geotiff file using the 
    #co predictor=3 option for best compression of the floating point output
    #
    #finaltiff="gdal_translate -of GTiff -co COMPRESS=DEFLATE -co predictor=3 test.vrt %s"%(newtiff)
    #os.system(finaltiff)

def testIsString(input):
    return isinstance(input,basestring)
    
def SuperStacker(listRasters):
    import os
    strList = ""
    outName = listRasters[0].split('.')[0]+"_ss."+listRasters[0].split('.')[1]
    for items in listRasters:
        strList = strList+" "+items
    os.system("gdal_merge -separate "+strList+" -o "+outName)

def StackProcess(input_listTif_or_Tif):
    #if testIsString(input_listTif_or_Tif):
    funNDVI(input_listTif_or_Tif)
    listRast = []
    listRast.append(input_listTif_or_Tif)
    listRast.append(input_listTif_or_Tif.split('.')[0]+"_ndvi."+input_listTif_or_Tif.split('.')[1])
    SuperStacker(listRast)
    
def SuperStackMe(input_listTif_or_Tif):
    if testIsString(input_listTif_or_Tif):
        StackProcess(input_listTif_or_Tif)
    else:
        for f in input_listTif_or_Tif:
            #print f
            StackProcess(f) 

