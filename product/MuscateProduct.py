#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

"""
Muscate product

@version: 1.0 

@author: Aurelie COURTOIS (THALES)
@date: 06/06/2017
"""

try:
#----------------------------------------------------------------------------------------------------------
# IMPORTS
#----------------------------------------------------------------------------------------------------------
    import os
    import logging
    
    from AOTMap.MuscateAOTMap import MuscateAOTMap
    from reflectImgs.MuscateReflectImgs import MuscateReflectImgs
    from masks.MuscateMasks import MuscateMasks
    from waterVapor.MuscateWaterVapor import MuscateWaterVapor
    from dimap.MuscateDimap import MuscateDimap
    
except Exception, e :
    print "Probleme with Python library : %s" %e
    raise Exception, "System exit with error"


class MuscateProduct:

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
        If there are Muscate masks then return object of class MuscateProduct
        else return None
        """
		
        t_masks = MuscateMasks.getMasks(_s_productPath)
        if len(t_masks) > 0:
            logging.info('Product type is Muscate for %s'%_s_productPath)
            return cls
        else:
            return None


    def getName( self ):
        """
        Get name to create directory
        """
        
        s_productName = os.path.basename(self.s_productPath).split('_')
        
        # date
        s_date = s_productName[1].split('-')
        
        # product level
        s_level = s_productName[2]
        
        # tile name
        s_tile = s_productName[3]
        
        # Create a directory name
        s_name = '_'.join([s_level,s_tile,'A000000',s_date[0] + 'T' + s_date[1]])
        
        return s_name
        

    def ConvertWaterVapor( self ):
        """
        Convert water vapor from Muscate product to Sen2cor product
        """
        
        MuscateWaterVapor.Convert(self.s_productPath, self.s_workingDir)


    def ConvertReflectImgs( self ):
        """
        Convert reflectance images from Muscate product to Sen2cor product
        """
        
        MuscateReflectImgs.Convert(self.s_productPath, self.s_workingDir, self.s_reflType)
        
        
    def ConvertAOTMap( self ):
        """
        Convert AOT from Muscate product to Sen2cor product
        """
        
        MuscateAOTMap.Convert(self.s_productPath, self.s_workingDir)
        
        
    def ConvertMasks( self ):
        """
        Convert masks from Muscate product to Sen2cor product
        """
        
        MuscateMasks.Convert(self.s_productPath, self.s_workingDir)
        
        
    def ConvertDimap( self ):
        """
        Convert dimap from Muscate product to Sen2cor product
        """
        
        MuscateDimap.Convert(self.s_productPath, self.s_workingDir)
