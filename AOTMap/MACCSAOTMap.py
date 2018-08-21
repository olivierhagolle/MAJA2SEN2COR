#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

"""
Class for AOT MACCS product

@version: 1.0 

@author: Aurelie COURTOIS (THALES) for French Space Agency (CNES)
@date: 06/06/2017

This converter is a free and open source software under the CeCILL-v2.1 license (French equivalent to GPL)
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
    
class MACCSAOTMap:
	
    @classmethod
    def Convert( cls
               , _s_productPath
               , _s_workingDir
               ):
		
        """
        Convert AOT image from MACCS product to Sen2cor product
        @param _s_productPath : path for product to convert
        @param _s_workingDir : directory where the new image will be saved
        """
        
        t_matches = []
        # search AOT file(s)
        s_productPath = glob.glob(os.path.join(_s_productPath,'*SC_*.DBL.DIR'))[0]
        for root,dirnames,filenames in os.walk(s_productPath):
            for filename in fnmatch.filter(filenames, '*_ATB*.DBL.TIF'):
                t_matches.append(os.path.abspath(os.path.join(root,filename)))
        
        if len(t_matches) == 0:
			logging.warn('No AOT image find')
			
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
            s_level = 'L2A'

            # tile name
            s_tile = 'T' + s_productName[4]
        
            # Create water vapor image name
            s_name = '_'.join([s_level,s_tile,s_date[0:8] + 'T' + s_date[9:],'AOT_'+str(s_resol)+'m.jp2'])
        
            # Path for AOT image
            s_AOTPath = os.path.join(s_path, 'R' + str(s_resol) + 'm',s_name)

            # Translate to jp2 with lossless compression
            cmd = "gdal_translate -of JP2OpenJPEG -ot UInt16 -b 2 -co QUALITY=100 -co REVERSIBLE=YES " + t_matches[i] + " " + s_AOTPath
            os.system(cmd)

            logging.info('AOT image for resolution %sm : %s' %(s_resol,s_AOTPath))

            if os.path.exists(s_AOTPath + '.aux.xml'):
                os.remove(s_AOTPath + '.aux.xml')
