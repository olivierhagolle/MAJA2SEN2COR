#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

"""
Class for water vapor MACCS product

@version: 1.0 

@author: Aurelie COURTOIS (THALES)
@date: 06/06/2017
"""

try:
#----------------------------------------------------------------------------------------------------------
# IMPORTS
#----------------------------------------------------------------------------------------------------------
    import os
    import subprocess
    import fnmatch
    import glob
    import logging
    import xml.dom.minidom
    
except Exception, e :
    print "Probleme with Python library : %s" %e
    raise Exception, "System exit with error"
    
    
class MACCSWaterVapor:
	
    @classmethod
    def Convert( cls
               , _s_productPath
               , _s_workingDir
               ):

        """
        Convert water vapor image from MACCS product to Sen2cor product
        @param _s_productPath : path for product to convert
        @param _s_workingDir : directory where the new image will be saved
        """
        
        t_matches = []
        # search water vapor file(s)
        s_productPath = glob.glob(os.path.join(_s_productPath,'*SC_*.DBL.DIR'))[0]
        for root,dirnames,filenames in os.walk(s_productPath):
            for filename in fnmatch.filter(filenames, '*_ATB*.DBL.TIF'):
                t_matches.append(os.path.abspath(os.path.join(root,filename)))
        
        
        if len(t_matches) == 0:
			logging.warn('No water vapor image find')
        
        # Search resolution for water vapor image
        for i in range(len(t_matches)):
            GdalInfo = subprocess.check_output('gdalinfo {}'.format(t_matches[i]), shell=True).split('\n')
            for line in GdalInfo:
                if 'Pixel Size' in line:
                    s_resol = int(float(line.split('(')[1].split(')')[0].split(',')[0]))
        
        
            s_path = glob.glob(os.path.join(_s_workingDir,'GRANULE','*','IMG_DATA'))[0]
            # Create directory at resol s_resol if it doesn't exist
            if not os.path.exists(os.path.join(s_path, 'R' + str(s_resol) + 'm')):
                os.mkdir(os.path.join(s_path, 'R' + str(s_resol) + 'm'))
                logging.info('Creating directory for resolution %sm' %s_resol)
            
            
            s_productName = os.path.basename(s_productPath).split('_')
            s_header = glob.glob(os.path.join(_s_productPath,'*SC_*.HDR'))[0]
            o_file = open(s_header,'r')
            s_file = o_file.read()
            o_doc = xml.dom.minidom.parseString( s_file )
        
            # date
            s_date = str(o_doc.getElementsByTagName('Acquisition_Date_Time').item(0).childNodes[0].nodeValue).replace('UTC=','').replace('-','').replace(':','')
        
            # product level
            s_level = 'XXX'

            # tile name
            s_tile = 'T' + s_productName[4]
        
            # Create water vapor image name
            s_name = '_'.join([s_level,s_tile,s_date[0] + 'T' + s_date[1],'WVP_'+str(s_resol)+'m.jp2'])
        
            # Path for water vapor image
            s_WVPPath = os.path.join(s_path, 'R' + str(s_resol) + 'm',s_name)

            # Translate to jp2 with lossless compression
            cmd = "gdal_translate -of JP2OpenJPEG -b 1 -co QUALITY=100 -co REVERSIBLE=YES " + t_matches[i] + " " + s_WVPPath
            os.system(cmd)

            logging.info('Water vapor image for resolution %sm : %s' %(s_resol,s_WVPPath))

            os.system('rm ' + s_WVPPath + '.aux.xml')

