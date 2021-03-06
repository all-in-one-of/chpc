# -*- coding: utf-8 -*-

"""An user interface that allows user to directly change Houdini parameter callback script.
"""

import sys, os
from time import strftime, localtime

import hou

global gDIALOG

UI_TITLE = 'Change Houdini Parameter Callback Script'
UI_FILE = '%s.ui' % os.path.splitext(__file__)[0]
LANG_TO_INDEX = {'Hscript':0, 'Python':1}
INDEX_TO_HOULANG = {0:hou.scriptLanguage.Hscript, 1:hou.scriptLanguage.Python}


def start():
    '''Mian Function.'''

    # Parse .ui file.
    global gDIALOG
    gDIALOG = hou.ui.createDialog(UI_FILE)

    # Setup gadget callback functions.
    gDIALOG.addCallback('btn_getParmCallback.val', cb_btn_getParmCallback)
    gDIALOG.addCallback('btn_change.val', cb_btn_change)
    
    # Setup gadget values.
    cb_btn_getParmCallback()

    # Show dialog window.
    gDIALOG.setValue('dialog.val', True)

def cb_btn_change():
    '''Callback function called by "Change" button, and "start" function for initialization.'''
    
    parmPath = gDIALOG.value('strField_tarParm.val')
    parm = hou.parm(parmPath)
    if parm:
        script = gDIALOG.value('strField_newScript.val')
        houLang = INDEX_TO_HOULANG[gDIALOG.value('menu_lang.val')]
        
        if script:
            # Edit parameter template.
            templ = parm.parmTemplate()
            templ.setScriptCallback(script)
            templ.setScriptCallbackLanguage(houLang)

            # Replace parameter by edited template.
            result = parm.node().replaceSpareParmTuple(parm.name(), templ)
            if result:
                print ''
                print '[chpc - cb_btn_change] Callback information has been updated!'
                print '[chpc log] %s %s callback script: %s | %s' % (strftime('%H:%M:%S', localtime()), parmPath, houLang.name(), script)
            else:
                print '[chpc - cb_btn_change] Warning! Can not change callback information!'
        else:
            hou.ui.displayMessage('Empty script, skip writing!', title=UI_TITLE)
    else:
        hou.ui.displayMessage('Invalid parameter path!', title=UI_TITLE)

def cb_btn_getParmCallback():
    '''Callback function called by "Get Parameter Callback info" button.'''
    
    # Check if the parameter path is valid or not.
    path = getParmPath()
    if path:
        # Check if target parameter is a valid spare parameter of its node.
        parm = hou.parm(path)
        if parm in parm.node().spareParms():
            # Target parameter string field.
            gDIALOG.enableValue('strField_tarParm.val', True)
            gDIALOG.setValue('strField_tarParm.val', path)
            #gDIALOG.enableValue('strField_tarParm.val', False)

            # Old script string field, and language menu item.
            script, lang = getCallbackInfo(path)
            gDIALOG.setValue('strField_oldScript.val', script)
            gDIALOG.setValue('menu_lang.val', LANG_TO_INDEX[lang])
        else:
            hou.ui.displayMessage('This parameter is not allow to edit!', title=UI_TITLE)
    else:
        hou.ui.displayMessage('No parameter copied!', title=UI_TITLE)

    gDIALOG.enableValue('strField_tarParm.val', False)

def getParmPath():
    '''Function used to get parameter info by checking internal parameter clipboard.'''
    
    contents = hou.parmClipboardContents()
    if contents:
        return contents[0].get('path')
    
    return None

def getCallbackInfo(parmPath):
    '''Function used to get callback information, such as script and language.'''

    parm = hou.parm(parmPath)
    parmTemp = parm.parmTemplate()
    
    script = parmTemp.scriptCallback()
    language = parmTemp.scriptCallbackLanguage().name()
    
    return (script, language)
