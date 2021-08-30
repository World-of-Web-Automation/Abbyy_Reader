"""
The main ABBYY Class for handling the HTTP requests and exception
"""

try:
    from requests import post, get
    import shutil as sh
    import xml.dom.minidom as xmlDOM

except ImportError as e:
    print('Error Note : ', e, "\n", "Run 'pip install requests | fix OS environment ' to resolve  it.")
    exit()


class ProcessingSettings:
    Language = "English"
    OutputFormat = 'txt'


class Task:
    Status = "Unknown"
    Id = None
    DownloadUrl = None

    def is_active(self):
        if self.Status == "InProgress" or self.Status == "Queued":
            return True
        else:
            return False

class Abby_Lib_Py:
    ServerUrl = "http://cloud-eu.ocrsdk.com/"
    ApplicationId = 'abc'
    Password = 'xXxxxx'
    Proxies = {}

    def process_image(self, file_path, settings):
        url_params = {"language": settings.Language, "exportFormat": settings.OutputFormat}
        request_url = self.get_request_url("processImage")

        with open(file_path, 'rb') as image_file:
            image_data = image_file.read()

        response = post(request_url, data=image_data, params=url_params,
                        auth=(self.ApplicationId, self.Password), verify=True)

        # Raises any error if ny exception is thrown
        response.raise_for_status()

        # Creates the task ID for every new process
        task = self.decode_response(response.text)
        return task

    def get_task_status(self, task):
        if task.Id.find('00000000-0') != -1:
            # GUID_NULL is being passed. This may be caused by a logical error in the calling code
            print("Null task id passed")
            return None

        url_params = {"taskId": task.Id}
        status_url = self.get_request_url("getTaskStatus")

        response = get(status_url, params=url_params,
                       auth=(self.ApplicationId, self.Password), proxies=self.Proxies, verify=True)
        task = self.decode_response(response.text)
        return task

    def download_result(self, task, output_path):
        get_result_url = task.DownloadUrl
        if get_result_url is None:
            print("No download URL found")
            return

        file_response = get(get_result_url, stream=True, proxies=self.Proxies)
        with open(output_path, 'wb') as output_file:
            sh.copyfileobj(file_response.raw, output_file)

    def decode_response(self, xml_response):
        """
        Decode xml response of the server. Return Task object

        """
        dom = xmlDOM.parseString(xml_response)
        task_node = dom.getElementsByTagName("task")[0]
        task = Task()
        task.Id = task_node.getAttribute("id")
        task.Status = task_node.getAttribute("status")
        if task.Status == "Completed":
            task.DownloadUrl = task_node.getAttribute("resultUrl")
        return task

    def get_request_url(self, url):
        return self.ServerUrl.strip('/') + '/' + url.strip('/')
