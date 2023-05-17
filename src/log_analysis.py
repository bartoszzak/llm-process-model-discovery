import os
import re
import json
from dotenv import load_dotenv

import pandas as pd
import openai
import pm4py

import prompt_generation
import xml_parser


def rename_bpmn_objects(object_names: str) -> dict:
    prompt = prompt_generation.generate_rename_objects_prompt(object_names)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"{prompt}"}],
        temperature=0,
    )
    renamed_elements = json.loads(response["choices"][0]["message"]["content"].replace('\'', '\"'))

    return renamed_elements


def distinguish_tasks_events(object_names: str) -> dict:
    prompt = prompt_generation.generate_task_events_prompt(object_names)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"{prompt}"}],
        temperature=0,
    )

    classified_objects = json.loads(response["choices"][0]["message"]["content"].replace('\'', '\"'))

    return classified_objects


def determine_object_types(bpmn_objects: str) -> dict:
    prompt = prompt_generation.generate_types_prompt(bpmn_objects)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"{prompt}"}],
        temperature=0,
    )

    object_types = json.loads(response["choices"][0]["message"]["content"].replace('\'', '\"'))

    return object_types


def convert_to_bpmn_format(object_types: str) -> dict:
    prompt = prompt_generation.generate_convert_to_bpmn_type_names_prompt(object_types)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"{prompt}"}],
        temperature=0,
    )

    bpmn_object_types = json.loads(response["choices"][0]["message"]["content"].replace('\'', '\"'))

    return bpmn_object_types


def __get_unique_logs_by_name(logs: pd.DataFrame) -> str:
    """
    Get logs with unique concept:name fields.
    :param logs: pandas DataFrame of logs converted from .xes format.
    :type logs: pandas.DataFrame
    :return: list of logs with unique names as str objects
    :rtype: list[str]
    """

    unique_logs_str = ''
    unique_logs: pd.DataFrame = logs.drop_duplicates('concept:name').reset_index()
    for _, log in unique_logs.iterrows():
        unique_logs_str += re.sub(' +', '  ', f'{str(log.values)}')  # remove multiple spaces and add to str

    return unique_logs_str


if __name__ == '__main__':
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

    #logs = pm4py.read_xes('../data/logs/BPI_Challenge 2017.xes')
    #logs.to_pickle('../data/pickled_logs/BPI_Challenge 2017.pickle')
    logs: pd.DataFrame = pd.read_pickle('../data/pickled_logs/BPI_Challenge 2017.pickle')
    process_model = pm4py.discover_bpmn_inductive(logs)
    pm4py.write_bpmn(process_model, '../data/model')
    unique_obj_names = logs['concept:name'].unique()
    renamed = rename_bpmn_objects(unique_obj_names)
    new_names = list(renamed.values())
    classified_objects = distinguish_tasks_events(str(new_names))
    print(classified_objects)
    object_types = determine_object_types(str(classified_objects))
    print(object_types)
    bpmn_objects = convert_to_bpmn_format(str(object_types))
    print(bpmn_objects)
    xml_parser.replace_task_names('../data/model.bpmn', renamed, bpmn_objects)
