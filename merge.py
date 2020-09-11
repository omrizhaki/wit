# Upload 177
import datetime
import distutils.core
from filecmp import dircmp
import os
import random
import shutil
import sys

from graphviz import Digraph


def init():
    pathlist = ('.wit', 'staging_area', 'images')
    for path in pathlist[1:]:
        newpath = os.path.join(pathlist[0], path)
        os.makedirs(newpath, exist_ok=True)
    with open(os.path.join('.wit', 'activated.txt'), 'w+') as activated_file:
        activated_file.write('master')


def add(path):
    src = os.path.abspath(path)
    witlocation = find_wit(path)
    witlocation = witlocation[::-1]
    witdirectory = os.getcwd()
    dst = os.path.join(witdirectory, '.wit', 'staging_area')
    if os.path.isdir(src):
        for item in witlocation:
            dst = os.path.join(dst, item)
        shutil.rmtree(dst, ignore_errors=True)
        shutil.copytree(src, dst)
    else:
        for item in witlocation[:-1]:
            dst = os.path.join(dst, item)
        shutil.copy(src, dst)


def find_wit(path):
    which_dir_list = [path]
    parentpath = os.path.basename(os.getcwd())
    while parentpath != '':
        if '.wit' in os.listdir(os.getcwd()):
            return which_dir_list
        else:
            which_dir_list.append(parentpath)
            parentpath = os.path.basename(os.getcwd())
            os.chdir("..")
    raise ValueError("No wit")
    return False
    

def commit(MESSAGE):
    try:
        if find_wit(path):
            pass
    except Exception:
        return False
    new_folder_name = ''.join(random.choice('1234567890abcdef') for _ in range(40))
    metadata(new_folder_name, references(new_folder_name), MESSAGE)
    src = os.path.join('.wit', 'staging_area')
    dst = os.path.join('.wit', 'images', new_folder_name)
    shutil.copytree(src, dst, symlinks=True)
    with open(os.path.join('.wit', 'activated.txt'), 'r') as activated_file:
        branch_active = activated_file.read()
    if branch_active == '':
        reference_text = f'HEAD = {new_folder_name}\nmaster = {new_folder_name}\n'
    else:
        if os.path.isfile(os.path.join('.wit', 'references.txt')):
            with open(os.path.join('.wit', 'references.txt'), 'r') as references_file:
                lines = references_file.readlines()
            for i in range(len(lines)):
                if branch_active == lines[i][: len(branch_active)]:
                    if lines[0][5:-1] == lines[i][len(branch_active) + 1: -1]:
                        lines[i] = f'{branch_active}={new_folder_name}\n'
            lines[0] = f'HEAD={new_folder_name}\n'
            reference_text = ''.join(lines)
        else:
            reference_text = f'HEAD = {new_folder_name}\nmaster = {new_folder_name}\n'
        with open(os.path.join('.wit', 'references.txt'), 'w+') as references_file:
            references_file.write(reference_text)


def metadata(new_folder_name, parent_folder_name, MESSAGE):
    date = datetime.datetime.now().strftime('%a %b %d %H:%M:%S %Y %Z')
    text = f"parent={parent_folder_name}\ndate={date}\nmessage=" + MESSAGE
    metadata_name = new_folder_name + '.txt'
    with open(os.path.join('.wit', 'images', metadata_name), 'w') as metadata_file:
        metadata_file.write(text)


def references(new_folder_name):
    parent_folder_name = 'None'
    if os.path.isfile(os.path.join('.wit', 'references.txt')):
        with open(os.path.join('.wit', 'references.txt'), 'r') as references_file:
            lines = references_file.readlines()
            parent_folder_name = lines[0][5:-1]
    else:
        with open(os.path.join('.wit', 'references.txt'), 'w+') as references_file:
            reference_text = f'HEAD = {new_folder_name}\nmaster = {new_folder_name}\n'
            references_file.write(reference_text)
    return parent_folder_name


def status():
    try:
        if find_wit(path):
            pass
    except Exception:
        return False
    with open(os.path.join('.wit', 'references.txt'), 'r') as references_file:
        commit_id = references_file.readline()[5:-1]
    dcmp = dircmp(os.path.join('.wit', "images", commit_id), os.path.join(".wit", 'staging_area'))
    path_dict = compare_trees(dcmp)
    dcmp = dircmp(os.getcwd(), os.path.join('.wit', 'staging_area'), ignore=['.wit'])
    path_dict = compare_trees(dcmp)
    print(f"""
    Present commit_id: {commit_id}
    Changes to be committed: {path_dict['Changes to be committed']}
    Changes not staged for commit: {path_dict['Changes not staged for commit']}
    Untracked files: {path_dict['Untracked files']}
    """)
    return path_dict


def compare_trees(dcmp):
    path_dict = {'Changes not staged for commit': [], 'Untracked files': [], 'Changes to be committed': []}
    for fileorfolder in dcmp.diff_files:
        path_dict['Changes not staged for commit'].append(fileorfolder)
    for fileorfolder in dcmp.left_only:
        path_dict['Untracked files'].append(fileorfolder)
    for fileorfolder in dcmp.right_only:
        path_dict['Changes to be committed'].append(fileorfolder)
    for sub_dcmp in dcmp.subdirs.values():
        compare_trees(sub_dcmp)
    return path_dict


def checkout(commit_id):
    try:
        if find_wit(path):
            pass
    except Exception:
        return False
    new_activated = ''
    path_dict = status()
    with open(os.path.join('.wit', 'references.txt'), 'r') as references_file:
        lines = references_file.readlines()
    for branch_name in lines:
        if commit_id == branch_name[: len(commit_id)]:
            new_activated = commit_id
            commit_id = branch_name[len(commit_id) + 1: -1]
    with open(os.path.join('.wit', 'activated.txt'), 'w+') as activated_file:
        activated_file.write(new_activated)
    if len(path_dict['Changes to be committed']) < 1 or len(path_dict['Changes not staged for commit']) < 1:
        src = os.path.join('.wit', 'images', commit_id)
        dst = os.getcwd()
        distutils.dir_util.copy_tree(src, dst, preserve_mode=0)
    else:
        return "Checkout did not run"
    with open(os.path.join('.wit', 'references.txt'), 'r') as references_file:
        lines = references_file.readlines()
    lines[0] = f'HEAD={commit_id}\n'
    with open(os.path.join('.wit', 'references.txt'), 'w+') as references_file:
        references_file.writelines(lines)
    src = os.path.join('.wit', 'images', commit_id)
    dst = os.path.join('.wit', 'staging_area')
    shutil.rmtree(dst, ignore_errors=True)
    shutil.copytree(src, dst)


def graph():
    try:
        if find_wit(path):
            pass
    except Exception:
        return False
    our_graph = Digraph('G', filename='something',
                        format='png', strict=True)
    with open(os.path.join('.wit', 'references.txt'), 'r') as references_file:
        lines = references_file.readlines()
    parents_list = []
    for i in range(len(lines)):
        parents_list.append(lines[i].split('=')[1][: -1])
    for i in parents_list:
        parent_line = i + '.txt'
        while parent_line[: 4] != 'None':
            with open(os.path.join('.wit', 'images', parent_line), 'r') as images_file:
                lines = images_file.readlines()
            new_parent_line = lines[0].split('=')[1][: 40]
            if new_parent_line[: 4] != 'None':
                new_parent_line += '.txt'
                our_graph.edge(parent_line[0:40], new_parent_line[0:40])
                if ',' in lines[0]:
                    second_parent = lines[0].split('=')[1][41: -1]
                    our_graph.edge(parent_line[0:40], second_parent)
            parent_line = new_parent_line
    our_graph.view()


def branch(NAME):
    try:
        if find_wit(path):
            pass
    except Exception:
        return False
    with open(os.path.join('.wit', 'references.txt'), 'r') as references_file:
        lines = references_file.readlines()
    commit_id = lines[0][5:-1]
    lines[-1] = f'{lines[-1]}{NAME}={commit_id}\n'
    with open(os.path.join('.wit', 'references.txt'), 'w+') as references_file:
        references_file.writelines(lines)


def merge(BRANCH_NAME):
    try:
        if find_wit(path):
            pass
    except Exception:
        return False
    heads = []
    branches = []
    with open(os.path.join('.wit', 'references.txt'), 'r') as references_file:
        head_lines = references_file.readlines()
    head_commit_id = head_lines[0][5:-1] + '.txt'
    heads.append(head_commit_id[0:40])
    while head_commit_id != 'None':
        with open(os.path.join('.wit', 'images', head_commit_id), 'r') as images_file:
            head_lines = images_file.readlines()
        new_parent_line = head_lines[0][7:-1]
        if new_parent_line != 'None':
            new_parent_line += '.txt'
            heads.append(new_parent_line[0:40])
        head_commit_id = new_parent_line
    with open(os.path.join('.wit', 'references.txt'), 'r') as references_file:
        branch_lines = references_file.readlines()
    for branch_name in branch_lines:
        if BRANCH_NAME == branch_name[: len(BRANCH_NAME)]:
            branch_commitid = branch_name[len(BRANCH_NAME) + 1: -1]
            head_commit_id = branch_commitid + '.txt'
    branches.append(head_commit_id[0:40])
    while head_commit_id != 'None':
        with open(os.path.join('.wit', 'images', head_commit_id), 'r') as images_file:
            head_lines = images_file.readlines()
        new_parent_line = head_lines[0][7:-1]
        if new_parent_line != 'None':
            new_parent_line += '.txt'
            branches.append(new_parent_line[0:40])
        head_commit_id = new_parent_line
    common_parent = [com_par for com_par in heads if com_par in branches][0]
    print(f"common_parent: {common_parent}")
    print(f"branch_commitid: {branch_commitid}")
    dcmp = dircmp(os.path.join(".wit", "images", common_parent),
                    os.path.join(".wit", 'images', branch_commitid))
    differe_files, new = find_differences(dcmp)
    for branch_item in differe_files:
        add(branch_item)
    for branch_item in new:
        add(branch_item)
    commit(f'Merge branch: {BRANCH_NAME}')
    with open(os.path.join('.wit', 'references.txt'), 'r') as references_file:
        head_lines = references_file.readlines()
    head_commit_id = head_lines[0][5:-1] + '.txt'
    with open(os.path.join('.wit', 'images', head_commit_id), 'r') as images_file:
        head_lines = images_file.readlines()
    new_parent_line = head_lines[0][:-1] + ',' + branch_commitid + '\n'
    head_lines[0] = new_parent_line
    with open(os.path.join('.wit', 'images', head_commit_id), 'w') as log_file:
        log_file.writelines(head_lines)


def find_differences(dcmp):
    different = list(dcmp.diff_files)
    new = list(dcmp.right_only)
    for sub_dcmp in dcmp.subdirs.values():
        find_differences(sub_dcmp)
    return different, new


if __name__ == "__main__":
    path = None
    if len(sys.argv) == 3 and sys.argv[1] == 'add':
        add(sys.argv[2])
    elif len(sys.argv) == 3 and sys.argv[1] == 'commit':
        commit(sys.argv[2])
    elif len(sys.argv) == 3 and sys.argv[1] == 'checkout':
        checkout(sys.argv[2])
    elif len(sys.argv) == 3 and sys.argv[1] == 'branch':
        branch(sys.argv[2])
    elif len(sys.argv) == 3 and sys.argv[1] == 'merge':
        merge(sys.argv[2])
    elif len(sys.argv) == 2 and sys.argv[1] == 'init':
        init()
    elif len(sys.argv) == 2 and sys.argv[1] == 'status':
        status()
    elif len(sys.argv) == 2 and sys.argv[1] == 'graph':
        graph()
    else:
        print('Does not compute, try again dumdum')
