import argparse
import os

import openai
import pandas as pd
import pm4py
from dotenv import load_dotenv

from src import xml_parser
from src.log_analysis import rename_bpmn_objects, determine_object_types, distinguish_tasks_events

def parse_arguments():
    parser = argparse.ArgumentParser(description='Process logs and generate BPMN model')
    parser.add_argument('output_file', help='Path to the output BPMN file')
    return parser.parse_args()


if __name__ == '__main__':
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

    args = parse_arguments()
    enhanced_bpmn_path = args.output_file

    # read logs from xes
    logs = pm4py.read_xes('data/logs/BPI_Challenge 2017.xes')
    logs.to_pickle('data/pickled_logs/BPI_Challenge 2017.pickle')
    logs: pd.DataFrame = pd.read_pickle('data/pickled_logs/log.pickle')

    # generate initial process model
    process_model = pm4py.discover_bpmn_inductive(logs)
    pm4py.write_bpmn(process_model, 'data/model')
    process_model = pm4py.read_bpmn('data/model.bpmn')

    # rename objects
    unique_obj_names = logs['concept:name'].unique()
    renamed = rename_bpmn_objects(unique_obj_names)
    new_names = list(renamed.values())

    # classify objects
    classified_objects = distinguish_tasks_events(str(new_names))
    tasks = [obj for obj, obj_type in classified_objects.items() if obj_type.lower() == 'task']
    events = [obj for obj, obj_type in classified_objects.items() if obj_type.lower() == 'event']
    task_types = determine_object_types(tasks, 'task')
    event_types = determine_object_types(events, 'event')

    # convert to actual BPMN format names
    object_types = {**task_types, **event_types}

    xml_parser.replace_task_names('data/model.bpmn', enhanced_bpmn_path, renamed, object_types)
