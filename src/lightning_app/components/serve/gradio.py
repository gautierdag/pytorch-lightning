import abc
from functools import partial
from types import ModuleType
from typing import Any, List, Optional

from lightning_app import LightningWork
from lightning_app.utilities.imports import _is_gradio_available, requires

if _is_gradio_available():
    import gradio
else:
    gradio = ModuleType("gradio")


class ServeGradio(LightningWork, abc.ABC):

    """The ServeGradio Class enables to quickly create a ``gradio`` based UI for your LightningApp.

    In the example below, the ``ServeGradio`` is subclassed to deploy ``AnimeGANv2``.

    .. literalinclude:: ../../../examples/app_components/serve/gradio/app.py
        :language: python

    The result would be the following:

    .. image:: https://pl-flash-data.s3.amazonaws.com/assets_lightning/anime_gan.gif
        :alt: Animation showing how to AnimeGANv2 UI would looks like.
    """

    inputs: Any
    outputs: Any
    examples: Optional[List] = None
    enable_queue: bool = False

    def __init__(self, *args, **kwargs):
        requires("gradio")(super().__init__(*args, **kwargs))
        assert self.inputs
        assert self.outputs
        self._model = None

    @property
    def model(self):
        return self._model

    @abc.abstractmethod
    def predict(self, *args, **kwargs):
        """Override with your logic to make a prediction."""

    @abc.abstractmethod
    def build_model(self) -> Any:
        """Override to instantiate and return your model.

        The model would be accessible under self.model
        """

    def run(self, *args, **kwargs):
        if self._model is None:
            self._model = self.build_model()
        fn = partial(self.predict, *args, **kwargs)
        fn.__name__ = self.predict.__name__
        gradio.Interface(fn=fn, inputs=self.inputs, outputs=self.outputs, examples=self.examples).launch(
            server_name=self.host,
            server_port=self.port,
            enable_queue=self.enable_queue,
        )
