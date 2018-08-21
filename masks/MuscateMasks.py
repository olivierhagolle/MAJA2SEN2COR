#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

"""
Class for masks Muscate product

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
    import sys
    import gdal
    from gdalconst import *
    import numpy as np
    
except Exception, e :
    print "Probleme with Python library : %s" %e
    raise Exception, "System exit with error"
    

class MuscateMasks:
    
    @classmethod
    def getMasks( cls
                 , _s_productPath
                 ):
        
        """
        Get masks (cloud, shadow, snow, ...)
        """
        
        t_matches = []
        
        # Search masks files
        t_matches = os.listdir(_s_productPath + '/MASKS')
                
        if len(t_matches) == 0:
            logging.info('No mask found')
        
        return t_matches
        
    @classmethod
    def imageReader( cls
                   , _s_imgName
                   , _u_gdalBand
                   ):
        
        """
        Function to read image with gdal
        @param _s_imgName : image name to read
        @param _u_gdalBand : number of gdal band
        """
        
        dataset = gdal.Open(_s_imgName)
        
        if _u_gdalBand > dataset.RasterCount:
            logging.warn('There is only %s gdal band for image %s'%(dataset.RasterCount, _s_imagName))
            sys.exit(0)
        else:
            o_band = dataset.GetRasterBand(_u_gdalBand)
            t_array = o_band.ReadAsArray()
            return t_array

        
    @classmethod
    def calculatePercentageValue( cls
                                , _s_productPath
                                ):
        
        """
        Calculate percentage value for no data pixels, saturated pixels, ...
        """
        
        t_masks = cls.getMasks(_s_productPath)
        
        d_ImageContent = {}
        
        # No data pixels : mask DFP
        filename = fnmatch.filter(t_masks, '*_DFP_*.tif')
        if len(filename) > 1:
            logging.warn('%s no data pixels masks found.'%(str(len(filename))))
            filename = fnmatch.filter(t_masks, '*_DFP_R1.tif')[0]
            filename = os.path.join(_s_productPath, 'MASKS', filename)
            logging.info('No data pixels mask : %s'%filename)
            t_no_data = cls.imageReader(filename, 1)
            t_no_data[np.where(t_no_data!=0)] = 1
            d_ImageContent['no_data'] = float(t_no_data.sum())/np.size(t_no_data)
        elif len(filename) == 1:
            filename = os.path.join(_s_productPath, 'MASKS', filename[0])
            logging.info('No data pixels mask : %s'%filename)
            t_no_data = cls.imageReader(filename, 1)
            t_no_data[np.where(t_no_data!=0)] = 1
            d_ImageContent['no_data'] = float(t_no_data.sum())/np.size(t_no_data)
        else:
            logging.warn('No data pixels mask not found')
            d_ImageContent['no_data'] = 'N/A'
        
        # Saturated pixels : mask SAT
        filename = fnmatch.filter(t_masks, '*_SAT_*.tif')
        if len(filename) > 1:
            logging.warn('%s saturated pixels masks found.'%(str(len(filename))))
            filename = fnmatch.filter(t_masks, '*_SAT_R1.tif')[0]
            filename = os.path.join(_s_productPath, 'MASKS', filename)
            logging.info('Saturated pixels mask : %s'%filename)
            t_sat = cls.imageReader(filename,1)
            t_sat[np.where(t_sat!=0)] = 1
            d_ImageContent['sat'] = float(t_sat.sum())/np.size(t_sat)
        elif len(filename) == 1:
            filename = os.path.join(_s_productPath, 'MASKS', filename[0])
            logging.info('Saturated pixels mask : %s'%filename)
            t_sat = cls.imageReader(filename,1)
            t_sat[np.where(t_sat!=0)] = 1
            d_ImageContent['sat'] = float(t_sat.sum())/np.size(t_sat)
        else:
            logging.warn('Saturated pixels mask not found')
            d_ImageContent['sat'] = 'N/A'
            
        # Shadows mask from clouds : mask MG2, useful bit 4th
        filename = fnmatch.filter(t_masks, '*_MG2_*.tif')
        if len(filename) > 1:
            logging.warn('%s shadows masks found.'%(str(len(filename))))
            filename = fnmatch.filter(t_masks, '*_MG2_R1.tif')[0]
            filename = os.path.join(_s_productPath, 'MASKS', filename)
            logging.info('Shadows mask : %s'%filename)
            t_mg2 = cls.imageReader(filename,1)
            t_shad = np.where(t_mg2 & 8, 1, 0)
            if len(t_shad) == 0:
                d_ImageContent['shad'] = 0.0
            else:
                d_ImageContent['shad'] = float(t_shad.sum())/np.size(t_shad)
        elif len(filename) == 1:
            filename = os.path.join(_s_productPath, 'MASKS', filename[0])
            logging.info('Shadows mask : %s'%filename)
            t_mg2 = cls.imageReader(filename,1)
            t_shad = np.where(t_mg2 & 8, 1, 0)
            if len(t_shad) == 0:
                d_ImageContent['shad'] = 0.0
            else:
                d_ImageContent['shad'] = float(t_shad.sum())/np.size(t_shad)
        else:
            logging.warn('Shadows mask not found')
            d_ImageContent['shad'] = 'N/A'
        
        # Water mask : mask MG2, useful bit 1st
        filename = fnmatch.filter(t_masks, '*_MG2_*.tif')
        if len(filename) > 1:
            logging.warn('%s water masks found.'%(str(len(filename))))
            filename = fnmatch.filter(t_masks, '*_MG2_R1.tif')[0]
            filename = os.path.join(_s_productPath, 'MASKS', filename)
            logging.info('Water mask : %s'%filename)
            t_mg2 = cls.imageReader(filename,1)
            t_water = np.where(t_mg2 & 1, 1, 0)
            if len(t_water) == 0:
                d_ImageContent['water'] = 0.0
            else:
                d_ImageContent['water'] = float(t_water.sum())/np.size(t_water)
        elif len(filename) == 1:
            filename = os.path.join(_s_productPath, 'MASKS', filename[0])
            logging.info('Water mask : %s'%filename)
            t_mg2 = cls.imageReader(filename,1)
            t_water = np.where(t_mg2 & 1, 1, 0)
            if len(t_water) == 0:
                d_ImageContent['water'] = 0.0
            else:
                d_ImageContent['water'] = float(t_water.sum())/np.size(t_water)
        else:
            logging.warn('Water mask not found')
            d_ImageContent['water'] = 'N/A'
            
        # Cirrus mask : mask CLM, useful bit 8th
        filename = fnmatch.filter(t_masks, '*_CLM_*.tif')
        if len(filename) > 1:
            logging.warn('%s cirrus masks found.'%(str(len(filename))))
            filename = fnmatch.filter(t_masks, '*_CLM_R1.tif')[0]
            filename = os.path.join(_s_productPath, 'MASKS', filename)
            logging.info('Cirrus mask : %s'%filename)
            t_clm = cls.imageReader(filename,1)
            t_cirrus = np.where(t_clm & 128, 1, 0)
            if len(t_cirrus) == 0:
                d_ImageContent['cirrus'] = 0.0
            else:
                d_ImageContent['cirrus'] = float(t_cirrus.sum())/np.size(t_cirrus)
        elif len(filename) == 1:
            filename = os.path.join(_s_productPath, 'MASKS', filename[0])
            logging.info('Cirrus mask : %s'%filename)
            t_clm = cls.imageReader(filename,1)
            t_cirrus = np.where(t_clm & 128, 1, 0)
            if len(t_cirrus) == 0:
                d_ImageContent['cirrus'] = 0.0
            else:
                d_ImageContent['cirrus'] = float(t_cirrus.sum())/np.size(t_cirrus)
        else:
            logging.warn('Cirrus mask not found')
            d_ImageContent['cirrus'] = 'N/A'
            
        # Snow mask : mask MG2, useful bit 3rd
        filename = fnmatch.filter(t_masks, '*_MG2_*.tif')
        if len(filename) > 1:
            logging.warn('%s snow masks found.'%(str(len(filename))))
            filename = fnmatch.filter(t_masks, '*_MG2_R1.tif')[0]
            filename = os.path.join(_s_productPath, 'MASKS', filename)
            logging.info('Snow mask : %s'%filename)
            t_mg2 = cls.imageReader(filename,1)
            t_snow = np.where(t_mg2 & 4, 1, 0)
            if len(t_snow) == 0:
                d_ImageContent['snow'] = 0.0
            else:
                d_ImageContent['snow'] = float(t_snow.sum())/np.size(t_snow)
        elif len(filename) == 1:
            filename = os.path.join(_s_productPath, 'MASKS', filename[0])
            logging.info('Snow mask : %s'%filename)
            t_mg2 = cls.imageReader(filename,1)
            t_snow = np.where(t_mg2 & 4, 1, 0)
            if len(t_snow) == 0:
                d_ImageContent['snow'] = 0.0
            else:
                d_ImageContent['snow'] = float(t_snow.sum())/np.size(t_snow)
        else:
            logging.warn('Snow mask not found')
            d_ImageContent['snow'] = 'N/A'
            
        # Cloud medium probability : mask CLM, useful bits 2nd (all clouds except extension) and 5th (extension)
        filename = fnmatch.filter(t_masks, '*_CLM_*.tif')
        if len(filename) > 1:
            logging.warn('%s cloud medium probability masks found.'%(str(len(filename))))
            filename = fnmatch.filter(t_masks, '*_CLM_R1.tif')[0]
            filename = os.path.join(_s_productPath, 'MASKS', filename)
            logging.info('Cloud medium probability mask : %s'%filename)
            t_clm = cls.imageReader(filename,1)
            t_cloudMP = np.where((t_clm & 2) | (t_clm & 16), 1, 0)
            if len(t_cloudMP) == 0:
                d_ImageContent['cloudMP'] = 0.0
            else:
                d_ImageContent['cloudMP'] = float(t_cloudMP.sum())/np.size(t_cloudMP)
        elif len(filename) == 1:
            filename = os.path.join(_s_productPath, 'MASKS', filename[0])
            logging.info('Cloud medium probability mask : %s'%filename)
            t_clm = cls.imageReader(filename,1)
            t_cloudMP = np.where((t_clm & 2) | (t_clm & 16), 1, 0)
            if len(t_cloudMP) == 0:
                d_ImageContent['cloudMP'] = 0.0
            else:
                d_ImageContent['cloudMP'] = float(t_cloudMP.sum())/np.size(t_cloudMP)
        else:
            logging.warn('Cloud medium probability mask not found')
            d_ImageContent['cloudMP'] = 'N/A'
        
        # Cloud high probability : mask CLM, useful bits 2nd (all clouds except extension)
        filename = fnmatch.filter(t_masks, '*_CLM_*.tif')
        if len(filename) > 1:
            logging.warn('%s cloud high probability masks found.'%(str(len(filename))))
            filename = fnmatch.filter(t_masks, '*_CLM_R1.tif')[0]
            filename = os.path.join(_s_productPath, 'MASKS', filename)
            logging.info('Cloud high probability mask : %s'%filename)
            t_clm = cls.imageReader(filename,1)
            t_cloudHP = np.where(t_clm & 2, 1, 0)
            if len(t_cloudHP) == 0:
                d_ImageContent['cloudHP'] = 0.0
            else:
                d_ImageContent['cloudHP'] = float(t_cloudHP.sum())/np.size(t_cloudHP)
        elif len(filename) == 1:
            filename = os.path.join(_s_productPath, 'MASKS', filename[0])
            logging.info('Cloud high probability mask : %s'%filename)
            t_clm = cls.imageReader(filename,1)
            t_cloudHP = np.where(t_clm & 2, 1, 0)
            if len(t_cloudHP) == 0:
                d_ImageContent['cloudHP'] = 0.0
            else:
                d_ImageContent['cloudHP'] = float(t_cloudHP.sum())/np.size(t_cloudHP)
        else:
            logging.warn('Cloud high probability mask not found')
            d_ImageContent['cloudHP'] = 'N/A'
        
        return d_ImageContent
	
    @classmethod
    def Convert( cls
               , _s_productPath
	           , _s_workingDir
               ):
                   
        """
        Convert masks from Muscate product to Sen2cor product
        @param _s_productPath : path for product to convert
        @param _s_workingDir : directory where the new image will be saved
        """
		
        t_matches = []
        d_mask = {}
        
        # Search masks files
        t_matches = cls.getMasks(_s_productPath)#os.listdir(os.path.join(_s_productPath, 'MASKS'))
        
        if len(t_matches) == 0:
            logging.info('No mask found')
        
        # Search resolution for masks
        for i in range(len(t_matches)):
            s_mask = os.path.join(_s_productPath, 'MASKS', t_matches[i])
            GdalInfo = subprocess.check_output('gdalinfo {}'.format(s_mask), shell=True).split('\n')
            for line in GdalInfo:
                if 'Pixel Size' in line:
                    s_resol = int(float(line.split('(')[1].split(')')[0].split(',')[0]))
        
            if d_mask.keys() == [] or not s_resol in d_mask.keys():
                d_mask[s_resol] = [s_mask]
            else:
                d_mask[s_resol].append(s_mask)
        
        for s_resol in d_mask.keys():
            s_path = glob.glob(os.path.join(_s_workingDir,'GRANULE','*','IMG_DATA'))[0]
            # Create directory at resol s_resol if it doesn't exist
            if not os.path.exists(os.path.join(s_path, 'R' + str(s_resol) + 'm')):
                os.mkdir(os.path.join(s_path, 'R' + str(s_resol) + 'm'))
                logging.info('Creating directory for resolution %sm' %s_resol)
            
            t_mask = []
            
            s_productName = os.path.basename(_s_productPath).split('_')
        
            # date
            s_date = s_productName[1].split('-')
        
            # product level
            s_level = s_productName[2]
        
            # tile name
            s_tile = s_productName[3]
        
            # Create mask name
            s_name = '_'.join([s_level,s_tile,s_date[0] + 'T' + s_date[1],'SCL',str(s_resol)+'m.'])
        
            # Path for mask
            s_MaskPath = os.path.join(s_path, 'R' + str(s_resol) + 'm',s_name)
            
            # Initialise mask for resol s_resol
            dataset = cls.imageReader( d_mask[s_resol][0], 1 )
            nRows, nCols = dataset.shape
            t_newMask = np.ones((nRows, nCols))
            
                
            for s_mask in d_mask[s_resol]:
                t_mask = cls.imageReader( s_mask, 1 )              
                if 'EDG' in s_mask:
                    t_newMask = np.where(t_mask != 0, 0, t_newMask)
                if 'CLM' in s_mask:
                    t_newMask = np.where((t_mask & 2) | (t_mask & 16), 8, t_newMask)
                    t_newMask = np.where(t_mask & 2, 9, t_newMask)
                if 'MG2' in s_mask:
                    t_newMask = np.where((t_mask & 8), 3, t_newMask)
                    t_newMask = np.where((t_mask & 4), 11, t_newMask)
                    t_newMask = np.where((t_mask & 1), 6, t_newMask)

            # Create image tif
            driver = gdal.GetDriverByName("GTiff")
            o_newMask = driver.Create(s_MaskPath+'tif', nCols, nRows, 1, gdal.GDT_Byte )
            o_newMask.GetRasterBand(1).WriteArray(t_newMask)
            o_newMask=None
            
            # Translate to jp2 with lossless compression
            cmd = "gdal_translate -of JP2OpenJPEG -ot Byte -b 1 -co QUALITY=100 -co REVERSIBLE=YES " + s_MaskPath+'tif' + " " + s_MaskPath+'jp2'
            os.system(cmd)
            
            
            logging.info('Mask for resolution %sm : %s' %(s_resol,s_MaskPath+'jp2'))

            if os.path.exists(s_MaskPath + 'jp2' + '.aux.xml'):
                os.remove(s_MaskPath + 'jp2' + '.aux.xml')
            if os.path.exists(s_MaskPath + 'tif'):
                os.remove(s_MaskPath + 'tif')

