import argparse
import os
import time
from main_abbyy_class import *

processor = None


def setup_processor():
    """
    This function Sets-up the parse environment...
    :return: none
    """
    if "ABBYY_APPID" in os.environ:
        processor.ApplicationId = os.environ["ABBYY_APPID"]

    if "ABBYY_PWD" in os.environ:
        processor.Password = os.environ["ABBYY_PWD"]

    # Proxy settings
    if "http_proxy" in os.environ:
        proxy_string = os.environ["http_proxy"]
        print("Using http proxy at {}".format(proxy_string))
        processor.Proxies["http"] = proxy_string

    if "https_proxy" in os.environ:
        proxy_string = os.environ["https_proxy"]
        print("Using https proxy at {}".format(proxy_string))
        processor.Proxies["https"] = proxy_string


# Recognize a file at filePath and save result to resultFilePath
def recognize_file(file_path, result_file_path, language, output_format):
    """
    returns the validation output for valid/invalid file path
    :param file_path: str
    :param result_file_path: str
    :param language: str
    :param output_format: .txt
    :return: filepath
    """
    print("Processing...")
    settings = ProcessingSettings()
    settings.Language = language
    settings.OutputFormat = output_format
    task = processor.process_image(file_path, settings)
    if task is None:
        print("Error !! , there is No Task ")
        return

    print("Id = {}".format(task.Id))
    print("Status = {}".format(task.Status))

    # Wait for the task to be completed
    print("running the Task....")

    while task.is_active():
        time.sleep(5)
        print(".....sill processing......")
        task = processor.get_task_status(task)

    print("Status = {}".format(task.Status))

    if task.Status == "Completed":
        if task.DownloadUrl is not None:
            processor.download_result(task, result_file_path)
            print("Result was written to {}".format(result_file_path))
    else:
        print("Error processing task")


def create_parser():
    """
    identifies the file extension and the default language
    :return: None
    """
    parser = argparse.ArgumentParser(description="Identifies the File")

    parser.add_argument('-l', '--language', default='English', help='Recognition language (default: %(default)s)')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-txt', action='store_const', const='txt', dest='format', default='txt')

    return parser


def main():
    global processor
    processor = Abby_Lib_Py()
    setup_processor()
    source_file = input("Please Provide the name of image input file with extension e.g ( abc.jpg) : \t")
    target_file = "result.txt"

    args = create_parser().parse_args()
    language = args.language
    output_format = args.format

    if os.path.isfile(source_file):
        recognize_file(source_file, target_file, language, output_format)
    else:
        print("No such file: {}".format(source_file))


if __name__ == "__main__":
    main()
