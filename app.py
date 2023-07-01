import os
import re
import json
from dotenv import load_dotenv
import logging

import pandas as pd
import openai
import pm4py

from src.log_analysis import rename_bpmn_objects, determine_object_types, distinguish_tasks_events, \
    convert_to_bpmn_format
from src import xml_parser

if __name__ == '__main__':
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # read logs from xes
    # logs = pm4py.read_xes('data/logs/ApacheCommons-Crypto-1.0.0-StreamCbcNopad-splitted.xes')
    # logs.to_pickle('data/pickled_logs/ApacheCommons-Crypto-1.0.0-StreamCbcNopad-splitted.pickle')
    logs: pd.DataFrame = pd.read_pickle('data/pickled_logs/BPI_Challenge_2012.pickle')

    # generate initial process model
    process_model = pm4py.discover_bpmn_inductive(logs)
    pm4py.write_bpmn(process_model, 'data/model')

    # rename objects
    unique_obj_names = logs['concept:name'].unique()
    renamed = rename_bpmn_objects(unique_obj_names)
    new_names = list(renamed.values())

    # classify objects
    classified_objects = distinguish_tasks_events(str(new_names))
    print(classified_objects)
    object_types = determine_object_types(str(classified_objects))
    print(object_types)

    # convert to actual BPMN format names
    bpmn_objects = convert_to_bpmn_format(str(object_types))
    print(bpmn_objects)

    enhanced_bpmn_path = 'data/model_changed.bpmn'
    xml_parser.replace_task_names('data/model.bpmn', enhanced_bpmn_path, renamed, bpmn_objects)
    layout_path = 'data/model_layout.bpmn'
    layout_bpmn = pm4py.objects.bpmn.layout.layouter.apply(pm4py.read_bpmn(enhanced_bpmn_path))
    pm4py.write_bpmn(layout_bpmn, 'data/model_layout.bpmn')

