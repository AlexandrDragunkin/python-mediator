#!/usr/bin/env python3
from typing import Any, Dict, Hashable, Iterable, Optional, Sequence

from mediator.common.factory import (
    CallableHandlerPolicy,
    HandlerFactoryCascade,
    PolicyType,
)
from mediator.common.modifiers import ModifierFactory
from mediator.common.registry import (
    HandlerEntry,
    HandlerRegistry,
    LookupHandlerStoreError,
    MappingHandlerStore,
)
from mediator.common.types import ActionCallType, ActionResult, ActionSubject
from mediator.request.base import RequestExecutor


class _RequestExecutorHandlerStore(MappingHandlerStore):
    """
    Utility request handler store, based on mapping handler store to work with local request execution.
    Хранилище обработчиков служебных запросов, основанное на сопоставлении хранилища обработчиков для работы с локальным выполнением запросов.
    """

    _calls: Dict[Hashable, ActionCallType]

    def __init__(self):
        """
        Инициализирует пустое хранилище обработчиков исполнителя запроса.
        """
        super().__init__()
        self._calls = {}

    def add(self, entry: HandlerEntry):
        """
        Добавляет данную запись обработчика(handler entry) в хранилище и подключает запись обработчика(handler entry) к запросам на обработку(process requests).
        :param entry: запись обработчика для подключения
        :raises CollisionHandlerStoreError:
        когда запись обработчика с заданным ключом уже существует в этом хранилище
        """
        super().add(entry)
        self._map_call(entry)

    def include(self, entries: Iterable[HandlerEntry]):
        """
        Adds all handler entries from given iterable into store and connects all handler entries from given iterable to process requests.
        Добавляет все записи обработчика из данного iterable в хранилище и соединяет все записи обработчика из данного iterable с запросами на обработку.
        :param entries: итератор записей обработчика
        :raises CollisionHandlerStoreError:
        когда запись обработчика с заданным ключом уже существует в этом хранилище
        """
        super().include(entries)
        for entry in entries:
            self._map_call(entry)

    def _map_call(self, entry: HandlerEntry):
        """
        Sets given handler entry to request processing.
        :param entry: handler entry to add
        """
        self._calls[entry.key] = entry.handler_pipeline()

    async def __call__(self, action: ActionSubject) -> ActionResult:
        """
        Executes given action object to be processed as request
        by related handler.
        :param action: request action to be processed
        :raises LookupHandlerStoreError:
        when there is no matching handler to process given request
        :return: request processing action result
        """
        key = action.key
        call = self._calls.get(key)
        if call is None:
            raise LookupHandlerStoreError(f"Handler not defined for key {key}")
        return await call(action)


class LocalRequestBus(HandlerRegistry, RequestExecutor):
    """
    Local request bus.

    Performs request execution locally in-place.
    Connects behaviours of handler registry and request executor interface.
    """

    def __init__(
        self,
        policies: Optional[Sequence[PolicyType]] = None,
        cascade: Optional[HandlerFactoryCascade] = None,
        modifiers: Sequence[ModifierFactory] = (),
    ):
        """
        Initializes local request bus with given specification.
        :param policies:
        (optional) sequence of policies to be used as recipe
        to convert raw objects into handlers;
        if not provided default `CallableHandlerPolicy` will be used;
        overwritten when cascade is provided
        :param cascade:
        (optional) custom handler factory cascade to customize
        policy into handler factory mapping
        :param modifiers: sequence of modifiers to be applied on new handler entries
        """
        executor_store = _RequestExecutorHandlerStore()
        HandlerRegistry.__init__(
            self,
            store=executor_store,
            policies=policies or [CallableHandlerPolicy()],
            cascade=cascade,
            modifiers=modifiers,
        )
        self._executor = executor_store

    async def execute(self, obj: Any, **kwargs):
        """
        Executes given request.
        :param obj: request object
        :param kwargs: request extra arguments
        :raises LookupHandlerStoreError:
        when there is no matching handler to process given request
        :return: request processing result
        """
        result = await self._executor(ActionSubject(subject=obj, inject=kwargs))
        assert isinstance(
            result, ActionResult
        ), "modifier or handler should provide `ActionResult` type object"
        return result.result
