import os
import sys
import logging
from typing import List, Dict

from features.steps.support.templator import populate_template


def get_all_files_in_dir(dir_path: str) -> List[str]:
    "lists all the files in a given directory path"
    try:
        result = []
        for name in os.listdir(dir_path):
            result.append(name)
        return result
    except Exception as ex:
        raise RuntimeError(f"Ex Listing Dir {dir_path}: {str(ex)}")


def generate_file_content(filepath: str, secrets: dict) -> str:
    "loads the file, populates the templates, returns the content"
    try:
        with open(filepath, 'r') as fhandle:
            file_content = fhandle.read()
            return populate_template(file_content, secrets)
    except Exception as ex:
        raise RuntimeError(f"Ex Generating File Content For {filepath}: {str(ex)}")


def write_content_to_file(output_filepath: str, content: str) -> bool:
    "write the given content into the output_filepath"
    try:
        with open(output_filepath, 'w') as fhandle:
            fhandle.write(content)
            return True
    except Exception as ex:
        raise RuntimeError(f"Ex Writing Content To {output_filepath}: {str(ex)}")


def populate_jinja_template_tags(file_content: str) -> str:
    "replaces '[[' and ']]' with the correct Jinja2 tags"
    file_content = file_content.replace("[[", "{{")
    return file_content.replace("]]", "}}")


def get_secrets(args: List[str]) -> Dict[str, str]:
    "get the secrets from the key-value params passed as cmd-args and return as a dictionary"
    if not len(args) >= 2:
        return None

    result: Dict[str, str] = {}

    for i in range(2, len(args)):
        raw_param = args[i]

        if len(raw_param):
            tuple_param = raw_param.split("=")
            if len(tuple_param) == 2:
                result[tuple_param[0]] = tuple_param[1]
        else:
            break

    return result


# take the files from /features
# populate the secrets
# paste the output into /test-framework/features

if __name__ == "__main__":
    logging.info("Beginning Script")

    if len(sys.argv) < 2:
        logging.fatal("< 1 cmd arg")
        sys.exit(1)

    repo_root = sys.argv[1]

    if not len(repo_root):
        logging.error("Repo Root Arg Not Supplied")
        sys.exit(1)

    dir_path = f"{repo_root}/features"
    out_dir_path = f"{repo_root}/test-framework/features"

    if not os.path.isdir(dir_path):
        logging.error(dir_path + " Not Found")

    secrets = get_secrets(sys.argv)

    if not len(secrets):
        logging.warning("No Secrets Specified In Script")

    file_list = get_all_files_in_dir(dir_path)

    if not len(file_list):
        logging.error(f"No '.feature' Files Found In {dir_path}")
        sys.exit(1)

    for filename in file_list:
        new_content = generate_file_content(f"{dir_path}/{filename}", secrets)
        new_content = populate_jinja_template_tags(new_content)

        if write_content_to_file(f"{out_dir_path}/{filename}", new_content):
            logging.info(f"File {filename} Populated")

    logging.info("Script Complete")
