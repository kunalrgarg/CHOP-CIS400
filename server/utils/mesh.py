import pandas as pd
import pandas.io.formats.excel
import csv
import os
import records

def main():
    print(os.getcwd())
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
    print('writing out')
    mesh_df.to_csv('../template/2019MeshFull.csv', index=False)
    print('done')


if __name__ == '__main__':
    main()