# UAIEOS Engine Specification: Autonomous Debugger

This document specifies the traceback parsing logic, dynamic repair prompt generators, and sandboxed test execution loops that implement the UAIEOS Autonomous Debugger Engine.

---

## 1. Debugger Subsystem Architecture

The Autonomous Debugger intercepts execution errors, isolates them inside a secure sandbox container, and runs a repair event-loop until tests pass or the circuit breaker is tripped.

```
                  [Runtime Error Intercepted]
                              |
                              v
                +----------------------------+
                |    Error Traceback Parser  |
                +----------------------------+
                              |
                              v
                +----------------------------+
                | Dynamic Prompt Generator   | -> (Creates system query prompt)
                +----------------------------+
                              |
                              v
                +----------------------------+
                |      Sandbox Executor      | -> (Runs candidate code in isolation)
                +----------------------------+
                              |
                 /------------+------------\
                /                           \
               v                             v
       [Verification Fails]          [Verification Passes]
       (Retry up to Limit)           (Merge Code to Core)
```

---

## 2. Traceback Parser & Context Collector

To provide highly specific diagnostic context to the healing models, the debugger parses standard output and errors into structured records.

```python
import traceback
import sys
from typing import Dict, Any

class TracebackParser:
    @staticmethod
    def parse_exception(exc: Exception) -> Dict[str, Any]:
        """Parses a runtime python exception into structured diagnostic metrics."""
        exc_type, exc_value, exc_traceback = sys.exc_info()
        
        # Format the full standard traceback list
        formatted_list = traceback.format_tb(exc_traceback)
        tb_string = "".join(formatted_list)
        
        # Extract the line of failure from the last stack frame
        tb_frames = traceback.extract_tb(exc_traceback)
        last_frame = tb_frames[-1] if tb_frames else None
        
        return {
            "error_type": exc.__class__.__name__,
            "error_message": str(exc),
            "traceback": tb_string,
            "filename": last_frame.filename if last_frame else "Unknown",
            "line_number": last_frame.lineno if last_frame else -1,
            "failed_statement": last_frame.line if last_frame else "Unknown"
        }
```

---

## 3. Sandboxed Execution Runner

The sandbox runner compiles the generated script in an isolated thread or sub-process to prevent side effects (such as memory leaks or filesystem damage).

```python
import sys
import io
from typing import Tuple

class SandboxExecutionRunner:
    @staticmethod
    def run_safe(code_string: str, global_context: dict = None) -> Tuple[bool, str]:
        """Executes candidate code inside a restricted execution namespace.
        Returns a tuple: (success: bool, output_log: str)
        """
        # Save standard streams
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        
        # Redirect outputs
        redirected_output = io.StringIO()
        redirected_error = io.StringIO()
        sys.stdout = redirected_output
        sys.stderr = redirected_error
        
        # Restrict environment execution flags
        local_scope = {}
        if global_context is None:
            global_context = {
                "__builtins__": {
                    "abs": abs,
                    "dict": dict,
                    "list": list,
                    "int": int,
                    "float": float,
                    "str": str,
                    "range": range,
                    "len": len,
                    "Exception": Exception,
                    "TypeError": TypeError,
                    "ValueError": ValueError,
                    "print": print
                }
            }
            
        success = True
        try:
            # Compile first to catch syntax errors immediately
            compiled = compile(code_string, "<sandbox_eval>", "exec")
            exec(compiled, global_context, local_scope)
        except Exception as e:
            success = False
            sys.stderr.write(traceback.format_exc())
        finally:
            # Restore standard streams
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            
        logs = redirected_output.getvalue() + redirected_error.getvalue()
        return success, logs
```

---

## 4. Self-Healing Integration Loop

The self-healing workflow orchestrates the traceback parsing, LLM calls (guided by prompts in [PART_14_AUTONOMOUS_AI_OPERATIONS.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/PART_14_AUTONOMOUS_AI_OPERATIONS.md#L35-L65)), and the sandbox runner.

```python
class SelfHealingLoop:
    def __init__(self, llm_client: Any, max_attempts: int = 3):
        self.llm_client = llm_client
        self.max_attempts = max_attempts

    def repair_pipeline_code(self, original_code: str, target_exception: Exception) -> Tuple[bool, str]:
        diagnostics = TracebackParser.parse_exception(target_exception)
        current_code_attempt = original_code
        
        for attempt in range(1, self.max_attempts + 1):
            # Formulate the healing prompt
            prompt = self._build_prompt(current_code_attempt, diagnostics)
            
            # Request patched code from LLM
            llm_response = self.llm_client.generate(prompt)
            parsed_patch = self._parse_json_block(llm_response)
            candidate_code = parsed_patch.get("corrected_code", "")
            
            # Verify candidate inside the sandbox runner
            success, logs = SandboxExecutionRunner.run_safe(candidate_code)
            if success:
                return True, candidate_code
                
            # If sandbox validation fails, feed the compiler traceback back into loop
            diagnostics["traceback"] = logs
            diagnostics["error_message"] = "Sandbox compilation verification failure."
            current_code_attempt = candidate_code
            
        return False, original_code

    def _build_prompt(self, code: str, diag: dict) -> str:
        return f"""
        REPAIR PROMPT FOR CODE SUITE.
        Code containing error:
        {code}
        
        Error Traceback:
        {diag['traceback']}
        Error Message: {diag['error_message']}
        
        Output the corrected_code inside a JSON dictionary block.
        """

    def _parse_json_block(self, response: str) -> dict:
        import json
        try:
            return json.loads(response)
        except:
            return {"corrected_code": ""}
```

---

## 5. System Cross-References
*   For the self-healing process architecture manual, see [PART_14_AUTONOMOUS_AI_OPERATIONS.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/PART_14_AUTONOMOUS_AI_OPERATIONS.md).
*   For the core runtime error routing protocols, see [ENGINE_CORE_RUNTIME.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/ENGINE_CORE_RUNTIME.md).
*   For tracing schemas that record debugger actions, see [ENGINE_OBSERVABILITY_TELEMETRY.md](file:///Users/dronpancholi/Developer/01_Strategic/Venus/uaieos_parts/ENGINE_OBSERVABILITY_TELEMETRY.md).
