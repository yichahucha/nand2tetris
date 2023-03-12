import os,glob
from CompilationEngine import CompilationEngine

class JackAnalayzer:
    def __init__(self, filePath):
        if os.path.isdir(filePath):
            files = glob.glob(os.path.join(filePath, '*.jack'))
        else:
            files = [filePath]
        
        for file in files:
            engine = CompilationEngine(file)
            engine.outputVM()
    
if __name__ == "__main__":
    JackAnalayzer("../Pong")