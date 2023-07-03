import json
import inspect


def generate_rename_objects_prompt(names: list | str) -> str:
    prompt = f"""Given the names of tasks/events in a BPMN model:
                {names}
                decide if each of them has an understandable name in English and if it does not,\
                extend it or add spaces.
                give me only a python dict containing \"name: new_name\" and no other comments."""
    return inspect.cleandoc(prompt)


def generate_task_events_prompt(logs: list | str) -> str:
    prompt = f"""Decide whether given BPMN task/event is a task or an event.\
                The list containing unique task/event names is below:
                {logs}
                return only one python dict containing \"name: event/task\" and no other output."""
    return inspect.cleandoc(prompt)


def generate_task_types_prompt(tasks: dict | str) -> str:
    task_types = ''

    with open("data/bpmn_types.json") as f:
        bpmn_types = json.load(f)
    possible_tasks = bpmn_types['task']

    for task in possible_tasks.keys():
        task_types += f"{possible_tasks[task]['name']}-{possible_tasks[task]['description']}\n"

    task_types = task_types[:-1]

    prompt = f"""Given that a BPMN model has tasks given below:
                {tasks}
                determine task types, knowing that the task types are:
                {task_types}.
                return only one python dict containing \"name: type\" and no other output.
                Use exact provided names."""
    return inspect.cleandoc(prompt)


def generate_event_types_prompt(events: dict | str) -> str:
    event_types = ''

    with open("data/bpmn_types.json") as f:
        bpmn_types = json.load(f)
    possible_events = bpmn_types['event']

    for event in possible_events.keys():
        event_types += f"{possible_events[event]['name']}-{possible_events[event]['description']}\n"

    event_types = event_types[:-1]

    prompt = f"""Given that a BPMN model has events withe names given below:
                    {events}
                    Guess event types, knowing that the event types are:
                    {event_types}.
                    Try not to use the None event type if possible.
                    return only one python dict containing \"name: type\" and no other output."""
    return inspect.cleandoc(prompt)
