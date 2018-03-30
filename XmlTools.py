#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

"""
Class XmlTools

@version: 1.0 

@author: Aurelie COURTOIS (THALES) for French Space Agency (CNES)
@date: 06/06/2017

This converter is a free and open source software under the CeCILL-v2.1 license (French equivalent to GPL)
"""

try:
#----------------------------------------------------------------------------------------------------------
# IMPORTS
#----------------------------------------------------------------------------------------------------------
    import xml.dom.minidom
    from xml.dom import Node
    #from xml.dom.ext import PrettyPrint
    #from StringIO import StringIO
except Exception, e :
    print "Probleme with Python library : %s" %e
    raise Exception, "System exit with error"
    

class XmlTools:

    def __init__( self
                , _s_filename
                ):
        
        """
        @param _s_filename : xml filename to read
        """
        
        self.s_filename = _s_filename


    def getRootNode( self ):
        """
        Get root node of a xml file
        """
        
        o_doc = None

        fp_file = open(self.s_filename,'r')

        # Read
        s_str = fp_file.read()

        fp_file.close()

        o_doc = xml.dom.minidom.parseString( s_str )

        return o_doc
    
    
    def getNode(self,_o_parent, _s_tag):
        """
        Get child node with tag _s_tag
        @param _o_parent : parent node
        @param _s_tag : search tag
        """
        o_node = None
        
        for o_currentNode in self.getChildrenElementNodes(_o_parent):
            if ( o_currentNode.tagName == _s_tag ):
                return o_currentNode

        return None
    
    
    def getAllTaggedNodes(cls,_o_parent, _s_tag):
        """Get all child node with tag _s_tag

        @param _o_parent : parent node
        @param _s_tag : search tag
        """
        
        return _o_parent.getElementsByTagName(_s_tag)


    def getChildrenElementNodes(self,_o_parent):
        """
        Get all children node of _o_parent node
        @param _o_parent : parent node
        """
        
        t_childrenElementNodes = []
        for o_node in _o_parent.childNodes:
            if o_node.nodeType == Node.ELEMENT_NODE:
                t_childrenElementNodes.append(o_node)

        return t_childrenElementNodes
        

    def getNodeValue(self, _o_node):
        """
        Get node value for node _o_node
        @param _o_node : considered node
        """
        
        if ( _o_node.hasChildNodes() ) :
             if ( _o_node.childNodes[0].nodeType == Node.TEXT_NODE ):
                 return _o_node.childNodes[0].nodeValue
             else:
                 return None
        else:
            return None


    def getIndirectNode(self,_o_parent, _s_tag):
        """
        Get first indirect node from _o_parent with tag _s_tag
        @param _o_parent : parent node
        @param _s_tag : search tag
        """
        
        o_node = None

        t_nodeList = _o_parent.getElementsByTagName(_s_tag)
        if ( t_nodeList ):
            o_node = t_nodeList.item(0)

        return o_node
        
        
    def getIndirectNodes(self,_o_parent, _s_tag):
        """
        Get all indirect node from _o_parent with tag _s_tag
        @param _o_parent : parent node
        @param _s_tag : search tag
        """

        t_nodeList = _o_parent.getElementsByTagName(_s_tag)

        return t_nodeList


    def getTagNodeValue(self, _o_node, _s_tag):
        """
        Get value for a node _o_node with tag _s_tag
        @param _o_node : considered node
        @param _s_tag : search tag
        """
        
        t_valueList = _o_node.getElementsByTagName(_s_tag)
        
        if len(t_valueList)>=0:
            return t_valueList.item(0).childNodes[0].nodeValue


    def extractNode(self, _o_node):
        """
        Extract node _o_node
        @param _o_node : extract noeud
        """
        
        if ( _o_node.parentNode != None ):
            _o_node.parentNode.removeChild( _o_node )
            return _o_node

        else:
            return _o_node
    
    
    def removeNode(self, _o_node):
        """
        Remove node _o_node
        @param _o_node : remove node
        """
        
        if ( _o_node.parentNode != None ):
            _o_node.parentNode.removeChild( _o_node )
            _o_node.unlink()
            return True
        else:
            return False
    
    def toprettyxml_fixed(cls, _o_node, _s_encoding='utf-8'):
        """
        Return node at string format
        @param _o_node : considered node
        @param _s_encoding : format encoding
        """
        
        #o_stream = StringIO()
        #PrettyPrint(_o_node, stream=o_stream, encoding=_s_encoding)
        #return o_stream.getvalue()
            
        return _o_node.toxml()

        
    def createElementNode(self, _o_doc, _o_parentNode, _s_tag, _t_attribute, _s_text):
        """
        Create element node
        @param _o_doc : document to create an element node
        @param _o_parentNode : parent node for creating node
        @param _s_tag : tag for creating node
        @param _t_attribute : attribute(s) for creating node
        @param _s_text : text node
        """
        
        o_child = _o_doc.createElement(_s_tag)
        
        for s_key in _t_attribute:
            o_child.setAttribute(s_key, str(_t_attribute[s_key]))
        o_child.appendChild(_o_doc.createTextNode(_s_text))
        _o_parentNode.appendChild(o_child)
        
        return o_child
    
    
    def insertElementNode(self, _o_doc, _o_parentNode, _s_tag, _t_attribute = {}):
        """
        Create element node without text node
        @param _o_doc : document to create an element node
        @param _o_parentNode : parent node for creating node
        @param _s_tag : tag for creating node
        @param _t_attribute : attribute(s) for creating node
        """
        o_node = _o_doc.createElement( _s_tag )

        for s_key in _t_attribute:
            o_node.setAttribute( s_key, str(_t_attribute[s_key]) )

        _o_parentNode.appendChild(o_node)

        return o_node
        
        
    def createTextNode(self, _o_doc, _o_parentNode, _s_tag, _s_text):
        """
        Create text node
        @param _o_doc : document to create a text node
        @param _o_parentNode : parent node of creating node
        @param _s_tag : tag for creating node
        @param _s_text : text node
        """
    
        o_child = _o_doc.createElement(_s_tag)
        o_textNode = _o_doc.createTextNode(_s_text)
        o_child.appendChild(o_textNode)
        _o_parentNode.appendChild(o_child)


    def createNode(self, _o_doc, _o_parentNode, _s_tag):
        """
        Create node without text
        @param _o_doc : document to create node
        @param _o_parentNode : parent node of creating node
        @param _s_tag : tag for creating node
        """
        
        o_child = _o_doc.createElement(_s_tag)
        _o_parentNode.appendChild(o_child)
        
        return o_child
