import re
import os

for root, _, files in os.walk('.'):
    for f in files:
        if f.endswith('.py'):
            with open(os.path.join(root, f), 'r') as fp:
                for line in fp:
                    if 'CONF_PORT' in line:
                        print(f"Found in {os.path.join(root, f)}")
                        break
