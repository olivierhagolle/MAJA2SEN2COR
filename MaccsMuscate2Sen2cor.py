#!/usr/bin/env python2.7
# -*- coding: iso-8859-15 -*-

"""
Converte MACCS or Muscate product to Sen2cor

@version: 1.0

@author: Aurelie COURTOIS (THALES) for French Space Agency (CNES)
@date: 06/06/2017

This converter is a free and open source software under the CeCILL-v2.1 license (French equivalent to GPL)
"""


try:
#----------------------------------------------------------------------------------------------------------
# IMPORTS
#----------------------------------------------------------------------------------------------------------
    import argparse
    import sys
    from datetime import datetime
    import logging
    import os
    import numpy as np
    import shutil
    
    
    from product.MACCSS2Product import MACCSS2Product
    from product.MACCSProduct import MACCSProduct
    from product.MuscateProduct import MuscateProduct
    
except Exception, e :
    print "Probleme with Python library : %s" %e
    raise Exception, "System exit with error"
    
T_PRODUCT_CLASSES= [ MACCSS2Product,
                     MACCSProduct,
                     MuscateProduct
                   ]
                   
if __name__ == '__main__':

    try:

        # Initialise logger
        nowDate = datetime.strftime(datetime.now(),'%Y-%m-%dT%H-%M-%S')
        logging.basicConfig(filename='Convert2Sen2cor_%s.log'%(nowDate), \
            format='%(asctime)s %(levelname)s %(message)s \t', level=logging.INFO)
            
        logConsole = logging.StreamHandler(sys.stdout)
        logConsole.setLevel(logging.INFO)
        logging.getLogger().addHandler(logConsole)

        args = None

        try:
            print 'Read command line'
            # Creation du parser
            parser = argparse.ArgumentParser(description = 'Convert MACCS or Muscate product to Sen2cor')

            # Product to convert
            parser.add_argument('-p', '--product', metavar = '[string]', help = 'Product to convert', required = True)

            # Type of reflectance image to use
            parser.add_argument('-r', '--reflType', metavar = '[string]', choices = ['FRE', 'SRE'], help = 'Type of reflectance image to use', \
            required = False, default = 'FRE')
            # Workspace
            parser.add_argument('-w', '--workspace', metavar = '[string]', help = 'Location of workspace.')

            # Parameters into dictionnary
            args = vars(parser.parse_args())

        except Exception, e:
            print 'Error in parsing of command line'
            print e
            sys.exit(-1)
        
        logging.info('############')
        logging.info('Command line')
        logging.info('############')
        
        logging.info('Product path: %s'%args['product'])
        logging.info('Reflectance type: %s'%args['reflType'])
        logging.info('Workspace: %s'%args['workspace'])
        
        
        logging.info('#########################################')    
        logging.info('Create repository for new Sen2cor product')
        logging.info('#########################################')
        
        s_workspace = os.path.join(args['workspace'], 'Sen2cor_' + os.path.basename(args['product']))
        
        if not (os.path.exists(s_workspace)):
            logging.info('No directory name %s : creation of directory' %s_workspace)
            os.makedirs(s_workspace)
        else:
            logging.info('There is already a directory named %s' %s_workspace)
            logging.info('Change name ...')
            i = 1
            suff = ''
            while os.path.exists(s_workspace + suff):
                suff = '_%s'%str(i)
                i += 1
            os.makedirs(s_workspace + suff)
        
            s_workspace = s_workspace + suff
            logging.info('New name for workspace : %s'%(s_workspace))

        
            
        
        logging.info('################')
        logging.info('Get product type')
        logging.info('################')

        for cls in T_PRODUCT_CLASSES:
            try:
                o_product = cls(args['product'], s_workspace, args['reflType'])
                o_Product = o_product.ProductType(args['product'])
            except Exception as e:
                s_exception = e
		
            else:
                if not o_Product is None:
					break
                    
        if o_Product is None:
            logging.warn('Product type is not recognized')
            sys.exit(0)
            
        
        # Create directories
        s_name = o_product.getName()
        os.makedirs(os.path.join(s_workspace, 'GRANULE', s_name, 'IMG_DATA'))
        os.makedirs(os.path.join(s_workspace, 'GRANULE', s_name, 'QI_DATA'))
        
        
        
        logging.info('######################')
        logging.info('Process of water vapor')
        logging.info('######################')
        
        o_product.ConvertWaterVapor()
        
        
        logging.info('##############')
        logging.info('Process of AOT')
        logging.info('##############')
        
        o_product.ConvertAOTMap()
        
        
        logging.info('######################')
        logging.info('Process of reflectance')
        logging.info('######################')
        
        o_product.ConvertReflectImgs()
        
        
        logging.info('################')
        logging.info('Process of masks')
        logging.info('################')
        
        o_product.ConvertMasks()
        
        
        logging.info('################')
        logging.info('Process of dimap')
        logging.info('################')
        
        o_product.ConvertDimap()
        
        
        
        # move log into workspace
        shutil.move('Convert2Sen2cor_%s.log'%nowDate, s_workspace)
    except SystemExit:
        logging.info('Programme stop')
        # move log into workspace
        if args != None:
            shutil.move('Convert2Sen2cor_%s.log'%nowDate, s_workspace)
        sys.exit(0)
    except Exception, e:
        logging.exception("Exception : %s" % e)
        # move log into workspace
        shutil.move('Convert2Sen2cor_%s.log'%nowDate, s_workspace)
        logging.info('Programme stop')
        sys.exit(100)
