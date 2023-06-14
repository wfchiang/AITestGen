from functools import wraps 

# ====
# Decorator 
# ====
def analyze (): 
    def _analyze_wrapper (f): 
        # Analyze function "f" 
        print("Analyzing function {}".format(f)) 

        # Wrap the original function "f" and return 
        @wraps(f) 
        def _f_wrapper (*args, **kwargs): 
            return f(*args, **kwargs) 

        return _f_wrapper 
    
    return _analyze_wrapper