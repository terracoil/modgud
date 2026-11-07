"""AST transformation for implicit return functionality."""

from __future__ import annotations

import ast
import builtins
import functools
import inspect
import textwrap
import types
from collections.abc import Mapping
from typing import Any, Callable, ParamSpec, TypeVar, TypeVarTuple, cast

from idunn import Adapter, LifecycleEnum

from modgud.domain.enums import EopFormEnum
from modgud.domain.errors import ExplicitReturnDisallowedError, UnsupportedConstructError
from modgud.domain.ports import EopPort, ImplicitReturnPort
from modgud.domain.types import F, T
from modgud.infrastructure.ast import (
  FormLowerer,
  MarkerResolver,
  NoExplicitReturnChecker,
  TailRewriter,
  TopLevelTransformer,
)
from modgud.infrastructure.internal import MethodDescriptors


@Adapter(ImplicitReturnPort, lifecycle=LifecycleEnum.SINGLETON)
class ImplicitReturnAdapter(ImplicitReturnPort):
  """AST transformation for implicit return functionality; Idunn's adapter for the port."""

  def transform(self, func: F, *, forms: Mapping[EopFormEnum, EopPort]) -> F:
    """Transform a function so the last expression in each branch is returned.

    ``func`` may also be a ``staticmethod`` / ``classmethod`` object; the result is then a
    descriptor of the same kind. Every ``eop_`` form in the body is lowered through ``forms``.

    :raises TypeError: if ``func`` is already a ``guarded_expression`` wrapper. The rewrite
      re-reads the original source, so the guards would silently disappear.
    """
    plain, kind = MethodDescriptors.unwrap(func)
    if getattr(plain, '__modgud_guarded__', False):
      raise TypeError(
        '@implicit_return() must sit below @guarded_expression; put it closer to the def, '
        'or pass implicit_return=True'
      )
    transformed: Callable[..., Any] = self.transform_function(plain, forms=forms)
    transformed.__implicit_return__ = True  # type: ignore[attr-defined]
    return cast(F, MethodDescriptors.rewrap(transformed, kind))

  def transform_function(
    self,
    func: Callable[..., T],
    *,
    forms: Mapping[EopFormEnum, EopPort],
    implicit_return: bool = True,
  ) -> Callable[..., T]:
    """Transform a function to use implicit returns and lower its ``eop_`` forms.

    Extracts source, lowers every form through its port in ``forms``, applies the
    implicit-return AST rewrite, recompiles in the function's original global namespace, and
    preserves metadata. With ``implicit_return=False`` the tail rewrite is skipped, and a
    function that references no form is returned as it is, without reading its source.

    :param func: Function to transform.
    :param forms: The port that lowers each form.
    :param implicit_return: Whether to apply the tail rewrite as well.
    :returns: Transformed function.
    :raises ValueError: If source cannot be extracted.
    :raises ImplicitReturnError: If transformation fails.
    """
    resolver: MarkerResolver = MarkerResolver(self._scope_of(func))
    code: Any = getattr(func, '__code__', None)
    if not implicit_return and (code is None or not resolver.references(code)):
      return func
    try:
      source = inspect.getsource(func)
    except (TypeError, OSError) as e:
      raise ValueError(f'Cannot extract source from {func.__name__}: {str(e)}') from e

    class_path: tuple[str, ...] = self._class_path(func)
    dedented_src = textwrap.dedent(source)
    transformed_ast, _ = self.apply_implicit_return_transform(
      dedented_src,
      func.__name__,
      class_path,
      self._enclosing_type_params(func),
      lowerer=FormLowerer(forms, resolver),
      implicit_return=implicit_return,
    )
    self._strip_signature_expressions(transformed_ast, func.__name__)
    code = compile(transformed_ast, f'<implicit_return:{func.__qualname__}>', 'exec')
    # Only builtins: defaults and annotations were stripped above and are reused from `func`,
    # so nothing in the signature needs module or class scope while this exec runs.
    namespace: dict[str, Any] = {'__builtins__': func.__globals__.get('__builtins__', __builtins__)}
    exec(code, namespace)
    owner: Any = namespace
    for name in class_path:
      owner = owner[name] if isinstance(owner, dict) else getattr(owner, name)
    compiled: Any = (
      owner[func.__name__] if isinstance(owner, dict) else getattr(owner, func.__name__)
    )
    # Re-bind the code object to the function's *live* globals: the body then sees names defined
    # after decoration (and its own class, once the class statement finishes), not a snapshot.
    transformed_func: Callable[..., T] = types.FunctionType(
      compiled.__code__,
      func.__globals__,
      func.__name__,
      func.__defaults__,  # already evaluated in the original scope (class body included)
      compiled.__closure__,
    )
    transformed_func.__kwdefaults__ = func.__kwdefaults__
    transformed_func.__qualname__ = func.__qualname__
    self._share_type_params(func, transformed_func)
    transformed_func.__doc__ = func.__doc__
    transformed_func.__dict__.update(func.__dict__)
    annotate: Any = getattr(func, '__annotate__', None)
    if annotate is not None:
      transformed_func.__annotate__ = annotate  # type: ignore[attr-defined]  # 3.14+: keep lazy
    else:
      transformed_func.__annotations__ = func.__annotations__
    return transformed_func

  @classmethod
  def _scope_of(cls, func: Callable[..., Any]) -> dict[str, Any]:
    """Where the body's free names resolve: builtins, then globals, then the closure."""
    globals_: dict[str, Any] = getattr(func, '__globals__', {})
    module_builtins: Any = globals_.get('__builtins__', builtins)
    found: dict[str, Any] = (
      dict(module_builtins) if isinstance(module_builtins, dict) else vars(module_builtins)
    )
    found.update(globals_)
    if hasattr(func, '__code__'):
      found.update(cls._closure_values(func))
    return found

  @staticmethod
  def _closure_values(func: Callable[..., Any]) -> dict[str, Any]:
    """Return ``func``'s closure as ``{name: value}``, skipping cells that are still empty."""
    values: dict[str, Any] = {}
    for name, cell in zip(func.__code__.co_freevars, func.__closure__ or (), strict=True):
      try:
        values[name] = cell.cell_contents
      except ValueError:  # an empty cell: the enclosing scope never assigned it
        continue
    return values

  @classmethod
  def _enclosing_type_params(cls, func: Callable[..., Any]) -> tuple[str, ...]:
    """Names of PEP 695 type parameters ``func`` closes over from an enclosing generic class.

    ``class Box[T]`` gives its methods a closure cell for ``T``. The stand-in class the method
    is re-compiled in declares the same names, so the body still resolves them as free
    variables and ``_share_type_params`` can point them at the originals.
    """
    kinds: tuple[type, ...] = (TypeVar, ParamSpec, TypeVarTuple)
    return tuple(
      name for name, value in cls._closure_values(func).items() if isinstance(value, kinds)
    )

  @classmethod
  def _share_type_params(cls, original: Callable[..., Any], rebuilt: Callable[..., Any]) -> None:
    """Make the rebuilt function see the original's PEP 695 type parameters (Python 3.12+).

    The re-compile creates fresh ``T`` objects for ``def f[T]`` and for the stand-in class's
    parameters. Every closure cell of the rebuilt function that is named like one of the
    original's type parameters, or like a value in the original's closure, is retargeted at
    that object; ``__type_params__`` is copied, so ``f.__type_params__[0]`` is the ``T`` the
    body returns.
    """
    params: tuple[Any, ...] = getattr(original, '__type_params__', ())
    if params:
      rebuilt.__type_params__ = params  # type: ignore[attr-defined]
    by_name: dict[str, Any] = {
      **cls._closure_values(original),
      **{param.__name__: param for param in params},
    }
    for name, cell in zip(rebuilt.__code__.co_freevars, rebuilt.__closure__ or (), strict=True):
      if name in by_name:
        cell.cell_contents = by_name[name]

  @staticmethod
  def _strip_signature_expressions(tree: ast.Module, func_name: str) -> None:
    """Drop defaults and annotations from the target definition before it is re-compiled.

    Their values are taken from the original function instead, so a default that names a
    class attribute or a module global never has to be re-evaluated out of scope.
    """
    for node in ast.walk(tree):
      if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func_name:
        node.args.defaults = []
        node.args.kw_defaults = [None] * len(node.args.kwonlyargs)
        node.returns = None
        for arg in (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs):
          arg.annotation = None
        for star in (node.args.vararg, node.args.kwarg):
          if star is not None:
            star.annotation = None

  @staticmethod
  def _class_cell_uses(fn_node: ast.AST) -> ast.AST | None:
    """First zero-argument ``super()`` or bare ``__class__`` in the body, nested classes excluded.

    Nested classes build their own ``__class__`` cell at runtime, so they are left alone.
    """
    found: ast.AST | None = None
    pending: list[ast.AST] = [fn_node]
    while pending and found is None:
      node = pending.pop()
      is_super = (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == 'super'
        and not node.args
        and not node.keywords
      )
      if is_super or (isinstance(node, ast.Name) and node.id == '__class__'):
        found = node
      elif not isinstance(node, ast.ClassDef) or node is fn_node:
        pending.extend(ast.iter_child_nodes(node))
    return found

  @staticmethod
  def _class_path(func: Callable[..., Any]) -> tuple[str, ...]:
    """Names of the classes enclosing ``func``, innermost last; empty for a plain function.

    Only the part of ``__qualname__`` after the last ``<locals>`` counts: classes defined
    inside a function body are still re-created, functions are not.
    """
    tail: str = func.__qualname__.rsplit('<locals>.', 1)[-1]
    return tuple(tail.split('.')[:-1])

  @classmethod
  def transform_function_ast(
    cls,
    fn_node: ast.AST,
    func_name: str,
    *,
    lowerer: FormLowerer | None = None,
    implicit_return: bool = True,
  ) -> ast.AST:
    """Transform function AST to enforce implicit return semantics.

    Transforms a FunctionDef/AsyncFunctionDef AST node to enforce
    implicit return semantics.

    Steps:
      1. Verify no explicit `return` anywhere in the body, nested defs included
      2. Lower every ``eop_`` form through ``lowerer``, when one is given
      3. Rewrite tail of the function body to assign to a hidden result var
      4. Append a single `return __implicit_result`

    With ``implicit_return=False`` steps 1, 3 and 4 are skipped: the body keeps its explicit
    ``return`` statements and only the forms are lowered.

    :param fn_node: The function AST node to transform.
    :param func_name: Name of the function (for error messages).
    :param lowerer: Lowers the ``eop_`` forms; ``None`` leaves the body's calls as they are.
    :param implicit_return: Whether to apply the tail rewrite.
    :returns: The transformed AST node with implicit return semantics.
    :raises ExplicitReturnDisallowedError: If an explicit return is found anywhere in the body.
    :raises MissingImplicitReturnError: If a block cannot yield a name.
    :raises UnsupportedConstructError: If an unsupported construct is found.
    :raises MarkerUsageError: If an ``eop_`` form is malformed.
    :raises MarkerPlacementError: If an ``eop_`` form sits where it cannot be lowered.
    """
    assert isinstance(fn_node, (ast.FunctionDef, ast.AsyncFunctionDef))
    body = fn_node.body

    class_cell_use: ast.AST | None = cls._class_cell_uses(fn_node)
    if class_cell_use is not None:
      raise UnsupportedConstructError(
        f'Zero-argument super() and __class__ are not supported in implicit-return function '
        f"'{func_name}'; the re-compiled body has no __class__ cell. Use super(ClassName, self).",
        getattr(class_cell_use, 'lineno', None),
        getattr(class_cell_use, 'col_offset', None),
      )

    # Refuse any explicit return in the body, nested defs included
    checker = NoExplicitReturnChecker()
    for stmt in body:
      checker.visit(stmt)
    if implicit_return and checker.found is not None:
      line, col = checker.found
      raise ExplicitReturnDisallowedError(
        f"Explicit `return` is disallowed in implicit-return function '{func_name}'; "
        'let the last expression of each branch be the value, or pass implicit_return=False.',
        line,
        col,
      )

    # Checks first, so a refused function is never half rewritten; the lowering may add
    # generated nested functions that hold their own `return`, which the tail rewrite never enters.
    if lowerer is not None:
      lowerer.lower_function(fn_node)
      body = fn_node.body
    if not implicit_return:
      return fn_node

    result_name = '__implicit_result'
    rewriter = TailRewriter(result_name)

    # Preserve docstrings - they're metadata, not executable code to transform
    actual_body = body
    docstring_stmt = None
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
      if isinstance(body[0].value.value, str):
        # First statement is a docstring, skip it
        docstring_stmt = body[0]
        actual_body = body[1:]

    # Transform the actual body (excluding docstring)
    if actual_body:
      new_body = rewriter.rewrite_block(actual_body)
    else:
      # Only docstring, no actual code - return None
      new_body = [
        ast.Assign(
          targets=[ast.Name(id=result_name, ctx=ast.Store())], value=ast.Constant(value=None)
        )
      ]

    # Prepend docstring if it existed
    if docstring_stmt:
      new_body.insert(0, docstring_stmt)

    # Append the single return
    new_body.append(ast.Return(value=ast.Name(id=result_name, ctx=ast.Load())))
    fn_node.body = new_body
    return fn_node

  @classmethod
  def apply_implicit_return_transform(
    cls,
    func_source: str,
    func_name: str,
    class_path: tuple[str, ...] = (),
    class_type_params: tuple[str, ...] = (),
    *,
    lowerer: FormLowerer | None = None,
    implicit_return: bool = True,
  ) -> tuple[ast.Module, str]:
    """Apply implicit return transformation to function source code.

    :param func_source: The source code of the function (dedented).
    :param func_name: The name of the function to transform.
    :param class_path: Enclosing class names, outermost first. The rewritten function is
      nested in empty stand-in classes of those names so private-name mangling
      (``self.__x`` -> ``self._Cls__x``) happens exactly as it did in the original class.
    :param class_type_params: PEP 695 type-parameter names the innermost stand-in class
      declares (Python 3.12+), so a body that names ``T`` from ``class Box[T]`` still
      compiles as a closure over ``T``.
    :param lowerer: Lowers the ``eop_`` forms; ``None`` leaves the body's calls as they are.
    :param implicit_return: Whether to apply the tail rewrite.
    :returns: Tuple of (transformed_ast, filename hint for compile()).
    :raises ExplicitReturnDisallowedError: If explicit return found.
    :raises MissingImplicitReturnError: If a block cannot yield a name.
    :raises UnsupportedConstructError: If an unsupported construct is found.
    """
    tree = ast.parse(func_source)
    transformer = TopLevelTransformer(
      func_name,
      functools.partial(
        cls.transform_function_ast, lowerer=lowerer, implicit_return=implicit_return
      ),
    )
    new_tree: ast.Module = transformer.visit(tree)
    for depth, class_name in enumerate(reversed(class_path)):
      stand_in = ast.ClassDef(
        name=class_name, bases=[], keywords=[], body=new_tree.body, decorator_list=[]
      )
      if depth == 0 and class_type_params:
        type_var: Any = getattr(ast, 'TypeVar')  # noqa: B009 - absent before Python 3.12
        stand_in.type_params = [type_var(name=name) for name in class_type_params]  # type: ignore[attr-defined]
      new_tree.body = [stand_in]
    ast.fix_missing_locations(new_tree)
    return new_tree, f'<{func_name}-implicit>'
