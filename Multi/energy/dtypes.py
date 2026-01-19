import numpy as np
import h5py

def get_event_dtype():
    dtype = []
    for v in ['veto_', '']:
        for r in ['er', 'nr']:
            dtype += [(f'{v}sum_{r}', np.float64)]
            dtype += [(f'{v}num_{r}', np.uint32)]
            for a in ['max', 'alt']:
                dtype += [(f'{v}{a}_{r}', np.float64)]
                for x in ['x', 'y', 'z', 't']:
                    dtype += [(f'{v}{a}_{r}_{x}', np.float64)]
                s = 'parentId'
                dtype += [(f'{v}{a}_{r}_{s}', np.uint32)]
                for s in ['type', 'parentType', 'creatorProcess', 'depositionProcess']:
                    dtype += [(f'{v}{a}_{r}_{s}', h5py.string_dtype())]
    return dtype

event_dtype = np.dtype([('runId', np.uint32), ('eventId', np.uint32),
                        ('nHits', np.uint32), ('nClusters', np.uint32),
                        ('nPrimaries', np.uint32)] + get_event_dtype())

primary_dtype = np.dtype([('runId', np.uint32), ('eventId', np.uint32),
                          ('nPrimaries', np.uint32),
                          ('primaryEnergy', np.float64),
                          ('primaryPx', np.float64), ('primaryPy', np.float64),
                          ('primaryPz', np.float64),
                          ('primaryX', np.float64), ('primaryY', np.float64),
                          ('primaryZ', np.float64),
                          ('primaryId', np.uint32),
                          ('primaryType', h5py.string_dtype())])

def get_cluster_dtype(nr_or_er):
    dtype = []
    for r in nr_or_er:
        for x in ['x', 'y', 'z', 't']:
            dtype += [(f'{r}{x}', np.float64)]
        for s in ['parentId']:
            dtype += [(f'{r}{s}', np.uint32)]
        for s in ['type', 'parentType', 'creatorProcess', 'depositionProcess', 'volume']:
            dtype += [(f'{r}{s}', h5py.string_dtype())]
    return dtype

energy_dtype = np.dtype([('runId', np.uint32), ('eventId', np.uint32),
                         ('energy', np.float64), ('label', np.uint32)] + get_cluster_dtype(['']))

cluster_dtype = np.dtype([('runId', np.uint32), ('eventId', np.uint32),
                          ('energy', np.float64), ('nr', np.float64),
                          ('er', np.float64)] + get_cluster_dtype(['er_', 'nr_']))

def set_nan_defaults(result):
    for field in result.dtype.names:
        if np.issubdtype(result.dtype[field], np.integer):
            result[field][:] = 0
        elif np.issubdtype(result.dtype[field], float):
            result[field][:] = np.nan
        elif np.issubdtype(result.dtype[field], object):
            result[field][:] = 'unknown'
