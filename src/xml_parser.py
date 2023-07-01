import xml.etree.ElementTree as ET


def fix_bpmn_format(path: str):
    with open(path, 'r') as file:
        content = file.read()
    content = content.replace('ns0', 'bpmn')
    content = content.replace('ns1', 'bpmndi')
    content = content.replace('ns2', 'omgdc')
    content = content.replace('ns3', 'omgdi')
    with open(path, 'w') as file:
        file.write(content)


def change_task_type(task, child_tag) -> str:
    tag_tokens = child_tag.split('}')
    tag_tokens[1] = task
    return '}'.join(tag_tokens)


def replace_task_names(input_path: str, output_path: str, names_dict, task_type_dict):
    tree = ET.parse(input_path)
    root = tree.getroot()
    for child in root:
        if child.tag.split('}')[1] == 'process':
            for process_child in child:
                if process_child.tag.split('}')[1] == 'task':
                    task_name = process_child.attrib['name'].strip()
                    new_name = names_dict[task_name]
                    process_child.tag = change_task_type(task_type_dict[new_name], process_child.tag)
                    process_child.attrib['name'] = new_name
    tree.write(output_path)
    fix_bpmn_format(output_path)
