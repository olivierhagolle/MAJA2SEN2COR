#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

"""
MACCS product

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
    import glob
    import xml.dom.minidom
    import logging
    
    from AOTMap.MACCSAOTMap import MACCSAOTMap
    from reflectImgs.MACCSReflectImgs import MACCSReflectImgs
    from masks.MACCSMasks import MACCSMasks
    from waterVapor.MACCSWaterVapor import MACCSWaterVapor
    from dimap.MACCSDimap import MACCSDimap

    
except Exception, e :
    print "Probleme with Python library : %s" %e
    raise Exception, "System exit with error"
    
    
class MACCSProduct:

    def __init__( self
                , _s_productPath
                , _s_workingDir
                , _s_reflType
                ):

        self.s_productPath = _s_productPath
        self.s_workingDir = _s_workingDir
        self.s_reflType = _s_reflType

        
    @classmethod
    def ProductType( cls
                   , _s_productPath
                   ):
		
        """
        If there are MACCS masks then return object of class MACCSProduct
        else return None
        """
        
        t_masks = MACCSMasks.getMasks(_s_productPath)
        if len(t_masks) > 0:
            logging.info('Product type is MACCS for %s'%_s_productPath)
            return cls
        else:
            return None


    def getName(self):
        """
        Get name to create directory
        """
        
        s_productName = os.path.basename(glob.glob(os.path.join(self.s_productPath,'*SC_*.DBL.DIR'))[0]).split('_')
        s_header = glob.glob(os.path.join(self.s_productPath,'*SC_*.HDR'))[0]
        
        o_file = open(s_header,'r')
        s_file = o_file.read()
        o_doc = xml.dom.minidom.parseString( s_file )
        
        # date
        s_date = str(o_doc.getElementsByTagName('Acquisition_Date_Time').item(0).childNodes[0].nodeValue).replace('UTC=','').replace('-','').replace(':','')
        
        # product level
        s_level = 'L2A'
        
        # Orbit number
        if o_doc.getElementsByTagName('Acquisition_Orbit_Number'):
            s_orbit = str(o_doc.getElementsByTagName('Acquisition_Orbit_Number').item(0).childNodes[0].nodeValue)
            s_default = '000000'
            s_orbit = s_default[0:6-len(s_orbit)] + s_orbit
        else:
            s_orbit = 'A000000'
        
        # tile name
        s_tile = 'T' + s_productName[4]
        
        # Create a directory name
        s_name = '_'.join([s_level,s_tile,s_orbit,s_date])
        
        return s_name
        

    def ConvertWaterVapor( self ):
        """
        Convert water vapor from MACCS product to Sen2cor product
        """
        
        MACCSWaterVapor.Convert(self.s_productPath, self.s_workingDir)


    def ConvertReflectImgs( self ):
        """
        Convert reflectance images from MACCS product to Sen2cor product
        """
        
        MACCSReflectImgs.Convert(self.s_productPath, self.s_workingDir, self.s_reflType)
        
        
    def ConvertAOTMap( self ):
        """
        Convert AOT from MACCS product to Sen2cor product
        """
        
        MACCSAOTMap.Convert(self.s_productPath, self.s_workingDir)
        
        
    def ConvertMasks( self ):
        """
        Convert masks from MACCS product to Sen2cor product
        """
        
        MACCSMasks.Convert(self.s_productPath, self.s_workingDir)
        
        
    def ConvertDimap( self ):
        """
        Convert dimap from MACCS product to Sen2cor product
        """
        
        MACCSDimap.Convert(self.s_productPath, self.s_workingDir)
