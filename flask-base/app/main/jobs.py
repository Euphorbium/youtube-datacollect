from flask.ext.rq import job


@job
def process(i):
    pass
    #  Long stuff to process
