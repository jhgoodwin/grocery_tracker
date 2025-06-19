#!/usr/bin/env python3
import sys
import os

# Add src to PYTHONPATH
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Keep this version check in sync with pyproject.toml's requires-python value
if sys.version_info < (3, 13):
    sys.stderr.write("Python 3.13 or later required\n")
    sys.exit(1)

import argparse
import functools
import inspect
import logging
import os
import shutil
import subprocess
from typing import Callable, Set, Any

from config.logging import setup_logging
logger = logging.getLogger(__name__)

setup_logging()

# Exit codes
EXIT_CODE_SUCCESS = 0
EXIT_CODE_INVALID_COMMAND_LINE_ARGUMENTS = 1
EXIT_CODE_ENVIRONMENT_FILE_NOT_FOUND = 2
EXIT_CODE_TASK_CANNOT_CHAIN_MANUAL_INTERVENTION_REQUIRED = 3
EXIT_CODE_UNKNOWN_ERROR = -1

def task(*, depends_on: list[str] = []):
    def decorator(func: Callable) -> Callable:
        func._is_task = True  # ty: ignore[unresolved-attribute]
        func._depends_on = depends_on  # ty: ignore[unresolved-attribute]
        @functools.wraps(func)
        def wrapper(self, *args: Any, **kwargs: Any):
            # Get all dependencies including inherited ones
            all_deps = []
            deps_to_check = list(depends_on)
            while deps_to_check:
                dep = deps_to_check.pop()
                if dep not in all_deps and hasattr(self, dep):
                    all_deps.append(dep)
                    dep_fn = getattr(self.__class__, dep)
                    if hasattr(dep_fn, '_depends_on'):
                        deps_to_check.extend(dep_fn._depends_on)
            
            # Run all dependencies in order if not completed
            for dep in all_deps:
                if dep not in self._completed:
                    getattr(self, dep)()
            
            # Get the function's signature
            sig = inspect.signature(func)
            
            # If the function expects args parameter, pass it through
            if len(args) == 1 and len(sig.parameters) >= 2:
                second_param = list(sig.parameters.values())[1]
                if second_param.name == 'args':
                    return func(self, args[0])
            
            # Otherwise bind arguments to parameters
            bound = sig.bind(self, *args, **kwargs)
            bound.apply_defaults()
            result = func(*bound.args, **bound.kwargs)
            # Mark task as completed
            task_name = getattr(self, args[0]).__name__ if args else func.__name__ # ty: ignore[unresolved-attribute]
            self._completed.add(task_name)
            return result
        return wrapper
    return decorator

class EnvironmentFileNotFound(FileNotFoundError):
    def __init__(self, env_file: str):
        super().__init__(f"Environment file not found: {env_file}. Copy .env.example to {env_file} to create a new one.")

class SetupBeforeLoadEnvError(RuntimeError):
    def __init__(self):
        super().__init__("setup must be run before load_env")

class TaskCannotChainManualInterventionRequired(RuntimeError):
    def __init__(self, task_name: str):
        super().__init__(f"Task {task_name} stopped. Manual intervention is required.")

class Builder:
    def __init__(self):
        self._completed: Set[str] = set()

    @property
    def tasks(self) -> Set[str]:
        return {name for name, attr in self.__class__.__dict__.items() 
               if getattr(attr, '_is_task', False)}

    def configure_parser(self, parser: argparse.ArgumentParser) -> None:
        subparsers = parser.add_subparsers(dest='task', required=True)
        for task in sorted(self.tasks):
            task_parser = subparsers.add_parser(task)
            task_method = getattr(self, task)
            setup_method = getattr(task_method, '_setup_parser', None)
            if setup_method:
                setup_method(task_parser)

    def __getattribute__(self, name: str):
        # Don't auto-run tasks during attribute lookup
        # This prevents recursive task execution during dependency resolution
        return super().__getattribute__(name)
    
    def load_env(self, env_file: str = '.env'):
        if not "setup" in self._completed:
            raise SetupBeforeLoadEnvError()
        if not os.path.exists(env_file):
            raise EnvironmentFileNotFound(env_file)
        from dotenv import load_dotenv
        load_dotenv(env_file)

    # region Task parsers
    @task(depends_on=["setup"])
    def clean(self, all: bool = False):
        """Clean temporary files and logs"""
        def _setup_parser(parser: argparse.ArgumentParser) -> None:
            parser.add_argument('--all', action='store_true', help='Remove all generated files')
        
        logger.info("Cleaning temporary files and logs...")
        paths = [
            "./logs",
            "./__pycache__",
            "./build",
            "./dist"
        ]
        if all:
            paths.extend(["./generated_files"])
        for path in paths:
            if not os.path.exists(path):
                continue
            if os.path.isfile(path):
                os.remove(path)
            else:
                shutil.rmtree(path)

    @task(depends_on=["setup"])
    def config(self, env_file: str = '.env'):
        """Validate and configure settings"""
        def _setup_parser(parser: argparse.ArgumentParser) -> None:
            parser.add_argument('--env-file', default=env_file, help='Environment file to load')
        
        logger.info("Validating configuration...")
        if not os.path.exists(env_file):
            if env_file == '.env':
                shutil.copyfile('.env.example', env_file)
                logger.info(f"Created {env_file} from .env.example")
                # guide user to edit the values in the file.
                logger.info(f"Please edit {env_file} to configure your environment.")
                raise TaskCannotChainManualInterventionRequired("config")
            else:
                raise EnvironmentFileNotFound(env_file)
        # TODO: Implement configuration validation
        # This would typically check environment variables, config files, etc.

    @task(depends_on=["test"])
    def deploy(self, env: str = "dev"):
        """Deploy the application"""
        def _setup_parser(parser: argparse.ArgumentParser) -> None:
            parser.add_argument('--env', default='dev', help='Environment to deploy to')

        logger.info(f"Deploying to {env}...")
        # TODO: Implement deployment logic

    @task(depends_on=["config"])
    def run(self):
        """Run the FastAPI server and website"""
        def _setup_parser(parser: argparse.ArgumentParser) -> None:
            pass

        logger.info("Starting FastAPI server...")
        from webapp.main import main
        main()

    @task()
    def setup(self):
        """Setup local environment and verify dependencies"""
        logger.info("Setting up environment...")
        
        try:
            subprocess.run(["uv", "sync"], check=True)
        except FileNotFoundError:
            logger.error("uv not found. Please install uv first: brew install uv")
            raise
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install dependencies: {e}")
            raise

    @task(depends_on=["setup"])
    def test(self):
        """Run tests using pytest"""
        import pytest
        logger.info("Running tests...")
        try:
            exit_code = pytest.main(["src/tests", "-v"])
            if exit_code != 0:
                raise RuntimeError(f"Tests failed with exit code {exit_code}")
        except Exception as e:
            logger.error(f"Tests failed: {e}")
            raise

    # endregion Task parsers

def get_task_plus_args(builder: Builder, args: argparse.Namespace):
    fn_task: Callable = getattr(builder, args.task)
    sig = inspect.signature(fn_task)
    
    pos_args = []
    kwargs = {}
    
    for name, param in sig.parameters.items():
        if name == "self" or not hasattr(args, name):
            continue
            
        value = getattr(args, name)
        if param.kind in (param.POSITIONAL_ONLY, param.POSITIONAL_OR_KEYWORD):
            pos_args.append(value)
        elif param.kind == param.KEYWORD_ONLY:
            kwargs[name] = value
            
    return fn_task, pos_args, kwargs

def main() -> int:
    parser = argparse.ArgumentParser(description="Build and development tools")
    builder = Builder()
    builder.configure_parser(parser)
    
    args = parser.parse_args()
    if not hasattr(builder, args.task):
        logger.error(f"Unknown task: {args.task}")
        return EXIT_CODE_INVALID_COMMAND_LINE_ARGUMENTS

    try:
        task_method = getattr(builder, args.task)
        if not getattr(task_method, '_is_task', False):
            logger.error(f"{args.task} is not a valid task")
            return EXIT_CODE_INVALID_COMMAND_LINE_ARGUMENTS
            
        fn_task, pos_args, kwargs = get_task_plus_args(builder, args)
        return_val = fn_task(*pos_args, **kwargs)
        if return_val is not None:
            return return_val
        return EXIT_CODE_SUCCESS
    except Exception as e:
        logger.error(f"Task failed: {e}")
        return EXIT_CODE_UNKNOWN_ERROR

if __name__ == '__main__':
    sys.exit(main())
