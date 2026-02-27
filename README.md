
# Debug Probe

```py
import debugpy
debugpy.listen(("0.0.0.0", 5678))

print("Astept conexiunea debugger-ului...")
# Codul se va opri aici pana la atasarea debugger-ului din VS Code
debugpy.wait_for_client()

print("Debugger conectat! Rulez restul codului.")

```