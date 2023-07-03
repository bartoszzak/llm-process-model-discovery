import json
import logging
import re

import openai
import pandas as pd

from src import prompt_generation

logger = logging.getLogger(__name__)


def rename_bpmn_objects(object_names: str) -> dict[str, str]:
    prompt = prompt_generation.generate_rename_objects_prompt(object_names)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"{prompt}"}],
        temperature=0,
    )
    response_message = response["choices"][0]["message"]["content"]
    response_message = response_message.replace('\'', '\"')
    logger.debug(response_message)

    renamed_elements = json.loads(response_message)

    return renamed_elements


def distinguish_tasks_events(object_names: str) -> dict[str, str]:
    prompt = prompt_generation.generate_task_events_prompt(object_names)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"{prompt}"}],
        temperature=0,
    )

    response_message = response["choices"][0]["message"]["content"]
    response_message = response_message.replace('\'', '\"')
    logger.debug(response_message)
    extracted_dicts = __extract_dicts_from_str(response_message.replace('\'', '\"'))
    if len(extracted_dicts) > 1:
        logger.warning("More than 1 dict found in output! Taking the first one.")
    classified_objects = extracted_dicts[0]

    return classified_objects


def determine_object_types(bpmn_objects: list[str], obj_name: str) -> dict[str, str]:
    if obj_name == 'task':
        prompt = prompt_generation.generate_task_types_prompt(bpmn_objects)
    elif obj_name == 'event':
        prompt = prompt_generation.generate_event_types_prompt(bpmn_objects)
    else:
        raise ValueError("Wrong object name.")

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"{prompt}"}],
        temperature=0,
    )

    response_message = response["choices"][0]["message"]["content"]
    response_message = response_message.replace('\'', '\"')
    logger.debug(response_message)
    extracted_dicts = __extract_dicts_from_str(response_message.replace('\'', '\"'))
    if len(extracted_dicts) > 1:
        logger.warning("More than 1 dict found in output! Taking the first one.")
    object_types = extracted_dicts[0]

    return object_types


def __extract_dicts_from_str(s: str) -> list:
    results = []
    s_ = ' '.join(s.split('\n')).strip()
    exp = re.compile(r'(\{[^{}]+})')
    for i in exp.findall(s_):
        try:
            results.append(json.loads(i))
        except json.JSONDecodeError as e:
            logger.error(e)
    return results
