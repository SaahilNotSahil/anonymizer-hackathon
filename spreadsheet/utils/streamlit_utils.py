import pandas as pd
import streamlit as st
from utils.anon_utils import exec_num_anon, exec_pii_anon
from utils.openai_utils import (chat_api, get_context, get_prompt,
                                parse_response_json)


@st.cache_data
def handle_files(files):
    file_names = []

    for file in files:
        file_name = file.name.strip().replace(" ", "_")
        file.seek(0)
        df = pd.read_csv(file)
        df.to_csv(f"{file_name}", index=False)

        st.write(df)

        file_names.append(file_name)

    context1 = get_context(f"{file_names[0]}")
    prompt1 = get_prompt(context1)
    response1 = chat_api(prompt1)

    linked_col = []

    if len(file_names) == 2:
        context2 = get_context(f"{file_names[1]}")
        prompt2 = get_prompt(context2)
        response2 = chat_api(prompt2)

        col1 = context1.keys()
        col2 = context2.keys()
        col = list(set(col1) | set(col2))  # all the cols

        num_col = []
        pii_col = []

        print("Response 1:", response1)
        print("Response 2:", response2)

        for c in col:
            if c in col1:
                if response1[c]['numerical'].lower() == 'yes':
                    num_col.append(c)
                else:
                    pii_col.append(c)
            elif c in col2:
                if response2[c]['numerical'].lower() == 'yes':
                    num_col.append(c)
                else:
                    pii_col.append(c)

        response = {}
        num_rep = {}

        num_rep['numerical'] = "Yes"
        num_rep['category'] = "None"

        for c in num_col:
            response[c] = num_rep

        linked_tag = []
        pii_top_down = {}

        tags = [
            'name',
            'last_name',
            'first_name',
            'email',
            'phone_number',
            'zip code',
            'street',
            'street_address',
            'city',
            'word',
            'sentence'
        ]

        for tag in tags:
            pii_top_down[tag] = []

        for c in pii_col:
            if c in col1:
                if response1[c]['category'] != 'None':
                    pii_top_down[response1[c]['category']].append(c)
            else:
                if response2[c]['category'] != 'None':
                    pii_top_down[response2[c]['category']].append(c)

        print(pii_top_down)

        for key in pii_top_down.keys():
            if len(pii_top_down[key]) == 0:
                continue

            if len(pii_top_down[key]) > 1:
                linked_col.append(pii_top_down[key])
                linked_tag.append(key)

            response[pii_top_down[key][0]] = {
                'numerical': 'No',
                'category': key
            }

        response = parse_response_json(response)
    else:
        response = parse_response_json(response1)

    return response, file_names, linked_col, linked_tag


def handle_selection(key):
    print(st.session_state[key])


def handle_submit(data, file_names, linked_col, linked_tag):
    st.session_state.display_modified = True

    if not data:
        return

    for d in data:
        d.append(st.session_state[f"{d[0]}_selectbox"])

    print("Data:", data)

    num_anon = {}

    num_anon['remove'] = []
    num_anon['min-max'] = []
    num_anon['binarize'] = []

    pii_anon = {}

    for option in data:
        if option[1] is True:
            if option[3].lower() == 'remove':
                num_anon['remove'].append(option[0])
            elif option[3].lower() == 'min-max':
                num_anon['min-max'].append(option[0])
            elif option[3].lower() == 'binarize':
                num_anon['binarize'].append(option[0])
        else:
            if option[3].lower() == 'yes':
                pii_anon[option[0]] = option[2]

    if st.session_state.display_modified:
        if len(file_names) == 2:
            df1, df2 = pd.read_csv(file_names[0]), pd.read_csv(file_names[1])

            print(df1.head())
            print(df2.head())

            num_anon_df1, num_anon_df2 = exec_num_anon(df1, df2, num_anon)

            num_anon_df1.to_csv('anon_temp1.csv', index=False)
            num_anon_df2.to_csv('anon_temp2.csv', index=False)

            pii_anon_status, anon_df1, anon_df2 = exec_pii_anon(
                num_anon_df1, num_anon_df2, pii_anon, linked_col, linked_tag
            )

            st.info(pii_anon_status)

            st.write(anon_df1)
            st.write(anon_df2)
        else:
            df1 = pd.read_csv(file_names[0])

            print(df1.head())

            num_anon_df1, _ = exec_num_anon(df1, None, num_anon)

            num_anon_df1.to_csv('anon_temp1.csv', index=False)

            pii_anon_status, anon_df1, _ = exec_pii_anon(
                num_anon_df1, None, pii_anon, linked_col, linked_tag
            )

            st.info(pii_anon_status)

            st.write(anon_df1)
