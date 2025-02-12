import contextlib
from typing import Any, Callable, List, Self, Sequence, Type

from dash import Dash, Patch

from .callback_manager import CallbackManager
from .library import Figure


class Context:
    """A context manager class for handling Dash figures and their callbacks.

    This class manages a collection of figures and their associated callbacks in a Dash application.
    It provides functionality for loading callback managers, building figures, and registering callbacks.

    Attributes:
        figures (List[Figure]): A list of Figure instances managed by this context.
        callback_manager (CallbackManager): The callback manager instance for handling figure callbacks.
        callback_manager_type (Type[CallbackManager]): The type of callback manager to be used.
    """

    figures: List[Figure]
    callback_manager: CallbackManager

    def __new__(cls, *, figures: Sequence[Figure], callback_manager_type: Type[CallbackManager] | None):
        """Initialize a new Context instance.

        Args:
            figures (Sequence[Figure]): A sequence of Figure instances to be managed by this context.
            callback_manager_type (Type[CallbackManager] | None): The type of callback manager to use.
                Can be None if no callback management is needed.

        Returns:
            Context: The class itself, as this implements the singleton pattern.

        Raises:
            AssertionError: If figures is empty, contains non-Figure instances, or if
                callback_manager_type is not a subclass of CallbackManager.
        """
        figures = list(figures)
        assert len(figures) > 0
        assert all([isinstance(fig, Figure) for fig in figures])
        with contextlib.suppress(TypeError):
            assert issubclass(callback_manager_type, CallbackManager)

        cls.figures = figures
        cls.callback_manager_type = callback_manager_type
        cls.callback_manager = None
        return cls

    @classmethod
    def load_callback_manager(cls, app: Dash, **kwargs) -> Type[Self]:
        """Load and initialize the callback manager for the context.

        Args:
            app (Dash): The Dash application instance to register callbacks with.
            **kwargs: Additional keyword arguments passed to the callback manager constructor.

        Returns:
            Type[Self]: The context class with an initialized callback manager.
        """
        if not cls.callback_manager and cls.callback_manager_type:
            cls.callback_manager = cls.callback_manager_type(app, **kwargs)

        return cls

    @classmethod
    def build_figures(cls, clear_before: bool = True) -> List[Any]:
        """Build all figures managed by this context.

        Args:
            clear_before (bool, optional): Whether to clear existing figures before building new ones.
                Defaults to True.

        Returns:
            List[Any]: A Patch object containing all built figures.
        """
        patch = Patch()
        if clear_before:
            patch.clear()

        patch.extend([fig.build() for fig in cls.figures])
        return patch

    @classmethod
    def register_callbacks(cls) -> List[Callable]:
        """Register callbacks for all figures managed by this context.

        Returns:
            List[Callable]: A list of registered callback functions. Returns an empty list if no
            callback manager is available.
        """
        if not cls.callback_manager:
            return []

        return [fig.register_callback(callback_manager=cls.callback_manager) for fig in cls.figures]
