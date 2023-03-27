"""
Sieve workflow to query copilot for video editing.
"""
import sieve


@sieve.function(name="temp_query", persist_output=True)
def temp_query(command: str) -> str:
    for i in range(5):
        yield command


@sieve.workflow(name="copilot_query")
def copilot_query(command: str) -> str:
    return temp_query(command)
