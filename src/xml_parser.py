import json
import random
import string
import xml.etree.ElementTree as ET


def get_random_string(length: int) -> str:
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for _ in range(length))
    return result_str


def change_task_type(task: str, child_tag: str) -> str:
    tag_tokens = child_tag.split('}')
    tag_tokens[1] = task
    return '}'.join(tag_tokens)


def replace_task_names(input_path: str, output_path: str, names_dict: dict[str, str],
                       obj_type_dict: dict[str, dict[str, str | dict[str, str]]]) -> None:
    with open("data/bpmn_definitions.json") as f:
        bpmn_definitions = json.load(f)
    tree = ET.parse(input_path)
    root = tree.getroot()
    for child in root:
        if child.tag.split('}')[1] == 'process':
            for process_child in child:
                if process_child.tag.split('}')[1] == 'task':
                    task_name = process_child.attrib['name'].strip()
                    new_name = names_dict[task_name]
                    obj_type = obj_type_dict[new_name]
                    if obj_type in bpmn_definitions['event'].keys():
                        # is Event
                        process_child.tag = change_task_type(bpmn_definitions['event'][obj_type]['event type'],
                                                             process_child.tag)
                        process_child.attrib['name'] = new_name
                        event_definition = bpmn_definitions['event'][obj_type]['event definition']
                        el = ET.Element('}'.join([process_child.tag.split('}')[0], event_definition]))
                        rand_id = get_random_string(6)
                        el.set('id', event_definition + '_' + rand_id)
                        process_child.append(el)
                    elif obj_type in bpmn_definitions['task'].keys():
                        # is Task
                        process_child.tag = change_task_type(bpmn_definitions['task'][obj_type], process_child.tag)
                        process_child.attrib['name'] = new_name
                    else:
                        # assume None event
                        process_child.tag = change_task_type("IntermediateCatchEvent", process_child.tag)
                        process_child.attrib['name'] = new_name

    tree.write(output_path)
