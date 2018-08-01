# Copyright 2018 Rubrik, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License prop
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This module contains the Rubrik SDK API class.
"""

import requests
import json
import sys
import time
try:
    from urllib import quote  # Python 2.X
except ImportError:
    from urllib.parse import quote  # Python 3+
from random import choice


class Api():
    """This class contains the base API methods that can be called independeintly or internally
    in standalone functions.
    """

    def __init__(self, node_ip):
        super().__init__(node_ip)

    def _common_api(self, call_type, api_version, api_endpoint, config=None, job_status_url=None, timeout=15, authentication=True):
        """Internal method that consolidates the base API functions

        Arguments:
            call_type {str} -- The type of API call you wish to make. Valid choices are 'GET', 'POST', 'PATCH', 'DELETE', and 'JOB_STATUS'.
            api_version {str} -- The version of the Rubrik CDM API to call.
            api_endpoint {str} -- The endpoint (ex. cluster/me) of the Rubrik CDM API to call.

        Keyword Arguments:
            config {dict} -- The specified data to send with POST and PATCH API calls. (default: {None})
            job_status_url {str} -- The job status URL provided by a previous API call. (default: {None})
            timeout {int} -- The number of seconds to wait to establish a connection the Rubrik Cluster. (default: {15})
            authentication {bool} -- Flag that specifies whether or not to utilize authentication when making the API call. (default: {True})

        Returns:
            dict -- The API call response.
        """
        if call_type is not 'JOB_STATUS':
            self._api_validation(api_version, api_endpoint)

        """In order to dynamically select a node to interact with, the SDK will first use the node ip provided
        by the user to get a list of all node ips in the cluster. This code will determine if the SDK has gathered
        that list yet or not. If it has it will randomly select a node ip from the list to interact with."""
        if isinstance(self.node_ip, str):
            node_ip = self.node_ip
        else:
            node_ip = choice(self.node_ip)

        valid_call_type = ['GET', 'POST', 'PATCH', 'DELETE', 'JOB_STATUS']

        # Determine which call type is being used and then set the relevant variables for that call type
        if call_type is 'GET':
            request_url = "https://{}/api/{}{}".format(node_ip, api_version, api_endpoint)
            request_url = quote(request_url, '://?=&')
            self.log('GET {}'.format(request_url))
        elif call_type is 'POST':
            config = json.dumps(config)
            request_url = "https://{}/api/{}{}".format(node_ip, api_version, api_endpoint)
            self.log('POST {}'.format(request_url))
            self.log('Config: {}'.format(config))
        elif call_type is 'PATCH':
            config = json.dumps(config)
            request_url = "https://{}/api/{}{}".format(node_ip, api_version, api_endpoint)
            self.log('PATCH {}'.format(request_url))
            self.log('Config: {}'.format(config))
        elif call_type is 'DELETE':
            request_url = "https://{}/api/{}{}".format(node_ip, api_version, api_endpoint)
            self.log('DELETE {}'.format(request_url))
        elif call_type is 'JOB_STATUS':
            self.log('JOB STATUS for {}'.format(job_status_url))
        else:
            sys.exit('Error: "authentication" must be either True or False')

        # Determine if authentication should be sent as part of the API Header
        if authentication == True:
            header = self._authorization_header()
        elif authentication == False:
            header = self._header()
        else:
            sys.exit('Error: the _common_api() call_type must be one of the following: {}'.format(valid_call_type))

        try:
            if call_type is 'GET':
                api_request = requests.get(request_url, verify=False, headers=header, timeout=timeout)
            elif call_type is 'POST':
                api_request = requests.post(request_url, verify=False, headers=header, data=config, timeout=timeout)
            elif call_type is 'PATCH':
                api_request = requests.patch(request_url, verify=False, headers=header, data=config, timeout=timeout)
            elif call_type is 'DELETE':
                api_request = requests.delete(request_url, verify=False, headers=header, timeout=timeout)
            elif call_type is 'JOB_STATUS':
                api_request = requests.get(job_status_url, verify=False, headers=header, timeout=timeout)

            self.log(str(api_request) + "\n")
            try:
                api_response = api_request.json()
                # Check to see if an error message has been provided by Rubrik
                for key, value in api_response.items():
                    if key == "errorType":
                        error_message = api_response['message']
                        api_request.raise_for_status()
            except:
                api_request.raise_for_status()
        except requests.exceptions.ConnectTimeout:
            sys.exit('Error: Unable to establish a connection to the Rubrik Cluster.')
        except requests.exceptions.RequestException as error:
            # If "error_message" has be defined sys.exit that message else sys.exit the request exception error
            try:
                error_message
            except NameError:
                sys.exit(error)
            else:
                sys.exit('Error: ' + error_message)

        return api_request.json()

    def get(self, api_version, api_endpoint, timeout=15, authentication=True):
        """Connect to a Rubrik Cluster and perform a GET operation.

        Arguments:
            api_version {str} -- The version of the Rubrik CDM API to call.
            api_endpoint {str} -- The endpoint (ex. cluster/me) of the Rubrik CDM API to call.

        Keyword Arguments:
            timeout {int} -- The number of seconds to wait to establish a connection the Rubrik Cluster. (default: {15})
            authentication {bool} -- Flag that specifies whether or not to utilize authentication when making the API call. (default: {True})

        Returns:
            dict -- The response body of the API call.
        """

        api_call = self._common_api('GET', api_version, api_endpoint, config=None,
                                    job_status_url=None, timeout=timeout, authentication=authentication)

        return api_call

    def post(self, api_version, api_endpoint, config, timeout=15, authentication=True):
        """Connect to a Rubrik Cluster and perform a POST operation.

        Arguments:
            api_version {str} -- The version of the Rubrik CDM API to call.
            api_endpoint {str} -- The endpoint (ex. cluster/me) of the Rubrik CDM API to call.
            config {dict} -- The specified data to send with the API call.

        Keyword Arguments:
            timeout {int} -- The number of seconds to wait to establish a connection the Rubrik Cluster. (default: {15})
            authentication {bool} -- Flag that specifies whether or not to utilize authentication when making the API call. (default: {True})

        Returns:
            dict -- The response body of the API call.
        """

        api_call = self._common_api('POST', api_version, api_endpoint, config=config,
                                    job_status_url=None, timeout=timeout, authentication=authentication)

        return api_call

    def patch(self, api_version, api_endpoint, config, timeout=15, authentication=True):
        """Connect to a Rubrik Cluster and perform a PATCH operation.

        Arguments:
            api_version {str} -- The version of the Rubrik CDM API to call.
            api_endpoint {str} -- The endpoint (ex. cluster/me) of the Rubrik CDM API to call.
            config {dict} -- The specified data to send with the API call.

        Keyword Arguments:
            timeout {int} -- The number of seconds to wait to establish a connection the Rubrik Cluster. (default: {15})
            authentication {bool} -- Flag that specifies whether or not to utilize authentication when making the API call. (default: {True})

        Returns:
            dict -- The response body of the API call.
        """

        api_call = self._common_api('PATCH', api_version, api_endpoint, config=config,
                                    job_status_url=None, timeout=timeout, authentication=authentication)

        return api_call

    def delete(self, api_version, api_endpoint, timeout=15, authentication=True):
        """Connect to a Rubrik Cluster and perform a DELETE operation.
        Arguments:
            api_version {str} -- The version of the Rubrik CDM API to call.
            api_endpoint {str} -- The endpoint (ex. cluster/me) of the Rubrik CDM API to call.

        Keyword Arguments:
            timeout {int} -- The number of seconds to wait to establish a connection the Rubrik Cluster. (default: {15})
            authentication {bool} -- Flag that specifies whether or not to utilize authentication when making the API call. (default: {True})

        Returns:
            dict -- The response body of the API call.
        """

        api_call = self._common_api('DELETE', api_version, api_endpoint, config=None,
                                    job_status_url=None, timeout=timeout, authentication=authentication)

        return api_call

    def job_status(self, url, wait_for_completion=True, timeout=15):
        """Connect to the Rubrik Cluster and get the status of a particular job.

        Arguments:
            url {str} -- The job status URL provided by a previous API call.

        Keyword Arguments:
            timeout {int} -- The number of seconds to wait to establish a connection the Rubrik Cluster. (default: {15})
            wait_for_completion {bool} -- Flag that determines if the method should wait for the job to complete before exiting. (default: {True})

        Returns:
            dict -- The response body of the API call.
        """

        if not isinstance(wait_for_completion, bool):
            sys.exit('Error: The job_status() wait_for_completion argument must be True or False')

        if wait_for_completion:
            self.log('Job Status: Waiting for the job to complete.')
            api_call = self._common_api('JOB_STATUS', api_version=None, api_endpoint=None,
                                        config=None, job_status_url=url, timeout=timeout)
            while True:
                api_call = self._common_api('JOB_STATUS', api_version=None, api_endpoint=None,
                                            config=None, job_status_url=url, timeout=timeout)

                job_status = api_call['status']

                if job_status == "SUCCEEDED":
                    self.log('Job Progress 100%\n')
                    job_status = api_call['status']
                    break
                elif job_status == "QUEUED" or "RUNNING":
                    self.log('Job Progress {}%\n'.format(api_call['progress']))
                    job_status = api_call['status']
                    time.sleep(10)
                    continue
                else:
                    sys.exit('Error: {}'.format(str(api_call)))

        else:
            api_call = self._common_api('JOB_STATUS', api_version=None, api_endpoint=None,
                                        config=None, job_status_url=url, timeout=timeout)

        return api_call
