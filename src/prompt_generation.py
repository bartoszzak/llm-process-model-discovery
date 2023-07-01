import json
import inspect


def generate_rename_objects_prompt(names: list or str) -> str:
    prompt = f"""Given the names of tasks/events in a BPMN model:
                {names}
                decide if each of them has an understandable name in English and if it does not, extend it.
                give me only a python dict containing \"name: new_name\" and no other comments."""
    return inspect.cleandoc(prompt)


def generate_task_events_prompt(logs: list or str) -> str:
    prompt = f"""Decide whether given BPMN task/event is a task or an event.\
                The list logs containing unique task/event names is below:
                {logs}
                return only one python dict containing \"name: event/task\" and no other output."""
    return inspect.cleandoc(prompt)


def generate_types_prompt(tasks_and_events: dict or str) -> str:
    task_types = ''
    event_types = ''

    with open("data/bpmn_types.json") as f:
        bpmn_types = json.load(f)
    tasks = bpmn_types['task']
    events = bpmn_types['event']

    for task in tasks.keys():
        task_types += f"{tasks[task]['name']}-{tasks[task]['description']}\n"

    task_types = task_types[:-1]

    for event in events.keys():
        event_types += f"{events[event]['name']}-{events[event]['description']}\n"

    task_types = task_types[:-1]
    event_types = event_types[:-1]

    prompt = f"""Given that a BPMN model has tasks and events given below:
                {tasks_and_events}
                determine task types, knowing that the task types are:
                {task_types}.
                Determine event types and decide if they are \"catch\" or \"throw\", knowing that the event types are:
                {event_types}.
                All events are intermediate, so consider it while naming them.
                return only a python dict containing \"name: type\" and no other output."""
    return inspect.cleandoc(prompt)

def generate_types_prompt_no_description(tasks_and_events: dict or str) -> str:
    task_types = ''
    event_types = ''

    with open("data/bpmn_types.json") as f:
        bpmn_types = json.load(f)
    tasks = bpmn_types['task']
    events = bpmn_types['event']

    for task in tasks.keys():
        task_types += f"{tasks[task]['name']}\n"

    task_types = task_types[:-1]

    for event in events.keys():
        event_types += f"{events[event]['name']}\n"

    task_types = task_types[:-1]
    event_types = event_types[:-1]

    prompt = f"""Given that a BPMN model has tasks and events given below:
                    {tasks_and_events}
                    determine task types, knowing that the task types are:
                    {task_types}.
                    Determine event types and decide if they are \"catch\" or \"throw\", knowing that the event types are:
                    {event_types}.
                    All events are intermediate, so consider it while naming them.
                    return only a python dict containing \"name: type\" and no other output."""
    return inspect.cleandoc(prompt)


def generate_convert_to_bpmn_type_names_prompt(types: dict or str) -> str:
    return f"""Given this dict containing \"object_name: type\":\n
                {types}\n
                change the type names to actual names used in .bpmn format files without the \"bpmn:\" prefix.
                give me only a python dict containing \"object_name: type\" and no other comments."""
