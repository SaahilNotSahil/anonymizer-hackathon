import os

import pandas as pd
from ruamel.yaml.comments import CommentedMap as OrderedDict
from ruamel.yaml.main import round_trip_dump as yaml_dump
from utils.utils import flatten


def exec_num_anon(df1, df2, num_anon):
    if df1 is not None:
        c1 = df1.columns
    else:
        c1 = None

    if df2 is not None:
        c2 = df2.columns
    else:
        c2 = None

    for op in num_anon.keys():
        if op == 'remove':
            for col in num_anon[op]:
                if c1 is not None and col in c1:
                    df1 = df1.drop(col, axis=1)
                elif c2 is not None and col in c2:
                    df2 = df2.drop(col, axis=1)
        elif op == 'min-max':
            for col in num_anon[op]:
                if c1 is not None and col in c1:
                    df1[col] = \
                        (df1[col] - df1[col].min()) / \
                        (df1[col].max() - df1[col].min())
                elif c2 is not None and col in c2:
                    df2[col] = \
                        (df2[col] - df2[col].min()) / \
                        (df2[col].max() - df2[col].min())
        elif op == 'binarize':
            for col in num_anon[op]:
                if c1 is not None and col in c1:
                    mid = df1[col].mean()
                    df1[col] = df1[col].apply(lambda x: 1 if x > mid else 0)
                elif c2 is not None and col in c2:
                    mid = df2[col].mean()
                    df2[col] = df2[col].apply(lambda x: 1 if x > mid else 0)

    return df1, df2


def exec_pii_anon(df1, df2, pii_anon, linked_col, linked_tag):
    print("Linked col:", linked_col)
    print("Linked tag:", linked_tag)

    if df1 is not None:
        c1 = df1.columns
        pii_anon1 = {}
    else:
        c1 = None
        pii_anon1 = None

    if df2 is not None:
        c2 = df2.columns
        pii_anon2 = {}
    else:
        c2 = None
        pii_anon2 = None

    print(pii_anon)

    for col in pii_anon.keys():
        if col not in flatten(linked_col):
            if c1 is not None and col in c1:
                pii_anon1[col] = pii_anon[col]
            elif c2 is not None and col in c2:
                pii_anon2[col] = pii_anon[col]

    print(pii_anon1)
    print(pii_anon2)

    if pii_anon1:
        pii_yaml1 = OrderedDict({
            'columns': OrderedDict(pii_anon1)
        })

        print(pii_yaml1)
    else:
        pii_yaml1 = None

    if pii_anon2:
        pii_yaml2 = OrderedDict({
            'columns': OrderedDict(pii_anon2)
        })

        print(pii_yaml2)
    else:
        pii_yaml2 = None

    if pii_yaml1:
        with open('pii1.yaml', 'w') as f:
            f.write(yaml_dump(pii_yaml1))

    if pii_yaml2:
        with open('pii2.yaml', 'w') as f:
            f.write(yaml_dump(pii_yaml2))

    if pii_yaml1:
        cmd_status = os.system(
            'vendetta anonymize pii1.yaml <anon_temp1.csv> anon1.csv'
        )

        os.system('rm pii1.yaml')
        os.system('rm anon_temp1.csv')

        if not cmd_status:
            status = "File(s) anonymized successfully"
        else:
            status = "There was an error while anonymizing the file(s)"
    else:
        if df1 is not None:
            df1.to_csv('anon1.csv', index=False)

            status = "File(s) anonymized successfully"

    if pii_yaml2:
        cmd_status = os.system(
            'vendetta anonymize pii2.yaml <anon_temp2.csv> anon2.csv'
        )

        os.system('rm pii2.yaml')
        os.system('rm anon_temp2.csv')

        if not cmd_status:
            status = "File(s) anonymized successfully"
        else:
            status = "There was an error while anonymizing the file(s)"
    else:
        if df2 is not None:
            df2.to_csv('anon2.csv', index=False)

            status = "File(s) anonymized successfully"

    if len(linked_tag) > 0:
        print("Linked tag:", linked_tag)
        print("Linked col:", linked_col)

        print("DF1:", df1.columns)
        print("DF2:", df2.columns)

        for i in range(len(linked_tag)):
            try:
                col1 = list(df1.columns).index(linked_col[i][0])
            except Exception:
                if len((linked_col[i])) > 1:
                    col1 = list(df1.columns).index(linked_col[i][1])

            try:
                col2 = list(df2.columns).index(linked_col[i][0])
            except Exception:
                if len((linked_col[i])) > 1:
                    col2 = list(df2.columns).index(linked_col[i][1])

            cmd_status = os.system(
                f"""python scripts/multi_anonymizer.py -i anon1.csv:{col1}
                anon2.csv:{col2} -t {linked_tag[i]} -d ',' --header-lines 1"""
            )

            if not cmd_status:
                status = "File(s) anonymized successfully"
                df1 = pd.read_csv("anon1.csv_anonymized")
                df2 = pd.read_csv("anon2.csv_anonymized")

                return status, df1, df2

    try:
        df1 = pd.read_csv('anon1.csv')
    except Exception:
        df1 = None

    try:
        df2 = pd.read_csv('anon2.csv')
    except Exception:
        df2 = None

    return status, df1, df2
