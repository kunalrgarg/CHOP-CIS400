import pandas as pd
import pandas.io.formats.excel
import csv
import json
import os
import records

def clean_entry(entry):
    if 'number' in entry:
        del entry['number']
    if 'children' in entry:
        for child in entry['children']:
            clean_entry(child)


def write_mesh_tree_json():
    root = {'name': 'MeSH Tree', 'number': '', 'children': []}
    root['children'] = [{'name': 'Anatomy', 'number': 'A', 'children': []},
                        {'name': 'Organisms', 'number': 'B', 'children': []},
                        {'name': 'Diseases', 'number': 'C', 'children': []},
                        {'name': 'Chemicals and Drugs', 'number': 'D', 'children': []},
                        {'name': 'Analytical, Diagnostic and Therapeutic Techniques, and Equipment', 'number': 'E', 'children': []},
                        {'name': 'Psychiatry and Psychology', 'number': 'F', 'children': []},
                        {'name': 'Phenomena and Processes', 'number': 'G', 'children': []},
                        {'name': 'Disciplines and Occupations', 'number': 'H', 'children': []},
                        {'name': 'Anthropology, Education, Sociology, and Social Phenomena', 'number': 'I', 'children': []},
                        {'name': 'Technology, Industry, and Agriculture', 'number': 'J', 'children': []},
                        {'name': 'Humanities', 'number': 'K', 'children': []},
                        {'name': 'Information Science', 'number': 'L', 'children': []},
                        {'name': 'Named Groups', 'number': 'M', 'children': []},
                        {'name': 'Health Care', 'number': 'N', 'children': []},
                        {'name': 'Publication Characteristics', 'number': 'V', 'children': []},
                        {'name': 'Geographicals', 'number': 'Z', 'children': []}]
    with open('../template/2019MeshFull.csv') as mesh_tree_csv:
        csv_reader = csv.reader(mesh_tree_csv, delimiter=',')
        for row in csv_reader:
            mesh = records.get_mesh(row)
            for nums in mesh.numbers:
                if nums == '':
                     continue
                parent = None
                numbers = nums.split('.')
                for topLevelMesh in root['children']:
                    if numbers[0][0].upper() == topLevelMesh['number']:
                        parent = topLevelMesh
                        break
                if parent == None:
                    print(numbers[0][0])
                for number in numbers:
                    found = False
                    if 'children' in parent:
                        for child in parent['children']:
                            if number == child['number']:
                                parent = child
                                found = True
                                break
                    if not found:
                        child = {'name': mesh.term, 'number': number}
                        try:
                            parent['children'].append(child)
                        except KeyError:
                            parent['children'] = [child]
                        break
    # remove number attr from each entry
    clean_entry(root)
    with open('../template/2019MeshTree.json', 'w') as outfile:
        json.dump(root, outfile)
    
    for top_level_mesh in root['children']:
        with open('../template/mesh_subtrees/{0}.json'.format(top_level_mesh['name']), 'w') as outfile:  
            json.dump(top_level_mesh['children'], outfile)


def main():
    mesh_df = pd.DataFrame(columns=['numbers','term','entries'])
    mesh = None
    with open('../template/d2019.txt') as mesh_record:
        for line in mesh_record:
            tokens = line.split(' ')
            key = tokens[0]
            if key == 'MH':         # new mesh term
                if mesh is not None:
                    row = pd.DataFrame([[';'.join(mesh.numbers), mesh.term, ';'.join(mesh.entries)]], columns=['numbers','term','entries'])
                    mesh_df = mesh_df.append(row, ignore_index=True)
                mesh = records.Mesh()
                mesh.term = ' '.join(tokens[2:])
                mesh.term = mesh.term.replace('\n', '').strip()
            elif key == 'ENTRY':    # new entry
                entry = ' '.join(tokens[2:])
                entry = entry.split('|')[0].replace('\n','').strip()
                mesh.entries.append(entry)
            elif tokens[0] == 'PRINT' and tokens[1] == 'ENTRY':
                entry = ' '.join(tokens[3:])
                entry = entry.split('|')[0].replace('\n','').strip()
                mesh.entries.append(entry)
            elif key == 'MN':       # mesh number
                mesh.numbers.append(tokens[2].replace('\n','').strip())
    mesh_df.to_csv('../template/2019MeshFull.csv', index=False)
    write_mesh_tree_json()


if __name__ == '__main__':
    main()