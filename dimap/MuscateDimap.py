#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

"""
Class for dimap Muscate product

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
    import logging
    import glob
    from xml.dom import minidom
    import xml.dom.minidom
    from numpy import*
    
    from XmlTools import XmlTools
    from masks.MuscateMasks import MuscateMasks
    
except Exception, e :
    print "Probleme with Python library : %s" %e
    raise Exception, "System exit with error"
    
    

class MuscateDimap(MuscateMasks):
	
    @classmethod
    def ReadMuscateMetadata( cls
                           , _s_productPath
                           ):
        """
        Function to read Muscate Metadata and to transform it to Sen2cor metadata
        @param _s_productPath : path of product to convert
        return : dictionnary with some values and nodes with other values
        """

        logging.info('Read metadata from Muscate product : %s',_s_productPath)
        
        # Metadata from Muscate
        s_dimapPathOld = glob.glob(os.path.join(_s_productPath, '*_MTD_ALL.xml'))
        if len(s_dimapPathOld) == 0:
            logging.warn('No dimap for product %s'%_s_productPath)
        else:
            s_dimapPathOld = s_dimapPathOld[0]
            
        # Initialise dictionnary with metadata values
        d_dimapValue = {}
        
        o_docMuscate = XmlTools(s_dimapPathOld)
        o_rootMuscate = o_docMuscate.getRootNode()
        
        # Product name
        o_parent = o_docMuscate.getIndirectNode(o_rootMuscate,'Inputs_List')
        d_dimapValue['product'] = o_docMuscate.getTagNodeValue(o_parent,'PRODUCT_ID')
        
        # date
        d_dimapValue['acquisitionDate'] = o_docMuscate.getNodeValue( o_docMuscate.getIndirectNode( o_rootMuscate, 'ACQUISITION_DATE' ) )
        d_dimapValue['prodDate'] = o_docMuscate.getNodeValue( o_docMuscate.getIndirectNode( o_rootMuscate, 'PRODUCTION_DATE' ) )
        
        # orbit
        d_dimapValue['orbit'] = o_docMuscate.getNodeValue( o_docMuscate.getIndirectNode( o_rootMuscate, 'ORBIT_NUMBER' ) )
        
        # Geocoding
        d_dimapValue['HORIZONTAL_CS_NAME'] = o_docMuscate.getNodeValue( o_docMuscate.getIndirectNode( o_rootMuscate, 'HORIZONTAL_CS_NAME' ) )
        d_dimapValue['HORIZONTAL_CS_CODE'] = o_docMuscate.getNodeValue( o_docMuscate.getIndirectNode( o_rootMuscate, 'HORIZONTAL_CS_CODE' ) )
        
        # Geoposition
        o_ULX = o_docMuscate.getIndirectNodes( o_rootMuscate, 'ULX' )
        o_ULY = o_docMuscate.getIndirectNodes( o_rootMuscate, 'ULY' )
        o_XDIM = o_docMuscate.getIndirectNodes( o_rootMuscate, 'XDIM' )
        o_YDIM = o_docMuscate.getIndirectNodes( o_rootMuscate, 'YDIM' )
        o_NROWS = o_docMuscate.getIndirectNodes( o_rootMuscate, 'NROWS' )
        o_NCOLS = o_docMuscate.getIndirectNodes( o_rootMuscate, 'NCOLS' )
        s_ULX = []
        s_ULY = []
        s_XDIM = []
        s_YDIM = []
        s_NROWS = []
        s_NCOLS = []
        for i in range(len(o_ULX)):
            s_ULX.append(o_docMuscate.getNodeValue(o_ULX[i]))
            s_ULY.append(o_docMuscate.getNodeValue(o_ULY[i]))
            s_XDIM.append(o_docMuscate.getNodeValue(o_XDIM[i]))
            s_YDIM.append(o_docMuscate.getNodeValue(o_YDIM[i]))
            s_NROWS.append(o_docMuscate.getNodeValue(o_NROWS[i]))
            s_NCOLS.append(o_docMuscate.getNodeValue(o_NCOLS[i]))
        
        d_dimapValue['ULX'] = s_ULX
        d_dimapValue['ULY'] = s_ULY
        d_dimapValue['XDIM'] = s_XDIM
        d_dimapValue['YDIM'] = s_YDIM
        d_dimapValue['NROWS'] = s_NROWS
        d_dimapValue['NCOLS'] = s_NCOLS
        
        
        ## Transform node Mean_Viewing_Incidence_Angle_List
        o_Mean_Value_List = o_docMuscate.extractNode(o_docMuscate.getIndirectNode( o_rootMuscate, 'Mean_Viewing_Incidence_Angle_List' ))
        attr_Mean_Value_List = o_docMuscate.getIndirectNodes(o_Mean_Value_List,'Mean_Viewing_Incidence_Angle')
        for i in range(len(attr_Mean_Value_List)):
            attr_Mean_Value = attr_Mean_Value_List[i].attributes['band_id']
            s_bandID = str(attr_Mean_Value.value).replace('B','')
            if not ('a' in s_bandID or 'A' in s_bandID):
                if int(s_bandID)<=8:
                    s_bandID = str(int(s_bandID) - 1)
            else:
                s_bandID = '8'
            attr_Mean_Value_List[i].setAttribute('bandId',s_bandID)
            attr_Mean_Value_List[i].removeAttribute(attr_Mean_Value.name)
            



        ## Transform node Sun_Angles_Grids
        o_Sun_Angles_Grids = o_docMuscate.extractNode(o_docMuscate.getIndirectNode( o_rootMuscate, 'Sun_Angles_Grids' ))
        
        # Node Zenith
        o_zenith = o_docMuscate.getIndirectNode(o_Sun_Angles_Grids,'Zenith')
        attr_Sun_Angles_Grids = o_zenith.attributes['values_unit']
        o_zenith.removeAttributeNode(attr_Sun_Angles_Grids)
        d_dimapValue['unitValue'] = attr_Sun_Angles_Grids.value
        attr_Sun_Angles_Grids = o_zenith.attributes['step_unit']
        step_unit = attr_Sun_Angles_Grids.value
        o_zenith.removeAttributeNode(attr_Sun_Angles_Grids)
        o_col_step = o_docMuscate.getIndirectNode(o_zenith,'COL_STEP')
        o_col_step.setAttribute('unit',step_unit)
        o_row_step = o_docMuscate.getIndirectNode(o_zenith,'ROW_STEP')
        o_row_step.setAttribute('unit',step_unit)
        f_sum = 0.
        u_nbVal = 0
        for zenithValues in o_docMuscate.getIndirectNodes(o_zenith,'VALUES' ):
            s_line = array(str(o_docMuscate.getNodeValue(zenithValues)).split(' ')).astype(float)
            f_sum = f_sum + s_line.sum()
            u_nbVal = u_nbVal + len(s_line)
            
        if u_nbVal == 0 or f_sum == 0:
            s_meanZenith = 'N/A'
        else:
            s_meanZenith = str( f_sum/u_nbVal )
        d_dimapValue['meanZenith'] = s_meanZenith
        
        # Node Azimuth
        o_azimuth= o_docMuscate.getIndirectNode(o_Sun_Angles_Grids,'Azimuth')
        attr_Sun_Angles_Grids = o_azimuth.attributes['values_unit']
        o_azimuth.removeAttributeNode(attr_Sun_Angles_Grids)
        attr_Sun_Angles_Grids = o_azimuth.attributes['step_unit']
        step_unit = attr_Sun_Angles_Grids.value
        o_azimuth.removeAttributeNode(attr_Sun_Angles_Grids)
        o_col_step = o_docMuscate.getIndirectNode(o_azimuth,'COL_STEP')
        o_col_step.setAttribute('unit',step_unit)
        o_row_step = o_docMuscate.getIndirectNode(o_azimuth,'ROW_STEP')
        o_row_step.setAttribute('unit',step_unit)
        f_sum = 0.
        u_nbVal = 0
        for azimuthValues in o_docMuscate.getIndirectNodes(o_azimuth,'VALUES' ):
            s_line = array(str(o_docMuscate.getNodeValue(azimuthValues)).split(' ')).astype(float)
            f_sum = f_sum + s_line.sum()
            u_nbVal = u_nbVal + len(s_line)
            
        if u_nbVal == 0 or f_sum == 0:
            s_meanAzimuth = 'N/A'
        else:
            s_meanAzimuth = str( f_sum/u_nbVal )
        d_dimapValue['meanAzimuth'] = s_meanAzimuth
        
        # Rename node
        o_Sun_Angles_Grids.tagName = 'Sun_Angles_Grid'
        
        ## Transform node Viewing_Incidence_Angles_Grids_List
        o_IncidenceAnglesList = o_docMuscate.extractNode(o_docMuscate.getIndirectNode( o_rootMuscate, 'Viewing_Incidence_Angles_Grids_List'))
        for o_band in o_docMuscate.getIndirectNodes(o_IncidenceAnglesList,'Band_Viewing_Incidence_Angles_Grids_List'):
            attr_band = o_band.attributes['band_id']
            s_band = attr_band.value.replace('B','')
            if not ('a' in s_band or 'A' in s_band):
                if int(s_band)<=8:
                    s_band = str(int(s_band) - 1)
            else:
                s_band = '8'
            for o_IncidenceAngles in o_docMuscate.getIndirectNodes(o_band,'Viewing_Incidence_Angles_Grids'):
                o_IncidenceAngles.setAttribute('bandId',s_band)
                attr_IncidenceAngles = o_IncidenceAngles.attributes['detector_id']
                o_IncidenceAngles.setAttribute('detectorId', str(int(attr_IncidenceAngles.value)))
                o_IncidenceAngles.removeAttribute(attr_IncidenceAngles.name)
                
            
            
                # Node Zenith
                o_zenith = o_docMuscate.getIndirectNode(o_IncidenceAngles,'Zenith')
                attr_Sun_Angles_Grids = o_zenith.attributes['values_unit']
                o_zenith.removeAttributeNode(attr_Sun_Angles_Grids)
                attr_Sun_Angles_Grids = o_zenith.attributes['step_unit']
                step_unit = attr_Sun_Angles_Grids.value
                o_zenith.removeAttributeNode(attr_Sun_Angles_Grids)
                o_col_step = o_docMuscate.getIndirectNode(o_zenith,'COL_STEP')
                o_col_step.setAttribute('unit',step_unit)
                o_row_step = o_docMuscate.getIndirectNode(o_zenith,'ROW_STEP')
                o_row_step.setAttribute('unit',step_unit)
                
                # Node Azimuth
                o_azimuth= o_docMuscate.getIndirectNode(o_IncidenceAngles,'Azimuth')
                attr_Sun_Angles_Grids = o_azimuth.attributes['values_unit']
                o_azimuth.removeAttributeNode(attr_Sun_Angles_Grids)
                attr_Sun_Angles_Grids = o_azimuth.attributes['step_unit']
                step_unit = attr_Sun_Angles_Grids.value
                o_azimuth.removeAttributeNode(attr_Sun_Angles_Grids)
                o_col_step = o_docMuscate.getIndirectNode(o_azimuth,'COL_STEP')
                o_col_step.setAttribute('unit',step_unit)
                o_row_step = o_docMuscate.getIndirectNode(o_azimuth,'ROW_STEP')
                o_row_step.setAttribute('unit',step_unit)
                
        o_Incidence_Angles_Grids_List = o_docMuscate.getIndirectNodes(o_IncidenceAnglesList,'Viewing_Incidence_Angles_Grids')
        
        logging.info('Read metadata from Muscate product finish without error : %s',_s_productPath)
        
        
        return d_dimapValue, o_Mean_Value_List, o_Sun_Angles_Grids, o_Incidence_Angles_Grids_List


    @classmethod
    def WriteSen2corMetadata( cls
                            , _s_productPath
                            , _d_dimapValue
                            , _o_Mean_Value_List
                            , _o_Sun_Angles_Grids
                            , _o_Incidence_Angles_Grids_List
                            , _s_dimapPathNew
                            ):
        
        """
        Function to write Sen2cor metadata
        @param _s_productPath : path for product to convert
        @param _d_dimapValue : dictionnary with some values to write
        @param _o_MeanValue_List : xml node with mean incidence angle values
        @param _o_Sun_Angles_Grids : xml node with sun angles grids
        @param _o_Incidence_Angles_Grids_List : xml nodes with incidence angles grids
        @param _s_dimapPathNew : directory to save metadata
        """
        
        logging.info('Write metadata for Sen2cor product in %s', _s_dimapPathNew)
        
        o_docSen2cor = XmlTools(_s_dimapPathNew)
        doc = minidom.Document()
        
        # Parent Node
        o_parentNode = o_docSen2cor.insertElementNode(doc, doc, "n1:Level-2A_Tile_ID", {'xmlns:n1':"https://psd-12.sentinel2.eo.esa.int/PSD/S2_PDI_Level-2A_Tile_Metadata.xsd", \
                                                                                        'xmlns:xsi':"http://www.w3.org/2001/XMLSchema-instance", \
                                                                                        'xsi:schemaLocation':"https://psd-12.sentinel2.eo.esa.int/PSD/S2_PDI_Level-2A_Tile_Metadata.xsd /dpc/app/s2ipf/FORMAT_METADATA_TILE_L1C/02.10.02/scripts/../../../schemas/02.12.05/PSD/S2_PDI_Level-2A_Tile_Metadata.xsd"})
        
        # Node General_Info
        o_childGeneral_Info = doc.createElement('n1:General_Info')
        o_parentNode.appendChild(o_childGeneral_Info)
        
        # Node TILE_ID_2A
        s_class = 'OPER'
        s_date = ''.join(''.join(_d_dimapValue['acquisitionDate'].split('-')).split(':')).split('.')[0]
        s_orbit = '000000'
        s_orbit = s_orbit[0:6-len(str(_d_dimapValue['orbit']))] + str(_d_dimapValue['orbit'])
        s_tileID = _d_dimapValue['product'].split('_')[5]
        s_tile = 'S2A_%s_MSI_L2A_TL_SGS__%s_A%s_%s_N02.04'%(s_class, s_date, s_orbit, s_tileID)
        o_docSen2cor.createElementNode(doc, o_childGeneral_Info, 'TILE_ID_2A',{'metadataLevel':'Brief'}, s_tile)
        
        # Node DATASTRIP_ID_2A
        o_docSen2cor.createElementNode(doc, o_childGeneral_Info, 'DATASTRIP_ID_2A',{'metadataLevel':'Standard'}, _d_dimapValue['product'])
        
        # Node DOWNLINK_PRIORITY
        o_docSen2cor.createElementNode(doc, o_childGeneral_Info, 'DOWNLINK_PRIORITY',{'metadataLevel':'Standard'}, 'NOMINAL')
        
        # Node SENSING_TIME
        o_docSen2cor.createElementNode(doc, o_childGeneral_Info, 'SENSING_TIME',{'metadataLevel':'Standard'}, _d_dimapValue['acquisitionDate'])

        # Node Archiving_Info
        o_childArchiving_Info = o_docSen2cor.insertElementNode(doc,o_childGeneral_Info,'Archiving_Info', {'metadataLevel':'Expertise'})
        o_docSen2cor.createTextNode(doc, o_childArchiving_Info, 'ARCHIVING_CENTRE', 'SGS_')
        o_docSen2cor.createTextNode(doc, o_childArchiving_Info, 'ARCHIVING_TIME', _d_dimapValue['prodDate'])
        
        # Node Geometric_Info
        t_resolS2 = ['10', '20', '60']
        o_childGeometric_Info = doc.createElement('n1:Geometric_Info')
        o_parentNode.appendChild(o_childGeometric_Info)
        o_childTile_Geocoding = o_docSen2cor.insertElementNode(doc, o_childGeometric_Info, 'Tile_Geocoding', {'metadataLevel':'Brief'})
        o_docSen2cor.createTextNode(doc, o_childTile_Geocoding, 'HORIZONTAL_CS_NAME', _d_dimapValue['HORIZONTAL_CS_NAME'])
        if not 'EPSG' in _d_dimapValue['HORIZONTAL_CS_CODE']:
            o_docSen2cor.createTextNode(doc, o_childTile_Geocoding, 'HORIZONTAL_CS_CODE', 'EPSG:' + _d_dimapValue['HORIZONTAL_CS_CODE'])
        else:
            o_docSen2cor.createTextNode(doc, o_childTile_Geocoding, 'HORIZONTAL_CS_CODE', _d_dimapValue['HORIZONTAL_CS_CODE'])
            
        for i in range(len(_d_dimapValue['XDIM'])):
            s_resol = str(_d_dimapValue['XDIM'][i])
            o_childSize = o_docSen2cor.insertElementNode(doc, o_childTile_Geocoding, 'Size',{'resolution':s_resol})
            o_docSen2cor.createTextNode(doc, o_childSize, 'NROWS', _d_dimapValue['NROWS'][i])
            o_docSen2cor.createTextNode(doc, o_childSize, 'NCOLS', _d_dimapValue['NCOLS'][i])
            
        # Add missing resolutions with value -999 for SNAP
        for s_resolS2 in t_resolS2:
            if not s_resolS2 in _d_dimapValue['XDIM']:
                o_childSize = o_docSen2cor.insertElementNode(doc, o_childTile_Geocoding, 'Size', {'resolution':s_resolS2})
                o_docSen2cor.createTextNode(doc, o_childSize, 'NROWS', '-999')
                o_docSen2cor.createTextNode(doc, o_childSize, 'NCOLS', '-999')
        
        for i in range(len(_d_dimapValue['XDIM'])):
            s_resol = str(_d_dimapValue['XDIM'][i])
            o_childSize = o_docSen2cor.insertElementNode(doc, o_childTile_Geocoding, 'Geoposition', {'resolution':s_resol})
            o_docSen2cor.createTextNode(doc, o_childSize, 'ULX', _d_dimapValue['ULX'][i])
            o_docSen2cor.createTextNode(doc, o_childSize, 'ULY', _d_dimapValue['ULY'][i])
            o_docSen2cor.createTextNode(doc, o_childSize, 'XDIM', _d_dimapValue['XDIM'][i])
            o_docSen2cor.createTextNode(doc, o_childSize, 'YDIM', _d_dimapValue['YDIM'][i])   
            
        # Add missing resolutions with value -999 for SNAP
        for s_resolS2 in t_resolS2:
            if not s_resolS2 in _d_dimapValue['XDIM']:
                o_childSize = o_docSen2cor.insertElementNode(doc, o_childTile_Geocoding, 'Geoposition', {'resolution':s_resolS2})
                o_docSen2cor.createTextNode(doc, o_childSize, 'ULX', '-999')
                o_docSen2cor.createTextNode(doc, o_childSize, 'ULY', '-999')
                o_docSen2cor.createTextNode(doc, o_childSize, 'XDIM', '-999')
                o_docSen2cor.createTextNode(doc, o_childSize, 'YDIM', '-999')

        o_childTile_Angles = o_docSen2cor.insertElementNode(doc, o_childGeometric_Info, 'Tile_Angles', {'metadataLevel':'Standard'})
        
        # Node Sun_Angles_Grid
        o_childTile_Angles.appendChild(_o_Sun_Angles_Grids)
        
        # Node Mean_Sun_Angle
        o_childMean_Sun_Angle = o_docSen2cor.createNode(doc, o_childTile_Angles, 'Mean_Sun_Angle')
        o_docSen2cor.createElementNode(doc, o_childMean_Sun_Angle, 'ZENITH_ANGLE',{'unit':_d_dimapValue['unitValue']}, _d_dimapValue['meanZenith'])
        o_docSen2cor.createElementNode(doc, o_childMean_Sun_Angle, 'AZIMUTH_ANGLE',{'unit':_d_dimapValue['unitValue']}, _d_dimapValue['meanAzimuth'])
        
        # Node Viewing_Incidence_Angles_Grids
        for i in range(len(_o_Incidence_Angles_Grids_List)):
            o_childTile_Angles.appendChild(_o_Incidence_Angles_Grids_List[i])
        
        # Node Mean_Viewing_Incidence_Angle_List
        o_childTile_Angles.appendChild(_o_Mean_Value_List)
        
        # Node Quality_Indicators_Info
        o_childQuality_Indicators_Info = o_docSen2cor.insertElementNode(doc, o_parentNode, 'n1:Quality_Indicators_Info', {'metadataLevel':'Standard'})
        
        # Node L1C_Image_Content_QI
        o_childL1C_Image_Content_QI = o_docSen2cor.createNode(doc, o_childQuality_Indicators_Info, 'L1C_Image_Content_QI')
        o_docSen2cor.createTextNode(doc, o_childL1C_Image_Content_QI, 'CLOUDY_PIXEL_PERCENTAGE', 'N/A')
        o_docSen2cor.createTextNode(doc, o_childL1C_Image_Content_QI, 'DEGRADED_MSI_DATA_PERCENTAGE', 'N/A')
        
        # Node L2A_Image_Content_QI
        d_ImageContent = cls.calculatePercentageValue( _s_productPath )
        o_childL2A_Image_Content_QI = o_docSen2cor.createNode(doc, o_childQuality_Indicators_Info, 'L2A_Image_Content_QI')
        o_docSen2cor.createTextNode(doc, o_childL2A_Image_Content_QI, 'NODATA_PIXEL_PERCENTAGE', str(d_ImageContent['no_data']))
        o_docSen2cor.createTextNode(doc, o_childL2A_Image_Content_QI, 'SATURATED_DEFECTIVE_PIXEL_PERCENTAGE', str(d_ImageContent['sat']))
        o_docSen2cor.createTextNode(doc, o_childL2A_Image_Content_QI, 'DARK_FEATURES_PERCENTAGE', 'N/A')
        o_docSen2cor.createTextNode(doc, o_childL2A_Image_Content_QI, 'CLOUD_SHADOW_PERCENTAGE', str(d_ImageContent['shad']))
        o_docSen2cor.createTextNode(doc, o_childL2A_Image_Content_QI, 'VEGETATION_PERCENTAGE', 'N/A')
        o_docSen2cor.createTextNode(doc, o_childL2A_Image_Content_QI, 'BARE_SOILS_PERCENTAGE', 'N/A')
        o_docSen2cor.createTextNode(doc, o_childL2A_Image_Content_QI, 'WATER_PERCENTAGE', str(d_ImageContent['water']))
        o_docSen2cor.createTextNode(doc, o_childL2A_Image_Content_QI, 'LOW_PROBA_CLOUDS_PERCENTAGE', 'N/A')
        o_docSen2cor.createTextNode(doc, o_childL2A_Image_Content_QI, 'MEDIUM_PROBA_CLOUDS_PERCENTAGE', str(d_ImageContent['cloudMP']))
        o_docSen2cor.createTextNode(doc, o_childL2A_Image_Content_QI, 'HIGH_PROBA_CLOUDS_PERCENTAGE', str(d_ImageContent['cloudHP']))
        o_docSen2cor.createTextNode(doc, o_childL2A_Image_Content_QI, 'THIN_CIRRUS_PERCENTAGE', str(d_ImageContent['cirrus']))
        o_docSen2cor.createTextNode(doc, o_childL2A_Image_Content_QI, 'CLOUD_COVERAGE_PERCENTAGE', 'N/A')
        o_docSen2cor.createTextNode(doc, o_childL2A_Image_Content_QI, 'SNOW_ICE_PERCENTAGE', str(d_ImageContent['snow']))
        o_docSen2cor.createTextNode(doc, o_childL2A_Image_Content_QI, 'RADIATIVE_TRANSFER_ACCURAY', '0.0')
        o_docSen2cor.createTextNode(doc, o_childL2A_Image_Content_QI, 'WATER_VAPOUR_RETRIEVAL_ACCURACY', '0.0')
        o_docSen2cor.createTextNode(doc, o_childL2A_Image_Content_QI, 'AOT_RETRIEVAL_ACCURACY', '0.0')
        
        # Node L1C_Pixel_Level_QI
        o_childL1C_Pixel_Level_QI = o_docSen2cor.insertElementNode(doc, o_childQuality_Indicators_Info, 'L1C_Pixel_Level_QI', {'geometry':'FULL_RESOLUTION'})
        o_docSen2cor.createElementNode(doc, o_childL1C_Pixel_Level_QI, 'MASK_FILENAME',{'bandId':'N/A','type':'N/A'}, 'N/A')
        
        # Node L2A_Pixel_Level_QI
        o_childL2A_Pixel_Level_QI = o_docSen2cor.createNode(doc, o_childQuality_Indicators_Info, 'L2A_Pixel_Level_QI')
        o_docSen2cor.createTextNode(doc, o_childL2A_Pixel_Level_QI, 'CLOUD_CONFIDENCE_MASK', 'N/A')
        o_docSen2cor.createTextNode(doc, o_childL2A_Pixel_Level_QI, 'SNOW_ICE_CONFIDENCE_MASK', 'N/A')
        
        # Node PVI_FILENAME
        o_docSen2cor.createTextNode(doc, o_childQuality_Indicators_Info, 'PVI_FILENAME', 'N/A')
        

        fp_out = open( _s_dimapPathNew, 'w' )
        fp_out.write( o_docSen2cor.toprettyxml_fixed( doc, _s_encoding='utf-8')  )
        fp_out.close()
        
        logging.info('Write metadata from Sen2cor product finish without error')
    
    
    @classmethod
    def ReadMuscateMetadata_2( cls
                           , _s_productPath
                           ):
        """
        Function to read Muscate Metadata and to transform it to Sen2cor metadata
        @param _s_productPath : path of product to convert
        return : dictionnary with some values and nodes with other values
        """

        logging.info('Read metadata from Muscate product : %s',_s_productPath)
        
        # Metadata from Muscate
        s_dimapPathOld = glob.glob(os.path.join(_s_productPath, '*_MTD_ALL.xml'))
        if len(s_dimapPathOld) == 0:
            logging.warn('No dimap for product %s'%_s_productPath)
        else:
            s_dimapPathOld = s_dimapPathOld[0]
            
        # Initialise dictionnary with metadata values
        d_dimapValue = {}
        
        o_docMuscate = XmlTools(s_dimapPathOld)
        o_rootMuscate = o_docMuscate.getRootNode()
        
        # date
        d_dimapValue['date_start'] = o_docMuscate.getNodeValue( o_docMuscate.getIndirectNode( o_rootMuscate, 'ACQUISITION_DATE' ) )
        d_dimapValue['date_stop'] = o_docMuscate.getNodeValue( o_docMuscate.getIndirectNode( o_rootMuscate, 'ACQUISITION_DATE' ) )
        d_dimapValue['acquisitionDate'] = o_docMuscate.getNodeValue( o_docMuscate.getIndirectNode( o_rootMuscate, 'ACQUISITION_DATE' ) )
        d_dimapValue['Creation_Date'] = o_docMuscate.getNodeValue( o_docMuscate.getIndirectNode( o_rootMuscate, 'PRODUCTION_DATE' ) )
        
        # Name
        d_dimapValue['file_name'] = o_docMuscate.getNodeValue( o_docMuscate.getIndirectNode( o_rootMuscate, 'PRODUCT_ID' ) )
        
        # orbit
        d_dimapValue['orbit'] = o_docMuscate.getNodeValue( o_docMuscate.getIndirectNode( o_rootMuscate, 'ORBIT_NUMBER' ) )
        
        # quantifiaction value
        d_dimapValue['VAP_quantification_value'] = o_docMuscate.getNodeValue( o_docMuscate.getIndirectNode( o_rootMuscate, 'WATER_VAPOR_CONTENT_QUANTIFICATION_VALUE' ) )
        d_dimapValue['AOT_quantification_value'] = o_docMuscate.getNodeValue( o_docMuscate.getIndirectNode( o_rootMuscate, 'AEROSOL_OPTICAL_THICKNESS_QUANTIFICATION_VALUE' ) )
        
        # GIPP
        o_GIPP_files = o_docMuscate.extractNode(o_docMuscate.getIndirectNode( o_rootMuscate, 'Auxiliary_Data_List' ))
        t_typeGIPP = []
        t_GIPP = []
        for o_node in o_docMuscate.getAllTaggedNodes(o_GIPP_files, 'NATURE'):
            t_typeGIPP.append(o_docMuscate.getNodeValue(o_node))
        for o_node in o_docMuscate.getAllTaggedNodes(o_GIPP_files, 'DATA'):
            t_GIPP.append(o_docMuscate.getNodeValue(o_node))
        
        return d_dimapValue, t_typeGIPP, t_GIPP
        
    

    @classmethod
    def WriteSen2corMetadata_2( cls
                            , _s_productPath
                            , _d_dimapValue
                            , _t_typeGIPP
                            , _t_GIPP
                            , _s_dimapPathNew
                            ):
        
        """
        Function to write Sen2cor metadata
        @param _s_productPath : path for product to convert
        @param _d_dimapValue : dictionnary with some values to write
        @param _t_typeGIPP : GIPP type
        @param _t_GIPP : GIPP name
        @param _s_dimapPathNew : directory to save second metadata file
        """
    
        logging.info('Write metadata for Sen2cor product in %s', _s_dimapPathNew)
        
        o_docSen2cor = XmlTools(_s_dimapPathNew)
        doc = minidom.Document()
        
        # Parent Node
        o_parentNode = o_docSen2cor.insertElementNode(doc, doc, "n1:Level-2A_User_Product", {'xmlns:n1':"https://psd-14.sentinel2.eo.esa.int/PSD/User_Product_Level-2A.xsd", \
                                                                                        'xmlns:xsi':"http://www.w3.org/2001/XMLSchema-instance", \
                                                                                        'xsi:schemaLocation':"https://psd-14.sentinel2.eo.esa.int/PSD/User_Product_Level-2A.xsd"})
                                                                                        
        # Node General_Info
        o_childGeneral_Info = doc.createElement('n1:General_Info')
        o_parentNode.appendChild(o_childGeneral_Info)
        
        # Node L2A_Product_Info
        o_childL2A_Product_Info = doc.createElement('L2A_Product_Info')
        o_childGeneral_Info.appendChild(o_childL2A_Product_Info)
        
        # dates
        o_docSen2cor.createTextNode(doc, o_childL2A_Product_Info, 'PRODUCT_START_TIME', _d_dimapValue['date_start'])
        o_docSen2cor.createTextNode(doc, o_childL2A_Product_Info, 'PRODUCT_STOP_TIME', _d_dimapValue['date_stop'])
        
        o_docSen2cor.createTextNode(doc, o_childL2A_Product_Info, 'PRODUCT_URI_1C', 'Not applicable')
        o_docSen2cor.createTextNode(doc, o_childL2A_Product_Info, 'PRODUCT_URI_2A', _d_dimapValue['file_name'])
        o_docSen2cor.createTextNode(doc, o_childL2A_Product_Info, 'PROCESSING_LEVEL', 'Level-2Ap')
        o_docSen2cor.createTextNode(doc, o_childL2A_Product_Info, 'PRODUCT_TYPE', 'S2MSI2Ap')
        o_docSen2cor.createTextNode(doc, o_childL2A_Product_Info, 'PROCESSING_BASELINE', '02.04')
        o_docSen2cor.createTextNode(doc, o_childL2A_Product_Info, 'GENERATION_TIME', _d_dimapValue['Creation_Date'])
        o_docSen2cor.createTextNode(doc, o_childL2A_Product_Info, 'PREVIEW_IMAGE_URL', 'Not applicable')
        o_docSen2cor.createTextNode(doc, o_childL2A_Product_Info, 'PREVIEW_GEO_INFO', 'Not applicable')
        
        # Datatake
        s_date = ''.join(''.join(_d_dimapValue['acquisitionDate'].split('-')).split(':'))
        s_identifier = 'G' + _d_dimapValue['file_name'].split('_')[0] + '_' + s_date + '_' + _d_dimapValue['orbit'] + '_N02.04'
        o_dataTake = o_docSen2cor.insertElementNode(doc, o_childL2A_Product_Info, 'Datatake', {'datatakeIdentifier':s_identifier})
        o_docSen2cor.createTextNode(doc, o_dataTake, 'SPACECRAFT_NAME', _d_dimapValue['file_name'].split('_')[0])
        o_docSen2cor.createTextNode(doc, o_dataTake, 'DATATAKE_TYPE', 'N/A')
        o_docSen2cor.createTextNode(doc, o_dataTake, 'DATATAKE_SENSING_START', _d_dimapValue['acquisitionDate'] + '.001Z')
        o_docSen2cor.createTextNode(doc, o_dataTake, 'SENSING_ORBIT_NUMBER', _d_dimapValue['orbit'])
        o_docSen2cor.createTextNode(doc, o_dataTake, 'SENSING_ORBIT_DIRECTION', 'N/A')
        
        # query options
        o_queryOptions = o_docSen2cor.insertElementNode(doc, o_childL2A_Product_Info, 'Query_Options', {'completeSingleTile':'true'})
        o_docSen2cor.createTextNode(doc, o_queryOptions, 'PRODUCT_FORMAT', 'SAFE_COMPACT')
        
        # L2A product organisation
        o_childL2A_Product_Organisation = doc.createElement('L2A_Product_Organisation')
        o_childL2A_Product_Info.appendChild(o_childL2A_Product_Organisation)
        o_childGranule_List = doc.createElement('Granule_List')
        o_childL2A_Product_Organisation.appendChild(o_childGranule_List)
        
        s_date = ''.join(''.join(_d_dimapValue['acquisitionDate'].split('-')).split(':')).split('.')[0]
        s_orbit = '000000'
        s_orbit = s_orbit[0:6-len(str(_d_dimapValue['orbit']))] + str(_d_dimapValue['orbit'])
        s_tileID = _d_dimapValue['file_name'].split('_')[3]
        s_tile = 'S2A_OPER_MSI_L2A_TL_SGS__%s_A%s_%s_N02.04'%(s_date, s_orbit, s_tileID)
        
        t_R10m, t_R20m, t_R60m = cls.getImagesByResol( _s_dimapPathNew )
        
        if t_R60m != []:
            o_granule = o_docSen2cor.insertElementNode(doc, o_childGranule_List, 'Granule', {'granuleIdentifier':s_tile, 'datastripIdentifier':s_tile, 'imageFormat':'JPEG2000'})
            for image in t_R60m:
                o_docSen2cor.createTextNode(doc, o_granule, 'IMAGE_FILE_2A', image)
        if t_R20m != []:
            o_granule = o_docSen2cor.insertElementNode(doc, o_childGranule_List, 'Granule', {'granuleIdentifier':s_tile, 'datastripIdentifier':s_tile, 'imageFormat':'JPEG2000'})
            for image in t_R20m:
                o_docSen2cor.createTextNode(doc, o_granule, 'IMAGE_FILE_2A', image)
        if t_R10m != []:
            o_granule = o_docSen2cor.insertElementNode(doc, o_childGranule_List, 'Granule', {'granuleIdentifier':s_tile, 'datastripIdentifier':s_tile, 'imageFormat':'JPEG2000'})
            for image in t_R10m:
                o_docSen2cor.createTextNode(doc, o_granule, 'IMAGE_FILE_2A', image)
        
        # L2A product image characteristics
        o_childL2A_Product_Characteristics = doc.createElement('L2A_Product_Image_Characteristics')
        o_childGeneral_Info.appendChild(o_childL2A_Product_Characteristics)
        o_childSpecialValues = doc.createElement('Special_Values')
        o_childL2A_Product_Characteristics.appendChild(o_childSpecialValues)
        o_docSen2cor.createTextNode(doc, o_childSpecialValues, 'SPECIAL_VALUE_TEXT', 'NODATA')
        o_docSen2cor.createTextNode(doc, o_childSpecialValues, 'SPECIAL_VALUE_INDEX', '0')
        o_childSpecialValues = doc.createElement('Special_Values')
        o_childL2A_Product_Characteristics.appendChild(o_childSpecialValues)
        o_docSen2cor.createTextNode(doc, o_childSpecialValues, 'SPECIAL_VALUE_TEXT', 'SATURATED')
        o_docSen2cor.createTextNode(doc, o_childSpecialValues, 'SPECIAL_VALUE_INDEX', '65535')
        o_childDisplayOrder = doc.createElement('Image_Display_Order')
        o_childL2A_Product_Characteristics.appendChild(o_childDisplayOrder)
        o_docSen2cor.createTextNode(doc, o_childDisplayOrder, 'RED_CHANNEL', '3')
        o_docSen2cor.createTextNode(doc, o_childDisplayOrder, 'GREEN_CHANNEL', '2')
        o_docSen2cor.createTextNode(doc, o_childDisplayOrder, 'BLUE_CHANNEL', '1')
        
        o_childQuantificationValue = doc.createElement('L1C_L2A_Quantification_Values_List')
        o_childL2A_Product_Characteristics.appendChild(o_childQuantificationValue)
        o_docSen2cor.createElementNode(doc, o_childQuantificationValue, 'L1C_TOA_QUANTIFICATION_VALUE',{'unit':'none'}, '0')
        o_docSen2cor.createElementNode(doc, o_childQuantificationValue, 'L2A_BOA_QUANTIFICATION_VALUE',{'unit':'none'}, '0')
        o_docSen2cor.createElementNode(doc, o_childQuantificationValue, 'L2A_AOT_QUANTIFICATION_VALUE',{'unit':'none'}, str(1/float(_d_dimapValue['AOT_quantification_value'])))
        o_docSen2cor.createElementNode(doc, o_childQuantificationValue, 'L2A_WVP_QUANTIFICATION_VALUE',{'unit':'cm'}, str(1/float(_d_dimapValue['VAP_quantification_value'])))
        
        o_childReflectance = doc.createElement('Reflectance_Conversion')
        o_childL2A_Product_Characteristics.appendChild(o_childReflectance)
        o_docSen2cor.createTextNode(doc, o_childReflectance, 'U', 'N/A')
        o_childIrradiance = doc.createElement('Solar_Irradiance_List')
        o_childReflectance.appendChild(o_childIrradiance)
        o_docSen2cor.createElementNode(doc, o_childIrradiance, 'SOLAR_IRRADIANCE',{'bandId':'0', 'unit':'W/m&#178;/&#181;m'}, 'N/A')
        o_docSen2cor.createElementNode(doc, o_childIrradiance, 'SOLAR_IRRADIANCE',{'bandId':'1', 'unit':'W/m&#178;/&#181;m'}, 'N/A')
        o_docSen2cor.createElementNode(doc, o_childIrradiance, 'SOLAR_IRRADIANCE',{'bandId':'2', 'unit':'W/m&#178;/&#181;m'}, 'N/A')
        o_docSen2cor.createElementNode(doc, o_childIrradiance, 'SOLAR_IRRADIANCE',{'bandId':'3', 'unit':'W/m&#178;/&#181;m'}, 'N/A')
        o_docSen2cor.createElementNode(doc, o_childIrradiance, 'SOLAR_IRRADIANCE',{'bandId':'4', 'unit':'W/m&#178;/&#181;m'}, 'N/A')
        o_docSen2cor.createElementNode(doc, o_childIrradiance, 'SOLAR_IRRADIANCE',{'bandId':'5', 'unit':'W/m&#178;/&#181;m'}, 'N/A')
        o_docSen2cor.createElementNode(doc, o_childIrradiance, 'SOLAR_IRRADIANCE',{'bandId':'6', 'unit':'W/m&#178;/&#181;m'}, 'N/A')
        o_docSen2cor.createElementNode(doc, o_childIrradiance, 'SOLAR_IRRADIANCE',{'bandId':'7', 'unit':'W/m&#178;/&#181;m'}, 'N/A')
        o_docSen2cor.createElementNode(doc, o_childIrradiance, 'SOLAR_IRRADIANCE',{'bandId':'8', 'unit':'W/m&#178;/&#181;m'}, 'N/A')
        o_docSen2cor.createElementNode(doc, o_childIrradiance, 'SOLAR_IRRADIANCE',{'bandId':'9', 'unit':'W/m&#178;/&#181;m'}, 'N/A')
        o_docSen2cor.createElementNode(doc, o_childIrradiance, 'SOLAR_IRRADIANCE',{'bandId':'10', 'unit':'W/m&#178;/&#181;m'}, 'N/A')
        o_docSen2cor.createElementNode(doc, o_childIrradiance, 'SOLAR_IRRADIANCE',{'bandId':'11', 'unit':'W/m&#178;/&#181;m'}, 'N/A')
        o_docSen2cor.createElementNode(doc, o_childIrradiance, 'SOLAR_IRRADIANCE',{'bandId':'12', 'unit':'W/m&#178;/&#181;m'}, 'N/A')

        o_childSpectralInformationList = doc.createElement('Spectral_Information_List')
                
        t_bands = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B9', 'B10', 'B11', 'B12']
        for j,s_band in enumerate(t_bands):
            b_band = False
            s_resol = 'N/A'
            for i in range(len(t_R10m)):
                if s_band in t_R10m[i]:
                    b_band = True
                    s_resol = '10'
                    break
            if not b_band:
                for i in range(len(t_R20m)):
                    if s_band in t_R20m[i]:
                        b_band = True
                        s_resol = '20'
                        break
            if not b_band:
                for i in range(len(t_R60m)):
                    if s_band in t_R60m[i]:
                        b_band = True
                        s_resol = '60'
                        break
            o_childL2A_Product_Characteristics.appendChild(o_childSpectralInformationList)
            o_childSpectralInformation = o_docSen2cor.insertElementNode(doc, o_childSpectralInformationList, 'Spectral_Information', {'bandId':str(j), 'physicalBand':s_band})
            o_docSen2cor.createTextNode(doc, o_childSpectralInformation, 'RESOLUTION', s_resol)
            o_childWavelength = doc.createElement('Wavelength')
            o_childSpectralInformation.appendChild(o_childWavelength)
            o_docSen2cor.createElementNode(doc, o_childWavelength, 'MIN',{'unit':'nm'}, 'N/A')
            o_docSen2cor.createElementNode(doc, o_childWavelength, 'MAX',{'unit':'nm'}, 'N/A')
            o_docSen2cor.createElementNode(doc, o_childWavelength, 'CENTRAL',{'unit':'nm'}, 'N/A')
            o_childSpectralReponse = doc.createElement('Spectral_Response')
            o_childSpectralInformation.appendChild(o_childSpectralReponse)
            o_docSen2cor.createElementNode(doc, o_childSpectralReponse, 'STEP',{'unit':'nm'}, 'N/A')
            o_docSen2cor.createTextNode(doc, o_childSpectralReponse, 'VALUES', 'N/A')

        for j,s_band in enumerate(t_bands):
            o_docSen2cor.createElementNode(doc, o_childL2A_Product_Characteristics, 'PHYSICAL_GAINS',{'bandId':str(j)}, 'N/A')
        
        o_docSen2cor.createTextNode(doc, o_childL2A_Product_Characteristics, 'REFERENCE_BAND', '0')
        
        # L2A scene classification
        o_childSceneClassificationList = doc.createElement('L2A_Scene_Classification_List')
        o_childL2A_Product_Characteristics.appendChild(o_childSceneClassificationList)
        
        t_text = ['SC_NODATA', 'SC_SATURATED_DEFECTIVE', 'SC_DARK_FEATURE_SHADOW', 'SC_CLOUD_SHADOW', 'SC_VEGETATION', \
                  'SC_BARE_SOIL_DESERT', 'SC_WATER', 'SC_CLOUD_LOW_PROBA', 'SC_CLOUD_MEDIUM_PROBA', 'SC_CLOUD_HIGH_PROBA', \
                   'SC_THIN_CIRRUS', 'SC_SNOW_ICE']
        t_index = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11']
        
        for i in range(len(t_text)):
            o_childSceneClassification = doc.createElement('L2A_Scene_Classification_ID')
            o_childSceneClassificationList.appendChild(o_childSceneClassification)
            o_docSen2cor.createTextNode(doc, o_childSceneClassification, 'L2A_SCENE_CLASSIFICATION_TEXT', t_text[i])
            o_docSen2cor.createTextNode(doc, o_childSceneClassification, 'L2A_SCENE_CLASSIFICATION_INDEX', t_index[i])

        # Geometric info
        o_childGeometricInfo = doc.createElement('n1:Geometric_Info')
        o_parentNode.appendChild(o_childGeometricInfo)
        o_childProduct1 = doc.createElement('Product_Footprint')
        o_childGeometricInfo.appendChild(o_childProduct1)
        o_childProduct2 = doc.createElement('Product_Footprint')
        o_childProduct1.appendChild(o_childProduct2)
        o_childGlobalFootprint = doc.createElement('Global_Footprint')
        o_childProduct2.appendChild(o_childGlobalFootprint)
        o_docSen2cor.createTextNode(doc, o_childGlobalFootprint, 'EXT_POS_LIST', 'N/A')
        o_docSen2cor.createTextNode(doc, o_childProduct1, 'RASTER_CS_TYPE', 'POINT')
        o_docSen2cor.createTextNode(doc, o_childProduct1, 'PIXEL_ORIGIN', '1')
        o_childCRS = doc.createElement('Coordinate_Reference_System')
        o_childGeometricInfo.appendChild(o_childCRS)
        o_docSen2cor.createElementNode(doc, o_childCRS, 'GEO_TABLES',{'version':'1'}, 'EPSG')
        o_docSen2cor.createTextNode(doc, o_childCRS, 'HORIZONTAL_CS_TYPE', 'GEOGRAPHIC')

        # Auxiliary info
        o_childAuxiliaryInfo = doc.createElement('n1:Auxiliary_Data_Info')
        o_parentNode.appendChild(o_childAuxiliaryInfo)
        o_childGIPPList = doc.createElement('GIPP_List')
        o_childAuxiliaryInfo.appendChild(o_childGIPPList)

        for i,s_GIPP in enumerate(_t_GIPP):
            o_docSen2cor.createElementNode(doc, o_childGIPPList, 'GIPP_FILENAME',{'type':_t_typeGIPP[i], 'version':'N/A'}, s_GIPP)
            
        # L2A Auxiliary info
        o_childL2AAuxiliaryInfo = doc.createElement('n1:L2A_Auxiliary_Data_Info')
        o_parentNode.appendChild(o_childL2AAuxiliaryInfo)
        o_childAuxData = doc.createElement('Aux_Data')
        o_childL2AAuxiliaryInfo.appendChild(o_childAuxData)
        o_childL2AGIPP = doc.createElement('L2A_GIPP_List')
        o_childAuxData.appendChild(o_childL2AGIPP)
        s_date = _d_dimapValue['acquisitionDate'].replace('-','').replace(':','')
        s_default = '000000'
        s_orbit = 'A' + s_default[0:6-len(_d_dimapValue['orbit'])] + _d_dimapValue['orbit']
        s_tile = 'T' + _d_dimapValue['file_name'].split('_')[4]
        s_GIPPL2A = '_'.join(['L2A',s_tile,s_orbit,s_date])
        o_docSen2cor.createElementNode(doc, o_childL2AGIPP, 'GIPP_FILENAME',{'type':'GIP_Level-2Ap', 'version':'N/A'}, s_GIPPL2A)
        o_docSen2cor.createElementNode(doc, o_childL2AGIPP, 'GIPP_FILENAME',{'type':'GIP_Level-2Ap', 'version':'N/A'}, s_GIPPL2A)
        o_docSen2cor.createElementNode(doc, o_childL2AGIPP, 'GIPP_FILENAME',{'type':'GIP_Level-2Ap', 'version':'N/A'}, s_GIPPL2A)
        o_docSen2cor.createTextNode(doc, o_childAuxData, 'L2A_PRODUCTION_DEM_TYPE', 'http://data_public:GDdci@data.cgiar-csi.org/srtm/tiles/GeoTIFF/')
        o_childL2ALUTS = doc.createElement('L2A_LIBRADTRAN_LUTS')
        o_childAuxData.appendChild(o_childL2ALUTS)
        o_docSen2cor.createTextNode(doc, o_childAuxData, 'L2A_SNOW_CLIMATOLOGY', 'GlobalSnowMap.tiff')
        
        # quality indicators info
        o_childQualityIndicator = doc.createElement('n1:Quality_Indicators_Info')
        o_parentNode.appendChild(o_childQualityIndicator)
        o_docSen2cor.createTextNode(doc, o_childQualityIndicator, 'Cloud_Coverage_Assessment', 'N/A')
        o_childTechnicalQuality = doc.createElement('Technical_Quality_Assessment')
        o_childQualityIndicator.appendChild(o_childTechnicalQuality)
        o_docSen2cor.createTextNode(doc, o_childTechnicalQuality, 'DEGRADED_ANC_DATA_PERCENTAGE', '0')
        o_docSen2cor.createTextNode(doc, o_childTechnicalQuality, 'DEGRADED_MSI_DATA_PERCENTAGE', '0')
        o_childQualityControl = doc.createElement('Quality_Control_Checks')
        o_childQualityIndicator.appendChild(o_childQualityControl)
        o_childQualityInspection = doc.createElement('Quality_Inspections')
        o_childQualityControl.appendChild(o_childQualityInspection)
        o_docSen2cor.createTextNode(doc, o_childQualityInspection, 'SENSOR_QUALITY_FLAG', 'N/A')
        o_docSen2cor.createTextNode(doc, o_childQualityInspection, 'GEOMETRIC_QUALITY_FLAG', 'N/A')
        o_docSen2cor.createTextNode(doc, o_childQualityInspection, 'GENERAL_QUALITY_FLAG', 'N/A')
        o_docSen2cor.createTextNode(doc, o_childQualityInspection, 'FORMAT_CORRECTNESS_FLAG', 'N/A')
        o_docSen2cor.createTextNode(doc, o_childQualityInspection, 'RADIOMETRIC_QUALITY_FLAG', 'N/A')
        o_childFailedInspection = doc.createElement('Failed_Inspections')
        o_childQualityControl.appendChild(o_childFailedInspection)
  
        # Node L2A Quality indicators info
        d_ImageContent = cls.calculatePercentageValue( _s_productPath )
        o_childL2AQualityIndicator = doc.createElement('n1:L2A_Quality_Indicators_Info')
        o_parentNode.appendChild(o_childL2AQualityIndicator)
        o_childL2A_Image_Content_QI = o_docSen2cor.createNode(doc, o_childL2AQualityIndicator, 'Image_Content_QI')
        o_docSen2cor.createTextNode(doc, o_childL2A_Image_Content_QI, 'NODATA_PIXEL_PERCENTAGE', str(d_ImageContent['no_data']))
        o_docSen2cor.createTextNode(doc, o_childL2A_Image_Content_QI, 'SATURATED_DEFECTIVE_PIXEL_PERCENTAGE', str(d_ImageContent['sat']))
        o_docSen2cor.createTextNode(doc, o_childL2A_Image_Content_QI, 'DARK_FEATURES_PERCENTAGE', 'N/A')
        o_docSen2cor.createTextNode(doc, o_childL2A_Image_Content_QI, 'CLOUD_SHADOW_PERCENTAGE', str(d_ImageContent['shad']))
        o_docSen2cor.createTextNode(doc, o_childL2A_Image_Content_QI, 'VEGETATION_PERCENTAGE', 'N/A')
        o_docSen2cor.createTextNode(doc, o_childL2A_Image_Content_QI, 'BARE_SOILS_PERCENTAGE', 'N/A')
        o_docSen2cor.createTextNode(doc, o_childL2A_Image_Content_QI, 'WATER_PERCENTAGE', str(d_ImageContent['water']))
        o_docSen2cor.createTextNode(doc, o_childL2A_Image_Content_QI, 'LOW_PROBA_CLOUDS_PERCENTAGE', 'N/A')
        o_docSen2cor.createTextNode(doc, o_childL2A_Image_Content_QI, 'MEDIUM_PROBA_CLOUDS_PERCENTAGE', str(d_ImageContent['cloudMP']))
        o_docSen2cor.createTextNode(doc, o_childL2A_Image_Content_QI, 'HIGH_PROBA_CLOUDS_PERCENTAGE', str(d_ImageContent['cloudHP']))
        o_docSen2cor.createTextNode(doc, o_childL2A_Image_Content_QI, 'THIN_CIRRUS_PERCENTAGE', str(d_ImageContent['cirrus']))
        o_docSen2cor.createTextNode(doc, o_childL2A_Image_Content_QI, 'CLOUD_COVERAGE_PERCENTAGE', 'N/A')
        o_docSen2cor.createTextNode(doc, o_childL2A_Image_Content_QI, 'SNOW_ICE_PERCENTAGE', str(d_ImageContent['snow']))
        o_docSen2cor.createTextNode(doc, o_childL2A_Image_Content_QI, 'RADIATIVE_TRANSFER_ACCURAY', '0.0')
        o_docSen2cor.createTextNode(doc, o_childL2A_Image_Content_QI, 'WATER_VAPOUR_RETRIEVAL_ACCURACY', '0.0')
        o_docSen2cor.createTextNode(doc, o_childL2A_Image_Content_QI, 'AOT_RETRIEVAL_ACCURACY', '0.0')
  

        
        fp_out = open( _s_dimapPathNew, 'w' )
        fp_out.write( o_docSen2cor.toprettyxml_fixed( doc, _s_encoding='utf-8')  )
        fp_out.close()

        logging.info('Write metadata from Sen2cor product finish without error')


    @classmethod
    def getImagesByResol( cls, _s_productPath ):
        """
        Get directories for all images by resolutions
        @param _s_productPath : Sen2cor product path
        """
		
        t_matches = glob.glob(os.path.join(os.path.split(_s_productPath)[0], 'GRANULE', '*', 'IMG_DATA', '*', '*.jp2'))
		
        t_R10m = []
        t_R20m = []
        t_R60m = []
        for s_image in t_matches:
            if 'R10m' in s_image:
                t_R10m.append('/'.join(s_image.split(os.sep)[-5:]))
            elif 'R20m' in s_image:
                t_R20m.append('/'.join(s_image.split(os.sep)[-5:]))
            elif 'R60m' in s_image:
                t_R60m.append('/'.join(s_image.split(os.sep)[-5:]))
		
        return t_R10m, t_R20m, t_R60m
        

    @classmethod
    def Convert( cls
               , _s_productPath
               , _s_workingDir
               ):
	
        """
        Convert metadata from Muscate product to metadata for Sen2cor product
        @param _s_productPath : path for product to convert
        @param _s_workingDir : directory where the new image will be saved
        """

        # Directory to save metadata 1
        s_dimapPathNew = os.path.join(glob.glob(os.path.join(_s_workingDir,'GRANULE','*'))[0],'MTD_TL.xml')

        # Read Muscate metadata file
        d_dimapValue, o_Mean_Value_List, o_Sun_Angles_Grids, o_Incidence_Angles_Grids_List = cls.ReadMuscateMetadata(_s_productPath)
        
        # Write Sen2cor metadata 1
        cls.WriteSen2corMetadata(_s_productPath, d_dimapValue, o_Mean_Value_List, o_Sun_Angles_Grids, o_Incidence_Angles_Grids_List, s_dimapPathNew)


        # Directory to save metadata 2
        s_dimapPathNew = os.path.join(_s_workingDir,'MTD_MSIL2A.xml')

        # Read MACCS metadata file
        d_dimapValue, t_typeGIPP, t_GIPP = cls.ReadMuscateMetadata_2(_s_productPath)
        
        # Write Sen2cor metadata 2
        cls.WriteSen2corMetadata_2(_s_productPath, d_dimapValue, t_typeGIPP, t_GIPP, s_dimapPathNew)


    def getQuantificationValue( self
                              , _s_productPath
                              ):
        """
        Get reflectance quantification value from Muscate metadata file
        @param _s_productPath : path for product to convert
        """
        
        logging.info('Read metadata from Muscate product : %s to get reflectance quantification value',_s_productPath)
        
        # Metadata from Muscate
        s_dimapPathOld = glob.glob(os.path.join(_s_productPath, '*_MTD_ALL.xml'))
        if len(s_dimapPathOld) == 0:
            logging.warn('No dimap for product %s'%_s_productPath)
        else:
            s_dimapPathOld = s_dimapPathOld[0]
        
        o_docMuscate = XmlTools(s_dimapPathOld)
        o_rootMuscate = o_docMuscate.getRootNode()
        Refl_QV = o_docMuscate.getNodeValue( o_docMuscate.getIndirectNode( o_rootMuscate, 'REFLECTANCE_QUANTIFICATION_VALUE' ) )
        
        return Refl_QV
