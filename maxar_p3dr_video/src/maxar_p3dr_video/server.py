from __future__ import annotations  # noqa

from .socket import create_and_connect, receive_payload, send_payload
import maxar_p3dr_video.p3dr_message_definition_pb2 as pb

import json
import math
import pathlib
from PIL import Image
import subprocess
import tempfile
import time
from typing import Any, Dict


class Server():
    """
    Representation of a live video server, with programmatic access
    to various operations.
    """

    def __init__(self: Server) -> None:
        """
        Create a 'dead' Server object. I.e., the object cannot
        do anything after just calling the constructor. Instead for most
        uses objects should be made by calling 'public_server()' or
        'private_server()' instead.
        """
        self._socket = None
        self._server_proc = None
        self._url = None

    @staticmethod
    def public_server(host: str, port: int) -> Server:
        """
        Create a Server object connected to a public server.

        Parameters:
            host: The host address to the server.
            port: The network port for the server.

        Returns:
            A Server object.
        """
        self = Server()
        self._socket = create_and_connect(host, port)
        self._url = f'tcp://{host}:{port}'

        return self

    @staticmethod
    def private_server(server_path: pathlib.Path,
                       severity: str) -> Server:
        """
        Start and connect to a private server.

        Parameters:
            server_path: Path to the server to start.            
            severity: The desired log severity for the server.

        Returns:
            A Server object.
        """
        result = Server._start(server_path=server_path,
                               severity=severity)
        if result is None:
            raise RuntimeError('Failed to start a private server')

        server_proc, host, port = result

        self = Server()
        self._server_proc = server_proc
        self._socket = create_and_connect(host, port)
        self._url = f'tcp://{host}:{port}'

        return self

    def url(self: Server) -> str:
        """
        Get the URL of the live video server.

        Returns:
            The URL.
        """
        return self._url

    def query_version(self: Server) -> Dict[str, str]:
        """
        Query the server version.

        Returns:
            A dictionary with branch and revision.
        """
        version_request = pb.VersionRequest()
        user_message = pb.UserMessage()
        user_message.versionRequest.CopyFrom(version_request)

        self.push(user_message)
        p3dr_message = self.pop()

        if p3dr_message.WhichOneof('message') == 'versionResponse':
            version_response = p3dr_message.versionResponse
            return {
                'branch': version_response.branch,
                'revision': version_response.revision
            }
        else:
            raise ValueError('Unexpected message type from video server')

    def open_stream(self: Server, references: list[pathlib.Path]) -> int:
        """
        Open a new stream to the server. Yields a stream id that should be used
        in further communication with the server.

        Parameters:
            references: A list of reference database files.

        Returns:
            The new stream id.
        """
        open_stream_request = pb.OpenStreamRequest()
        for reference in references:
            reference.resolve()
            open_stream_request.reference_datasets.append(str(reference))

        user_message = pb.UserMessage()
        user_message.openStreamRequest.CopyFrom(open_stream_request)

        self.push(user_message)
        p3dr_message = self.pop()

        if p3dr_message.WhichOneof('message') == 'openStreamResponse':
            return p3dr_message.openStreamResponse.stream_id
        else:
            raise ValueError('Unexpected message type from video server')

    def query_references(self: Server, stream_id: int) -> list[pathlib.Path]:
        """
        Query the reference datasets the given stream is configured with.

        Parameters:
            stream_id: The stream id to query.

        Returns:
            The list of reference datasets.
        """
        list_reference_request = pb.ListReferenceDatasetsRequest()
        list_reference_request.stream_id = stream_id

        user_message = pb.UserMessage()
        user_message.listReferenceDatasetsRequest.CopyFrom(
            list_reference_request)

        self.push(user_message)
        p3dr_message = self.pop()

        if p3dr_message.WhichOneof('message') == 'listReferenceDatasetsResponse':
            list_reference_response = p3dr_message.listReferenceDatasetsResponse
            references = list()
            for reference in list_reference_response.reference_datasets:
                references.append(pathlib.Path(reference))

            return references
        else:
            raise ValueError('Unexpected message type from video server')

    def request_registration(self: Server, stream_id: int, frame_id: int,
                             camera: Dict[str, Any], image: Image.Image) -> bool:
        """
        Request an asynchronous registration of the image and its metadata.

        Parameters:
            stream_id: The id for the current stream.
            frame_id: The id for the current frame.
            camera: Dictionary with canonic camera metadata.
            image: Image in PIL format.

        Returns:
            True if the request was possible to push to the server, False otherwise.
        """
        try:
            latitude, longitude, height = camera['pos']
            position = pb.Point()
            position.latitude = latitude
            position.longitude = longitude
            position.height = height

            yaw, pitch, roll = camera['att']
            attitude = pb.Attitude()
            attitude.yaw = math.degrees(yaw)
            attitude.pitch = math.degrees(pitch)
            attitude.roll = math.degrees(roll)

            lens = camera['lens']
            fov = pb.FieldOfView()
            fov.horizontal = math.degrees(lens['hfov'])
            fov.vertical = math.degrees(lens['vfov'])

            lens_parameters = pb.LensParameters()
            lens_parameters.k2 = lens.get('k2', 0.0)
            lens_parameters.k3 = lens.get('k3', 0.0)
            lens_parameters.k4 = lens.get('k4', 0.0)

            metadata = pb.ImageMetadata()
            metadata.position.CopyFrom(position)
            metadata.attitude.CopyFrom(attitude)
            metadata.fov.CopyFrom(fov)
            metadata.lens_parameters.CopyFrom(lens_parameters)

            image = image if image.mode == 'L' else image.convert('L')
            grayscale_image = pb.GrayscaleImage()
            grayscale_image.width = image.width
            grayscale_image.height = image.height
            grayscale_image.raw = image.tobytes()

            frame = pb.Frame()
            frame.metadata.CopyFrom(metadata)
            frame.grayscale_image.CopyFrom(grayscale_image)

            request = pb.RegistrationRequest()
            request.stream_id = stream_id
            request.frame_id = frame_id
            request.frame.CopyFrom(frame)

            user_message = pb.UserMessage()
            user_message.request.CopyFrom(request)

            self.push(user_message)

        except KeyError as e:
            print(f'Error: Missing key={e}')
            return False
        except ValueError as e:
            print(f'Error: Value error={e}')
            return False

        return True

    def get_registration_result(self: Server) -> tuple[int, float, Dict[str, Any], str] | None:
        """
        Get the result from an asynchronous registration.

        Returns:
            A tuple frame_id, figure of merit, camera, error message, or None. The fields
            camera and error message are mutual exclusive.
        """
        p3dr_message = self.pop()

        if p3dr_message is None:
            return None  # Timeout
        elif p3dr_message.WhichOneof('message') == 'response':
            response = p3dr_message.response
            frame_id = response.frame_id
            fom = response.figure_of_merit

            camera = dict()

            metadata = response.metadata
            position = metadata.position
            camera['pos'] = [
                position.latitude,
                position.longitude,
                position.height
            ]

            attitude = metadata.attitude
            camera['att'] = [
                math.radians(attitude.yaw),
                math.radians(attitude.pitch),
                math.radians(attitude.roll)
            ]

            fov = metadata.fov
            lens_parameters = metadata.lens_parameters

            lens = dict()
            lens['hfov'] = math.radians(fov.horizontal)
            lens['vfov'] = math.radians(fov.vertical)
            if lens_parameters.k2 != 0.0:
                lens['k2'] = lens_parameters.k2
            if lens_parameters.k3 != 0.0:
                lens['k3'] = lens_parameters.k3
            if lens_parameters.k4 != 0.0:
                lens['k4'] = lens_parameters.k4

            camera['lens'] = lens

            return frame_id, fom, camera, None
        elif p3dr_message.WhichOneof('message') == 'error':
            error = p3dr_message.error
            return error.frame_id, -1.0, None, error.error_string
        else:
            print(
                f"Error: Unexpected message type='{p3dr_message.WhichOneof('message')}'")
            return None

    def push(self: Server, message: pb.UserMessage) -> None:
        """
        Push a UserMessage to the server.

        Parameters:
            message: The UserMessage.
        """
        assert self._socket is not None

        send_payload(self._socket, message.SerializeToString())

    def pop(self: Server) -> pb.P3DRMessage | None:
        """
        Pop a P3DRMessage from the server. The call is blocking,
        but will eventually be interrupted by a TimeoutError if
        no message is sent from the server.

        Returns:
            A P3DRMessage, or None.
        """
        assert self._socket is not None

        try:
            payload = receive_payload(self._socket)

            p3dr_message = pb.P3DRMessage()
            p3dr_message.ParseFromString(payload)

            return p3dr_message
        except TimeoutError:
            print('Error: Timeout')
            return None

    def shutdown(self: Server) -> None:
        """
        Shutdown a Server object. For an object connected
        to a public server only the connection is closes. For
        an object connected to a private server also the server
        process is terminated.
        """
        if self._socket is not None:
            self._socket.close()
            self._socket = None

            print('Info: Socket is closed')

        if self._server_proc is not None:
            Server._stop(self._server_proc)
            self._server_proc = None

            print('Info: Server is stopped')

    def __enter__(self: Server) -> Server:
        """
        Function required by context manager.
        """
        return self

    def __exit__(self: Server, *args, **kwargs) -> bool:
        """
        Function required by context manager.
        """
        self.shutdown()

        return False

    @staticmethod
    def _start(server_path: pathlib.Path,
               severity: str,
               max_attempts: int = 10) -> None | tuple[subprocess.Popen, str, int]:

        address_file = address_file = tempfile.NamedTemporaryFile()

        config_file = tempfile.NamedTemporaryFile()
        config_data = Server._config_data(severity=severity,
                                          address_file=address_file.name)
        config_file.write(json.dumps(config_data).encode('utf-8'))
        config_file.flush()

        server_proc = subprocess.Popen(
            [server_path, 'run', '-c', config_file.name])

        network_address = None
        for _ in range(max_attempts):
            try:
                address_file.seek(0)
                network_address = json.load(address_file)
                break
            except json.decoder.JSONDecodeError:
                pass

            time.sleep(1.0)

        if network_address is None:
            Server._stop(server_proc)
            return None

        return server_proc, network_address['address'], network_address['port']

    @staticmethod
    def _stop(server_proc: subprocess.Popen) -> None:
        assert server_proc is not None

        server_proc.kill()
        server_proc.wait()

    @staticmethod
    def _config_data(severity: str, address_file: str) -> Dict[str, Any]:
        config_data = {
            'address': 'localhost',
            'port': 0,
            'out': {},
            'log': {
                'level': severity
            },
            'beta': {
                'address-file': address_file
            }
        }

        return config_data
