from typing import Callable

from dash import Dash


class CallbackManager:
    """A utility class for managing Dash callbacks.

    This class provides a centralized way to register and manage callbacks in a Dash application.
    It ensures that callbacks are only registered once per callback_id and maintains a reference
    to all registered callbacks.

    Attributes:
        _callbacks (dict): A class-level dictionary storing registered callbacks.
        _app (Dash): A class-level reference to the Dash application instance.
    """

    _callbacks = {}
    _app = None

    def __new__(cls, app: Dash, **kwargs):
        """Initialize the CallbackManager with a Dash application instance.

        Args:
            app (Dash): The Dash application instance to register callbacks with.
            **kwargs: Additional keyword arguments (unused).

        Returns:
            CallbackManager: The class itself, as this implements the singleton pattern.
        """
        cls._app = app
        return cls

    @classmethod
    def register_callback(
        cls,
        callback_id: str,
        callback_func: Callable,
        *,
        outputs: list,
        inputs: list,
        states: list = [],
        prevent_initial_call: bool = True,
        allow_duplicate: bool = True,
        **kwargs,
    ) -> Callable | None:
        """Register a callback with the Dash application.

        This method registers a callback function with the specified parameters if it hasn't
        been registered before with the given callback_id.

        Args:
            callback_id (str): Unique identifier for the callback.
            callback_func (Callable): The callback function to register.
            outputs (list): List of Dash component properties that the callback updates.
            inputs (list): List of Dash component properties that trigger the callback.
            states (list, optional): List of Dash component properties that are read by the callback
                but don't trigger it. Defaults to an empty list.
            prevent_initial_call (bool, optional): Whether to prevent the callback from being called
                when the app starts. Defaults to True.
            allow_duplicate (bool, optional): Whether to allow duplicate callback registrations.
                Defaults to True.
            **kwargs: Additional keyword arguments passed to the Dash callback decorator.

        Returns:
            Callable | None: The registered callback function if successful, None if the registration
            fails due to missing callback_id or callback_func.
        """
        if callback_id is None or callback_func is None:
            return

        stored_callback = cls._callbacks.get(callback_id)
        if stored_callback is None:
            stored_callback = cls._app.callback(
                outputs,
                inputs,
                states,
                allow_duplicate=allow_duplicate,
                prevent_initial_call=prevent_initial_call,
                **kwargs,
            )(callback_func)
            cls._callbacks[callback_id] = stored_callback

        return stored_callback
