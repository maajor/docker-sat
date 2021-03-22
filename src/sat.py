import pysbs

def bake(config, cwd):
    handle = pysbs.batchtools.sbsbaker_run(json=config, cwd=cwd, output_handler=True)
    return handle

def _build_render_args(**kwargs):
    pargs = []
    if "output_path" in kwargs.keys():
        pargs.append("--output-path")
        pargs.append(kwargs['output_path'])
    if "output_name" in kwargs.keys():
        pargs.append("--output-name")
        pargs.append(kwargs['output_name'])
    if "entries" in kwargs.keys():
        for entry in kwargs['entries']:
            identifier, path = entry
            pargs.append("--set-entry")
            pargs.append("{0}@{1}".format(identifier, path))
    if "values" in kwargs.keys():
        for value in kwargs['values']:
            identifier, val = value
            pargs.append("--set-value")
            pargs.append("{0}@{1}".format(identifier, val))
    return pargs

def render(sbsar, **kwinputs):
    args = _build_render_args(**kwinputs)
    handle = pysbs.batchtools.sbsrender_render(sbsar, output_handler=True, *args)
    return handle