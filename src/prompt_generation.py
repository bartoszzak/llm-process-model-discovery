import json


def generate_rename_objects_prompt(names: list or str) -> str:
    return f"""Given the names of tasks/events in a BPMN model:\n
                {names}\n
                decide if each of them has a proper name in English and if it does not, rename it.
                return only a python dict containing \"name: new_name\" and no other comments."""


def generate_task_events_prompt(logs: list or str) -> str:
    return f"""Determine whether given BPMN task/event is a task or an event. The list logs containing unique task/event names is below:\n
                {logs}\n
                return only a python dict containing \"name: task/event\" and no other output."""


def generate_types_prompt(tasks_and_events: dict or str) -> str:
    task_types = ''

    with open("bpmn_types.json") as f:
        bpmn_types = json.load(f)
    tasks = bpmn_types['task']
    events = bpmn_types['event']

    for task in tasks.keys():
        task_types += f"{tasks[task]['name']}-{tasks[task]['description']}\n"

    task_types = task_types[:-1]

    return f"""Given that a BPMN model has tasks and events given below:\n
                {tasks_and_events}\n
                determine task types, knowing that the task types are:\n{task_types}.\n
                determine event types, knowing that the event types are {events}.\n
                return only a python dict containing \"name: type\" and no other output."""


def generate_convert_to_bpmn_type_names_prompt(types: dict or str) -> str:
    return f"""Given this dict containing \"object_name: type\":\n
                {types}\n
                convert the type names to actual names used in .bpmn format files.
                return only a python dict containing \"object_name: type\" and no other comments."""
