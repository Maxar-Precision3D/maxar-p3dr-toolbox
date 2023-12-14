from __future__ import annotations  # noqa

import pathlib
from PIL import Image
from typing import Any, Dict

from maxar_canv import Canv, Playback
from .server import Server


class CanvRegistrator():
    """
    Class that is using a Server to register a canonic video.
    """

    def __init__(self: CanvRegistrator, server: Server, max_in_flight: int) -> None:
        """
        Create a CanvRegistrator.

        Parameters:
            server: A live server.
            max_in_flight: Threshold telling how many requests that can be in
                           flight before the registrator is starting to throttle.
        """
        self._server = server
        self._max_in_flight = max_in_flight
        self._stream_id = -1
        self._active_frames = dict()
        self._canv = None

        url = self._server.url()
        version = self._server.query_version()
        print('Connected to server:')
        print(f' - URL={url}')
        print(f" - revision={version['revision']}")
        print(f" - branch={version['branch']}")

    def run(self: CanvRegistrator, playback: Playback,
            canv: Canv, references: list[pathlib.Path]) -> None:
        """
        Run the CanvRegistrator using its configured server.

        Parameters:
            playback: The canonic video playback object.
            canv: The Canv object where to put the registered frames.
            references: The reference databases to used for the registration.
        """
        self._stream_id = self._server.open_stream(references=references)
        print(f'Stream #{self._stream_id} is opened')

        self._active_frames = dict()
        self._canv = canv

        # Push all the data from the playback ...
        for request_id, data in enumerate(playback):
            self._push_request(frame_id=request_id, data=data)

            # ... and simultaneously handle responses so that the
            # max number in flight never is exceeded.
            while len(self._active_frames) >= self._max_in_flight:
                self._pop_response()

        # Wait for the last few frames.
        while len(self._active_frames) > 0:
            self._pop_response()

    def _push_request(self: CanvRegistrator, frame_id: int,
                      data: tuple[Dict[str, Any], Image.Image]) -> None:
        metadata, image = data
        camera = metadata['cam']

        if self._server.request_registration(stream_id=self._stream_id,
                                             frame_id=frame_id,
                                             camera=camera,
                                             image=image):
            assert frame_id not in self._active_frames
            self._active_frames[frame_id] = {
                'camera': camera,
                'received': False
            }

    def _pop_response(self: CanvRegistrator) -> None:
        result = self._server.get_registration_result()
        if result is not None:
            frame_id, fom, camera, err_msg = result
            assert frame_id in self._active_frames
            if camera is not None:
                self._active_frames[frame_id] = {
                    'camera': camera,
                    'received': True
                }
                print(f'Frame #{frame_id} received with FOM={fom:.2f}')
            else:
                self._active_frames[frame_id]['received'] = True
                print(f'Frame #{frame_id} received with error={err_msg}')

        earliest_id = list(self._active_frames)[0]
        if self._active_frames[earliest_id]['received']:
            metadata = {
                'cam': self._active_frames[earliest_id]['camera']
            }
            self._canv.append(metadata)
            del self._active_frames[earliest_id]
