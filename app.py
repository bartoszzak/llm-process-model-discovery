import argparse
import logging
import os
import warnings

import openai
import pm4py
from dotenv import load_dotenv

from src import xml_parser
from src.log_analysis import rename_bpmn_objects, determine_object_types, distinguish_tasks_events

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def parse_arguments():
    parser = argparse.ArgumentParser(description='Process logs and generate BPMN model')
    parser.add_argument('input_file', help='Path to the input .xes file')
    parser.add_argument('output_file', help='Path to the output BPMN file')
    return parser.parse_args()


if __name__ == '__main__':
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

    args = parse_arguments()
    logs_path = args.input_file
    enhanced_bpmn_path = args.output_file

    # read logs from xes
    logger.info("Reading .xes logs...")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        logs = pm4py.read_xes(os.path.abspath(logs_path))

    # generate initial process model
    logger.info("Discovering model...")
    process_model = pm4py.discover_bpmn_inductive(logs)
    pm4py.write_bpmn(process_model, 'data/model')
    logger.info("Model discovery complete")

    # rename objects
    logger.info("Renaming objects...")
    unique_obj_names = logs['concept:name'].unique()
    renamed = rename_bpmn_objects(unique_obj_names)
    new_names = list(renamed.values())

    # classify objects
    logger.info("Classifying objects...")
    classified_objects = distinguish_tasks_events(str(new_names))
    tasks = [obj for obj, obj_type in classified_objects.items() if obj_type.lower() == 'task']
    events = [obj for obj, obj_type in classified_objects.items() if obj_type.lower() == 'event']
    task_types = determine_object_types(tasks, 'task')
    event_types = determine_object_types(events, 'event')

    # convert to actual BPMN format names
    object_types = {**task_types, **event_types}
    logger.info("Replacing objects...")
    xml_parser.replace_task_names('data/model.bpmn', enhanced_bpmn_path, renamed, object_types)
    logger.info(f"Enhanced model saved to {os.path.abspath(enhanced_bpmn_path)}")
