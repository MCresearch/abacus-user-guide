import re

def StandardHtmlParser(FileName, header, footer) -> (dict, dict):
    '''
    # Standard HTML file parser
    This function is used to parse a standard html file, which is a file with tags and attributes.
    The file is parsed into two dictionaries, one is dict_TagConnection, which records the connection between tags, the other is dict_TagState, which records the state of each tag.
    The dict_TagConnection is a dictionary with tag names as keys and a dictionary as values, which has two keys: 'Parent' and 'Children'. The value of 'Parent' is the name of the parent tag, and the value of 'Children' is a list of names of children tags.
    The dict_TagState is a dictionary with tag names as keys and a dictionary as values, which has five keys: 'Data', 'Attributes', 'IsBlock', 'StartLine', 'EndLine', 'DataStartLine', 'DataEndLine'. The value of 'Data' is a list of strings, which are the content of the tag. The value of 'Attributes' is a dictionary with attribute names as keys and attribute values as values. The value of 'IsBlock' is a boolean value, which is True if the tag is a block, and False if the tag is a single tag. The value of 'StartLine' is the line number of the line where the tag is opened. The value of 'EndLine' is the line number of the line where the tag is closed. The value of 'DataStartLine' is the line number of the line where the content of the tag starts. The value of 'DataEndLine' is the line number of the line where the content of the tag ends.
    @param `FileName` is the name of the file to be parsed.
    @param `header` is the string of the header of the file, which is the string before the first tag.
    @param `footer` is the string of the footer of the file, which is the string after the last tag.
    @return `dict_TagConnection` is the dictionary of tag connection, which is a dictionary with tag names as keys and a dictionary as values, which has two keys: 'Parent' and 'Children'. The value of 'Parent' is the name of the parent tag, and the value of 'Children' is a list of names of children tags. `dict_TagsState` is the dictionary of tag state, which is a dictionary with tag names as keys and a dictionary as values, which has five keys: 'Data', 'Attributes', 'IsBlock', 'StartLine', 'EndLine', 'DataStartLine', 'DataEndLine'. The value of 'Data' is a list of strings, which are the content of the tag. The value of 'Attributes' is a dictionary with attribute names as keys and attribute values as values. The value of 'IsBlock' is a boolean value, which is True if the tag is a block, and False if the tag is a single tag. The value of 'StartLine' is the line number of the line where the tag is opened. The value of 'EndLine' is the line number of the line where the tag is closed. The value of 'DataStartLine' is the line number of the line where the content of the tag starts. The value of 'DataEndLine' is the line number of the line where the content of the tag ends.
    '''
    str_line = ''
    int_LineIndex = 0
    str_PresentTag = 'root'
    dict_TagConnection = {'root': {'Parent': 'nan', 'Children': []}}
    dict_TagState = {}
    b_WithinTag = False
    b_WithinBlock = False

    str_WordMakeUp = ''
    str_AttributeName = ''
    str_AttributeValue = ''
    
    with open(FileName, 'r') as f:
        while str_line != header:
            str_line = f.readline()
            str_line = str_line.strip()
            int_LineIndex += 1
        while str_line != footer:
            i = 0
            while i < len(str_line):
                if str_line[i] == '<':
                    if i >= len(str_line) - 1:
                        Warning('Name of tag is not closed in str_line: ' + str_line)
                    else:
                        if str_line[i+1] == '/':
                            # it is closing tag, implies there is a block closed
                            for j in range(i+2, len(str_line)):
                                if str_line[j] == ' ' or str_line[j] == '>':
                                    break
                                else:
                                    if str_line[j] != str_PresentTag[j-i-2]:
                                        Warning('Tag inconsistency in str_line: ' + str_line + ' in str_line: ' + str(int_LineIndex))
                                        quit()
                            i = j - 1 # we will not read the tag name again, but we will read the space or >

                            b_WithinBlock = False
                            b_WithinTag = False
                            dict_TagState[str_PresentTag]['IsBlock'] = True
                            dict_TagState[str_PresentTag]['EndLine'] = int_LineIndex
                            dict_TagState[str_PresentTag]['DataEndLine'] = int_LineIndex                      
                            str_PresentTag = dict_TagConnection[str_PresentTag]['Parent']
                        elif str_line[i+1] == '!' and str_line[i+2] == '-' and str_line[i+3] == '-':
                            # comment, ignore it
                            for j in range(i+2, len(str_line)):
                                if str_line[j] == '>':
                                    break
                            i = j
                        else:
                            # it is opening tag, implies there is a block opened
                            str_TagName = ''
                            for j in range(i+1, len(str_line)):
                                if str_line[j] == ' ' or str_line[j] == '>':
                                    break
                                else:
                                    str_TagName += str_line[j]
                            if str_TagName not in dict_TagConnection:
                                # yes it should... definitely not in dict_TagConnection
                                pass
                            else:
                                # no... this will only happen in a real html file, not in pseudopotential file
                                Warning('Tag ' + str_TagName + ' is not unique in str_line: ' + str_line+ ' in str_line: ' + str(int_LineIndex)+', will name it as '+str_TagName+'_'+str(int_LineIndex))
                                str_TagName = str_TagName + '_' + str(int_LineIndex)

                            dict_TagConnection[str_TagName] = {'Parent': str_PresentTag, 'Children': []}
                            dict_TagConnection[str_PresentTag]['Children'].append(str_TagName)
                            str_PresentTag = str_TagName
                            dict_TagState[str_PresentTag] = {}
                            dict_TagState[str_PresentTag]['Data'] = []
                            dict_TagState[str_PresentTag]['Attributes'] = {}
                            dict_TagState[str_PresentTag]['IsBlock'] = False
                            dict_TagState[str_PresentTag]['StartLine'] = int_LineIndex
                            dict_TagState[str_PresentTag]['EndLine'] = -1
                            dict_TagState[str_PresentTag]['DataStartLine'] = int_LineIndex
                            dict_TagState[str_PresentTag]['DataEndLine'] = -1
                            i = j - 1 # we will not read the tag name again, but we will read the space or >
                            
                            b_WithinTag = True
                            b_WithinBlock = False
                elif str_line[i] == '>':
                    if i <= 0:
                        Warning('Name of tag is not opened in str_line: ' + str_line)
                    else:
                        if str_line[i-1] == '/':
                            # it is a single tag closed here
                            b_WithinTag = False
                            dict_TagState[str_PresentTag]['IsBlock'] = False
                            dict_TagState[str_PresentTag]['EndLine'] = int_LineIndex
                            dict_TagState[str_PresentTag]['DataEndLine'] = int_LineIndex
                            str_PresentTag = dict_TagConnection[str_PresentTag]['Parent']
                        else:
                            # it is a block opened here
                            b_WithinTag = False
                            b_WithinBlock = True
                else:
                    # it is content of tag
                    if b_WithinTag:
                        # it is content of tag
                        if (str_line[i] == ' ' and str_line[i+1] != ' ' and str_line[i+1] != '>') or i == 0:
                            # it is a space, implies a new attribute is coming
                            if i == 0:
                                i = -1
                            for j in range(i+1, len(str_line)):
                                if str_line[j] == '=':
                                    break
                                else:
                                    str_AttributeName += str_line[j]
                            i = j
                            if str_line[i+1] != '"':
                                Warning('Attribute value is not started by " in str_line: ' + str_line)
                            else:
                                for j in range(i+2, len(str_line)):
                                    if str_line[j] == '"':
                                        break
                                    else:
                                        str_AttributeValue += str_line[j]
                                i = j
                                str_AttributeValue = str_AttributeValue.strip()
                                # this regular expression is written by Chat-AISI
                                if re.match(pattern = r'^[+-]?\d+(\.\d+)?([eE][+-]?\d+)?$', string = str_AttributeValue):
                                    str_AttributeValue = float(str_AttributeValue)
                                elif str_AttributeValue == 'F':
                                    str_AttributeValue = False
                                elif str_AttributeValue == 'T':
                                    str_AttributeValue = True
                                else:
                                    try:
                                        str_AttributeValue = int(str_AttributeValue)
                                    except ValueError:
                                        str_AttributeValue = str_AttributeValue
                                dict_TagState[str_PresentTag]['Attributes'][str_AttributeName] = str_AttributeValue
                                str_AttributeName = ''
                                str_AttributeValue = ''
                        else:
                            # I cannot imagine what will happen here
                            pass
                    elif b_WithinBlock:
                        # it is content of block
                        str_WordMakeUp = ''
                        for j in range(i, len(str_line)):
                            if str_line[j] == ' ':
                                break
                            else:
                                str_WordMakeUp += str_line[j]
                        i = j
                        if str_WordMakeUp != '':
                            try:
                                dict_TagState[str_PresentTag]['Data'].append(float(str_WordMakeUp))
                            except ValueError:
                                dict_TagState[str_PresentTag]['Data'].append(str_WordMakeUp)
                        str_WordMakeUp = ''
                    else:
                        # it is content of nothing
                        pass
                i += 1
            str_line = f.readline()
            str_line = str_line.strip()
            int_LineIndex += 1

    return dict_TagConnection, dict_TagState

if __name__ == '__main__':

    b_DrawTree = False
    b_DrawVloc = True

    import json
    import os
    Directory = 'D:/Documents/GitHub/abacus-develop/tests/PP_ORB/'
    FileName = 'Al_ONCV_PBE-1.0.upf'
    header = '<UPF version="2.0.1">'
    footer = '</UPF>'

    DataJsonFileName = FileName.replace('.upf', '.json')
    ConectionJsonFileName = FileName.replace('.upf', '_Connection.json')
    FileName = Directory + FileName

    if os.path.exists(Directory + DataJsonFileName) and os.path.exists(Directory + ConectionJsonFileName):
        with open(Directory + DataJsonFileName, 'r') as f:
            dict_TagState = json.load(f)
        with open(Directory + ConectionJsonFileName, 'r') as f:
            dict_TagConnection = json.load(f)
    else:
        dict_TagConnection, dict_TagState = StandardHtmlParser(FileName, header, footer)
        with open(Directory + DataJsonFileName, 'w') as f:
            json.dump(dict_TagState, f, indent=4)
        with open(Directory + ConectionJsonFileName, 'w') as f:
            json.dump(dict_TagConnection, f, indent=4)

    # actually I am not familar with this function at all, it is completed by Chat-AISI and Github.copilot
    if b_DrawTree:
        try:
            import networkx as nx
            import matplotlib.pyplot as plt
            # Load the JSON file
            data = dict_TagConnection
            # Create a directed graph
            G = nx.DiGraph()
            # Add edges to the graph
            for key, value in data.items():
                for child in value['Children']:
                    G.add_edge(key, child)
            # Plot the graph
            pos = nx.spring_layout(G)
            # sort the nodes by degree
            nodelist, node_sizes = zip(*sorted(G.degree, key=lambda x: x[1], reverse=True))
            # draw the graph
            nx.draw_networkx(G, pos, with_labels=True, node_size=1000, node_color='lightblue', alpha=0.9, font_size=8)
            plt.axis('off')
            plt.show()
        except ModuleNotFoundError:
            Warning('anytree is not installed, will not draw the tree')
            b_DrawTree = False
    if b_DrawVloc:
        try:
            import numpy as np
            import matplotlib.pyplot as plt
            r = dict_TagState['PP_R']['Data']
            VLocal = dict_TagState['PP_LOCAL']['Data']
            r = np.array(r)
            VLocal = np.array(VLocal)
            VCoulomb = -dict_TagState['PP_HEADER']['Attributes']['z_valence']/r*2
            # set font size
            plt.rcParams.update({'font.size': 16})
            # set figure size
            plt.figure(figsize=(8, 6))
            plt.plot(r, VLocal, '-', label='V_Local')
            plt.plot(r, VCoulomb, '--', label='V_Coulomb')
            plt.xlabel('r (a.u.)')
            plt.ylabel('V (a.u.)')
            plt.legend()
            plt.xlim(0, max(r))
            plt.ylim(-50, 1)
            plt.show()
        except ModuleNotFoundError:
            Warning('numpy or matplotlib is not installed, will not draw the vloc')
            b_DrawVloc = False