#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

"""
Class for dimap MACCS product

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
    import glob
    from xml.dom import minidom
    import xml.dom.minidom
    from numpy import*
    
    from XmlTools import XmlTools
    from masks.MACCSMasks import MACCSMasks
    
except Exception, e :
    print "Probleme with Python library : %s" %e
    raise Exception, "System exit with error"

class MACCSS2Dimap(MACCSMasks):
	
    @classmethod
    def ReadMACCSMetadata( cls
                           , _s_productPath
                           ):
        """
        Function to read MACCS Metadata and to transform it to Sen2cor metadata
        @param _s_productPath : path of product to convert
        return : dictionnary with some values and nodes with other values
        """

        logging.info('Read metadata from MACCS product : %s',_s_productPath)
        
        # Metadata from MACCS
        s_dimapPathOld = glob.glob(os.path.join(_s_productPath, '*SC_*.HDR'))
        if len(s_dimapPathOld) == 0:
            logging.warn('No dimap for product %s'%_s_productPath)
        else:
            s_dimapPathOld = s_dimapPathOld[0]
        
        # Initialise dictionnary with metadata values
        d_dimapValue = {}
        
        o_docMACCS = XmlTools(s_dimapPathOld)
        o_rootMACCS = o_docMACCS.getRootNode()
        
        # Product name
        o_parent = o_docMACCS.getIndirectNode(o_rootMACCS,'Earth_Explorer_Header')
        d_dimapValue['product'] = o_docMACCS.getTagNodeValue(o_parent,'File_Name')
        
        # date
        d_dimapValue['acquisitionDate'] = o_docMACCS.getNodeValue( o_docMACCS.getIndirectNode( o_rootMACCS, 'Acquisition_Date_Time' ) ).replace('UTC=','')
        d_dimapValue['prodDate'] = o_docMACCS.getNodeValue( o_docMACCS.getIndirectNode( o_rootMACCS, 'Date_Time' ) ).replace('UTC=','')
        
        # Geocoding
        o_parentGeocoding = o_docMACCS.getIndirectNode(o_rootMACCS,'Coordinate_Reference_System')
        d_dimapValue['HORIZONTAL_CS_NAME'] = o_docMACCS.getNodeValue( o_docMACCS.getIndirectNode( o_parentGeocoding, 'Short_Description' ) )
        d_dimapValue['HORIZONTAL_CS_CODE'] = o_docMACCS.getNodeValue( o_docMACCS.getIndirectNode( o_parentGeocoding, 'Code' ) )
        
        # Geoposition
        o_ULX = o_docMACCS.getIndirectNodes( o_rootMACCS, 'ULX' )
        o_ULY = o_docMACCS.getIndirectNodes( o_rootMACCS, 'ULY' )
        o_XDIM = o_docMACCS.getIndirectNodes( o_rootMACCS, 'By_Line' )
        o_YDIM = o_docMACCS.getIndirectNodes( o_rootMACCS, 'By_Column' )
        o_NROWS = o_docMACCS.getIndirectNodes( o_rootMACCS, 'Lines' )
        o_NCOLS = o_docMACCS.getIndirectNodes( o_rootMACCS, 'Columns' )
        s_ULX = []
        s_ULY = []
        s_XDIM = []
        s_YDIM = []
        s_NROWS = []
        s_NCOLS = []
        for i in range(len(o_ULX)):
            s_ULX.append(o_docMACCS.getNodeValue(o_ULX[i]))
            s_ULY.append(o_docMACCS.getNodeValue(o_ULY[i]))
            s_XDIM.append(o_docMACCS.getNodeValue(o_XDIM[i]))
            s_YDIM.append(o_docMACCS.getNodeValue(o_YDIM[i]))
            s_NROWS.append(o_docMACCS.getNodeValue(o_NROWS[i]))
            s_NCOLS.append(o_docMACCS.getNodeValue(o_NCOLS[i]))
        
        d_dimapValue['ULX'] = s_ULX
        d_dimapValue['ULY'] = s_ULY
        d_dimapValue['XDIM'] = s_XDIM
        d_dimapValue['YDIM'] = s_YDIM
        d_dimapValue['NROWS'] = s_NROWS
        d_dimapValue['NCOLS'] = s_NCOLS
        
        # Mean_Viewing_Incidence_Angle_List
        o_Mean_Value_List = o_docMACCS.extractNode(o_docMACCS.getIndirectNode( o_rootMACCS, 'Mean_Viewing_Incidence_Angle_List' ))
        o_Mean_Viewing_Incidence_Angle = o_docMACCS.getIndirectNodes(o_Mean_Value_List, 'Mean_Viewing_Incidence_Angle')
        for o_Mean_Value in o_Mean_Viewing_Incidence_Angle:
            attr_MeanValue = o_Mean_Value.attributes['band_id']
            attr_MeanValue.name = 'bandId'

        # Transform node Sun_Angles_Grids
        o_Sun_Angles_Grids = o_docMACCS.extractNode(o_docMACCS.getIndirectNode( o_rootMACCS, 'Solar_Angles' ))
        o_Sun_Angles_Grids.tagName = 'Sun_Angles_Grid'
        
        # Mean_Sun_Angle
        o_Mean_Sun_Angle = o_docMACCS.extractNode(o_docMACCS.getIndirectNode( o_rootMACCS, 'Mean_Sun_Angle'))
        
        # Transform node Viewing_Incidence_Angles_Grids
        o_Incidence_Angles_Grids_List = o_docMACCS.getIndirectNodes(o_rootMACCS,'Viewing_Incidence_Angles_Grids')
        for o_IncidenceAngles in o_Incidence_Angles_Grids_List:
            attr_IncidenceAngles = o_IncidenceAngles.attributes['detector_id']
            attr_IncidenceAngles.name = 'detectorId'
            attr_IncidenceAngles = o_IncidenceAngles.attributes['band_id']
            attr_IncidenceAngles.name = 'bandId'
            
        logging.info('Read metadata from MACCS product finish without error : %s',_s_productPath)
        
        return d_dimapValue, o_Mean_Value_List, o_Sun_Angles_Grids, o_Mean_Sun_Angle, o_Incidence_Angles_Grids_List


    @classmethod
    def WriteSen2corMetadata( cls
                            , _s_productPath
                            , _d_dimapValue
                            , _o_Mean_Value_List
                            , _o_Sun_Angles_Grids
                            , _o_Mean_Sun_Angle
                            , _o_Incidence_Angles_Grids_List
                            , _s_dimapPathNew
                            ):
        
        """
        Function to write Sen2cor metadata
        @param _s_productPath : path for product to convert
        @param _d_dimapValue : dictionnary with some values to write
        @param _o_MeanValue_List : xml node with mean incidence angle values
        @param _o_Sun_Angles_Grids : xml node with sun angles grids
        @param _o_Mean_Sun_Angle : xml node with mean sun angle
        @param _o_Incidence_Angles_Grids_List : xml nodes with incidence angles grids
        @param _s_dimapPathNew : directory to save metadata
        @param _s_reflType : type of reflectance image to use
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
        o_docSen2cor.createElementNode(doc, o_childGeneral_Info, 'TILE_ID_2A',{'metadataLevel':'Brief'}, _d_dimapValue['product'])
        
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
        o_childGeometric_Info = doc.createElement('n1:Geometric_Info')
        o_parentNode.appendChild(o_childGeometric_Info)
        o_childTile_Geocoding = o_docSen2cor.insertElementNode(doc, o_childGeometric_Info, 'Tile_Geocoding', {'metadataLevel':'Brief'})
        o_docSen2cor.createTextNode(doc, o_childTile_Geocoding, 'HORIZONTAL_CS_NAME', _d_dimapValue['HORIZONTAL_CS_NAME'])
        o_docSen2cor.createTextNode(doc, o_childTile_Geocoding, 'HORIZONTAL_CS_CODE', _d_dimapValue['HORIZONTAL_CS_CODE'])
        for i in range(len(_d_dimapValue['XDIM'])):
            s_resol = str(_d_dimapValue['XDIM'][i])
            o_childSize = o_docSen2cor.insertElementNode(doc, o_childTile_Geocoding, 'Size',{'resolution':s_resol})
            o_docSen2cor.createTextNode(doc, o_childSize, 'NROWS', _d_dimapValue['NROWS'][i])
            o_docSen2cor.createTextNode(doc, o_childSize, 'NCOLS', _d_dimapValue['NCOLS'][i])
        for i in range(len(_d_dimapValue['XDIM'])):
            s_resol = str(_d_dimapValue['XDIM'][i])
            o_childSize = o_docSen2cor.insertElementNode(doc, o_childTile_Geocoding, 'Geoposition', {'resolution':s_resol})
            o_docSen2cor.createTextNode(doc, o_childSize, 'ULX', _d_dimapValue['ULX'][i])
            o_docSen2cor.createTextNode(doc, o_childSize, 'ULY', _d_dimapValue['ULY'][i])
            o_docSen2cor.createTextNode(doc, o_childSize, 'XDIM', _d_dimapValue['XDIM'][i])
            o_docSen2cor.createTextNode(doc, o_childSize, 'YDIM', _d_dimapValue['YDIM'][i])   

        o_childTile_Angles = o_docSen2cor.insertElementNode(doc, o_childGeometric_Info, 'Tile_Angles', {'metadataLevel':'Standard'})
        
        # Node Sun_Angles_Grid
        o_childTile_Angles.appendChild(_o_Sun_Angles_Grids)
        
        # Node Mean_Sun_Angle
        o_childTile_Angles.appendChild(_o_Mean_Sun_Angle)
        
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
        d_ImageContent = cls.calculatePercentageValue( _s_productPath)
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
    def Convert( cls
               , _s_productPath
               , _s_workingDir
               ):
        
        # Directory to save metadata
        s_dimapPathNew = os.path.join(glob.glob(os.path.join(_s_workingDir,'GRANULE','*'))[0],'MTD_TL.xml')

        # Read MACCS metadata file
        d_dimapValue, o_Mean_Value_List, o_Sun_Angles_Grids, o_Mean_Sun_Angle, o_Incidence_Angles_Grids_List = cls.ReadMACCSMetadata(_s_productPath)
        
        # Write Sen2cor metadata
        cls.WriteSen2corMetadata(_s_productPath, d_dimapValue, o_Mean_Value_List, o_Sun_Angles_Grids, o_Mean_Sun_Angle, o_Incidence_Angles_Grids_List, s_dimapPathNew)

