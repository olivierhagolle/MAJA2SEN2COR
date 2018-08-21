#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

"""
Class for AOT Muscate product

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
    
except Exception, e :
    print "Probleme with Python library : %s" %e
    raise Exception, "System exit with error"
    
class MuscateAOTMap:
	
    @classmethod
    def Convert( cls
               , _s_productPath
               , _s_workingDir
               ):
		
        """
        Convert AOT image from Muscate product to Sen2cor product
        @param _s_productPath : path for product to convert
        @param _s_workingDir : directory where the new image will be saved
        """
        
        t_matches = []
        # search AOT file(s)
        for root,dirnames,filenames in os.walk(_s_productPath):
            for filename in fnmatch.filter(filenames, '*_ATB_*tif'):
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
            
            s_productName = os.path.basename(_s_productPath).split('_')
        
            # date
            s_date = s_productName[1].split('-')
        
            # product level
            s_level = s_productName[2]
        
            # tile name
            s_tile = s_productName[3]
        
            # Create AOT image name
            s_name = '_'.join([s_level,s_tile,s_date[0] + 'T' + s_date[1],'AOT_'+str(s_resol)+'m.jp2'])
        
            # Path for AOT image
            s_AOTPath = os.path.join(s_path, 'R' + str(s_resol) + 'm',s_name)

            # Translate to jp2 with lossless compression
            cmd = "gdal_translate -of JP2OpenJPEG -ot UInt16 -b 2 -co QUALITY=100 -co REVERSIBLE=YES " + t_matches[i] + " " + s_AOTPath
            os.system(cmd)

            logging.info('AOT image for resolution %sm : %s' %(s_resol,s_AOTPath))

            if os.path.exists(s_AOTPath + '.aux.xml'):
                os.remove(s_AOTPath + '.aux.xml')
