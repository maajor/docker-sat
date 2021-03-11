import pysbs

def bake(config, cwd):
    return pysbs.batchtools.sbsbaker_run(json=config, cwd=cwd)
