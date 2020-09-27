import os
import sys
import logging

from populate_secrets import get_all_files_in_dir

if __name__ == "__main__":
    logging.info("Beginning Script")

    if len(sys.argv) < 2:
        logging.fatal("< 2 cmd arg")
        sys.exit(1)

    repo_root = sys.argv[1]
    if not len(repo_root):
        logging.error("unable to find repo root")

    dir_path = f"{repo_root}/test-framework/features"
    all_files = get_all_files_in_dir(dir_path)

    if not len(all_files):
        logging.error("No Files Found To Delete In " + dir_path)
        sys.exit(0)

    for filename in all_files:
        if filename.find(".feature") > -1:
            os.remove(dir_path + "/" + filename)
            logging.info(filename + " Removed")

    logging.info("Script Complete")
