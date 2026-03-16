from violet_poolcontroller_api.api import VioletPoolAPI
import inspect

sig = inspect.signature(VioletPoolAPI.__init__)
print(sig)
