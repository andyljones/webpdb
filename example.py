from webdebugger import post_mortem

try: 
    raise ValueError()
except:
    post_mortem()
